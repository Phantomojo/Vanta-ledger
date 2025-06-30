import 'package:flutter/material.dart';
import 'dashboard_screen.dart';
import 'transactions_screen.dart';
import 'account_screen.dart';
import 'category_screen.dart';
import 'budgets_screen.dart';
import 'reports_screen.dart';
import 'bills_screen.dart';
import 'investments_screen.dart';

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
    const CategoryScreen(),
    const BudgetsScreen(),
    const BillsScreen(),
    const ReportsScreen(),
    const InvestmentsScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _screens[_selectedIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: (index) => setState(() => _selectedIndex = index),
        type: BottomNavigationBarType.fixed,
        selectedItemColor: Colors.deepPurple,
        unselectedItemColor: Colors.grey,
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.dashboard), label: 'Dashboard'),
          BottomNavigationBarItem(icon: Icon(Icons.list_alt), label: 'Transactions'),
          BottomNavigationBarItem(icon: Icon(Icons.account_balance_wallet), label: 'Accounts'),
          BottomNavigationBarItem(icon: Icon(Icons.category), label: 'Categories'),
          BottomNavigationBarItem(icon: Icon(Icons.pie_chart), label: 'Budgets'),
          BottomNavigationBarItem(icon: Icon(Icons.notifications_active), label: 'Bills'),
          BottomNavigationBarItem(icon: Icon(Icons.bar_chart), label: 'Reports'),
          BottomNavigationBarItem(
            icon: Icon(Icons.trending_up),
            label: 'Investments',
          ),
        ],
      ),
    );
  }
} 