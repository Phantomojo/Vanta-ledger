import 'dart:convert';
import 'dart:io';
import 'package:path_provider/path_provider.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'database_service.dart';
import '../models/account.dart';
import '../models/transaction.dart';
import '../models/category.dart';
import '../models/budget.dart';
import '../models/bill.dart';
import '../models/investment.dart';

class BackupService {
  final DatabaseService _db = DatabaseService();

  Future<String> exportData() async {
    final accounts = await _db.getAccounts();
    final transactions = await _db.getTransactions();
    final categories = await _db.getCategories();
    final budgets = await _db.getBudgets();
    final bills = await _db.getBills();
    final data = {
      'accounts': accounts.map((a) => a.toMap()).toList(),
      'transactions': transactions.map((t) => t.toMap()).toList(),
      'categories': categories.map((c) => c.toMap()).toList(),
      'budgets': budgets.map((b) => b.toMap()).toList(),
      'bills': bills.map((b) => b.toMap()).toList(),
    };
    return jsonEncode(data);
  }

  Future<void> saveBackupFile(BuildContext context) async {
    final json = await exportData();
    final dir = await getApplicationDocumentsDirectory();
    final file = File('${dir.path}/vanta_ledger_backup_${DateTime.now().millisecondsSinceEpoch}.json');
    await file.writeAsString(json);
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Backup saved: ${file.path}')));
  }

  Future<void> restoreFromFile(BuildContext context) async {
    final result = await FilePicker.platform.pickFiles(type: FileType.custom, allowedExtensions: ['json']);
    if (result != null && result.files.single.path != null) {
      final file = File(result.files.single.path!);
      final json = await file.readAsString();
      final data = jsonDecode(json);
      await _restoreData(data);
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Data restored.')));
    }
  }

  Future<void> _restoreData(Map<String, dynamic> data) async {
    // Optionally: clear existing data first
    // await _db.clearAll();
    for (final a in (data['accounts'] ?? [])) {
      await _db.insertAccount(AccountModel.fromMap(a));
    }
    for (final c in (data['categories'] ?? [])) {
      await _db.insertCategory(CategoryModel.fromMap(c));
    }
    for (final t in (data['transactions'] ?? [])) {
      await _db.insertTransaction(TransactionModel.fromMap(t));
    }
    for (final b in (data['budgets'] ?? [])) {
      await _db.insertBudget(BudgetModel.fromMap(b));
    }
    for (final b in (data['bills'] ?? [])) {
      await _db.insertBill(BillModel.fromMap(b));
    }
  }
} 