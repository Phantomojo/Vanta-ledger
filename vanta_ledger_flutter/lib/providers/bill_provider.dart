import 'package:flutter/material.dart';
import '../models/bill.dart';
import '../services/database_service.dart';
import '../services/notifications_service.dart';

class BillProvider extends ChangeNotifier {
  List<BillModel> _bills = [];
  List<BillModel> get bills => _bills;
  final DatabaseService _db = DatabaseService();
  final NotificationsService _notifications = NotificationsService();

  Future<void> loadBills() async {
    _bills = await _db.getBills();
    notifyListeners();
  }

  Future<void> addBill(BillModel bill) async {
    await _db.insertBill(bill);
    await loadBills();
    if (bill.remindDaysBefore != null && bill.dueDate.isAfter(DateTime.now())) {
      await _notifications.scheduleBillReminder(
        billId: bill.id ?? DateTime.now().millisecondsSinceEpoch,
        title: 'Bill Due: ${bill.name}',
        body: 'Amount: ${bill.amount.toStringAsFixed(2)} due on ${bill.dueDate.toLocal().toString().split(' ')[0]}',
        scheduledDate: bill.dueDate.subtract(Duration(days: bill.remindDaysBefore!)),
      );
    }
  }

  Future<void> updateBill(BillModel bill) async {
    await _db.updateBill(bill);
    await loadBills();
    await _notifications.cancelBillReminder(bill.id!);
    if (!bill.isPaid && bill.remindDaysBefore != null && bill.dueDate.isAfter(DateTime.now())) {
      await _notifications.scheduleBillReminder(
        billId: bill.id!,
        title: 'Bill Due: ${bill.name}',
        body: 'Amount: ${bill.amount.toStringAsFixed(2)} due on ${bill.dueDate.toLocal().toString().split(' ')[0]}',
        scheduledDate: bill.dueDate.subtract(Duration(days: bill.remindDaysBefore!)),
      );
    }
  }

  Future<void> deleteBill(int id) async {
    await _db.deleteBill(id);
    await loadBills();
    await _notifications.cancelBillReminder(id);
  }

  Future<void> markAsPaid(int id, bool isPaid) async {
    final bill = _bills.firstWhere((b) => b.id == id);
    await _db.updateBill(bill.copyWith(isPaid: isPaid));
    await loadBills();
    if (isPaid) {
      await _notifications.cancelBillReminder(id);
    } else if (bill.remindDaysBefore != null && bill.dueDate.isAfter(DateTime.now())) {
      await _notifications.scheduleBillReminder(
        billId: id,
        title: 'Bill Due: ${bill.name}',
        body: 'Amount: ${bill.amount.toStringAsFixed(2)} due on ${bill.dueDate.toLocal().toString().split(' ')[0]}',
        scheduledDate: bill.dueDate.subtract(Duration(days: bill.remindDaysBefore!)),
      );
    }
  }
} 