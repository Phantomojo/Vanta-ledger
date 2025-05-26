"""
Login screen for Vanta Ledger Enhanced.

This module provides the login screen with authentication functionality.
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.properties import ObjectProperty

from frontend.components.forms import TextInputField, FormActions
from frontend.components.dialogs import show_alert, show_toast
from frontend.utils.auth import AuthManager
from frontend.models.user import UserManager

class LoginScreen(Screen):
    """
    Login screen for user authentication.
    
    Features:
    - Username and password input
    - Authentication
    - Error handling
    - Remember me functionality
    """
    
    on_login_success = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        """Initialize the login screen."""
        super(LoginScreen, self).__init__(**kwargs)
        
        # Main layout
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Logo and title section
        self.header_section = self._create_header_section()
        self.layout.add_widget(self.header_section)
        
        # Login form section
        self.form_section = self._create_form_section()
        self.layout.add_widget(self.form_section)
        
        # Add layout to screen
        self.add_widget(self.layout)
        
        # Initialize managers
        self.auth_manager = AuthManager()
        self.user_manager = UserManager()
    
    def _create_header_section(self):
        """Create the logo and title section."""
        section = BoxLayout(orientation='vertical', size_hint=(1, 0.4), spacing=10)
        
        # Logo placeholder
        logo = Image(
            source='',  # Would be a real image path in production
            size_hint=(1, 0.7)
        )
        
        # Use a colored box as placeholder
        with logo.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0, 0.6, 0.9, 1)  # Blue color
            Rectangle(pos=logo.pos, size=logo.size)
        
        logo.bind(pos=lambda *args: setattr(logo.canvas.before.children[-1], 'pos', logo.pos),
                 size=lambda *args: setattr(logo.canvas.before.children[-1], 'size', logo.size))
        
        # Title
        title = Label(
            text="Vanta Ledger",
            size_hint=(1, 0.15),
            halign='center',
            valign='middle',
            font_size='28sp',
            color=(0.2, 0.2, 0.2, 1),
            bold=True
        )
        
        # Subtitle
        subtitle = Label(
            text="Financial Management for Company Owners",
            size_hint=(1, 0.15),
            halign='center',
            valign='middle',
            font_size='16sp',
            color=(0.5, 0.5, 0.5, 1)
        )
        
        section.add_widget(logo)
        section.add_widget(title)
        section.add_widget(subtitle)
        
        return section
    
    def _create_form_section(self):
        """Create the login form section."""
        section = BoxLayout(orientation='vertical', size_hint=(1, 0.6), spacing=15)
        
        # Form title
        form_title = Label(
            text="Login to Your Account",
            size_hint=(1, 0.15),
            halign='center',
            valign='middle',
            font_size='20sp',
            color=(0.3, 0.3, 0.3, 1)
        )
        
        # Username field
        self.username_field = TextInputField(
            label_text="Username",
            hint_text="Enter your username",
            required=True
        )
        
        # Password field
        self.password_container = BoxLayout(orientation='vertical', size_hint=(1, None), height=70)
        
        password_label_row = BoxLayout(orientation='horizontal', size_hint=(1, 0.3))
        
        password_label = Label(
            text="Password",
            size_hint=(0.9, 1),
            halign='left',
            valign='bottom',
            color=(0.5, 0.5, 0.5, 1)
        )
        password_label.bind(size=password_label.setter('text_size'))
        
        required_indicator = Label(
            text="*",
            size_hint=(0.1, 1),
            halign='right',
            valign='bottom',
            color=(0.9, 0.3, 0.3, 1)
        )
        required_indicator.bind(size=required_indicator.setter('text_size'))
        
        password_label_row.add_widget(password_label)
        password_label_row.add_widget(required_indicator)
        
        self.password_input = TextInput(
            hint_text="Enter your password",
            password=True,
            multiline=False,
            size_hint=(1, 0.4)
        )
        
        # Apply styling
        with self.password_input.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(0.95, 0.95, 0.95, 1)
            RoundedRectangle(pos=self.password_input.pos, size=self.password_input.size, radius=[5])
        
        self.password_input.bind(pos=lambda *args: setattr(self.password_input.canvas.before.children[-1], 'pos', self.password_input.pos),
                                size=lambda *args: setattr(self.password_input.canvas.before.children[-1], 'size', self.password_input.size))
        
        self.password_error = Label(
            text="",
            size_hint=(1, 0.3),
            halign='left',
            valign='top',
            color=(0.9, 0.3, 0.3, 1),
            font_size='12sp'
        )
        self.password_error.bind(size=self.password_error.setter('text_size'))
        
        self.password_container.add_widget(password_label_row)
        self.password_container.add_widget(self.password_input)
        self.password_container.add_widget(self.password_error)
        
        # Remember me checkbox
        remember_row = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        
        from kivy.uix.checkbox import CheckBox
        self.remember_checkbox = CheckBox(
            active=False,
            size_hint=(0.1, 1),
            color=(0, 0.6, 0.9, 1)
        )
        
        remember_label = Label(
            text="Remember me",
            size_hint=(0.9, 1),
            halign='left',
            valign='middle',
            color=(0.5, 0.5, 0.5, 1)
        )
        remember_label.bind(size=remember_label.setter('text_size'))
        
        remember_row.add_widget(self.remember_checkbox)
        remember_row.add_widget(remember_label)
        
        # Login button
        self.login_button = Button(
            text="Login",
            size_hint=(1, 0.15),
            background_normal='',
            background_color=(0, 0.6, 0.9, 1),
            color=(1, 1, 1, 1)
        )
        self.login_button.bind(on_press=self._on_login)
        
        # Add all components to section
        section.add_widget(form_title)
        section.add_widget(self.username_field)
        section.add_widget(self.password_container)
        section.add_widget(remember_row)
        section.add_widget(self.login_button)
        
        return section
    
    def _on_login(self, instance):
        """Handle login button press."""
        # Validate username
        username_valid, username = self.username_field.validate()
        
        # Validate password
        password = self.password_input.text
        if not password:
            self.password_error.text = "Password is required"
            return
        else:
            self.password_error.text = ""
        
        if not username_valid:
            return
        
        # Authenticate user
        session_id = self.auth_manager.authenticate(
            username=username,
            password=password,
            user_manager=self.user_manager
        )
        
        if session_id:
            # Login successful
            show_toast(self, "Login successful", type="success")
            
            # Call success callback
            if self.on_login_success:
                self.on_login_success(self.auth_manager.current_user)
        else:
            # Login failed
            show_alert("Login Failed", "Invalid username or password")


class LogoutScreen(Screen):
    """
    Logout confirmation screen.
    
    Features:
    - Logout confirmation
    - Session termination
    """
    
    on_logout_success = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        """Initialize the logout screen."""
        super(LogoutScreen, self).__init__(**kwargs)
        
        # Main layout
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Confirmation message
        message = Label(
            text="Are you sure you want to log out?",
            size_hint=(1, 0.7),
            halign='center',
            valign='middle',
            font_size='20sp',
            color=(0.3, 0.3, 0.3, 1)
        )
        
        # Buttons
        buttons = BoxLayout(orientation='horizontal', size_hint=(1, 0.3), spacing=10)
        
        cancel_button = Button(
            text="Cancel",
            size_hint=(0.5, 0.5),
            pos_hint={'center_y': 0.5},
            background_normal='',
            background_color=(0.9, 0.9, 0.9, 1),
            color=(0.3, 0.3, 0.3, 1)
        )
        cancel_button.bind(on_press=self._on_cancel)
        
        logout_button = Button(
            text="Logout",
            size_hint=(0.5, 0.5),
            pos_hint={'center_y': 0.5},
            background_normal='',
            background_color=(0.9, 0.3, 0.3, 1),
            color=(1, 1, 1, 1)
        )
        logout_button.bind(on_press=self._on_logout)
        
        buttons.add_widget(cancel_button)
        buttons.add_widget(logout_button)
        
        # Add components to layout
        self.layout.add_widget(message)
        self.layout.add_widget(buttons)
        
        # Add layout to screen
        self.add_widget(self.layout)
        
        # Initialize auth manager
        self.auth_manager = AuthManager()
    
    def _on_cancel(self, instance):
        """Handle cancel button press."""
        # Go back to previous screen
        if self.manager:
            self.manager.current = self.manager.previous()
    
    def _on_logout(self, instance):
        """Handle logout button press."""
        # Logout user
        if self.auth_manager.current_session:
            self.auth_manager.logout()
            
            # Show success message
            show_toast(self, "Logged out successfully", type="success")
            
            # Call success callback
            if self.on_logout_success:
                self.on_logout_success()
        else:
            # Already logged out
            show_alert("Error", "No active session found")
            
            # Call success callback anyway
            if self.on_logout_success:
                self.on_logout_success()
