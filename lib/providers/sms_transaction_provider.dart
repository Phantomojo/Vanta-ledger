import 'package:flutter/material.dart';
import 'package:telephony/telephony.dart';

class SMSTransaction {
  final String sender;
  final String message;
  final DateTime date;
  final double amount;
  final String type; // 'in' or 'out'
  final String provider;

  SMSTransaction({
    required this.sender,
    required this.message,
    required this.date,
    required this.amount,
    required this.type,
    required this.provider,
  });
}

class SMSTransactionProvider extends ChangeNotifier {
  final List<SMSTransaction> _transactions = [];
  List<SMSTransaction> get transactions => _transactions;

  final Telephony telephony = Telephony.instance;

  Future<void> loadSMSTransactions() async {
    final bool? permissionsGranted = await telephony.requestSmsPermissions;
    if (permissionsGranted != true) return;
    final List<SmsMessage> messages = await telephony.getInboxSms(columns: [SmsColumn.ADDRESS, SmsColumn.BODY, SmsColumn.DATE]);
    _transactions.clear();
    for (final msg in messages) {
      final parsed = _parseFinancialSMS(msg);
      if (parsed != null) _transactions.add(parsed);
    }
    notifyListeners();
  }

  SMSTransaction? _parseFinancialSMS(SmsMessage msg) {
    // MPesa example
    final mpesaPattern = RegExp(r"([A-Z0-9]+) Confirmed\. (Ksh|KES) ([\d,]+\.\d{2}) (sent to|received from|on) (.+?) on (\d{1,2}/\d{1,2}/\d{2,4})");
    final bankPattern = RegExp(r"(credited|debited) with (KES|Ksh) ([\d,]+\.\d{2}) on (\d{1,2}-[A-Za-z]{3}-\d{2,4})");
    final body = msg.body ?? '';
    final sender = msg.address ?? '';
    final date = DateTime.fromMillisecondsSinceEpoch(msg.date ?? 0);
    // MPesa
    final mpesaMatch = mpesaPattern.firstMatch(body);
    if (mpesaMatch != null) {
      final amount = double.tryParse(mpesaMatch.group(3)!.replaceAll(',', '')) ?? 0.0;
      final type = body.contains('received from') ? 'in' : 'out';
      return SMSTransaction(
        sender: sender,
        message: body,
        date: date,
        amount: amount,
        type: type,
        provider: 'MPesa',
      );
    }
    // Bank
    final bankMatch = bankPattern.firstMatch(body);
    if (bankMatch != null) {
      final amount = double.tryParse(bankMatch.group(3)!.replaceAll(',', '')) ?? 0.0;
      final type = bankMatch.group(1) == 'credited' ? 'in' : 'out';
      return SMSTransaction(
        sender: sender,
        message: body,
        date: date,
        amount: amount,
        type: type,
        provider: 'Bank',
      );
    }
    // Add more providers here...
    return null;
  }
} 