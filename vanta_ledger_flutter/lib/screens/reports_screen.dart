import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/reports_provider.dart';
import 'package:flutter_svg/flutter_svg.dart';

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
            title: const Text('Reports & Analytics'),
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
                      const Text('Income vs Expense', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
                      const SizedBox(height: 24),
                      const Text('Net Worth Over Time', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
                      const SizedBox(height: 24),
                      const Text('Category Breakdown', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
                      const SizedBox(height: 24),
                      // Charts removed for compatibility. Add new charts here in the future.
                    ],
                  ),
                ),
        );
      },
    );
  }
} 