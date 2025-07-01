import 'package:flutter_test/flutter_test.dart';
import 'package:vanta_ledger_flutter/providers/budget_provider.dart';
import 'package:vanta_ledger_flutter/models/budget.dart';

void main() {
  test('BudgetProvider add, load, and delete', () async {
    final provider = BudgetProvider();
    final budget = BudgetModel(
      id: null,
      categoryId: 1,
      budgetLimit: 500.0,
      period: 'monthly',
      spent: 0.0,
    );
    await provider.addBudget(budget);
    await provider.loadBudgets();
    expect(provider.budgets.any((b) => b.budgetLimit == 500.0), true);
    final added = provider.budgets.firstWhere((b) => b.budgetLimit == 500.0);
    await provider.deleteBudget(added.id!);
    await provider.loadBudgets();
    expect(provider.budgets.any((b) => b.budgetLimit == 500.0), false);
  });
} 