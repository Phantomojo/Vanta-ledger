import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/transaction_provider.dart';
import '../models/transaction.dart';
import 'timeline_screen.dart';
import 'category_screen.dart';
import 'account_screen.dart';
import 'add_transaction_screen.dart';
import 'package:fl_chart/fl_chart.dart';
import '../providers/category_provider.dart';
import '../providers/account_provider.dart';
import 'dart:math';
import '../models/category.dart';

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

    // --- BAR CHART DATA: Expenses per day for last 30 days ---
    List<double> dailyExpenses = List.filled(30, 0.0);
    for (final tx in transactions.where((tx) => tx.type == TransactionType.expense)) {
      if (tx.date.isAfter(startDate.subtract(const Duration(days: 1))) && tx.date.isBefore(now.add(const Duration(days: 1)))) {
        int dayIndex = tx.date.difference(startDate).inDays;
        if (dayIndex >= 0 && dayIndex < 30) {
          dailyExpenses[dayIndex] += tx.amount;
        }
      }
    }
    double maxExpense = dailyExpenses.reduce(max);

    // --- SUMMARY CARDS ---
    // Top category
    int? topCategoryId;
    double topCategoryAmount = 0.0;
    final Map<int, double> expensesByCategory = {};
    for (final tx in transactions.where((tx) => tx.type == TransactionType.expense)) {
      expensesByCategory[tx.categoryId] = (expensesByCategory[tx.categoryId] ?? 0) + tx.amount;
      if (expensesByCategory[tx.categoryId]! > topCategoryAmount) {
        topCategoryAmount = expensesByCategory[tx.categoryId]!;
        topCategoryId = tx.categoryId;
      }
    }
    final topCategory = categories.firstWhere(
      (c) => c.id == topCategoryId,
      orElse: () => CategoryModel(id: -1, name: 'Other', icon: Icons.category, isCustom: false),
    );
    // Largest expense
    final largestExpense = transactions.where((tx) => tx.type == TransactionType.expense).fold<TransactionModel?>(null, (prev, tx) => prev == null || tx.amount > prev.amount ? tx : prev);

    // --- PIE CHART DATA (already present) ---
    final chartSections = expensesByCategory.entries.map((entry) {
      final cat = categories.firstWhere(
        (c) => c.id == entry.key,
        orElse: () => CategoryModel(id: -1, name: 'Other', icon: Icons.category, isCustom: false),
      );
      final color = cat != null ? Colors.primaries[entry.key % Colors.primaries.length] : Colors.grey;
      return PieChartSectionData(
        value: entry.value,
        color: color,
        title: cat?.name ?? 'Other',
        radius: 48,
        titleStyle: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.white),
      );
    }).toList();

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
              // --- FILTER CONTROLS ---
              Row(
                children: [
                  Expanded(
                    child: Text('Last 30 days', style: Theme.of(context).textTheme.labelLarge),
                  ),
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
              Row(
                children: [
                  if (topCategory != null)
                    Expanded(
                      child: Card(
                        color: Colors.deepPurple.shade800,
                        elevation: 2,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                        child: Padding(
                          padding: const EdgeInsets.all(12.0),
                          child: Column(
                            children: [
                              Icon(topCategory.icon, color: Colors.white, size: 28),
                              const SizedBox(height: 4),
                              Text('Top Category', style: Theme.of(context).textTheme.labelSmall?.copyWith(color: Colors.white70)),
                              Text(topCategory.name, style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: Colors.white)),
                              Text('Ksh ${topCategoryAmount.toStringAsFixed(2)}', style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
                            ],
                          ),
                        ),
                      ),
                    ),
                  if (largestExpense != null)
                    Expanded(
                      child: Card(
                        color: Colors.red.shade900,
                        elevation: 2,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                        child: Padding(
                          padding: const EdgeInsets.all(12.0),
                          child: Column(
                            children: [
                              const Icon(Icons.trending_up, color: Colors.white, size: 28),
                              const SizedBox(height: 4),
                              Text('Largest Expense', style: Theme.of(context).textTheme.labelSmall?.copyWith(color: Colors.white70)),
                              Text(largestExpense.description, style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: Colors.white)),
                              Text('Ksh ${largestExpense.amount.toStringAsFixed(2)}', style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
                            ],
                          ),
                        ),
                      ),
                    ),
                ],
              ),
              const SizedBox(height: 20),
              // --- BAR CHART: Expenses over last 30 days ---
              Card(
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                elevation: 2,
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    children: [
                      const Text('Expenses Over Time', style: TextStyle(fontWeight: FontWeight.bold)),
                      SizedBox(
                        height: 180,
                        child: BarChart(
                          BarChartData(
                            alignment: BarChartAlignment.spaceBetween,
                            maxY: maxExpense == 0 ? 100 : maxExpense * 1.2,
                            barTouchData: BarTouchData(enabled: true),
                            titlesData: FlTitlesData(
                              leftTitles: AxisTitles(
                                sideTitles: SideTitles(showTitles: true, reservedSize: 32),
                              ),
                              bottomTitles: AxisTitles(
                                sideTitles: SideTitles(
                                  showTitles: true,
                                  getTitlesWidget: (value, meta) {
                                    int day = value.toInt();
                                    if (day % 5 == 0 || day == 29) {
                                      DateTime date = startDate.add(Duration(days: day));
                                      return Text('${date.day}/${date.month}', style: const TextStyle(fontSize: 10));
                                    }
                                    return const SizedBox.shrink();
                                  },
                                ),
                              ),
                              rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                              topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                            ),
                            borderData: FlBorderData(show: false),
                            barGroups: [
                              for (int i = 0; i < 30; i++)
                                BarChartGroupData(
                                  x: i,
                                  barRods: [
                                    BarChartRodData(
                                      toY: dailyExpenses[i],
                                      color: Colors.deepPurple,
                                      width: 8,
                                      borderRadius: BorderRadius.circular(4),
                                    ),
                                  ],
                                ),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 24),
              // Animated Statistics Card (now with gradient background)
              AnimatedSlide(
                offset: _controller.drive(Tween(begin: const Offset(0, 0.2), end: Offset.zero)).value,
                duration: const Duration(milliseconds: 700),
                curve: Curves.easeOut,
                child: AnimatedOpacity(
                  opacity: _controller.value,
                  duration: const Duration(milliseconds: 700),
                  child: Container(
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [Colors.deepPurple.shade400, Colors.deepPurple.shade700],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                      borderRadius: BorderRadius.circular(20),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.deepPurple.withOpacity(0.18),
                          blurRadius: 16,
                          offset: const Offset(0, 8),
                        ),
                      ],
                    ),
                    child: Padding(
                      padding: const EdgeInsets.all(24.0),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceAround,
                        children: [
                          Column(
                            children: [
                              const Icon(Icons.trending_down, color: Colors.white, size: 32),
                              const SizedBox(height: 8),
                              Text('Expenses', style: Theme.of(context).textTheme.labelMedium?.copyWith(color: Colors.white70)),
                              Text('Ksh ${totalExpenses.toStringAsFixed(2)}', style: Theme.of(context).textTheme.titleLarge?.copyWith(color: Colors.white)),
                            ],
                          ),
                          Column(
                            children: [
                              const Icon(Icons.receipt_long, color: Colors.white, size: 32),
                              const SizedBox(height: 8),
                              Text('Transactions', style: Theme.of(context).textTheme.labelMedium?.copyWith(color: Colors.white70)),
                              Text('$totalTransactions', style: Theme.of(context).textTheme.titleLarge?.copyWith(color: Colors.white)),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 24),
              // Pie Chart for Expenses by Category
              if (chartSections.isNotEmpty)
                Card(
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  elevation: 2,
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      children: [
                        const Text('Expenses by Category', style: TextStyle(fontWeight: FontWeight.bold)),
                        SizedBox(
                          height: 180,
                          child: PieChart(
                            PieChartData(
                              sections: chartSections,
                              sectionsSpace: 2,
                              centerSpaceRadius: 32,
                              borderData: FlBorderData(show: false),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              if (chartSections.isNotEmpty) const SizedBox(height: 24),
              // Quick Actions (grouped in a rounded card)
              Center(
                child: Card(
                  color: Theme.of(context).colorScheme.surfaceVariant,
                  elevation: 4,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(32)),
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        _QuickActionButton(
                          icon: Icons.add,
                          label: 'Add',
                          onTap: () => _navigateWithFade(context, const AddTransactionScreen()),
                        ),
                        const SizedBox(width: 12),
                        _QuickActionButton(
                          icon: Icons.timeline,
                          label: 'Timeline',
                          onTap: () => _navigateWithFade(context, const TimelineScreen()),
                        ),
                        const SizedBox(width: 12),
                        _QuickActionButton(
                          icon: Icons.account_balance_wallet,
                          label: 'Accounts',
                          onTap: () => _navigateWithFade(context, const AccountScreen()),
                        ),
                        const SizedBox(width: 12),
                        _QuickActionButton(
                          icon: Icons.category,
                          label: 'Categories',
                          onTap: () => _navigateWithFade(context, const CategoryScreen()),
                        ),
                      ],
                    ),
                  ),
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