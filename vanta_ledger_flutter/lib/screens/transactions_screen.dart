import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/transaction_provider.dart';
import '../models/transaction.dart';
import 'add_transaction_screen.dart';
import 'package:intl/intl.dart';
import 'package:flutter/services.dart';
import 'package:csv/csv.dart';
import 'package:file_picker/file_picker.dart';
import 'dart:io';
import 'package:flutter_svg/flutter_svg.dart';
import '../wakanda_text.dart';
import 'dashboard_screen.dart';
import 'package:flutter/rendering.dart';
import 'dart:ui';

class TransactionsScreen extends StatefulWidget {
  const TransactionsScreen({super.key});

  @override
  State<TransactionsScreen> createState() => _TransactionsScreenState();
}

class _TransactionsScreenState extends State<TransactionsScreen> {
  String _search = '';
  int _filterType = -1; // -1 = all, 0 = expense, 1 = income
  bool _selectionMode = false;
  final Set<int> _selectedIds = {};
  int _clearedFilter = -1; // -1 = all, 0 = uncleared, 1 = cleared

  void _toggleSelection(int id) {
    setState(() {
      if (_selectedIds.contains(id)) {
        _selectedIds.remove(id);
      } else {
        _selectedIds.add(id);
      }
      _selectionMode = _selectedIds.isNotEmpty;
    });
  }
  void _clearSelection() {
    setState(() {
      _selectedIds.clear();
      _selectionMode = false;
    });
  }

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
    final transactions = context.watch<TransactionProvider>().transactions
        .where((tx) => _search.isEmpty || tx.description.toLowerCase().contains(_search.toLowerCase()))
        .where((tx) => _filterType == -1 || tx.type.index == _filterType)
        .where((tx) => _clearedFilter == -1 || (tx.cleared ? 1 : 0) == _clearedFilter)
        .toList();
    final provider = Provider.of<TransactionProvider>(context, listen: false);
    final grouped = <String, List<TransactionModel>>{};
    for (final tx in transactions) {
      final dateStr = DateFormat.yMMMMd().format(tx.date);
      grouped.putIfAbsent(dateStr, () => []).add(tx);
    }
    final dateKeys = grouped.keys.toList();

    return Scaffold(
      appBar: GlassyAppBar(
        title: 'Transactions',
      ),
      body: Stack(
        children: [
          Positioned.fill(
            child: Image.asset(
              'assets/images/purple_glass_bg.jpg',
              fit: BoxFit.cover,
            ),
          ),
          Positioned.fill(
            child: Container(
              color: Colors.black.withOpacity(0.45),
            ),
          ),
          // Main content
          Column(
            children: [
              Container(
                width: double.infinity,
                color: Colors.amber,
                padding: const EdgeInsets.all(8),
                child: const Text('DEBUG: TransactionsScreen loaded', textAlign: TextAlign.center),
              ),
              Expanded(
                child: provider.transactions.isEmpty
                    ? Center(
                        child: Semantics(
                          label: 'No transactions',
                          hint: 'Add your first transaction to get started',
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(Icons.receipt_long, size: 80, color: Colors.grey[500], semanticLabel: 'No transactions icon'),
                              const SizedBox(height: 16),
                              Text('No transactions yet.', style: TextStyle(fontSize: 18, color: Colors.white)),
                              const SizedBox(height: 8),
                              Text('Add your first transaction to get started!', style: TextStyle(color: Colors.white70)),
                            ],
                          ),
                        ),
                      )
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
                                    direction: _selectionMode ? DismissDirection.none : DismissDirection.endToStart,
                                    background: Container(
                                      color: Colors.red,
                                      alignment: Alignment.centerRight,
                                      padding: const EdgeInsets.symmetric(horizontal: 20),
                                      child: const Icon(Icons.delete, color: Colors.white),
                                    ),
                                    onDismissed: _selectionMode
                                        ? null
                                        : (_) {
                                            HapticFeedback.mediumImpact();
                                            _deleteTransaction(tx.id!);
                                          },
                                    child: Card(
                                      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                                      child: ListTile(
                                        leading: _selectionMode
                                            ? Checkbox(
                                                value: _selectedIds.contains(tx.id),
                                                onChanged: (_) => _toggleSelection(tx.id!),
                                              )
                                            : CircleAvatar(
                                                backgroundColor: tx.type == TransactionType.expense ? Colors.red[100] : Colors.green[100],
                                                child: Image.asset(
                                                  'assets/images/icon-512.png',
                                                  height: 28,
                                                  width: 28,
                                                  color: tx.type == TransactionType.expense ? Colors.red : Colors.green,
                                                ),
                                              ),
                                        title: Row(
                                          children: [
                                            Expanded(child: Text(tx.description)),
                                            Checkbox(
                                              value: tx.cleared,
                                              onChanged: (val) {
                                                context.read<TransactionProvider>().updateClearedStatus(tx.id!, val ?? false);
                                              },
                                              activeColor: Colors.deepPurple,
                                              materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                                            ),
                                          ],
                                        ),
                                        subtitle: Text('Ksh ${tx.amount.toStringAsFixed(2)}'),
                                        trailing: Row(
                                          mainAxisSize: MainAxisSize.min,
                                          children: [
                                            IconButton(
                                              icon: const Icon(Icons.edit),
                                              onPressed: () => _editTransaction(tx),
                                              constraints: const BoxConstraints(minWidth: 48, minHeight: 48),
                                            ),
                                            IconButton(
                                              icon: const Icon(Icons.delete),
                                              onPressed: () => _deleteTransaction(tx.id!),
                                              constraints: const BoxConstraints(minWidth: 48, minHeight: 48),
                                            ),
                                          ],
                                        ),
                                        onTap: _selectionMode
                                            ? () => _toggleSelection(tx.id!)
                                            : () async {
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
                                        onLongPress: () {
                                          if (!_selectionMode) _toggleSelection(tx.id!);
                                        },
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
        ],
      ),
      floatingActionButton: !_selectionMode
          ? Padding(
              padding: const EdgeInsets.only(bottom: 70),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(18),
                child: BackdropFilter(
                  filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
                  child: FloatingActionButton(
                    backgroundColor: Colors.white.withOpacity(0.18),
                    foregroundColor: Colors.deepPurpleAccent,
                    elevation: 0,
                    onPressed: _addTransaction,
                    child: const Icon(Icons.add),
                  ),
                ),
              ),
            )
          : null,
    );
  }

  void _addTransaction() async {
    HapticFeedback.mediumImpact();
    await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => AddTransactionScreen(),
      ),
    );
    if (mounted) {
      context.read<TransactionProvider>().loadTransactions();
    }
  }

  void _deleteTransaction(int id) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Transaction'),
        content: const Text('Are you sure you want to delete this transaction?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')),
          ElevatedButton(onPressed: () => Navigator.pop(context, true), child: const Text('Delete')),
        ],
      ),
    );
    if (confirm == true) {
      HapticFeedback.lightImpact();
      final provider = Provider.of<TransactionProvider>(context, listen: false);
      await provider.deleteTransaction(id);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Row(
              children: const [
                Icon(Icons.check_circle, color: Colors.green),
                SizedBox(width: 8),
                Text('Transaction deleted!'),
              ],
            ),
            duration: const Duration(seconds: 2),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    }
  }

  void _showError(String message) {
    HapticFeedback.heavyImpact();
    // ... existing code ...
  }

  void _editTransaction(TransactionModel tx) {
    // TODO: Implement edit logic or show edit dialog
  }
} 