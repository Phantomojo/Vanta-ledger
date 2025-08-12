import React, { useState, useEffect } from 'react';
import api from '../api';

interface Notification {
  id: number;
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  read: boolean;
  created_at: string;
  category: 'system' | 'document' | 'project' | 'financial' | 'user';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  action_url?: string;
  expires_at?: string;
}

interface NotificationSettings {
  email_notifications: boolean;
  push_notifications: boolean;
  document_notifications: boolean;
  project_notifications: boolean;
  financial_notifications: boolean;
  system_notifications: boolean;
  quiet_hours: {
    enabled: boolean;
    start_time: string;
    end_time: string;
  };
}

const Notifications: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [settings, setSettings] = useState<NotificationSettings>({
    email_notifications: true,
    push_notifications: true,
    document_notifications: true,
    project_notifications: true,
    financial_notifications: true,
    system_notifications: true,
    quiet_hours: {
      enabled: false,
      start_time: '22:00',
      end_time: '08:00'
    }
  });
  const [loading, setLoading] = useState(true);
  const [showSettings, setShowSettings] = useState(false);
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchNotifications();
    fetchSettings();
  }, []);

  const fetchNotifications = async () => {
    try {
      setLoading(true);
      const response = await api.get('/notifications/');
      setNotifications(response.data);
    } catch (error) {
      console.error('Error fetching notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSettings = async () => {
    try {
      const response = await api.get('/notifications/settings/');
      setSettings(response.data);
    } catch (error) {
      console.error('Error fetching notification settings:', error);
    }
  };

  const markAsRead = async (notificationId: number) => {
    try {
      await api.patch(`/notifications/${notificationId}/read`);
      setNotifications(notifications.map(notif => 
        notif.id === notificationId ? { ...notif, read: true } : notif
      ));
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  const markAllAsRead = async () => {
    try {
      await api.post('/notifications/mark-all-read');
      setNotifications(notifications.map(notif => ({ ...notif, read: true })));
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
    }
  };

  const deleteNotification = async (notificationId: number) => {
    try {
      await api.delete(`/notifications/${notificationId}`);
      setNotifications(notifications.filter(notif => notif.id !== notificationId));
    } catch (error) {
      console.error('Error deleting notification:', error);
    }
  };

  const updateSettings = async (newSettings: Partial<NotificationSettings>) => {
    try {
      const updatedSettings = { ...settings, ...newSettings };
      await api.put('/notifications/settings/', updatedSettings);
      setSettings(updatedSettings);
    } catch (error) {
      console.error('Error updating notification settings:', error);
    }
  };

  const getFilteredNotifications = () => {
    let filtered = notifications;

    // Apply filter
    if (filter !== 'all') {
      filtered = filtered.filter(notif => {
        if (filter === 'unread') return !notif.read;
        if (filter === 'read') return notif.read;
        return notif.type === filter;
      });
    }

    // Apply search
    if (searchTerm) {
      filtered = filtered.filter(notif =>
        notif.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        notif.message.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    return filtered.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'success': return 'bg-green-100 text-green-800 border-green-200';
      case 'warning': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'error': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-blue-100 text-blue-800 border-blue-200';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'bg-red-500';
      case 'high': return 'bg-orange-500';
      case 'medium': return 'bg-yellow-500';
      default: return 'bg-gray-500';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'document': return '📄';
      case 'project': return '📋';
      case 'financial': return '💰';
      case 'user': return '👤';
      default: return '🔔';
    }
  };

  const filteredNotifications = getFilteredNotifications();
  const unreadCount = notifications.filter(n => !n.read).length;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Notifications</h1>
          <p className="text-gray-600 mt-1">
            {unreadCount} unread notification{unreadCount !== 1 ? 's' : ''}
          </p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors"
          >
            Settings
          </button>
          <button
            onClick={markAllAsRead}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Mark All Read
          </button>
        </div>
      </div>

      {/* Notification Settings */}
      {showSettings && (
        <div className="bg-white p-6 rounded-lg shadow-sm mb-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Notification Settings</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-700 mb-3">Notification Types</h4>
              <div className="space-y-3">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.email_notifications}
                    onChange={(e) => updateSettings({ email_notifications: e.target.checked })}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">Email Notifications</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.push_notifications}
                    onChange={(e) => updateSettings({ push_notifications: e.target.checked })}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">Push Notifications</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.document_notifications}
                    onChange={(e) => updateSettings({ document_notifications: e.target.checked })}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">Document Notifications</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.project_notifications}
                    onChange={(e) => updateSettings({ project_notifications: e.target.checked })}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">Project Notifications</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.financial_notifications}
                    onChange={(e) => updateSettings({ financial_notifications: e.target.checked })}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">Financial Notifications</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.system_notifications}
                    onChange={(e) => updateSettings({ system_notifications: e.target.checked })}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">System Notifications</span>
                </label>
              </div>
            </div>
            <div>
              <h4 className="font-medium text-gray-700 mb-3">Quiet Hours</h4>
              <div className="space-y-3">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.quiet_hours.enabled}
                    onChange={(e) => updateSettings({
                      quiet_hours: { ...settings.quiet_hours, enabled: e.target.checked }
                    })}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">Enable Quiet Hours</span>
                </label>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm text-gray-700 mb-1">Start Time</label>
                    <input
                      type="time"
                      value={settings.quiet_hours.start_time}
                      onChange={(e) => updateSettings({
                        quiet_hours: { ...settings.quiet_hours, start_time: e.target.value }
                      })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-700 mb-1">End Time</label>
                    <input
                      type="time"
                      value={settings.quiet_hours.end_time}
                      onChange={(e) => updateSettings({
                        quiet_hours: { ...settings.quiet_hours, end_time: e.target.value }
                      })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow-sm mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Filter</label>
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Notifications</option>
              <option value="unread">Unread</option>
              <option value="read">Read</option>
              <option value="info">Info</option>
              <option value="success">Success</option>
              <option value="warning">Warning</option>
              <option value="error">Error</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
            <input
              type="text"
              placeholder="Search notifications..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="flex items-end">
            <button
              onClick={() => {
                setFilter('all');
                setSearchTerm('');
              }}
              className="w-full bg-gray-500 text-white px-4 py-2 rounded-md hover:bg-gray-600 transition-colors"
            >
              Clear Filters
            </button>
          </div>
        </div>
      </div>

      {/* Notifications List */}
      <div className="space-y-4">
        {filteredNotifications.length === 0 ? (
          <div className="bg-white p-8 rounded-lg shadow-sm text-center">
            <div className="text-gray-400 text-6xl mb-4">🔔</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No notifications</h3>
            <p className="text-gray-600">You're all caught up!</p>
          </div>
        ) : (
          filteredNotifications.map((notification) => (
            <div
              key={notification.id}
              className={`bg-white p-4 rounded-lg shadow-sm border-l-4 ${
                notification.read ? 'opacity-75' : ''
              } ${getTypeColor(notification.type)}`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3 flex-1">
                  <div className="flex-shrink-0">
                    <div className="flex items-center space-x-2">
                      <span className="text-lg">{getCategoryIcon(notification.category)}</span>
                      <div className={`w-2 h-2 rounded-full ${getPriorityColor(notification.priority)}`}></div>
                    </div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 mb-1">
                      <h4 className="text-sm font-medium text-gray-900">{notification.title}</h4>
                      {!notification.read && (
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                          New
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{notification.message}</p>
                    <div className="flex items-center space-x-4 text-xs text-gray-500">
                      <span>{new Date(notification.created_at).toLocaleString()}</span>
                      <span className="capitalize">{notification.category}</span>
                      <span className="capitalize">{notification.priority} priority</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {!notification.read && (
                    <button
                      onClick={() => markAsRead(notification.id)}
                      className="text-blue-600 hover:text-blue-800 text-sm"
                    >
                      Mark Read
                    </button>
                  )}
                  <button
                    onClick={() => deleteNotification(notification.id)}
                    className="text-red-600 hover:text-red-800 text-sm"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
  </div>
);
};

export default Notifications; 