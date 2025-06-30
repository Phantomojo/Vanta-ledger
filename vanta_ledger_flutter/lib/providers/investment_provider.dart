import 'package:flutter/material.dart';
import '../models/investment.dart';
import '../services/database_service.dart';

class InvestmentProvider extends ChangeNotifier {
  List<InvestmentModel> _investments = [];
  List<InvestmentModel> get investments => _investments;
  final DatabaseService _db = DatabaseService();

  Future<void> loadInvestments() async {
    _investments = await _db.getInvestments();
    notifyListeners();
  }

  Future<void> addInvestment(InvestmentModel investment) async {
    await _db.insertInvestment(investment);
    await loadInvestments();
  }

  Future<void> updateInvestment(InvestmentModel investment) async {
    await _db.updateInvestment(investment);
    await loadInvestments();
  }

  Future<void> deleteInvestment(int id) async {
    await _db.deleteInvestment(id);
    await loadInvestments();
  }
} 