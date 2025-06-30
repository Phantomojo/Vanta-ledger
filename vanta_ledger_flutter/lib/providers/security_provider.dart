import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:local_auth/local_auth.dart';

class SecurityProvider extends ChangeNotifier {
  final _storage = const FlutterSecureStorage();
  final _auth = LocalAuthentication();

  String? _pin;
  bool _biometricEnabled = false;
  bool get biometricEnabled => _biometricEnabled;

  Future<void> loadSecurity() async {
    _pin = await _storage.read(key: 'pin');
    _biometricEnabled = (await _storage.read(key: 'biometric')) == 'true';
    notifyListeners();
  }

  Future<void> setPin(String pin) async {
    _pin = pin;
    await _storage.write(key: 'pin', value: pin);
    notifyListeners();
  }

  Future<void> removePin() async {
    _pin = null;
    await _storage.delete(key: 'pin');
    notifyListeners();
  }

  Future<bool> checkPin(String pin) async {
    return _pin == pin;
  }

  Future<void> setBiometricEnabled(bool enabled) async {
    _biometricEnabled = enabled;
    await _storage.write(key: 'biometric', value: enabled.toString());
    notifyListeners();
  }

  Future<bool> authenticateWithBiometrics() async {
    try {
      return await _auth.authenticate(
        localizedReason: 'Authenticate to access Vanta Ledger',
        options: const AuthenticationOptions(biometricOnly: true),
      );
    } catch (_) {
      return false;
    }
  }

  bool get hasPin => _pin != null && _pin!.isNotEmpty;
} 