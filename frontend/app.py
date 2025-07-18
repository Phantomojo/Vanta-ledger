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
from frontend.screens.failed_documents import FailedDocumentsScreen
from frontend.screens.command_center import CommandCenterScreen
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
        sm = ScreenManager()
        self.screen_manager = sm
        
        # Add screens
        sm.add_widget(CommandCenterScreen(name='command_center'))
        # Optionally, keep other screens for navigation/testing:
        # sm.add_widget(DashboardScreen(name='dashboard'))
        # sm.add_widget(FailedDocumentsScreen(name='failed_documents'))
        
        # Create main layout
        main_layout = BoxLayout(orientation='vertical')
        
        # Add screen manager to layout
        main_layout.add_widget(sm)
        
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
        # Initialize with command center screen
        self.screen_manager.current = 'command_center'
        self.navigation_bar.set_active_tab('command_center')

if __name__ == '__main__':
    VantaLedgerApp().run()
