import 'package:flutter/material.dart';
import 'dashboard_screen.dart';
import 'transactions_screen.dart';
import 'account_screen.dart';
import 'category_screen.dart';
import 'budgets_screen.dart';
import 'reports_screen.dart';
import 'bills_screen.dart';
import 'investments_screen.dart';
import 'dart:ui';
import '../components/glassy_card.dart';

class MainNavScreen extends StatefulWidget {
  const MainNavScreen({super.key});

  @override
  State<MainNavScreen> createState() => _MainNavScreenState();
}

class _MainNavScreenState extends State<MainNavScreen> {
  int _selectedIndex = 0;

  static final List<Widget> _screens = [
    const DashboardScreen(),
    const TransactionsScreen(),
    const AccountScreen(),
    const ReportsScreen(),
    // 'More' will show a modal with the rest
  ];

  static final List<Widget> _moreScreens = [
    const CategoryScreen(),
    const BudgetsScreen(),
    const BillsScreen(),
    const InvestmentsScreen(),
  ];

  void _showMoreMenu(BuildContext context) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (context) => ClipRRect(
        borderRadius: const BorderRadius.vertical(top: Radius.circular(28)),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 18, sigmaY: 18),
          child: Container(
            color: Colors.black.withOpacity(0.55),
            child: ListView(
              shrinkWrap: true,
              children: [
                ListTile(
                  leading: const Icon(Icons.category_outlined, color: Colors.white70),
                  title: const Text('Categories', style: TextStyle(color: Colors.white)),
                  onTap: () {
                    Navigator.pop(context);
                    setState(() => _selectedIndex = 4);
                  },
                ),
                ListTile(
                  leading: const Icon(Icons.pie_chart_outline, color: Colors.white70),
                  title: const Text('Budgets', style: TextStyle(color: Colors.white)),
                  onTap: () {
                    Navigator.pop(context);
                    setState(() => _selectedIndex = 5);
                  },
                ),
                ListTile(
                  leading: const Icon(Icons.notifications_active_outlined, color: Colors.white70),
                  title: const Text('Bills', style: TextStyle(color: Colors.white)),
                  onTap: () {
                    Navigator.pop(context);
                    setState(() => _selectedIndex = 6);
                  },
                ),
                ListTile(
                  leading: const Icon(Icons.trending_up_outlined, color: Colors.white70),
                  title: const Text('Investments', style: TextStyle(color: Colors.white)),
                  onTap: () {
                    Navigator.pop(context);
                    setState(() => _selectedIndex = 7);
                  },
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final int mainTabs = 4;
    final bool isMore = _selectedIndex >= mainTabs;
    return Scaffold(
      body: isMore ? _moreScreens[_selectedIndex - mainTabs] : _screens[_selectedIndex],
      extendBody: true,
      bottomNavigationBar: Padding(
        padding: const EdgeInsets.only(left: 18, right: 18, bottom: 18),
        child: ClipRRect(
          borderRadius: const BorderRadius.vertical(top: Radius.circular(28), bottom: Radius.circular(18)),
          child: BackdropFilter(
            filter: ImageFilter.blur(sigmaX: 18, sigmaY: 18),
            child: Container(
              decoration: BoxDecoration(
                color: Colors.black.withOpacity(0.55),
                borderRadius: const BorderRadius.vertical(top: Radius.circular(28), bottom: Radius.circular(18)),
                border: Border.all(color: Colors.white.withOpacity(0.07), width: 1.2),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  _NavBarIcon(
                    icon: Icons.dashboard_outlined,
                    label: 'Dashboard',
                    selected: _selectedIndex == 0,
                    onTap: () => setState(() => _selectedIndex = 0),
                  ),
                  _NavBarIcon(
                    icon: Icons.list_alt_outlined,
                    label: 'Transactions',
                    selected: _selectedIndex == 1,
                    onTap: () => setState(() => _selectedIndex = 1),
                  ),
                  _NavBarIcon(
                    icon: Icons.account_balance_wallet_outlined,
                    label: 'Accounts',
                    selected: _selectedIndex == 2,
                    onTap: () => setState(() => _selectedIndex = 2),
                  ),
                  _NavBarIcon(
                    icon: Icons.bar_chart_outlined,
                    label: 'Reports',
                    selected: _selectedIndex == 3,
                    onTap: () => setState(() => _selectedIndex = 3),
                  ),
                  _NavBarIcon(
                    icon: Icons.more_horiz,
                    label: 'More',
                    selected: isMore,
                    onTap: () => _showMoreMenu(context),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _NavBarIcon extends StatelessWidget {
  final IconData icon;
  final String label;
  final bool selected;
  final VoidCallback onTap;
  const _NavBarIcon({required this.icon, required this.label, required this.selected, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: GestureDetector(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 8),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                icon,
                color: selected ? Colors.deepPurpleAccent : Colors.white.withOpacity(0.55),
                size: selected ? 30 : 26,
              ),
              AnimatedSwitcher(
                duration: const Duration(milliseconds: 200),
                child: selected
                    ? Text(
                        label,
                        key: ValueKey(label),
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.w600,
                          fontSize: 13,
                          letterSpacing: 0.2,
                          shadows: [Shadow(color: Colors.black26, blurRadius: 2)],
                        ),
                      )
                    : const SizedBox(height: 16),
              ),
            ],
          ),
        ),
      ),
    );
  }
} 