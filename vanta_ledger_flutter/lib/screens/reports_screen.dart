import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/reports_provider.dart';
import 'package:charts_flutter/flutter.dart' as charts;

class ReportsScreen extends StatefulWidget {
  const ReportsScreen({Key? key}) : super(key: key);

  @override
  State<ReportsScreen> createState() => _ReportsScreenState();
}

class _ReportsScreenState extends State<ReportsScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<ReportsProvider>(context, listen: false).loadData();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<ReportsProvider>(
      builder: (context, provider, _) {
        return Scaffold(
          appBar: AppBar(title: const Text('Reports & Analytics')),
          body: provider.incomeByMonth.isEmpty && provider.expenseByMonth.isEmpty
              ? Center(
                  child: Semantics(
                    label: 'No reports data',
                    hint: 'Add transactions to see analytics and charts',
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.bar_chart, size: 80, color: Colors.grey[500], semanticLabel: 'No reports icon'),
                        const SizedBox(height: 16),
                        Text('No data yet.', style: TextStyle(fontSize: 18, color: Colors.white)),
                        const SizedBox(height: 8),
                        Text('Add transactions to see analytics and charts', style: TextStyle(color: Colors.white70)),
                      ],
                    ),
                  ),
                )
              : SingleChildScrollView(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Income vs Expense', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
                      SizedBox(
                        height: 200,
                        child: charts.BarChart([
                          charts.Series<MapEntry<String, double>, String>(
                            id: 'Income',
                            colorFn: (_, __) => charts.MaterialPalette.green.shadeDefault,
                            domainFn: (entry, _) => entry.key,
                            measureFn: (entry, _) => entry.value,
                            data: provider.incomeByMonth.entries.toList(),
                          ),
                          charts.Series<MapEntry<String, double>, String>(
                            id: 'Expense',
                            colorFn: (_, __) => charts.MaterialPalette.red.shadeDefault,
                            domainFn: (entry, _) => entry.key,
                            measureFn: (entry, _) => entry.value,
                            data: provider.expenseByMonth.entries.toList(),
                          ),
                        ], animate: true, barGroupingType: charts.BarGroupingType.grouped),
                      ),
                      const SizedBox(height: 24),
                      const Text('Net Worth Over Time', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
                      SizedBox(
                        height: 200,
                        child: charts.LineChart([
                          charts.Series<double, int>(
                            id: 'Net Worth',
                            colorFn: (_, __) => charts.MaterialPalette.purple.shadeDefault,
                            domainFn: (value, idx) => idx!,
                            measureFn: (value, _) => value,
                            data: provider.netWorthOverTime,
                          ),
                        ], animate: true),
                      ),
                      const SizedBox(height: 24),
                      const Text('Category Breakdown', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
                      SizedBox(
                        height: 200,
                        child: charts.PieChart([
                          charts.Series<MapEntry<String, double>, String>(
                            id: 'Categories',
                            domainFn: (entry, _) => entry.key,
                            measureFn: (entry, _) => entry.value,
                            data: provider.categoryBreakdown.entries.toList(),
                            labelAccessorFn: (entry, _) => '${entry.key}: ${entry.value.toStringAsFixed(0)}',
                          ),
                        ], animate: true, defaultRenderer: charts.ArcRendererConfig(arcRendererDecorators: [charts.ArcLabelDecorator()])),
                      ),
                    ],
                  ),
                ),
        );
      },
    );
  }
} 