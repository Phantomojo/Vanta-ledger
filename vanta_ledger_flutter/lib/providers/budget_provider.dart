import 'package:flutter/material.dart';
import '../models/budget.dart';
import '../services/database_service.dart';

class BudgetProvider extends ChangeNotifier {
  List<BudgetModel> _budgets = [];
  List<BudgetModel> get budgets => _budgets;
  final DatabaseService _db = DatabaseService();

  Future<void> loadBudgets() async {
    _budgets = await _db.getBudgets();
    notifyListeners();
  }

  Future<void> addBudget(BudgetModel budget) async {
    await _db.insertBudget(budget);
    await loadBudgets();
  }

  Future<void> updateBudget(BudgetModel budget) async {
    await _db.updateBudget(budget);
    await loadBudgets();
  }

  Future<void> deleteBudget(int id) async {
    await _db.deleteBudget(id);
    await loadBudgets();
  }
} 