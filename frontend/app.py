from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty

# Import components
from frontend.components.navigation import NavigationBar
from frontend.components.transaction_card import TransactionCard
from frontend.screens.dashboard import DashboardScreen
from frontend.screens.transactions import TransactionsScreen
from frontend.screens.analytics import AnalyticsScreen
from frontend.screens.settings import SettingsScreen
from frontend.screens.profile import ProfileScreen
from frontend.utils.api_client import ApiClient
from frontend.theme.colors import get_color_scheme

class VantaLedgerApp(App):
    """
    Main application class for Vanta Ledger Enhanced.
    
    This class serves as the entry point for the application and manages
    the screen navigation, theme, and global state.
    """
    
    def build(self):
        """Build and return the root widget for the application."""
        # Initialize API client
        self.api_client = ApiClient()
        
        # Set theme colors
        self.colors = get_color_scheme()
        
        # Create screen manager
        self.screen_manager = ScreenManager()
        
        # Add screens
        self.screen_manager.add_widget(DashboardScreen(name='dashboard'))
        self.screen_manager.add_widget(TransactionsScreen(name='transactions'))
        self.screen_manager.add_widget(AnalyticsScreen(name='analytics'))
        self.screen_manager.add_widget(SettingsScreen(name='settings'))
        self.screen_manager.add_widget(ProfileScreen(name='profile'))
        
        # Create main layout
        main_layout = BoxLayout(orientation='vertical')
        
        # Add screen manager to layout
        main_layout.add_widget(self.screen_manager)
        
        # Add navigation bar to layout
        self.navigation_bar = NavigationBar(
            on_tab_press=self.change_screen
        )
        main_layout.add_widget(self.navigation_bar)
        
        return main_layout
    
    def change_screen(self, screen_name):
        """Change to the specified screen."""
        self.screen_manager.current = screen_name
        self.navigation_bar.set_active_tab(screen_name)
    
    def on_start(self):
        """Called when the application starts."""
        # Initialize with dashboard screen
        self.screen_manager.current = 'dashboard'
        self.navigation_bar.set_active_tab('dashboard')

if __name__ == '__main__':
    VantaLedgerApp().run()
