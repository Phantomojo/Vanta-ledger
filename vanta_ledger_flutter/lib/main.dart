import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers/transaction_provider.dart';
import 'providers/category_provider.dart';
import 'providers/account_provider.dart';
// TODO: Replace with actual TimelineScreen implementation
import 'screens/dashboard_screen.dart';
import 'screens/settings_screen.dart';
import 'screens/account_screen.dart';
import 'screens/category_screen.dart';
import 'screens/main_nav_screen.dart';

void main() {
  runApp(const VantaLedgerApp());
}

class VantaLedgerApp extends StatelessWidget {
  const VantaLedgerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => TransactionProvider()),
        ChangeNotifierProvider(create: (_) => CategoryProvider()),
        ChangeNotifierProvider(create: (_) => AccountProvider()),
      ],
      child: MaterialApp(
        title: 'Vanta Ledger',
        theme: ThemeData(
          brightness: Brightness.dark,
          colorSchemeSeed: Colors.deepPurple,
          useMaterial3: true,
        ),
        home: const MainNavScreen(),
        routes: {
          '/settings': (context) => const SettingsScreen(),
          '/accounts': (context) => const AccountScreen(),
          '/categories': (context) => const CategoryScreen(),
        },
        debugShowCheckedModeBanner: false,
      ),
    );
  }
} 