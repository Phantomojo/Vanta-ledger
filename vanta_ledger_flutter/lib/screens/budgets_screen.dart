import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/budget.dart';
import '../providers/budget_provider.dart';
import 'package:flutter/services.dart';
import 'package:flutter_svg/flutter_svg.dart';
import '../wakanda_text.dart';
import 'dashboard_screen.dart';

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
    final _budgetLimitController = TextEditingController(text: budget?.budgetLimit.toString() ?? '');
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
                controller: _budgetLimitController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(labelText: 'Budget Limit'),
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
                final budgetLimit = double.tryParse(_budgetLimitController.text) ?? 0.0;
                final period = _periodController.text;
                final provider = Provider.of<BudgetProvider>(context, listen: false);
                if (budget == null) {
                  await provider.addBudget(BudgetModel(categoryId: 0, budgetLimit: budgetLimit, period: period));
                } else {
                  await provider.updateBudget(budget.copyWith(budgetLimit: budgetLimit, period: period));
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
          appBar: GlassyAppBar(
            title: 'Budgets',
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
              provider.budgets.isEmpty
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
                        final percent = (budget.spent / budget.budgetLimit).clamp(0.0, 1.0);
                        final over = budget.spent > budget.budgetLimit;
                        return Card(
                          margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                          child: ListTile(
                            title: Text('Budget Limit: ${budget.budgetLimit.toStringAsFixed(2)}'),
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
            ],
          ),
        );
      },
    );
  }
} 