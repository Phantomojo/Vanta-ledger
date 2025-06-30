import 'package:flutter/material.dart';
import '../services/database_service.dart';
import '../models/transaction.dart';
import '../models/account.dart';

class ReportsProvider extends ChangeNotifier {
  final DatabaseService _db = DatabaseService();

  List<TransactionModel> _transactions = [];
  List<AccountModel> _accounts = [];

  Map<String, double> incomeByMonth = {};
  Map<String, double> expenseByMonth = {};
  List<double> netWorthOverTime = [];
  Map<String, double> categoryBreakdown = {};

  Future<void> loadData() async {
    _transactions = await _db.getTransactions();
    _accounts = await _db.getAccounts();
    _computeReports();
    notifyListeners();
  }

  void _computeReports() {
    incomeByMonth.clear();
    expenseByMonth.clear();
    categoryBreakdown.clear();
    netWorthOverTime.clear();
    Map<String, double> netWorthMap = {};
    double runningNetWorth = _accounts.fold(0.0, (sum, a) => sum + a.balance);
    for (final tx in _transactions) {
      final month = '${tx.date.year}-${tx.date.month.toString().padLeft(2, '0')}';
      if (tx.type == 'income') {
        incomeByMonth[month] = (incomeByMonth[month] ?? 0) + tx.amount;
        runningNetWorth += tx.amount;
      } else {
        expenseByMonth[month] = (expenseByMonth[month] ?? 0) + tx.amount;
        runningNetWorth -= tx.amount;
      }
      netWorthMap[month] = runningNetWorth;
      categoryBreakdown[tx.categoryName ?? 'Other'] =
          (categoryBreakdown[tx.categoryName ?? 'Other'] ?? 0) + tx.amount;
    }
    netWorthOverTime = netWorthMap.values.toList();
  }
} 