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
        title: _selectionMode
            ? Text('${_selectedIds.length} selected')
            : const Text('Transactions'),
        actions: [
          if (_selectionMode)
            IconButton(
              icon: const Icon(Icons.delete),
              onPressed: () async {
                for (final id in _selectedIds) {
                  await provider.deleteTransaction(id);
                }
                _clearSelection();
              },
            ),
          if (_selectionMode)
            IconButton(
              icon: const Icon(Icons.close),
              onPressed: _clearSelection,
            ),
          if (!_selectionMode)
            IconButton(
              icon: const Icon(Icons.filter_list),
              onPressed: () async {
                final result = await showDialog<Map<String, int>>(
                  context: context,
                  builder: (context) => SimpleDialog(
                    title: const Text('Filter'),
                    children: [
                      const Padding(
                        padding: EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                        child: Text('Type'),
                      ),
                      SimpleDialogOption(
                        child: const Text('All'),
                        onPressed: () => Navigator.pop(context, {'type': -1, 'cleared': _clearedFilter}),
                      ),
                      SimpleDialogOption(
                        child: const Text('Expense'),
                        onPressed: () => Navigator.pop(context, {'type': 0, 'cleared': _clearedFilter}),
                      ),
                      SimpleDialogOption(
                        child: const Text('Income'),
                        onPressed: () => Navigator.pop(context, {'type': 1, 'cleared': _clearedFilter}),
                      ),
                      const Divider(),
                      const Padding(
                        padding: EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                        child: Text('Cleared'),
                      ),
                      SimpleDialogOption(
                        child: const Text('All'),
                        onPressed: () => Navigator.pop(context, {'type': _filterType, 'cleared': -1}),
                      ),
                      SimpleDialogOption(
                        child: const Text('Cleared'),
                        onPressed: () => Navigator.pop(context, {'type': _filterType, 'cleared': 1}),
                      ),
                      SimpleDialogOption(
                        child: const Text('Uncleared'),
                        onPressed: () => Navigator.pop(context, {'type': _filterType, 'cleared': 0}),
                      ),
                    ],
                  ),
                );
                if (result != null) setState(() {
                  _filterType = result['type']!;
                  _clearedFilter = result['cleared']!;
                });
              },
            ),
          if (!_selectionMode)
            IconButton(
              icon: const Icon(Icons.download),
              onPressed: () async {
                final txs = context.read<TransactionProvider>().transactions;
                final rows = [
                  [
                    'ID', 'Amount', 'Description', 'Date', 'CategoryId', 'AccountId', 'Type', 'Recurrence'
                  ],
                  ...txs.map((tx) => [
                        tx.id ?? '',
                        tx.amount,
                        tx.description,
                        tx.date.toIso8601String(),
                        tx.categoryId,
                        tx.accountId,
                        tx.type.index,
                        tx.recurrence.index,
                      ]),
                ];
                final csvData = const ListToCsvConverter().convert(rows);
                final output = await FilePicker.platform.getDirectoryPath();
                if (output != null) {
                  final file = File('$output/vanta_ledger_export.csv');
                  await file.writeAsString(csvData);
                  if (context.mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Exported to vanta_ledger_export.csv')),
                    );
                  }
                }
              },
            ),
          if (!_selectionMode)
            IconButton(icon: const Icon(Icons.more_vert), onPressed: () async {
              // Import from CSV
              final result = await FilePicker.platform.pickFiles(type: FileType.custom, allowedExtensions: ['csv']);
              if (result != null && result.files.single.path != null) {
                final file = File(result.files.single.path!);
                final csvString = await file.readAsString();
                final rows = const CsvToListConverter().convert(csvString, eol: '\n');
                // Skip header row
                for (var i = 1; i < rows.length; i++) {
                  final row = rows[i];
                  try {
                    final tx = TransactionModel(
                      amount: double.tryParse(row[1].toString()) ?? 0.0,
                      description: row[2].toString(),
                      date: DateTime.tryParse(row[3].toString()) ?? DateTime.now(),
                      categoryId: int.tryParse(row[4].toString()) ?? 1,
                      accountId: int.tryParse(row[5].toString()) ?? 1,
                      type: TransactionType.values[int.tryParse(row[6].toString()) ?? 0],
                      recurrence: RecurrenceType.values[int.tryParse(row[7].toString()) ?? 0],
                    );
                    await context.read<TransactionProvider>().addTransaction(tx);
                  } catch (_) {}
                }
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Imported transactions from CSV')),
                  );
                }
              }
            }),
        ],
        bottom: !_selectionMode
            ? PreferredSize(
                preferredSize: const Size.fromHeight(56),
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  child: TextField(
                    decoration: InputDecoration(
                      hintText: 'Search transactions...',
                      prefixIcon: const Icon(Icons.search),
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                      filled: true,
                      fillColor: Theme.of(context).colorScheme.surfaceVariant,
                    ),
                    onChanged: (val) => setState(() => _search = val),
                  ),
                ),
              )
            : null,
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
                                            child: Icon(
                                              tx.type == TransactionType.expense ? Icons.arrow_downward : Icons.arrow_upward,
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
      floatingActionButton: !_selectionMode
          ? FloatingActionButton(
              onPressed: _addTransaction,
              tooltip: 'Add Transaction',
              child: const Icon(Icons.add, semanticLabel: 'Add Transaction'),
            )
          : null,
    );
  }

  void _addTransaction() async {
    // ... existing code ...
    HapticFeedback.mediumImpact();
    // ... existing code ...
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Row(
            children: const [
              Icon(Icons.check_circle, color: Colors.green),
              SizedBox(width: 8),
              Text('Transaction added!'),
            ],
          ),
          duration: const Duration(seconds: 2),
          behavior: SnackBarBehavior.floating,
        ),
      );
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