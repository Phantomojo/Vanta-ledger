import 'package:flutter/material.dart';
import '../models/currency.dart';

class CurrencyProvider extends ChangeNotifier {
  final List<CurrencyModel> _currencies = [
    CurrencyModel(code: 'USD', name: 'US Dollar', symbol: ' 24'),
    CurrencyModel(code: 'KES', name: 'Kenyan Shilling', symbol: 'Ksh'),
    CurrencyModel(code: 'EUR', name: 'Euro', symbol: ' 80'),
    CurrencyModel(code: 'GBP', name: 'British Pound', symbol: ' A3'),
    CurrencyModel(code: 'JPY', name: 'Japanese Yen', symbol: ' A5'),
    // Add more as needed
  ];
  CurrencyModel _selected = CurrencyModel(code: 'USD', name: 'US Dollar', symbol: ' 24');

  List<CurrencyModel> get currencies => _currencies;
  CurrencyModel get selected => _selected;

  void selectCurrency(CurrencyModel currency) {
    _selected = currency;
    notifyListeners();
  }
} 