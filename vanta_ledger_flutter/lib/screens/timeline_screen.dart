import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/transaction_provider.dart';
import '../models/transaction.dart';
import 'add_transaction_screen.dart';
import 'package:flutter_svg/flutter_svg.dart';

class TimelineScreen extends StatefulWidget {
  const TimelineScreen({super.key});

  @override
  State<TimelineScreen> createState() => _TimelineScreenState();
}

class _TimelineScreenState extends State<TimelineScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<TransactionProvider>(context, listen: false).loadTransactions();
    });
  }

  @override
  Widget build(BuildContext context) {
    final transactions = context.watch<TransactionProvider>().transactions;
    return Scaffold(
      appBar: AppBar(
        leading: Padding(
          padding: const EdgeInsets.all(8.0),
          child: SvgPicture.asset(
            'assets/images/app_logo_placeholder.svg',
            height: 32,
            width: 32,
            semanticsLabel: 'Vanta Ledger Logo',
          ),
        ),
        title: const Text('Timeline'),
      ),
      body: transactions.isEmpty
          ? const Center(child: Text('No transactions yet.'))
          : ListView.builder(
              itemCount: transactions.length,
              itemBuilder: (context, index) {
                final tx = transactions[index];
                return ListTile(
                  leading: CircleAvatar(
                    child: Text(tx.amount.toStringAsFixed(0)),
                  ),
                  title: Text(tx.description),
                  subtitle: Text(tx.date.toIso8601String().split('T').first),
                  trailing: Text(tx.type == 0 ? 'Expense' : 'Income'),
                );
              },
            ),
      // floatingActionButton: FloatingActionButton(
      //   onPressed: () async {
      //     await Navigator.push(
      //       context,
      //       MaterialPageRoute(builder: (context) => const AddTransactionScreen()),
      //     );
      //     if (mounted) {
      //       Provider.of<TransactionProvider>(context, listen: false).loadTransactions();
      //     }
      //   },
      //   child: const Icon(Icons.add),
      // ),
    );
  }
} 