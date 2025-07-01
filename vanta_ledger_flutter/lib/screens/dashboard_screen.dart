import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/transaction_provider.dart';
import '../models/transaction.dart';
import 'timeline_screen.dart';
import 'category_screen.dart';
import 'account_screen.dart';
import 'add_transaction_screen.dart';
// import 'package:fl_chart/fl_chart.dart';
import '../providers/category_provider.dart';
import '../providers/account_provider.dart';
import 'dart:math';
import '../models/category.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:flutter/foundation.dart';
import 'dart:convert';
import 'package:flutter/services.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 900),
    );
    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final transactions = context.watch<TransactionProvider>().transactions;
    final categories = context.watch<CategoryProvider>().categories;
    final accounts = context.read<AccountProvider>().accounts;
    final totalExpenses = transactions
        .where((tx) => tx.type == TransactionType.expense)
        .fold<double>(0.0, (sum, tx) => sum + tx.amount);
    final totalTransactions = transactions.length;
    final recentTransactions = transactions.take(5).toList();

    // --- FILTER CONTROLS ---
    DateTime now = DateTime.now();
    DateTime startDate = now.subtract(const Duration(days: 29));
    int? selectedAccountId;

    // --- SUMMARY CARDS ---
    // Largest expense
    final largestExpense = transactions.where((tx) => tx.type == TransactionType.expense).fold<TransactionModel?>(null, (prev, tx) => prev == null || tx.amount > prev.amount ? tx : prev);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Vanta Ledger'),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () => Navigator.pushNamed(context, '/settings'),
          ),
        ],
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // --- DASHBOARD LOGO (polished) ---
              Center(
                child: Card(
                  elevation: 6,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(32)),
                  color: Colors.white.withOpacity(0.05),
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Image.asset(
                      'assets/images/icon-512.png',
                      height: 72,
                      width: 72,
                      semanticLabel: 'Vanta Ledger Custom Logo',
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 16),
              if (kDebugMode)
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
              const SizedBox(height: 24),
              // --- FILTER CONTROLS ---
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('Last 30 days', style: Theme.of(context).textTheme.labelLarge),
                  DropdownButton<int?>(
                    value: selectedAccountId,
                    hint: const Text('All Accounts'),
                    items: [
                      const DropdownMenuItem<int?>(value: null, child: Text('All Accounts')),
                      ...accounts.map((acc) => DropdownMenuItem<int?>(value: acc.id, child: Text(acc.name))),
                    ],
                    onChanged: (val) {
                      // TODO: Implement account filter logic
                    },
                  ),
                ],
              ),
              const SizedBox(height: 12),
              // --- SUMMARY CARDS ---
              if (largestExpense != null)
                Card(
                  color: Colors.red.shade900,
                  elevation: 2,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  child: Padding(
                    padding: const EdgeInsets.all(12.0),
                    child: Column(
                      children: [
                        SvgPicture.asset(
                          'assets/images/app_logo_placeholder.svg',
                          height: 28,
                          width: 28,
                          color: Colors.white,
                        ),
                        const SizedBox(height: 4),
                        Text('Largest Expense', style: Theme.of(context).textTheme.labelSmall?.copyWith(color: Colors.white70)),
                        Text(largestExpense.description, style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: Colors.white)),
                        Text('Ksh ${largestExpense.amount.toStringAsFixed(2)}', style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
                      ],
                    ),
                  ),
                ),
              const SizedBox(height: 24),
              // --- DASHBOARD STATISTICS CARD (redesigned) ---
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(
                  children: [
                    Card(
                      elevation: 4,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                      margin: const EdgeInsets.only(right: 12, bottom: 16, top: 16),
                      child: Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.trending_down, color: Colors.red, size: 32),
                            const SizedBox(height: 8),
                            Text('Expenses', style: Theme.of(context).textTheme.labelMedium?.copyWith(color: Colors.red)),
                            Text('Ksh ${totalExpenses.toStringAsFixed(2)}', style: Theme.of(context).textTheme.titleLarge),
                          ],
                        ),
                      ),
                    ),
                    Card(
                      elevation: 4,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                      margin: const EdgeInsets.only(right: 12, bottom: 16, top: 16),
                      child: Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.trending_up, color: Colors.green, size: 32),
                            const SizedBox(height: 8),
                            Text('Income', style: Theme.of(context).textTheme.labelMedium?.copyWith(color: Colors.green)),
                            Text('Ksh ${transactions.where((tx) => tx.type == TransactionType.income).fold<double>(0.0, (sum, tx) => sum + tx.amount).toStringAsFixed(2)}', style: Theme.of(context).textTheme.titleLarge),
                          ],
                        ),
                      ),
                    ),
                    Card(
                      elevation: 4,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                      margin: const EdgeInsets.only(right: 12, bottom: 16, top: 16),
                      child: Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.receipt_long, color: Colors.deepPurple, size: 32),
                            const SizedBox(height: 8),
                            Text('Transactions', style: Theme.of(context).textTheme.labelMedium?.copyWith(color: Colors.deepPurple)),
                            Text('$totalTransactions', style: Theme.of(context).textTheme.titleLarge),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),
              Text('Recent Activity', style: Theme.of(context).textTheme.titleMedium),
              const SizedBox(height: 8),
              if (recentTransactions.isEmpty)
                const Text('No recent transactions.')
              else
                ...recentTransactions.asMap().entries.map((entry) {
                  final i = entry.key;
                  final tx = entry.value;
                  return AnimatedSlide(
                    offset: _controller.drive(Tween(begin: Offset(0, 0.2 + i * 0.1), end: Offset.zero)).value,
                    duration: Duration(milliseconds: 500 + i * 100),
                    curve: Curves.easeOut,
                    child: AnimatedOpacity(
                      opacity: _controller.value,
                      duration: Duration(milliseconds: 500 + i * 100),
                      child: Card(
                        child: ListTile(
                          leading: CircleAvatar(
                            backgroundColor: tx.type == TransactionType.expense ? Colors.red[100] : Colors.green[100],
                            child: Icon(
                              tx.type == TransactionType.expense ? Icons.arrow_downward : Icons.arrow_upward,
                              color: tx.type == TransactionType.expense ? Colors.red : Colors.green,
                            ),
                          ),
                          title: Text(tx.description),
                          subtitle: Text(tx.date.toIso8601String().split('T').first),
                          trailing: Text('Ksh ${tx.amount.toStringAsFixed(2)}', style: TextStyle(
                            color: tx.type == TransactionType.expense ? Colors.red : Colors.green,
                            fontWeight: FontWeight.bold,
                          )),
                        ),
                      ),
                    ),
                  );
                }),
            ],
          ),
        ),
      ),
    );
  }

  void _navigateWithFade(BuildContext context, Widget page) {
    Navigator.of(context).push(PageRouteBuilder(
      pageBuilder: (context, animation, secondaryAnimation) => page,
      transitionsBuilder: (context, animation, secondaryAnimation, child) {
        return FadeTransition(opacity: animation, child: child);
      },
      transitionDuration: const Duration(milliseconds: 350),
    ));
  }
}

class _QuickActionButton extends StatefulWidget {
  final IconData icon;
  final String label;
  final VoidCallback onTap;
  const _QuickActionButton({required this.icon, required this.label, required this.onTap});

  @override
  State<_QuickActionButton> createState() => _QuickActionButtonState();
}

class _QuickActionButtonState extends State<_QuickActionButton> with SingleTickerProviderStateMixin {
  double _scale = 1.0;

  void _onTapDown(TapDownDetails details) {
    setState(() => _scale = 0.92);
  }

  void _onTapUp(TapUpDetails details) {
    setState(() => _scale = 1.0);
  }

  void _onTapCancel() {
    setState(() => _scale = 1.0);
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        GestureDetector(
          onTapDown: _onTapDown,
          onTapUp: _onTapUp,
          onTapCancel: _onTapCancel,
          onTap: widget.onTap,
          child: AnimatedScale(
            scale: _scale,
            duration: const Duration(milliseconds: 120),
            child: Ink(
              decoration: const ShapeDecoration(
                color: Colors.deepPurple,
                shape: CircleBorder(),
              ),
              child: Icon(widget.icon, color: Colors.white, size: 28),
            ),
          ),
        ),
        const SizedBox(height: 6),
        Text(widget.label, style: Theme.of(context).textTheme.labelSmall),
      ],
    );
  }
} 