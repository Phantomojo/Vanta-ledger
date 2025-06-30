import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/security_provider.dart';

class LockScreen extends StatefulWidget {
  const LockScreen({Key? key}) : super(key: key);

  @override
  State<LockScreen> createState() => _LockScreenState();
}

class _LockScreenState extends State<LockScreen> {
  final _pinController = TextEditingController();
  String? _error;
  bool _biometricTried = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      final provider = Provider.of<SecurityProvider>(context, listen: false);
      await provider.loadSecurity();
      if (provider.biometricEnabled && !_biometricTried) {
        _biometricTried = true;
        final success = await provider.authenticateWithBiometrics();
        if (success) {
          Navigator.of(context).pop(true);
        }
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Consumer<SecurityProvider>(
            builder: (context, provider, _) {
              return Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(Icons.lock, size: 64),
                  const SizedBox(height: 16),
                  const Text('Enter PIN to unlock', style: TextStyle(fontSize: 18)),
                  const SizedBox(height: 16),
                  TextField(
                    controller: _pinController,
                    obscureText: true,
                    keyboardType: TextInputType.number,
                    decoration: InputDecoration(
                      labelText: 'PIN',
                      errorText: _error,
                    ),
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: () async {
                      final ok = await provider.checkPin(_pinController.text);
                      if (ok) {
                        Navigator.of(context).pop(true);
                      } else {
                        setState(() => _error = 'Incorrect PIN');
                      }
                    },
                    child: const Text('Unlock'),
                  ),
                  if (provider.biometricEnabled)
                    TextButton(
                      onPressed: () async {
                        final success = await provider.authenticateWithBiometrics();
                        if (success) {
                          Navigator.of(context).pop(true);
                        } else {
                          setState(() => _error = 'Biometric failed');
                        }
                      },
                      child: const Text('Use Biometrics'),
                    ),
                ],
              );
            },
          ),
        ),
      ),
    );
  }
} 