import 'package:flutter/material.dart';
import '../models/transaction.dart';
import '../services/database_service.dart';
import 'package:collection/collection.dart';
import 'dart:convert';
import 'package:flutter/services.dart';

class TransactionProvider extends ChangeNotifier {
  List<TransactionModel> _transactions = [];
  List<TransactionModel> get transactions => _transactions;

  final DatabaseService _db = DatabaseService();

  Future<void> loadTransactions() async {
    _transactions = await _db.getTransactions();
    notifyListeners();
  }

  Future<void> addTransaction(TransactionModel tx) async {
    await _db.insertTransaction(tx);
    await loadTransactions();
  }

  Future<void> updateTransaction(TransactionModel tx) async {
    await _db.updateTransaction(tx);
    await loadTransactions();
  }

  Future<void> deleteTransaction(int id) async {
    await _db.deleteTransaction(id);
    await loadTransactions();
  }

  Future<void> updateClearedStatus(int id, bool cleared) async {
    final db = _db;
    final tx = _transactions.firstWhereOrNull((t) => t.id == id);
    if (tx != null) {
      final updated = tx.copyWith(cleared: cleared);
      await db.updateTransaction(updated);
      await loadTransactions();
    }
  }

  TransactionModel? getTransactionById(int id) {
    return _transactions.firstWhereOrNull((t) => t.id == id);
  }
} 