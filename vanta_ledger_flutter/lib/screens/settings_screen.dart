import 'package:flutter/material.dart';

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
          ListTile(
            leading: const Icon(Icons.color_lens),
            title: const Text('Theme'),
            subtitle: Text(_themeMode == ThemeMode.system
                ? 'System Default'
                : _themeMode == ThemeMode.dark
                    ? 'Dark'
                    : 'Light'),
            onTap: () async {
              final mode = await showDialog<ThemeMode>(
                context: context,
                builder: (context) => SimpleDialog(
                  title: const Text('Choose Theme'),
                  children: [
                    SimpleDialogOption(
                      child: const Text('System Default'),
                      onPressed: () => Navigator.pop(context, ThemeMode.system),
                    ),
                    SimpleDialogOption(
                      child: const Text('Light'),
                      onPressed: () => Navigator.pop(context, ThemeMode.light),
                    ),
                    SimpleDialogOption(
                      child: const Text('Dark'),
                      onPressed: () => Navigator.pop(context, ThemeMode.dark),
                    ),
                  ],
                ),
              );
              if (mode != null) setState(() => _themeMode = mode);
            },
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
            leading: const Icon(Icons.info_outline),
            title: const Text('About'),
            subtitle: const Text('Vanta Ledger v1.0.0'),
          ),
        ],
      ),
    );
  }
} 