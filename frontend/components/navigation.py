"""
Navigation bar component for Vanta Ledger Enhanced.

This component provides a bottom navigation bar with tabs for the main app sections.
"""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.properties import StringProperty, ObjectProperty

class NavigationBar(BoxLayout):
    """
    Bottom navigation bar with tabs for main app sections.
    
    Features:
    - Instagram-style bottom tab navigation
    - Visual indicators for active tab
    - Customizable tab icons and colors
    """
    
    on_tab_press = ObjectProperty(None)
    active_tab = StringProperty('dashboard')
    
    def __init__(self, **kwargs):
        """Initialize the navigation bar."""
        super(NavigationBar, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint = (1, None)
        self.height = 60
        
        # Create tabs
        self.tabs = {
            'dashboard': self._create_tab('Dashboard', 'dashboard'),
            'transactions': self._create_tab('Transactions', 'transactions'),
            'analytics': self._create_tab('Analytics', 'analytics'),
            'settings': self._create_tab('Settings', 'settings'),
            'profile': self._create_tab('Profile', 'profile')
        }
        
        # Add tabs to layout
        for tab_name, tab_widget in self.tabs.items():
            self.add_widget(tab_widget)
        
        # Set initial active tab
        self.set_active_tab(self.active_tab)
    
    def _create_tab(self, text, tab_name):
        """Create a navigation tab button."""
        tab = Button(
            text=text,
            size_hint=(1, 1),
            background_normal='',
            background_color=(0.9, 0.9, 0.9, 1),
            color=(0.5, 0.5, 0.5, 1)
        )
        
        tab.bind(on_press=lambda instance: self._on_tab_pressed(tab_name))
        return tab
    
    def _on_tab_pressed(self, tab_name):
        """Handle tab press event."""
        self.set_active_tab(tab_name)
        if self.on_tab_press:
            self.on_tab_press(tab_name)
    
    def set_active_tab(self, tab_name):
        """Set the active tab with visual indication."""
        if tab_name not in self.tabs:
            return
        
        self.active_tab = tab_name
        
        # Update tab appearances
        for name, tab in self.tabs.items():
            if name == tab_name:
                tab.background_color = (0.95, 0.95, 0.95, 1)
                tab.color = (0, 0.7, 1, 1)  # Active tab color
            else:
                tab.background_color = (0.9, 0.9, 0.9, 1)
                tab.color = (0.5, 0.5, 0.5, 1)  # Inactive tab color
