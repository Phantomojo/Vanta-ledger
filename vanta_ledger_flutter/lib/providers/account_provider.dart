import 'package:flutter/material.dart';
import '../models/account.dart';
import '../services/database_service.dart';

class AccountProvider extends ChangeNotifier {
  List<AccountModel> _accounts = [];
  List<AccountModel> get accounts => _accounts;

  final DatabaseService _db = DatabaseService();

  Future<void> loadAccounts() async {
    _accounts = await _db.getAccounts();
    notifyListeners();
  }

  Future<void> addAccount(AccountModel acc) async {
    await _db.insertAccount(acc);
    await loadAccounts();
  }

  Future<void> updateAccount(AccountModel acc) async {
    await _db.updateAccount(acc);
    await loadAccounts();
  }

  Future<void> deleteAccount(int id) async {
    await _db.deleteAccount(id);
    await loadAccounts();
  }
} 