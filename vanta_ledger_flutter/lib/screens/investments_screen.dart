import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/investment.dart';
import '../providers/investment_provider.dart';
import 'package:intl/intl.dart';
import 'package:flutter_svg/flutter_svg.dart';
import '../wakanda_text.dart';
import 'dashboard_screen.dart';

class InvestmentsScreen extends StatefulWidget {
  const InvestmentsScreen({Key? key}) : super(key: key);

  @override
  State<InvestmentsScreen> createState() => _InvestmentsScreenState();
}

class _InvestmentsScreenState extends State<InvestmentsScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<InvestmentProvider>(context, listen: false).loadInvestments();
    });
  }

  void _showInvestmentDialog({InvestmentModel? investment}) {
    final _nameController = TextEditingController(text: investment?.name ?? '');
    final _typeController = TextEditingController(text: investment?.type ?? 'Stock');
    final _amountController = TextEditingController(text: investment?.amount.toString() ?? '');
    final _currencyController = TextEditingController(text: investment?.currency ?? 'USD');
    DateTime? _date = investment?.date;
    final _notesController = TextEditingController(text: investment?.notes ?? '');
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text(investment == null ? 'Add Investment' : 'Edit Investment'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: _nameController,
                  decoration: const InputDecoration(labelText: 'Name'),
                ),
                TextField(
                  controller: _typeController,
                  decoration: const InputDecoration(labelText: 'Type'),
                ),
                TextField(
                  controller: _amountController,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(labelText: 'Amount'),
                ),
                TextField(
                  controller: _currencyController,
                  decoration: const InputDecoration(labelText: 'Currency'),
                ),
                Row(
                  children: [
                    Text(_date == null ? 'Pick Date' : DateFormat.yMMMd().format(_date!)),
                    IconButton(
                      icon: const Icon(Icons.calendar_today),
                      onPressed: () async {
                        final picked = await showDatePicker(
                          context: context,
                          initialDate: _date ?? DateTime.now(),
                          firstDate: DateTime(2000),
                          lastDate: DateTime(2100),
                        );
                        if (picked != null) {
                          setState(() {
                            _date = picked;
                          });
                        }
                      },
                    ),
                  ],
                ),
                TextField(
                  controller: _notesController,
                  decoration: const InputDecoration(labelText: 'Notes (optional)'),
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
                final name = _nameController.text;
                final type = _typeController.text;
                final amount = double.tryParse(_amountController.text) ?? 0.0;
                final currency = _currencyController.text;
                final date = _date ?? DateTime.now();
                final notes = _notesController.text.isEmpty ? null : _notesController.text;
                final provider = Provider.of<InvestmentProvider>(context, listen: false);
                if (investment == null) {
                  await provider.addInvestment(InvestmentModel(
                    name: name,
                    type: type,
                    amount: amount,
                    currency: currency,
                    date: date,
                    notes: notes,
                  ));
                  if (mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Row(
                          children: const [
                            Icon(Icons.check_circle, color: Colors.green),
                            SizedBox(width: 8),
                            Text('Investment added!'),
                          ],
                        ),
                        duration: const Duration(seconds: 2),
                        behavior: SnackBarBehavior.floating,
                      ),
                    );
                  }
                } else {
                  await provider.updateInvestment(investment.copyWith(
                    name: name,
                    type: type,
                    amount: amount,
                    currency: currency,
                    date: date,
                    notes: notes,
                  ));
                  if (mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Row(
                          children: const [
                            Icon(Icons.check_circle, color: Colors.green),
                            SizedBox(width: 8),
                            Text('Investment updated!'),
                          ],
                        ),
                        duration: const Duration(seconds: 2),
                        behavior: SnackBarBehavior.floating,
                      ),
                    );
                  }
                }
                Navigator.pop(context);
              },
              child: Text(investment == null ? 'Add' : 'Update'),
            ),
          ],
        );
      },
    );
  }

  void _deleteInvestment(int id) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Investment'),
        content: const Text('Are you sure you want to delete this investment?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')),
          ElevatedButton(onPressed: () => Navigator.pop(context, true), child: const Text('Delete')),
        ],
      ),
    );
    if (confirm == true) {
      final provider = Provider.of<InvestmentProvider>(context, listen: false);
      await provider.deleteInvestment(id);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Row(
              children: const [
                Icon(Icons.check_circle, color: Colors.green),
                SizedBox(width: 8),
                Text('Investment deleted!'),
              ],
            ),
            duration: const Duration(seconds: 2),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<InvestmentProvider>(
      builder: (context, provider, _) {
        return Scaffold(
          appBar: GlassyAppBar(
            title: 'Investments',
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
              provider.investments.isEmpty
                  ? Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.trending_up, size: 80, color: Colors.grey[400]),
                          const SizedBox(height: 16),
                          const Text('No investments yet.', style: TextStyle(fontSize: 18)),
                          const SizedBox(height: 8),
                          const Text('Add your first investment to get started!'),
                        ],
                      ),
                    )
                  : ListView.builder(
                      itemCount: provider.investments.length,
                      itemBuilder: (context, i) {
                        final inv = provider.investments[i];
                        return Card(
                          margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                          child: ListTile(
                            title: Text(inv.name),
                            subtitle: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text('Type: ${inv.type}'),
                                Text('Amount: ${inv.amount.toStringAsFixed(2)} ${inv.currency}'),
                                Text('Date: ${DateFormat.yMMMd().format(inv.date)}'),
                                if (inv.notes != null && inv.notes!.isNotEmpty)
                                  Text('Notes: ${inv.notes}'),
                              ],
                            ),
                            trailing: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                IconButton(
                                  icon: const Icon(Icons.edit),
                                  onPressed: () => _showInvestmentDialog(investment: inv),
                                ),
                                IconButton(
                                  icon: const Icon(Icons.delete),
                                  onPressed: () => _deleteInvestment(inv.id!),
                                ),
                              ],
                            ),
                          ),
                        );
                      },
                    ),
            ],
          ),
        );
      },
    );
  }
} 