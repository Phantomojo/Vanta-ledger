import 'package:flutter/material.dart';
import 'package:collection/collection.dart';

enum TransactionType { income, expense }

enum RecurrenceType { none, daily, weekly, monthly, yearly }

class TransactionModel {
  final int? id;
  final double amount;
  final String description;
  final DateTime date;
  final int categoryId;
  final int accountId;
  final TransactionType type;
  final RecurrenceType recurrence;
  final bool cleared;
  final String? categoryName;

  TransactionModel({
    this.id,
    required this.amount,
    required this.description,
    required this.date,
    required this.categoryId,
    required this.accountId,
    required this.type,
    this.recurrence = RecurrenceType.none,
    this.cleared = false,
    this.categoryName,
  });

  TransactionModel copyWith({
    int? id,
    double? amount,
    String? description,
    DateTime? date,
    int? categoryId,
    int? accountId,
    TransactionType? type,
    RecurrenceType? recurrence,
    bool? cleared,
    String? categoryName,
  }) {
    return TransactionModel(
      id: id ?? this.id,
      amount: amount ?? this.amount,
      description: description ?? this.description,
      date: date ?? this.date,
      categoryId: categoryId ?? this.categoryId,
      accountId: accountId ?? this.accountId,
      type: type ?? this.type,
      recurrence: recurrence ?? this.recurrence,
      cleared: cleared ?? this.cleared,
      categoryName: categoryName ?? this.categoryName,
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'amount': amount,
      'description': description,
      'date': date.toIso8601String(),
      'categoryId': categoryId,
      'accountId': accountId,
      'type': type.name,
      'recurrence': recurrence.index,
      'cleared': cleared ? 1 : 0,
      'categoryName': categoryName,
    };
  }

  factory TransactionModel.fromMap(Map<String, dynamic> map) {
    final type = TransactionType.values.firstWhereOrNull((e) => e.name == map['type']) ?? TransactionType.expense;
    final recurrence = (map['recurrence'] is int && (map['recurrence'] as int) < RecurrenceType.values.length)
      ? RecurrenceType.values[map['recurrence'] as int]
      : RecurrenceType.none;
    return TransactionModel(
      id: map['id'] as int?,
      amount: map['amount'] as double,
      description: map['description'] as String,
      date: DateTime.parse(map['date'] as String),
      categoryId: map['categoryId'] as int,
      accountId: map['accountId'] as int,
      type: type,
      recurrence: recurrence,
      cleared: (map['cleared'] ?? 0) == 1,
      categoryName: map['categoryName'] as String?,
    );
  }
} 