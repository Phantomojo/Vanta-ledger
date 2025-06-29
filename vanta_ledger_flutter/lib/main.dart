import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'theme/app_theme.dart';
import 'screens/timeline_screen.dart';

void main() {
  runApp(const VantaLedgerApp());
}

class VantaLedgerApp extends StatelessWidget {
  const VantaLedgerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Vanta Ledger',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkPurpleTheme,
      home: const TimelineScreen(),
    );
  }
} 