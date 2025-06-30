import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/transaction.dart';
import '../models/category.dart';
import '../models/account.dart';
import '../providers/transaction_provider.dart';
import '../providers/category_provider.dart';
import '../providers/account_provider.dart';

class AddTransactionScreen extends StatefulWidget {
  final TransactionModel? existing;
  const AddTransactionScreen({super.key, this.existing});

  @override
  State<AddTransactionScreen> createState() => _AddTransactionScreenState();
}

class _AddTransactionScreenState extends State<AddTransactionScreen> {
  final _formKey = GlobalKey<FormState>();
  double? _amount;
  String _description = '';
  DateTime _date = DateTime.now();
  int _type = 0; // 0 = expense, 1 = income
  CategoryModel? _selectedCategory;
  AccountModel? _selectedAccount;
  bool get isEditing => widget.existing != null;

  @override
  void initState() {
    super.initState();
    if (isEditing) {
      final tx = widget.existing!;
      _amount = tx.amount;
      _description = tx.description;
      _date = tx.date;
      _type = tx.type == TransactionType.expense ? 0 : 1;
      // Category/account will be set in build (after providers load)
    }
  }

  @override
  Widget build(BuildContext context) {
    final categories = context.watch<CategoryProvider>().categories;
    final accounts = context.watch<AccountProvider>().accounts;
    // Set selected category/account if editing and not set yet
    if (isEditing && _selectedCategory == null && categories.isNotEmpty) {
      _selectedCategory = categories.firstWhereOrNull((cat) => cat.id == widget.existing!.categoryId) ?? categories.first;
    }
    if (isEditing && _selectedAccount == null && accounts.isNotEmpty) {
      _selectedAccount = accounts.firstWhereOrNull((acc) => acc.id == widget.existing!.accountId) ?? accounts.first;
    }
    return Scaffold(
      appBar: AppBar(title: Text(isEditing ? 'Edit Transaction' : 'Add Transaction')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: ListView(
            children: [
              TextFormField(
                initialValue: _amount?.toString() ?? '',
                decoration: const InputDecoration(labelText: 'Amount'),
                keyboardType: TextInputType.number,
                validator: (val) => val == null || val.isEmpty ? 'Enter amount' : null,
                onSaved: (val) => _amount = double.tryParse(val ?? ''),
              ),
              TextFormField(
                initialValue: _description,
                decoration: const InputDecoration(labelText: 'Description'),
                onSaved: (val) => _description = val ?? '',
              ),
              ListTile(
                contentPadding: EdgeInsets.zero,
                title: const Text('Date'),
                subtitle: Text('${_date.year}-${_date.month.toString().padLeft(2, '0')}-${_date.day.toString().padLeft(2, '0')}'),
                trailing: IconButton(
                  icon: const Icon(Icons.calendar_today),
                  onPressed: () async {
                    final picked = await showDatePicker(
                      context: context,
                      initialDate: _date,
                      firstDate: DateTime(2000),
                      lastDate: DateTime(2100),
                    );
                    if (picked != null) setState(() => _date = picked);
                  },
                ),
              ),
              DropdownButtonFormField<int>(
                value: _type,
                decoration: const InputDecoration(labelText: 'Type'),
                items: const [
                  DropdownMenuItem(value: 0, child: Text('Expense')),
                  DropdownMenuItem(value: 1, child: Text('Income')),
                ],
                onChanged: (val) => setState(() => _type = val ?? 0),
              ),
              DropdownButtonFormField<CategoryModel>(
                value: _selectedCategory,
                decoration: const InputDecoration(labelText: 'Category'),
                items: categories
                    .map((cat) => DropdownMenuItem(
                          value: cat,
                          child: Text(cat.name),
                        ))
                    .toList(),
                onChanged: (val) => setState(() => _selectedCategory = val),
                validator: (val) => val == null ? 'Select category' : null,
              ),
              DropdownButtonFormField<AccountModel>(
                value: _selectedAccount,
                decoration: const InputDecoration(labelText: 'Account'),
                items: accounts
                    .map((acc) => DropdownMenuItem(
                          value: acc,
                          child: Text(acc.name),
                        ))
                    .toList(),
                onChanged: (val) => setState(() => _selectedAccount = val),
                validator: (val) => val == null ? 'Select account' : null,
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: () async {
                  if (_formKey.currentState?.validate() ?? false) {
                    _formKey.currentState?.save();
                    final tx = TransactionModel(
                      id: isEditing ? widget.existing!.id : null,
                      amount: _amount!,
                      description: _description,
                      date: _date,
                      categoryId: _selectedCategory!.id!,
                      accountId: _selectedAccount!.id!,
                      type: _type == 0 ? TransactionType.expense : TransactionType.income,
                      recurrence: RecurrenceType.none,
                    );
                    if (isEditing) {
                      await context.read<TransactionProvider>().updateTransaction(tx);
                    } else {
                      await context.read<TransactionProvider>().addTransaction(tx);
                    }
                    if (mounted) Navigator.pop(context);
                  }
                },
                child: Text(isEditing ? 'Save Changes' : 'Add Transaction'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

extension FirstWhereOrNullExtension<E> on List<E> {
  E? firstWhereOrNull(bool Function(E) test) {
    for (final e in this) {
      if (test(e)) return e;
    }
    return null;
  }
} 