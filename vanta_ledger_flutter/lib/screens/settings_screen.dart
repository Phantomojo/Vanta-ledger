import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/security_provider.dart';
import '../services/backup_service.dart';
import '../providers/theme_provider.dart';
import '../providers/currency_provider.dart';
import '../providers/notification_settings_provider.dart';

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
      appBar: AppBar(title: const Text('Settings')),
      body: ListView(
        children: [
          Consumer<ThemeProvider>(
            builder: (context, themeProvider, _) => ListTile(
              leading: const Icon(Icons.color_lens, semanticLabel: 'Theme'),
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
              leading: const Icon(Icons.attach_money, semanticLabel: 'Currency'),
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
          const Divider(),
          ListTile(
            leading: const Icon(Icons.account_balance_wallet),
            title: const Text('Manage Accounts'),
            onTap: () => Navigator.pushNamed(context, '/accounts'),
          ),
          ListTile(
            leading: const Icon(Icons.category),
            title: const Text('Manage Categories'),
            onTap: () => Navigator.pushNamed(context, '/categories'),
          ),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.info_outline, semanticLabel: 'About'),
            title: const Text('About', style: TextStyle(color: Colors.white)),
            subtitle: const Text('Vanta Ledger v1.0.0\nPrivacy: All data is stored locally.\nVisit: github.com/Phantomojo/Vanta-ledger'),
            onTap: () {},
          ),
          ListTile(
            leading: const Icon(Icons.lock, semanticLabel: 'Set or change PIN'),
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
              secondary: const Icon(Icons.fingerprint, semanticLabel: 'Enable biometrics'),
              title: const Text('Enable Biometrics', style: TextStyle(color: Colors.white)),
              value: provider.biometricEnabled,
              onChanged: (val) async {
                await provider.setBiometricEnabled(val);
              },
            ),
          ),
          ListTile(
            leading: const Icon(Icons.lock_open, semanticLabel: 'Remove PIN'),
            title: const Text('Remove PIN', style: TextStyle(color: Colors.white)),
            onTap: () async {
              await Provider.of<SecurityProvider>(context, listen: false).removePin();
              ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('PIN removed.')));
            },
          ),
          ListTile(
            leading: const Icon(Icons.backup, semanticLabel: 'Backup data'),
            title: const Text('Backup Data', style: TextStyle(color: Colors.white)),
            onTap: () async {
              await BackupService().saveBackupFile(context);
            },
          ),
          ListTile(
            leading: const Icon(Icons.restore, semanticLabel: 'Restore data'),
            title: const Text('Restore Data', style: TextStyle(color: Colors.white)),
            onTap: () async {
              await BackupService().restoreFromFile(context);
            },
          ),
          Consumer<NotificationSettingsProvider>(
            builder: (context, notifProvider, _) => SwitchListTile(
              secondary: const Icon(Icons.notifications_active, semanticLabel: 'Bill Reminders'),
              title: const Text('Bill Reminders', style: TextStyle(color: Colors.white)),
              value: notifProvider.billRemindersEnabled,
              onChanged: (val) => notifProvider.setBillRemindersEnabled(val),
            ),
          ),
          Consumer<NotificationSettingsProvider>(
            builder: (context, notifProvider, _) => ListTile(
              leading: const Icon(Icons.timer, semanticLabel: 'Default Reminder Time'),
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
    );
  }
} 