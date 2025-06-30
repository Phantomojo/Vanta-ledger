import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers/transaction_provider.dart';
import 'providers/category_provider.dart';
import 'providers/account_provider.dart';
import 'providers/budget_provider.dart';
import 'providers/bill_provider.dart';
import 'providers/reports_provider.dart';
import 'providers/security_provider.dart';
import 'providers/investment_provider.dart';
import 'providers/theme_provider.dart';
import 'theme/app_theme.dart';
// TODO: Replace with actual TimelineScreen implementation
import 'screens/dashboard_screen.dart';
import 'screens/settings_screen.dart';
import 'screens/account_screen.dart';
import 'screens/category_screen.dart';
import 'screens/main_nav_screen.dart';
import 'screens/onboarding_screen.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'providers/currency_provider.dart';
import 'providers/notification_settings_provider.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final prefs = await SharedPreferences.getInstance();
  final onboardingComplete = prefs.getBool('onboarding_complete') ?? false;
  runApp(MyApp(onboardingComplete: onboardingComplete));
}

class MyApp extends StatelessWidget {
  final bool onboardingComplete;
  const MyApp({required this.onboardingComplete, Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => TransactionProvider()),
        ChangeNotifierProvider(create: (_) => CategoryProvider()),
        ChangeNotifierProvider(create: (_) => AccountProvider()),
        ChangeNotifierProvider(create: (_) => BudgetProvider()),
        ChangeNotifierProvider(create: (_) => BillProvider()),
        ChangeNotifierProvider(create: (_) => ReportsProvider()),
        ChangeNotifierProvider(create: (_) => SecurityProvider()),
        ChangeNotifierProvider(create: (_) => InvestmentProvider()),
        ChangeNotifierProvider(create: (_) => ThemeProvider()),
        ChangeNotifierProvider(create: (_) => CurrencyProvider()),
        ChangeNotifierProvider(create: (_) => NotificationSettingsProvider()),
      ],
      child: Consumer<ThemeProvider>(
        builder: (context, themeProvider, _) => MaterialApp(
          title: 'Vanta Ledger',
          theme: AppTheme.lightTheme,
          darkTheme: AppTheme.darkTheme,
          themeMode: themeProvider.themeMode,
          initialRoute: onboardingComplete ? '/' : '/onboarding',
          routes: {
            '/': (context) => const MainNavScreen(),
            '/onboarding': (context) => const OnboardingScreen(),
            '/settings': (context) => const SettingsScreen(),
            '/accounts': (context) => const AccountScreen(),
            '/categories': (context) => const CategoryScreen(),
          },
          debugShowCheckedModeBanner: false,
        ),
      ),
    );
  }
} 