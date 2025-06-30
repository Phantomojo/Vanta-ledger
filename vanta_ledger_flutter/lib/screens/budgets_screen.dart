import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/budget.dart';
import '../providers/budget_provider.dart';
import 'package:flutter/services.dart';
import 'package:flutter_svg/flutter_svg.dart';

class BudgetsScreen extends StatefulWidget {
  const BudgetsScreen({Key? key}) : super(key: key);

  @override
  State<BudgetsScreen> createState() => _BudgetsScreenState();
}

class _BudgetsScreenState extends State<BudgetsScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<BudgetProvider>(context, listen: false).loadBudgets();
    });
  }

  void _showBudgetDialog({BudgetModel? budget}) {
    final _limitController = TextEditingController(text: budget?.limit.toString() ?? '');
    final _periodController = TextEditingController(text: budget?.period ?? 'monthly');
    HapticFeedback.mediumImpact();
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text(budget == null ? 'Add Budget' : 'Edit Budget'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: _limitController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(labelText: 'Limit'),
              ),
              TextField(
                controller: _periodController,
                decoration: const InputDecoration(labelText: 'Period (e.g. monthly)'),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () async {
                final limit = double.tryParse(_limitController.text) ?? 0.0;
                final period = _periodController.text;
                final provider = Provider.of<BudgetProvider>(context, listen: false);
                if (budget == null) {
                  await provider.addBudget(BudgetModel(categoryId: 0, limit: limit, period: period));
                } else {
                  await provider.updateBudget(budget.copyWith(limit: limit, period: period));
                }
                Navigator.pop(context);
              },
              child: Text(budget == null ? 'Add' : 'Update'),
            ),
          ],
        );
      },
    );
  }

  void _deleteBudget(int id) async {
    final provider = Provider.of<BudgetProvider>(context, listen: false);
    await provider.deleteBudget(id);
    HapticFeedback.lightImpact();
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<BudgetProvider>(
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
            title: const Text('Budgets'),
            actions: [
              IconButton(
                icon: const Icon(Icons.add, semanticLabel: 'Add Budget'),
                tooltip: 'Add Budget',
                onPressed: () => _showBudgetDialog(),
              ),
            ],
          ),
          body: provider.budgets.isEmpty
              ? Center(
                  child: Semantics(
                    label: 'No budgets',
                    hint: 'Create a budget to start tracking',
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.account_balance_wallet, size: 80, color: Colors.grey[500], semanticLabel: 'No budgets icon'),
                        const SizedBox(height: 16),
                        Text('No budgets yet.', style: TextStyle(fontSize: 18, color: Colors.white)),
                        const SizedBox(height: 8),
                        Text('Create a budget to start tracking!', style: TextStyle(color: Colors.white70)),
                      ],
                    ),
                  ),
                )
              : ListView.builder(
                  itemCount: provider.budgets.length,
                  itemBuilder: (context, i) {
                    final budget = provider.budgets[i];
                    final percent = (budget.spent / budget.limit).clamp(0.0, 1.0);
                    final over = budget.spent > budget.limit;
                    return Card(
                      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                      child: ListTile(
                        title: Text('Limit: ${budget.limit.toStringAsFixed(2)}'),
                        subtitle: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('Period: ${budget.period}'),
                            const SizedBox(height: 4),
                            LinearProgressIndicator(
                              value: percent,
                              color: over ? Colors.red : Colors.green,
                              backgroundColor: Colors.grey[300],
                            ),
                            const SizedBox(height: 4),
                            Text(
                              'Spent: ${budget.spent.toStringAsFixed(2)}',
                              style: TextStyle(
                                color: over ? Colors.red : null,
                                fontWeight: over ? FontWeight.bold : null,
                              ),
                            ),
                            if (over)
                              const Text(
                                'Over budget!',
                                style: TextStyle(color: Colors.red, fontWeight: FontWeight.bold),
                              ),
                          ],
                        ),
                        trailing: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            IconButton(
                              icon: const Icon(Icons.edit),
                              onPressed: () => _showBudgetDialog(budget: budget),
                            ),
                            IconButton(
                              icon: const Icon(Icons.delete),
                              onPressed: () => _deleteBudget(budget.id!),
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
} 