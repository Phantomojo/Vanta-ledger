import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:json_annotation/json_annotation.dart';
import 'package:provider/provider.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({Key? key}) : super(key: key);

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Dashboard'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(8.0),
        child: Column(
          children: [
            if (kDebugMode)
              Column(
                children: [
                  Center(
                    child: ElevatedButton(
                      onPressed: () async {
                        final data = await rootBundle.loadString('assets/test_data/transactions_sample.json');
                        final List<dynamic> jsonList = json.decode(data);
                        final txProvider = context.read<TransactionProvider>();
                        for (final tx in jsonList) {
                          await txProvider.addTransaction(TransactionModel(
                            amount: tx['amount'],
                            description: tx['description'],
                            date: DateTime.parse(tx['date']),
                            categoryId: tx['categoryId'],
                            accountId: tx['accountId'],
                            type: tx['type'] == 'income' ? TransactionType.income : TransactionType.expense,
                            recurrence: RecurrenceType.values[tx['recurrence'] ?? 0],
                            cleared: tx['cleared'] ?? false,
                          ));
                        }
                        if (context.mounted) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Test data imported!')),
                          );
                        }
                      },
                      child: const Text('Import 1 Year Test Data'),
                    ),
                  ),
                  const SizedBox(height: 8),
                  Center(
                    child: ElevatedButton(
                      onPressed: () async {
                        final data = await rootBundle.loadString('assets/test_data/transactions_huge.json');
                        final List<dynamic> jsonList = json.decode(data);
                        final txProvider = context.read<TransactionProvider>();
                        for (final tx in jsonList) {
                          await txProvider.addTransaction(TransactionModel(
                            amount: tx['amount'],
                            description: tx['description'],
                            date: DateTime.parse(tx['date']),
                            categoryId: tx['categoryId'],
                            accountId: tx['accountId'],
                            type: tx['type'] == 'income' ? TransactionType.income : TransactionType.expense,
                            recurrence: RecurrenceType.values[tx['recurrence'] ?? 0],
                            cleared: tx['cleared'] ?? false,
                          ));
                        }
                        if (context.mounted) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Huge test data imported!')),
                          );
                        }
                      },
                      child: const Text('Import Huge Test Data (10,000)'),
                    ),
                  ),
                ],
              ),
          ],
        ),
      ),
    );
  }
} 