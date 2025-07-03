import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/account_provider.dart';
import '../models/account.dart';
import '../wakanda_text.dart';
import 'dashboard_screen.dart';
import 'dart:ui';
import '../components/glassy_card.dart';

class AccountScreen extends StatefulWidget {
  const AccountScreen({super.key});

  @override
  State<AccountScreen> createState() => _AccountScreenState();
}

class _AccountScreenState extends State<AccountScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<AccountProvider>(context, listen: false).loadAccounts();
    });
  }

  Future<void> _showAddAccountDialog() async {
    final _formKey = GlobalKey<FormState>();
    String name = '';
    double? balance;
    await showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Add Account'),
        content: Form(
          key: _formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextFormField(
                decoration: const InputDecoration(labelText: 'Name'),
                validator: (val) => val == null || val.isEmpty ? 'Enter name' : null,
                onSaved: (val) => name = val ?? '',
              ),
              TextFormField(
                decoration: const InputDecoration(labelText: 'Balance'),
                keyboardType: TextInputType.number,
                validator: (val) => val == null || val.isEmpty ? 'Enter balance' : null,
                onSaved: (val) => balance = double.tryParse(val ?? ''),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () async {
              if (_formKey.currentState?.validate() ?? false) {
                _formKey.currentState?.save();
                final acc = AccountModel(
                  name: name,
                  balance: balance ?? 0.0,
                );
                await Provider.of<AccountProvider>(context, listen: false).addAccount(acc);
                if (mounted) Navigator.pop(context);
              }
            },
            child: const Text('Add'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final accounts = context.watch<AccountProvider>().accounts;
    return Scaffold(
      appBar: GlassyAppBar(
        title: 'Accounts',
      ),
      body: Stack(
        children: [
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
          Column(
            children: [
              Container(
                width: double.infinity,
                color: Colors.amber,
                padding: const EdgeInsets.all(8),
                child: const Text('DEBUG: AccountScreen loaded', textAlign: TextAlign.center),
              ),
              Expanded(
                child: accounts.isEmpty
                    ? const Center(child: Text('No accounts yet.'))
                    : ListView.builder(
                        itemCount: accounts.length,
                        itemBuilder: (context, index) {
                          final acc = accounts[index];
                          return Dismissible(
                            key: ValueKey(acc.id),
                            direction: accounts.length > 1 ? DismissDirection.endToStart : DismissDirection.none,
                            background: Container(
                              color: Colors.red,
                              alignment: Alignment.centerRight,
                              padding: const EdgeInsets.symmetric(horizontal: 20),
                              child: const Icon(Icons.delete, color: Colors.white),
                            ),
                            confirmDismiss: (direction) async {
                              if (accounts.length <= 1) return false;
                              return await showDialog(
                                context: context,
                                builder: (context) => AlertDialog(
                                  title: const Text('Delete Account'),
                                  content: Text('Are you sure you want to delete "${acc.name}"?'),
                                  actions: [
                                    TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')),
                                    ElevatedButton(onPressed: () => Navigator.pop(context, true), child: const Text('Delete')),
                                  ],
                                ),
                              );
                            },
                            onDismissed: (_) async {
                              await Provider.of<AccountProvider>(context, listen: false).deleteAccount(acc.id!);
                            },
                            child: ListTile(
                              leading: const Icon(Icons.account_balance_wallet),
                              title: Text(acc.name),
                              subtitle: Text('Balance: ${acc.balance.toStringAsFixed(2)}'),
                              trailing: IconButton(
                                icon: const Icon(Icons.edit),
                                onPressed: () async {
                                  final _formKey = GlobalKey<FormState>();
                                  String name = acc.name;
                                  await showDialog(
                                    context: context,
                                    builder: (context) => AlertDialog(
                                      title: const Text('Rename Account'),
                                      content: Form(
                                        key: _formKey,
                                        child: TextFormField(
                                          initialValue: name,
                                          validator: (val) => val == null || val.isEmpty ? 'Enter name' : null,
                                          onSaved: (val) => name = val ?? '',
                                        ),
                                      ),
                                      actions: [
                                        TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
                                        ElevatedButton(
                                          onPressed: () async {
                                            if (_formKey.currentState?.validate() ?? false) {
                                              _formKey.currentState?.save();
                                              await Provider.of<AccountProvider>(context, listen: false).updateAccount(
                                                acc.copyWith(name: name),
                                              );
                                              Navigator.pop(context);
                                            }
                                          },
                                          child: const Text('Save'),
                                        ),
                                      ],
                                    ),
                                  );
                                },
                              ),
                            ),
                          );
                        },
                      ),
              ),
            ],
          ),
        ],
      ),
      floatingActionButton: Padding(
        padding: const EdgeInsets.only(bottom: 70),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(18),
          child: BackdropFilter(
            filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
            child: FloatingActionButton(
              backgroundColor: Colors.white.withOpacity(0.18),
              foregroundColor: Colors.deepPurpleAccent,
              elevation: 0,
              onPressed: _showAddAccountDialog,
              child: const Icon(Icons.add),
            ),
          ),
        ),
      ),
    );
  }
} 