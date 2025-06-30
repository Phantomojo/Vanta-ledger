import 'package:flutter_test/flutter_test.dart';
import 'package:vanta_ledger_flutter/providers/transaction_provider.dart';
import 'package:vanta_ledger_flutter/models/transaction.dart';

void main() {
  test('TransactionProvider add, load, and delete', () async {
    final provider = TransactionProvider();
    final tx = TransactionModel(
      id: null,
      amount: 100.0,
      type: 'income',
      date: DateTime.now(),
      categoryId: 1,
      accountId: 1,
      description: 'Test',
      cleared: false,
    );
    await provider.addTransaction(tx);
    await provider.loadTransactions();
    expect(provider.transactions.any((t) => t.amount == 100.0), true);
    final added = provider.transactions.firstWhere((t) => t.amount == 100.0);
    await provider.deleteTransaction(added.id!);
    await provider.loadTransactions();
    expect(provider.transactions.any((t) => t.amount == 100.0), false);
  });
} 