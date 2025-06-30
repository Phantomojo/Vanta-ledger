import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:timezone/timezone.dart' as tz;

class NotificationsService {
  static final NotificationsService _instance = NotificationsService._internal();
  factory NotificationsService() => _instance;
  NotificationsService._internal();

  final FlutterLocalNotificationsPlugin _flutterLocalNotificationsPlugin = FlutterLocalNotificationsPlugin();

  Future<void> init() async {
    const AndroidInitializationSettings initializationSettingsAndroid =
        AndroidInitializationSettings('@mipmap/ic_launcher');
    const InitializationSettings initializationSettings = InitializationSettings(
      android: initializationSettingsAndroid,
    );
    await _flutterLocalNotificationsPlugin.initialize(initializationSettings);
  }

  Future<void> scheduleBillReminder({
    required int billId,
    required String title,
    required String body,
    required DateTime scheduledDate,
  }) async {
    await _flutterLocalNotificationsPlugin.zonedSchedule(
      billId,
      title,
      body,
      tz.TZDateTime.from(scheduledDate, tz.local),
      const NotificationDetails(
        android: AndroidNotificationDetails(
          'bills_channel',
          'Bill Reminders',
          channelDescription: 'Reminders for upcoming bills',
          importance: Importance.max,
          priority: Priority.high,
        ),
      ),
      androidAllowWhileIdle: true,
      uiLocalNotificationDateInterpretation:
          UILocalNotificationDateInterpretation.absoluteTime,
      matchDateTimeComponents: DateTimeComponents.dateAndTime,
    );
  }

  Future<void> cancelBillReminder(int billId) async {
    await _flutterLocalNotificationsPlugin.cancel(billId);
  }
} 