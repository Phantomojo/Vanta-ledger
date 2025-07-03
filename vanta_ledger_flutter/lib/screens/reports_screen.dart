import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/reports_provider.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:fl_chart/fl_chart.dart';
import 'dart:math';
import '../wakanda_text.dart';
import 'dashboard_screen.dart';

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
          appBar: GlassyAppBar(
            title: 'Reports',
          ),
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
                      // --- SUMMARY CARDS ---
                      SingleChildScrollView(
                        scrollDirection: Axis.horizontal,
                        child: Row(
                          children: [
                            _SummaryCard(
                              label: 'Income',
                              value: provider.incomeByMonth.values.fold(0.0, (a, b) => a + b),
                              color: Colors.green,
                            ),
                            const SizedBox(width: 12),
                            _SummaryCard(
                              label: 'Expenses',
                              value: provider.expenseByMonth.values.fold(0.0, (a, b) => a + b),
                              color: Colors.red,
                            ),
                            const SizedBox(width: 12),
                            _SummaryCard(
                              label: 'Net',
                              value: provider.incomeByMonth.values.fold(0.0, (a, b) => a + b) - provider.expenseByMonth.values.fold(0.0, (a, b) => a + b),
                              color: Colors.deepPurple,
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 24),
                      // --- PERIOD SELECTOR (placeholder, can be expanded) ---
                      Row(
                        mainAxisAlignment: MainAxisAlignment.end,
                        children: [
                          Chip(label: Text('This Year')),
                        ],
                      ),
                      const SizedBox(height: 24),
                      // --- INCOME VS EXPENSE CHART ---
                      Text('Income vs Expense', style: Theme.of(context).textTheme.titleMedium?.copyWith(color: Colors.white)),
                      SizedBox(
                        height: 200,
                        child: BarChart(
                          BarChartData(
                            barGroups: List.generate(provider.incomeByMonth.length, (i) {
                              final month = provider.incomeByMonth.keys.elementAt(i);
                              final income = provider.incomeByMonth[month] ?? 0.0;
                              final expense = provider.expenseByMonth[month] ?? 0.0;
                              return BarChartGroupData(x: i, barRods: [
                                BarChartRodData(toY: income, color: Colors.green),
                                BarChartRodData(toY: expense, color: Colors.red),
                              ]);
                            }),
                            titlesData: FlTitlesData(show: false),
                            borderData: FlBorderData(show: false),
                          ),
                        ),
                      ),
                      const SizedBox(height: 32),
                      // --- CATEGORY BREAKDOWN PIE CHART ---
                      Text('Category Breakdown', style: Theme.of(context).textTheme.titleMedium?.copyWith(color: Colors.white)),
                      SizedBox(
                        height: 200,
                        child: PieChart(
                          PieChartData(
                            sections: provider.categoryBreakdown.entries.map((e) {
                              final color = Colors.primaries[Random().nextInt(Colors.primaries.length)];
                              return PieChartSectionData(
                                value: e.value,
                                title: e.key,
                                color: color,
                                radius: 60,
                                titleStyle: const TextStyle(fontSize: 12, color: Colors.white),
                              );
                            }).toList(),
                          ),
                        ),
                      ),
                      const SizedBox(height: 32),
                      // --- NET WORTH OVER TIME ---
                      Text('Net Worth Over Time', style: Theme.of(context).textTheme.titleMedium?.copyWith(color: Colors.white)),
                      SizedBox(
                        height: 200,
                        child: LineChart(
                          LineChartData(
                            lineBarsData: [
                              LineChartBarData(
                                spots: List.generate(provider.netWorthOverTime.length, (i) => FlSpot(i.toDouble(), provider.netWorthOverTime[i])),
                                isCurved: true,
                                color: Colors.deepPurple,
                                barWidth: 3,
                              ),
                            ],
                            titlesData: FlTitlesData(show: false),
                            borderData: FlBorderData(show: false),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
        );
      },
    );
  }
}

// --- SUMMARY CARD WIDGET ---
class _SummaryCard extends StatelessWidget {
  final String label;
  final double value;
  final Color color;
  const _SummaryCard({required this.label, required this.value, required this.color});
  @override
  Widget build(BuildContext context) {
    return Card(
      color: color.withOpacity(0.1),
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        child: Column(
          children: [
            Text(label, style: TextStyle(color: color, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Text('Ksh ${value.toStringAsFixed(2)}', style: TextStyle(color: color, fontSize: 18, fontWeight: FontWeight.bold)),
          ],
        ),
      ),
    );
  }
} 