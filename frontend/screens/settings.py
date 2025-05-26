"""
Settings screen for Vanta Ledger Enhanced.

This module provides the application settings screen.
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.switch import Switch
from kivy.properties import ObjectProperty

class SettingsScreen(Screen):
    """
    Settings screen for configuring application preferences.
    
    Features:
    - Currency settings
    - Theme selection (light/dark)
    - Notification preferences
    - Data export/import options
    """
    
    api_client = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        """Initialize the settings screen."""
        super(SettingsScreen, self).__init__(**kwargs)
        
        # Main layout
        self.layout = BoxLayout(orientation='vertical', spacing=15, padding=20)
        
        # Add header
        self.header = self._create_header()
        self.layout.add_widget(self.header)
        
        # Add settings sections
        self.appearance_section = self._create_appearance_section()
        self.layout.add_widget(self.appearance_section)
        
        self.currency_section = self._create_currency_section()
        self.layout.add_widget(self.currency_section)
        
        self.notification_section = self._create_notification_section()
        self.layout.add_widget(self.notification_section)
        
        self.data_section = self._create_data_section()
        self.layout.add_widget(self.data_section)
        
        # Add save button
        self.save_button = Button(
            text="Save Settings",
            size_hint=(1, 0.1),
            background_normal='',
            background_color=(0, 0.6, 0.9, 1),
            color=(1, 1, 1, 1)
        )
        self.save_button.bind(on_press=self._on_save_settings)
        self.layout.add_widget(self.save_button)
        
        self.add_widget(self.layout)
    
    def on_enter(self):
        """Called when the screen is entered."""
        # Get API client from app
        if not self.api_client and hasattr(self.manager.parent.parent, 'api_client'):
            self.api_client = self.manager.parent.parent.api_client
        
        # Load current settings
        self.load_settings()
    
    def load_settings(self):
        """Load current settings."""
        if not self.api_client:
            return
        
        # In a real implementation, we would get settings from the API
        # For now, we'll use default values
        self.currency_input.text = "USD"
        self.dark_mode_switch.active = False
        self.notification_switch.active = True
        self.negative_balance_switch.active = False
    
    def _create_header(self):
        """Create the header section."""
        header = BoxLayout(orientation='vertical', size_hint=(1, 0.1))
        
        title = Label(
            text="Settings",
            size_hint=(1, 1),
            halign='left',
            valign='middle',
            font_size='22sp',
            color=(0.3, 0.3, 0.3, 1)
        )
        title.bind(size=title.setter('text_size'))
        
        header.add_widget(title)
        return header
    
    def _create_appearance_section(self):
        """Create the appearance settings section."""
        section = BoxLayout(orientation='vertical', size_hint=(1, 0.2), spacing=5)
        
        # Section title
        title = Label(
            text="Appearance",
            size_hint=(1, 0.3),
            halign='left',
            valign='middle',
            font_size='18sp',
            color=(0.3, 0.3, 0.3, 1)
        )
        title.bind(size=title.setter('text_size'))
        section.add_widget(title)
        
        # Dark mode setting
        dark_mode_row = BoxLayout(orientation='horizontal', size_hint=(1, 0.7))
        
        dark_mode_label = Label(
            text="Dark Mode",
            size_hint=(0.7, 1),
            halign='left',
            valign='middle',
            color=(0.5, 0.5, 0.5, 1)
        )
        dark_mode_label.bind(size=dark_mode_label.setter('text_size'))
        
        self.dark_mode_switch = Switch(
            size_hint=(0.3, 1),
            active=False
        )
        
        dark_mode_row.add_widget(dark_mode_label)
        dark_mode_row.add_widget(self.dark_mode_switch)
        
        section.add_widget(dark_mode_row)
        return section
    
    def _create_currency_section(self):
        """Create the currency settings section."""
        section = BoxLayout(orientation='vertical', size_hint=(1, 0.2), spacing=5)
        
        # Section title
        title = Label(
            text="Currency",
            size_hint=(1, 0.3),
            halign='left',
            valign='middle',
            font_size='18sp',
            color=(0.3, 0.3, 0.3, 1)
        )
        title.bind(size=title.setter('text_size'))
        section.add_widget(title)
        
        # Currency setting
        currency_row = BoxLayout(orientation='horizontal', size_hint=(1, 0.7))
        
        currency_label = Label(
            text="Currency Symbol",
            size_hint=(0.4, 1),
            halign='left',
            valign='middle',
            color=(0.5, 0.5, 0.5, 1)
        )
        currency_label.bind(size=currency_label.setter('text_size'))
        
        self.currency_input = TextInput(
            text="USD",
            size_hint=(0.6, 0.7),
            pos_hint={'center_y': 0.5},
            multiline=False
        )
        
        currency_row.add_widget(currency_label)
        currency_row.add_widget(self.currency_input)
        
        # Allow negative balance setting
        negative_balance_row = BoxLayout(orientation='horizontal', size_hint=(1, 0.7))
        
        negative_balance_label = Label(
            text="Allow Negative Balance",
            size_hint=(0.7, 1),
            halign='left',
            valign='middle',
            color=(0.5, 0.5, 0.5, 1)
        )
        negative_balance_label.bind(size=negative_balance_label.setter('text_size'))
        
        self.negative_balance_switch = Switch(
            size_hint=(0.3, 1),
            active=False
        )
        
        negative_balance_row.add_widget(negative_balance_label)
        negative_balance_row.add_widget(self.negative_balance_switch)
        
        section.add_widget(currency_row)
        section.add_widget(negative_balance_row)
        return section
    
    def _create_notification_section(self):
        """Create the notification settings section."""
        section = BoxLayout(orientation='vertical', size_hint=(1, 0.2), spacing=5)
        
        # Section title
        title = Label(
            text="Notifications",
            size_hint=(1, 0.3),
            halign='left',
            valign='middle',
            font_size='18sp',
            color=(0.3, 0.3, 0.3, 1)
        )
        title.bind(size=title.setter('text_size'))
        section.add_widget(title)
        
        # Enable notifications setting
        notification_row = BoxLayout(orientation='horizontal', size_hint=(1, 0.7))
        
        notification_label = Label(
            text="Enable Notifications",
            size_hint=(0.7, 1),
            halign='left',
            valign='middle',
            color=(0.5, 0.5, 0.5, 1)
        )
        notification_label.bind(size=notification_label.setter('text_size'))
        
        self.notification_switch = Switch(
            size_hint=(0.3, 1),
            active=True
        )
        
        notification_row.add_widget(notification_label)
        notification_row.add_widget(self.notification_switch)
        
        section.add_widget(notification_row)
        return section
    
    def _create_data_section(self):
        """Create the data management section."""
        section = BoxLayout(orientation='vertical', size_hint=(1, 0.2), spacing=5)
        
        # Section title
        title = Label(
            text="Data Management",
            size_hint=(1, 0.3),
            halign='left',
            valign='middle',
            font_size='18sp',
            color=(0.3, 0.3, 0.3, 1)
        )
        title.bind(size=title.setter('text_size'))
        section.add_widget(title)
        
        # Data buttons
        buttons_row = BoxLayout(orientation='horizontal', size_hint=(1, 0.7), spacing=10)
        
        export_button = Button(
            text="Export All Data",
            size_hint=(0.5, 0.8),
            pos_hint={'center_y': 0.5},
            background_normal='',
            background_color=(0, 0.7, 0.4, 1),
            color=(1, 1, 1, 1)
        )
        export_button.bind(on_press=self._on_export_data)
        
        import_button = Button(
            text="Import Data",
            size_hint=(0.5, 0.8),
            pos_hint={'center_y': 0.5},
            background_normal='',
            background_color=(0.9, 0.3, 0.3, 1),
            color=(1, 1, 1, 1)
        )
        import_button.bind(on_press=self._on_import_data)
        
        buttons_row.add_widget(export_button)
        buttons_row.add_widget(import_button)
        
        section.add_widget(buttons_row)
        return section
    
    def _on_save_settings(self, instance):
        """Handle save settings button press."""
        if not self.api_client:
            return
        
        # In a real implementation, we would save settings to the API
        # For now, we'll just print the settings
        settings = {
            'currency': self.currency_input.text,
            'dark_mode': self.dark_mode_switch.active,
            'notifications': self.notification_switch.active,
            'allow_negative_balance': self.negative_balance_switch.active
        }
        
        print(f"Saving settings: {settings}")
        
        # Apply theme if changed
        if hasattr(self.manager.parent.parent, 'colors'):
            self.manager.parent.parent.colors = self.manager.parent.parent.get_color_scheme(
                dark_mode=self.dark_mode_switch.active
            )
    
    def _on_export_data(self, instance):
        """Handle export data button press."""
        # In a real implementation, this would export all data
        # For now, we'll just print a message
        print("Exporting all data")
    
    def _on_import_data(self, instance):
        """Handle import data button press."""
        # In a real implementation, this would import data
        # For now, we'll just print a message
        print("Importing data")
