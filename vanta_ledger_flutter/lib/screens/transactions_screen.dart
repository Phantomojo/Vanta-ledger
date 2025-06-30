import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/transaction_provider.dart';
import '../models/transaction.dart';
import 'add_transaction_screen.dart';
import 'package:intl/intl.dart';
import 'package:flutter/services.dart';

class TransactionsScreen extends StatefulWidget {
  const TransactionsScreen({super.key});

  @override
  State<TransactionsScreen> createState() => _TransactionsScreenState();
}

class _TransactionsScreenState extends State<TransactionsScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<TransactionProvider>(context, listen: false).loadTransactions();
    });
  }

  @override
  Widget build(BuildContext context) {
    print('TransactionsScreen is building!');
    final transactions = context.watch<TransactionProvider>().transactions;
    final provider = Provider.of<TransactionProvider>(context, listen: false);
    final grouped = <String, List<TransactionModel>>{};
    for (final tx in transactions) {
      final dateStr = DateFormat.yMMMMd().format(tx.date);
      grouped.putIfAbsent(dateStr, () => []).add(tx);
    }
    final dateKeys = grouped.keys.toList();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Transactions'),
        actions: [
          IconButton(icon: const Icon(Icons.search), onPressed: () {/* TODO: Search/filter */}),
          IconButton(icon: const Icon(Icons.filter_list), onPressed: () {/* TODO: Advanced filter */}),
          IconButton(icon: const Icon(Icons.more_vert), onPressed: () {/* TODO: Bulk edit, import/export */}),
        ],
      ),
      body: Column(
        children: [
          Container(
            width: double.infinity,
            color: Colors.amber,
            padding: const EdgeInsets.all(8),
            child: const Text('DEBUG: TransactionsScreen loaded', textAlign: TextAlign.center),
          ),
          Expanded(
            child: transactions.isEmpty
                ? const Center(child: Text('No transactions yet.'))
                : ListView.builder(
                    itemCount: dateKeys.length,
                    itemBuilder: (context, i) {
                      final date = dateKeys[i];
                      final txs = grouped[date]!;
                      return Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                            child: Text(date, style: Theme.of(context).textTheme.titleSmall),
                          ),
                          ...txs.map((tx) => Dismissible(
                                key: ValueKey(tx.id),
                                direction: DismissDirection.endToStart,
                                background: Container(
                                  color: Colors.red,
                                  alignment: Alignment.centerRight,
                                  padding: const EdgeInsets.symmetric(horizontal: 20),
                                  child: const Icon(Icons.delete, color: Colors.white),
                                ),
                                onDismissed: (_) async {
                                  HapticFeedback.mediumImpact();
                                  await provider.deleteTransaction(tx.id!);
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    SnackBar(
                                      content: Text('Transaction deleted'),
                                      action: SnackBarAction(
                                        label: 'Undo',
                                        onPressed: () async {
                                          await provider.addTransaction(tx);
                                        },
                                      ),
                                    ),
                                  );
                                },
                                child: Card(
                                  margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                                  child: ListTile(
                                    leading: CircleAvatar(
                                      backgroundColor: tx.type == TransactionType.expense ? Colors.red[100] : Colors.green[100],
                                      child: Icon(
                                        tx.type == TransactionType.expense ? Icons.arrow_downward : Icons.arrow_upward,
                                        color: tx.type == TransactionType.expense ? Colors.red : Colors.green,
                                      ),
                                    ),
                                    title: Text(tx.description),
                                    subtitle: Text('Ksh ${tx.amount.toStringAsFixed(2)}'),
                                    trailing: Text(tx.type == TransactionType.expense ? 'Expense' : 'Income'),
                                    onTap: () async {
                                      HapticFeedback.selectionClick();
                                      await Navigator.push(
                                        context,
                                        MaterialPageRoute(
                                          builder: (context) => AddTransactionScreen(
                                            existing: tx,
                                          ),
                                        ),
                                      );
                                      if (mounted) {
                                        provider.loadTransactions();
                                      }
                                    },
                                    onLongPress: () {/* TODO: Bulk select */},
                                  ),
                                ),
                              )),
                        ],
                      );
                    },
                  ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () async {
          await Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => const AddTransactionScreen()),
          );
          if (mounted) {
            provider.loadTransactions();
          }
        },
        child: const Icon(Icons.add),
      ),
    );
  }
} 