import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/bill.dart';
import '../providers/bill_provider.dart';
import 'package:intl/intl.dart';
import 'package:flutter/services.dart';
import 'package:flutter_svg/flutter_svg.dart';

class BillsScreen extends StatefulWidget {
  const BillsScreen({Key? key}) : super(key: key);

  @override
  State<BillsScreen> createState() => _BillsScreenState();
}

class _BillsScreenState extends State<BillsScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<BillProvider>(context, listen: false).loadBills();
    });
  }

  void _showBillDialog({BillModel? bill}) {
    final _nameController = TextEditingController(text: bill?.name ?? '');
    final _amountController = TextEditingController(text: bill?.amount.toString() ?? '');
    DateTime? _dueDate = bill?.dueDate;
    final _repeatController = TextEditingController(text: bill?.repeat ?? '');
    final _notesController = TextEditingController(text: bill?.notes ?? '');
    final _remindController = TextEditingController(text: bill?.remindDaysBefore?.toString() ?? '');

    HapticFeedback.mediumImpact();

    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text(bill == null ? 'Add Bill' : 'Edit Bill'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: _nameController,
                  decoration: const InputDecoration(labelText: 'Name'),
                ),
                TextField(
                  controller: _amountController,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(labelText: 'Amount'),
                ),
                Row(
                  children: [
                    Text(_dueDate == null ? 'Pick Due Date' : DateFormat.yMMMd().format(_dueDate!)),
                    IconButton(
                      icon: const Icon(Icons.calendar_today),
                      onPressed: () async {
                        final picked = await showDatePicker(
                          context: context,
                          initialDate: _dueDate ?? DateTime.now(),
                          firstDate: DateTime(2000),
                          lastDate: DateTime(2100),
                        );
                        if (picked != null) {
                          setState(() {
                            _dueDate = picked;
                          });
                        }
                      },
                    ),
                  ],
                ),
                TextField(
                  controller: _repeatController,
                  decoration: const InputDecoration(labelText: 'Repeat (optional)'),
                ),
                TextField(
                  controller: _notesController,
                  decoration: const InputDecoration(labelText: 'Notes (optional)'),
                ),
                TextField(
                  controller: _remindController,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(labelText: 'Remind X days before (optional)'),
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
                final amount = double.tryParse(_amountController.text) ?? 0.0;
                final dueDate = _dueDate ?? DateTime.now();
                final repeat = _repeatController.text.isEmpty ? null : _repeatController.text;
                final notes = _notesController.text.isEmpty ? null : _notesController.text;
                final remindDaysBefore = int.tryParse(_remindController.text);
                final provider = Provider.of<BillProvider>(context, listen: false);
                if (bill == null) {
                  await provider.addBill(BillModel(
                    name: name,
                    amount: amount,
                    dueDate: dueDate,
                    repeat: repeat,
                    notes: notes,
                    remindDaysBefore: remindDaysBefore,
                  ));
                  if (mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Row(
                          children: const [
                            Icon(Icons.check_circle, color: Colors.green),
                            SizedBox(width: 8),
                            Text('Bill added!'),
                          ],
                        ),
                        duration: const Duration(seconds: 2),
                        behavior: SnackBarBehavior.floating,
                      ),
                    );
                  }
                } else {
                  await provider.updateBill(bill.copyWith(
                    name: name,
                    amount: amount,
                    dueDate: dueDate,
                    repeat: repeat,
                    notes: notes,
                    remindDaysBefore: remindDaysBefore,
                  ));
                  if (mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Row(
                          children: const [
                            Icon(Icons.check_circle, color: Colors.green),
                            SizedBox(width: 8),
                            Text('Bill updated!'),
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
              child: Text(bill == null ? 'Add' : 'Update'),
            ),
          ],
        );
      },
    );
  }

  Color _getBillColor(BillModel bill) {
    if (bill.isPaid) return Colors.green;
    final now = DateTime.now();
    if (bill.dueDate.isBefore(now)) return Colors.red;
    if (bill.dueDate.difference(now).inDays <= 3) return Colors.orange;
    return Colors.blueGrey;
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<BillProvider>(
      builder: (context, provider, _) {
        return Scaffold(
          appBar: AppBar(
            leading: Padding(
              padding: const EdgeInsets.all(8.0),
              child: SvgPicture.asset(
                'assets/images/app_logo_placeholder.svg',
                height: 32,
                width: 32,
                semanticsLabel: 'Vanta Ledger Logo',
              ),
            ),
            title: const Text('Bills'),
            actions: [
              IconButton(
                icon: const Icon(Icons.add, semanticLabel: 'Add Bill'),
                tooltip: 'Add Bill',
                onPressed: () => _showBillDialog(),
              ),
            ],
          ),
          body: provider.bills.isEmpty
              ? Center(
                  child: Semantics(
                    label: 'No bills',
                    hint: 'Add a bill to get reminders and stay on track',
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.receipt, size: 80, color: Colors.grey[500], semanticLabel: 'No bills icon'),
                        const SizedBox(height: 16),
                        Text('No bills yet.', style: TextStyle(fontSize: 18, color: Colors.white)),
                        const SizedBox(height: 8),
                        Text('Add a bill to get reminders and stay on track!', style: TextStyle(color: Colors.white70)),
                      ],
                    ),
                  ),
                )
              : ListView.builder(
                  itemCount: provider.bills.length,
                  itemBuilder: (context, i) {
                    final bill = provider.bills[i];
                    return Card(
                      color: _getBillColor(bill).withOpacity(0.1),
                      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                      child: ListTile(
                        title: Text(bill.name),
                        subtitle: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('Amount: ${bill.amount.toStringAsFixed(2)}'),
                            Text('Due: ${DateFormat.yMMMd().format(bill.dueDate)}'),
                            if (bill.repeat != null && bill.repeat!.isNotEmpty)
                              Text('Repeats: ${bill.repeat}'),
                            if (bill.notes != null && bill.notes!.isNotEmpty)
                              Text('Notes: ${bill.notes}'),
                            if (bill.isPaid)
                              const Text('Paid', style: TextStyle(color: Colors.green, fontWeight: FontWeight.bold)),
                            if (!bill.isPaid && bill.dueDate.isBefore(DateTime.now()))
                              const Text('Overdue', style: TextStyle(color: Colors.red, fontWeight: FontWeight.bold)),
                            if (!bill.isPaid && bill.dueDate.difference(DateTime.now()).inDays <= 3 && bill.dueDate.isAfter(DateTime.now()))
                              const Text('Due soon', style: TextStyle(color: Colors.orange, fontWeight: FontWeight.bold)),
                          ],
                        ),
                        trailing: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            IconButton(
                              icon: Icon(bill.isPaid ? Icons.undo : Icons.check_circle, color: bill.isPaid ? Colors.grey : Colors.green),
                              tooltip: bill.isPaid ? 'Mark as unpaid' : 'Mark as paid',
                              onPressed: () => _markAsPaid(bill.id!, !bill.isPaid),
                            ),
                            IconButton(
                              icon: const Icon(Icons.edit),
                              onPressed: () => _showBillDialog(bill: bill),
                            ),
                            IconButton(
                              icon: const Icon(Icons.delete),
                              onPressed: () => _deleteBill(bill.id!),
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
        );
      },
    );
  }

  void _deleteBill(int id) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Bill'),
        content: const Text('Are you sure you want to delete this bill?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')),
          ElevatedButton(onPressed: () => Navigator.pop(context, true), child: const Text('Delete')),
        ],
      ),
    );
    if (confirm == true) {
      HapticFeedback.lightImpact();
      final provider = Provider.of<BillProvider>(context, listen: false);
      await provider.deleteBill(id);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Row(
              children: const [
                Icon(Icons.check_circle, color: Colors.green),
                SizedBox(width: 8),
                Text('Bill deleted!'),
              ],
            ),
            duration: const Duration(seconds: 2),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    }
  }

  void _markAsPaid(int id, bool isPaid) async {
    HapticFeedback.selectionClick();
    final provider = Provider.of<BillProvider>(context, listen: false);
    await provider.markAsPaid(id, isPaid);
  }
} 