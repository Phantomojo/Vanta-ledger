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
import '../wakanda_text.dart';
import 'dart:ui';
import '../components/glassy_card.dart';

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
    final accounts = context.watch<AccountProvider>().accounts;
    final transactions = context.watch<TransactionProvider>().transactions;
    final totalBalance = accounts.fold<double>(0.0, (sum, acc) => sum + acc.balance);
    final recentTransactions = transactions.take(5).toList();

    return Scaffold(
      appBar: GlassyAppBar(
        title: 'Dashboard',
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 16, left: 8, top: 12, bottom: 12),
            child: IconButton(
              icon: const Icon(Icons.settings, color: Colors.white70, size: 26),
              onPressed: () => Navigator.pushNamed(context, '/settings'),
            ),
          ),
        ],
      ),
      body: Stack(
        children: [
          // Cinematic purple glass background image
          Positioned.fill(
            child: Image.asset(
              'assets/images/purple_glass_bg.jpg',
              fit: BoxFit.cover,
            ),
          ),
          // Dark overlay for readability
          Positioned.fill(
            child: Container(
              color: Colors.black.withOpacity(0.45),
            ),
          ),
          // Main content
          Padding(
            padding: const EdgeInsets.only(top: 0, left: 0, right: 0, bottom: 0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SizedBox(height: 12),
                // Summary Cards Row (always visible)
                SizedBox(
                  height: 120,
                  child: ListView(
                    scrollDirection: Axis.horizontal,
                    padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 8),
                    children: [
                      _GlassySummaryCard(
                        icon: Icons.trending_down,
                        label: 'Expenses',
                        value: 'Ksh ${transactions.where((tx) => tx.type == TransactionType.expense).fold<double>(0.0, (sum, tx) => sum + tx.amount).toStringAsFixed(2)}',
                        color: Colors.red,
                      ),
                      const SizedBox(width: 18),
                      _GlassySummaryCard(
                        icon: Icons.trending_up,
                        label: 'Income',
                        value: 'Ksh ${transactions.where((tx) => tx.type == TransactionType.income).fold<double>(0.0, (sum, tx) => sum + tx.amount).toStringAsFixed(2)}',
                        color: Colors.green,
                      ),
                      const SizedBox(width: 18),
                      _GlassySummaryCard(
                        icon: Icons.receipt_long,
                        label: 'Transactions',
                        value: '${transactions.length}',
                        color: Colors.deepPurple,
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 18),
                // Account Cards Carousel (glassy)
                SizedBox(
                  height: 200,
                  child: accounts.isEmpty
                      ? Center(child: Text('No accounts yet.', style: Theme.of(context).textTheme.bodyLarge))
                      : ListView.separated(
                          scrollDirection: Axis.horizontal,
                          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 18),
                          itemCount: accounts.length,
                          separatorBuilder: (_, __) => const SizedBox(width: 24),
                          itemBuilder: (context, i) {
                            final acc = accounts[i];
                            return ClipRRect(
                              borderRadius: BorderRadius.circular(32),
                              child: BackdropFilter(
                                filter: ImageFilter.blur(sigmaX: 22, sigmaY: 22),
                                child: Container(
                                  width: 320,
                                  height: 170,
                                  decoration: BoxDecoration(
                                    gradient: LinearGradient(
                                      begin: Alignment.topLeft,
                                      end: Alignment.bottomRight,
                                      colors: [
                                        Colors.white.withOpacity(0.10),
                                        Colors.deepPurple.withOpacity(0.08),
                                        Colors.transparent,
                                      ],
                                    ),
                                    borderRadius: BorderRadius.circular(32),
                                    border: Border.all(color: Colors.white.withOpacity(0.06), width: 1.0),
                                  ),
                                  child: Padding(
                                    padding: const EdgeInsets.all(20.0),
                                    child: SingleChildScrollView(
                                      child: Column(
                                        mainAxisSize: MainAxisSize.min,
                                        crossAxisAlignment: CrossAxisAlignment.start,
                                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                        children: [
                                          Row(
                                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                            children: [
                                              Icon(Icons.account_balance_wallet_rounded, color: Colors.white.withOpacity(0.65), size: 36),
                                              Icon(Icons.more_horiz, color: Colors.white38),
                                            ],
                                          ),
                                          const SizedBox(height: 16),
                                          Text(
                                            acc.name,
                                            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                                              fontWeight: FontWeight.bold,
                                              color: Colors.white.withOpacity(0.82),
                                              shadows: [Shadow(color: Colors.black.withOpacity(0.18), blurRadius: 3)],
                                            ),
                                          ),
                                          const SizedBox(height: 8),
                                          WakandaText(
                                            text: 'Ksh ${acc.balance.toStringAsFixed(2)}',
                                            style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                                              fontWeight: FontWeight.bold,
                                              fontSize: 32,
                                              color: Colors.white.withOpacity(0.88),
                                              shadows: [Shadow(color: Colors.black.withOpacity(0.22), blurRadius: 4)],
                                            ),
                                          ),
                                        ],
                                      ),
                                    ),
                                  ),
                                ),
                              ),
                            );
                          },
                        ),
                ),
                const SizedBox(height: 32),
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 0),
                  child: Text('Recent Transactions', style: Theme.of(context).textTheme.titleMedium),
                ),
                const SizedBox(height: 8),
                Expanded(
                  child: recentTransactions.isEmpty
                      ? const Center(child: Text('No recent transactions.'))
                      : ListView.separated(
                          padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 0),
                          itemCount: recentTransactions.length,
                          separatorBuilder: (_, __) => const SizedBox(height: 18),
                          itemBuilder: (context, i) {
                            final tx = recentTransactions[i];
                            return ClipRRect(
                              borderRadius: BorderRadius.circular(18),
                              child: BackdropFilter(
                                filter: ImageFilter.blur(sigmaX: 14, sigmaY: 14),
                                child: Container(
                                  decoration: BoxDecoration(
                                    gradient: LinearGradient(
                                      begin: Alignment.topLeft,
                                      end: Alignment.bottomRight,
                                      colors: [
                                        Colors.white.withOpacity(0.08),
                                        Colors.deepPurple.withOpacity(0.06),
                                        Colors.transparent,
                                      ],
                                    ),
                                    borderRadius: BorderRadius.circular(18),
                                    border: Border.all(color: Colors.white.withOpacity(0.05), width: 0.8),
                                  ),
                                  child: ListTile(
                                    leading: CircleAvatar(
                                      backgroundColor: tx.type == TransactionType.expense ? Colors.red.withOpacity(0.18) : Colors.green.withOpacity(0.18),
                                      child: Icon(
                                        tx.type == TransactionType.expense ? Icons.arrow_downward : Icons.arrow_upward,
                                        color: tx.type == TransactionType.expense ? Colors.red.withOpacity(0.7) : Colors.green.withOpacity(0.7),
                                      ),
                                    ),
                                    title: Text(
                                      tx.description,
                                      style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                                        color: Colors.white.withOpacity(0.82),
                                        shadows: [Shadow(color: Colors.black.withOpacity(0.14), blurRadius: 2)],
                                      ),
                                    ),
                                    subtitle: Text(
                                      tx.date.toIso8601String().split('T').first,
                                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                        color: Colors.white.withOpacity(0.55),
                                      ),
                                    ),
                                    trailing: WakandaText(
                                      text: 'Ksh ${tx.amount.toStringAsFixed(2)}',
                                      style: TextStyle(
                                        color: tx.type == TransactionType.expense ? Colors.red.withOpacity(0.8) : Colors.green.withOpacity(0.8),
                                        fontWeight: FontWeight.bold,
                                        fontSize: 18,
                                        shadows: [Shadow(color: Colors.black.withOpacity(0.18), blurRadius: 3)],
                                      ),
                                    ),
                                  ),
                                ),
                              ),
                            );
                          },
                        ),
                ),
              ],
            ),
          ),
        ],
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

class _GlassySummaryCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color color;
  const _GlassySummaryCard({required this.icon, required this.label, required this.value, required this.color});

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(24),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 22, sigmaY: 22),
        child: Container(
          width: 140,
          height: 130,
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                Colors.white.withOpacity(0.10),
                Colors.deepPurple.withOpacity(0.08),
                Colors.transparent,
              ],
            ),
            borderRadius: BorderRadius.circular(24),
            border: Border.all(color: Colors.white.withOpacity(0.06), width: 1.0),
          ),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(icon, color: color.withOpacity(0.65), size: 26),
                const SizedBox(height: 6),
                Text(
                  label,
                  style: Theme.of(context).textTheme.labelMedium?.copyWith(
                    color: Colors.white.withOpacity(0.68),
                    fontWeight: FontWeight.w500,
                    shadows: [Shadow(color: Colors.black.withOpacity(0.12), blurRadius: 2)],
                  ),
                ),
                const SizedBox(height: 2),
                WakandaText(
                  text: value,
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: Colors.white.withOpacity(0.82),
                    fontSize: 20,
                    shadows: [Shadow(color: Colors.black.withOpacity(0.18), blurRadius: 3)],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class GlassyAppBar extends StatelessWidget implements PreferredSizeWidget {
  final String title;
  final List<Widget>? actions;
  const GlassyAppBar({required this.title, this.actions, Key? key}) : super(key: key);

  @override
  Size get preferredSize => const Size.fromHeight(64);

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: const BorderRadius.vertical(bottom: Radius.circular(24)),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 18, sigmaY: 18),
        child: Container(
          decoration: BoxDecoration(
            color: Colors.black.withOpacity(0.22),
          ),
          child: Row(
            children: [
              Padding(
                padding: const EdgeInsets.only(left: 16, top: 12, bottom: 12, right: 8),
                child: Image.asset(
                  'assets/images/icon-512.png',
                  height: 32,
                  width: 32,
                  semanticLabel: 'Vanta Ledger Logo',
                ),
              ),
              Expanded(
                child: Center(
                  child: WakandaText(
                    text: title,
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      color: Colors.white.withOpacity(0.88),
                      fontWeight: FontWeight.bold,
                      fontSize: 22,
                      shadows: [Shadow(color: Colors.black.withOpacity(0.18), blurRadius: 3)],
                    ),
                  ),
                ),
              ),
              if (actions != null)
                ...actions!
              else
                const SizedBox(width: 48),
            ],
          ),
        ),
      ),
    );
  }
} 