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
import 'screens/lock_screen.dart';
import 'screens/splash_screen.dart';

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
          home: SplashScreenLauncher(onboardingComplete: onboardingComplete),
          routes: {
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

class SplashScreenLauncher extends StatefulWidget {
  final bool onboardingComplete;
  const SplashScreenLauncher({required this.onboardingComplete, Key? key}) : super(key: key);

  @override
  State<SplashScreenLauncher> createState() => _SplashScreenLauncherState();
}

class _SplashScreenLauncherState extends State<SplashScreenLauncher> {
  bool _showSplash = true;

  @override
  void initState() {
    super.initState();
  }

  void _onSplashFinish() async {
    setState(() => _showSplash = false);
  }

  @override
  Widget build(BuildContext context) {
    if (_showSplash) {
      return SplashScreen(onFinish: _onSplashFinish);
    }
    if (!widget.onboardingComplete) {
      return const OnboardingScreen();
    }
    return _SecureEntryWrapper(child: const MainNavScreen());
  }
}

class _SecureEntryWrapper extends StatefulWidget {
  final Widget child;
  const _SecureEntryWrapper({required this.child});

  @override
  State<_SecureEntryWrapper> createState() => _SecureEntryWrapperState();
}

class _SecureEntryWrapperState extends State<_SecureEntryWrapper> {
  bool _unlocked = false;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _checkSecurity();
  }

  Future<void> _checkSecurity() async {
    final security = Provider.of<SecurityProvider>(context, listen: false);
    await security.loadSecurity();
    if (security.hasPin || security.biometricEnabled) {
      final unlocked = await Navigator.of(context).push(
        MaterialPageRoute(builder: (_) => const LockScreen()),
      );
      setState(() {
        _unlocked = unlocked == true;
        _loading = false;
      });
    } else {
      setState(() {
        _unlocked = true;
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }
    return _unlocked ? widget.child : const SizedBox.shrink();
  }
} 