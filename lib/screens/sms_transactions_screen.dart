import 'package:flutter/material.dart';

class SMSTransactionsScreen extends StatelessWidget {
  const SMSTransactionsScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    // Placeholder for parsed SMS transactions
    return Scaffold(
      appBar: AppBar(title: const Text('SMS Transactions')),
      body: ListView.builder(
        itemCount: 0, // Will be replaced with actual parsed messages
        itemBuilder: (context, index) {
          return ListTile(
            leading: const Icon(Icons.sms),
            title: const Text('Sender/Provider'),
            subtitle: const Text('Message details...'),
            trailing: const Text('Amount'),
          );
        },
      ),
    );
  }
} 