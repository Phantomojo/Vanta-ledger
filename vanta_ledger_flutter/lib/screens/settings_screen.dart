import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/security_provider.dart';
import '../services/backup_service.dart';
import '../providers/theme_provider.dart';
import '../providers/currency_provider.dart';
import '../providers/notification_settings_provider.dart';
import 'package:flutter_svg/flutter_svg.dart';
import '../services/database_service.dart';
import '../wakanda_text.dart';
import 'dashboard_screen.dart';
import 'dart:ui';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  ThemeMode _themeMode = ThemeMode.system;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: const GlassyAppBar(title: 'Settings'),
      body: Stack(
        children: [
          // Cinematic background
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
          ListView(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
            children: [
              // Theme & Currency
              _GlassySettingsCard(
                child: Column(
                  children: [
                    Consumer<ThemeProvider>(
                      builder: (context, themeProvider, _) => ListTile(
                        leading: const Icon(Icons.color_lens_outlined, color: Colors.white70),
                        title: const Text('Theme', style: TextStyle(color: Colors.white)),
                        trailing: DropdownButton<ThemeMode>(
                          value: themeProvider.themeMode,
                          dropdownColor: Theme.of(context).colorScheme.surface,
                          items: const [
                            DropdownMenuItem(value: ThemeMode.system, child: Text('System')),
                            DropdownMenuItem(value: ThemeMode.light, child: Text('Light')),
                            DropdownMenuItem(value: ThemeMode.dark, child: Text('Dark')),
                          ],
                          onChanged: (mode) {
                            if (mode != null) themeProvider.setThemeMode(mode);
                          },
                        ),
                      ),
                    ),
                    Consumer<CurrencyProvider>(
                      builder: (context, currencyProvider, _) => ListTile(
                        leading: const Icon(Icons.attach_money_outlined, color: Colors.white70),
                        title: const Text('Currency', style: TextStyle(color: Colors.white)),
                        trailing: DropdownButton<String>(
                          value: currencyProvider.selected.code,
                          dropdownColor: Theme.of(context).colorScheme.surface,
                          items: currencyProvider.currencies.map((c) => DropdownMenuItem(
                            value: c.code,
                            child: Text('${c.symbol} ${c.code}'),
                          )).toList(),
                          onChanged: (code) {
                            final currency = currencyProvider.currencies.firstWhere((c) => c.code == code);
                            currencyProvider.selectCurrency(currency);
                          },
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 28),
              // Account & Category Management
              _GlassySettingsCard(
                child: Column(
                  children: [
                    ListTile(
                      leading: const Icon(Icons.account_balance_wallet_outlined, color: Colors.white70),
                      title: const Text('Manage Accounts', style: TextStyle(color: Colors.white)),
                      onTap: () => Navigator.pushNamed(context, '/accounts'),
                    ),
                    ListTile(
                      leading: const Icon(Icons.category_outlined, color: Colors.white70),
                      title: const Text('Manage Categories', style: TextStyle(color: Colors.white)),
                      onTap: () => Navigator.pushNamed(context, '/categories'),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 28),
              // Security Section
              _GlassySettingsCard(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Padding(
                      padding: const EdgeInsets.only(left: 12, top: 8, bottom: 4),
                      child: WakandaText(
                        text: 'Security',
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          color: Colors.white.withOpacity(0.82),
                          fontWeight: FontWeight.bold,
                          fontSize: 18,
                        ),
                        enableLoop: false,
                      ),
                    ),
                    ListTile(
                      leading: const Icon(Icons.lock_outline, color: Colors.white70),
                      title: const Text('Set/Change PIN', style: TextStyle(color: Colors.white)),
                      onTap: () async {
                        final controller = TextEditingController();
                        final result = await showDialog<String>(
                          context: context,
                          builder: (context) => AlertDialog(
                            title: const Text('Set/Change PIN'),
                            content: TextField(
                              controller: controller,
                              keyboardType: TextInputType.number,
                              obscureText: true,
                              decoration: const InputDecoration(labelText: 'New PIN'),
                            ),
                            actions: [
                              TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
                              ElevatedButton(onPressed: () => Navigator.pop(context, controller.text), child: const Text('Save')),
                            ],
                          ),
                        );
                        if (result != null && result.isNotEmpty) {
                          await Provider.of<SecurityProvider>(context, listen: false).setPin(result);
                          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('PIN set.')));
                        }
                      },
                    ),
                    Consumer<SecurityProvider>(
                      builder: (context, provider, _) => SwitchListTile(
                        secondary: const Icon(Icons.fingerprint_outlined, color: Colors.white70),
                        title: const Text('Enable Biometrics', style: TextStyle(color: Colors.white)),
                        value: provider.biometricEnabled,
                        onChanged: (val) async {
                          await provider.setBiometricEnabled(val);
                        },
                      ),
                    ),
                    ListTile(
                      leading: const Icon(Icons.lock_open_outlined, color: Colors.white70),
                      title: const Text('Remove PIN', style: TextStyle(color: Colors.white)),
                      onTap: () async {
                        await Provider.of<SecurityProvider>(context, listen: false).removePin();
                        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('PIN removed.')));
                      },
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 28),
              // Backup & Notifications
              _GlassySettingsCard(
                child: Column(
                  children: [
                    ListTile(
                      leading: const Icon(Icons.backup_outlined, color: Colors.white70),
                      title: const Text('Backup Data', style: TextStyle(color: Colors.white)),
                      onTap: () async {
                        await BackupService().saveBackupFile(context);
                      },
                    ),
                    ListTile(
                      leading: const Icon(Icons.restore_outlined, color: Colors.white70),
                      title: const Text('Restore Data', style: TextStyle(color: Colors.white)),
                      onTap: () async {
                        await BackupService().restoreFromFile(context);
                      },
                    ),
                    Consumer<NotificationSettingsProvider>(
                      builder: (context, notifProvider, _) => SwitchListTile(
                        secondary: const Icon(Icons.notifications_active_outlined, color: Colors.white70),
                        title: const Text('Bill Reminders', style: TextStyle(color: Colors.white)),
                        value: notifProvider.billRemindersEnabled,
                        onChanged: (val) => notifProvider.setBillRemindersEnabled(val),
                      ),
                    ),
                    Consumer<NotificationSettingsProvider>(
                      builder: (context, notifProvider, _) => ListTile(
                        leading: const Icon(Icons.timer_outlined, color: Colors.white70),
                        title: const Text('Default Reminder Time', style: TextStyle(color: Colors.white)),
                        trailing: DropdownButton<int>(
                          value: notifProvider.defaultReminderDays,
                          dropdownColor: Theme.of(context).colorScheme.surface,
                          items: const [
                            DropdownMenuItem(value: 1, child: Text('1 day before')),
                            DropdownMenuItem(value: 2, child: Text('2 days before')),
                            DropdownMenuItem(value: 3, child: Text('3 days before')),
                            DropdownMenuItem(value: 5, child: Text('5 days before')),
                            DropdownMenuItem(value: 7, child: Text('7 days before')),
                          ],
                          onChanged: (val) {
                            if (val != null) notifProvider.setDefaultReminderDays(val);
                          },
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 28),
              // About
              _GlassySettingsCard(
                child: ListTile(
                  leading: const Icon(Icons.info_outline, color: Colors.white70),
                  title: const Text('About', style: TextStyle(color: Colors.white)),
                  subtitle: const Text('Vanta Ledger v1.0.0\nPrivacy: All data is stored locally.\nVisit: github.com/Phantomojo/Vanta-ledger', style: TextStyle(color: Colors.white54)),
                  onTap: () {},
                ),
              ),
              const SizedBox(height: 28),
              // Reset App Data
              _GlassySettingsCard(
                accent: true,
                child: ListTile(
                  leading: const Icon(Icons.delete_forever_outlined, color: Colors.redAccent),
                  title: const Text('Reset App Data', style: TextStyle(color: Colors.redAccent)),
                  subtitle: const Text('Delete all transactions, accounts, categories, budgets, etc.', style: TextStyle(color: Colors.white54)),
                  onTap: () async {
                    final confirm = await showDialog<bool>(
                      context: context,
                      builder: (context) => AlertDialog(
                        title: const Text('Reset App Data'),
                        content: const Text('Are you sure you want to delete all app data? This cannot be undone.'),
                        actions: [
                          TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')),
                          ElevatedButton(onPressed: () => Navigator.pop(context, true), child: const Text('Delete All')),
                        ],
                      ),
                    );
                    if (confirm == true) {
                      await DatabaseService().deleteDatabaseFile();
                      if (mounted) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('All app data deleted.')),
                        );
                        Navigator.of(context).popUntil((route) => route.isFirst);
                      }
                    }
                  },
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _GlassySettingsCard extends StatelessWidget {
  final Widget child;
  final bool accent;
  const _GlassySettingsCard({required this.child, this.accent = false});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(24),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 18, sigmaY: 18),
          child: Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: accent
                    ? [
                        Colors.redAccent.withOpacity(0.10),
                        Colors.white.withOpacity(0.08),
                        Colors.transparent,
                      ]
                    : [
                        Colors.white.withOpacity(0.10),
                        Colors.deepPurple.withOpacity(0.08),
                        Colors.transparent,
                      ],
              ),
              borderRadius: BorderRadius.circular(24),
              border: Border.all(color: Colors.white.withOpacity(0.07), width: 1.0),
            ),
            child: child,
          ),
        ),
      ),
    );
  }
} 