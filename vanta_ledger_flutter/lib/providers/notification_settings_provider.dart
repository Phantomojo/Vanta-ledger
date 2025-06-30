import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class NotificationSettingsProvider extends ChangeNotifier {
  bool _billRemindersEnabled = true;
  int _defaultReminderDays = 3;

  bool get billRemindersEnabled => _billRemindersEnabled;
  int get defaultReminderDays => _defaultReminderDays;

  NotificationSettingsProvider() {
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    final prefs = await SharedPreferences.getInstance();
    _billRemindersEnabled = prefs.getBool('bill_reminders_enabled') ?? true;
    _defaultReminderDays = prefs.getInt('default_reminder_days') ?? 3;
    notifyListeners();
  }

  Future<void> setBillRemindersEnabled(bool enabled) async {
    _billRemindersEnabled = enabled;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('bill_reminders_enabled', enabled);
    notifyListeners();
  }

  Future<void> setDefaultReminderDays(int days) async {
    _defaultReminderDays = days;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt('default_reminder_days', days);
    notifyListeners();
  }
} 