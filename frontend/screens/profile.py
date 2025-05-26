"""
Profile screen for Vanta Ledger Enhanced.

This module provides the user profile screen for the application.
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.properties import ObjectProperty

class ProfileScreen(Screen):
    """
    User profile screen for managing account settings and preferences.
    
    Features:
    - User information display and editing
    - Role information (bookkeeper/owner)
    - Account settings
    - Logout functionality
    """
    
    api_client = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        """Initialize the profile screen."""
        super(ProfileScreen, self).__init__(**kwargs)
        
        # Main layout
        self.layout = BoxLayout(orientation='vertical', spacing=15, padding=20)
        
        # Add profile sections
        self.header_section = self._create_header_section()
        self.layout.add_widget(self.header_section)
        
        self.info_section = self._create_info_section()
        self.layout.add_widget(self.info_section)
        
        self.role_section = self._create_role_section()
        self.layout.add_widget(self.role_section)
        
        self.actions_section = self._create_actions_section()
        self.layout.add_widget(self.actions_section)
        
        self.add_widget(self.layout)
    
    def on_enter(self):
        """Called when the screen is entered."""
        # Get API client from app
        if not self.api_client and hasattr(self.manager.parent.parent, 'api_client'):
            self.api_client = self.manager.parent.parent.api_client
        
        # Load user data
        self.load_user_data()
    
    def load_user_data(self):
        """Load user profile data."""
        if not self.api_client:
            return
        
        # In a real implementation, we would get user data from the API
        # For now, we'll use placeholder data
        self.username_input.text = "johndoe"
        self.name_input.text = "John Doe"
        self.email_input.text = "john.doe@example.com"
        self.role_label.text = "Bookkeeper"
    
    def _create_header_section(self):
        """Create the profile header section."""
        section = BoxLayout(orientation='vertical', size_hint=(1, 0.3))
        
        # Profile title
        title = Label(
            text="My Profile",
            size_hint=(1, 0.3),
            halign='left',
            valign='middle',
            font_size='22sp',
            color=(0.3, 0.3, 0.3, 1)
        )
        title.bind(size=title.setter('text_size'))
        
        # Profile image and name
        profile_row = BoxLayout(orientation='horizontal', size_hint=(1, 0.7))
        
        # Profile image placeholder
        profile_image = Image(
            source='',  # Would be a real image path in production
            size_hint=(0.3, 1)
        )
        
        # Use a colored box as placeholder
        with profile_image.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0, 0.6, 0.9, 1)  # Blue color
            Rectangle(pos=profile_image.pos, size=profile_image.size)
        
        profile_image.bind(pos=lambda *args: setattr(profile_image.canvas.before.children[-1], 'pos', profile_image.pos),
                          size=lambda *args: setattr(profile_image.canvas.before.children[-1], 'size', profile_image.size))
        
        # Profile info
        profile_info = BoxLayout(orientation='vertical', size_hint=(0.7, 1), padding=(10, 0, 0, 0))
        
        self.name_display = Label(
            text="John Doe",
            size_hint=(1, 0.5),
            halign='left',
            valign='bottom',
            font_size='20sp',
            color=(0.3, 0.3, 0.3, 1)
        )
        self.name_display.bind(size=self.name_display.setter('text_size'))
        
        self.role_display = Label(
            text="Bookkeeper",
            size_hint=(1, 0.5),
            halign='left',
            valign='top',
            font_size='16sp',
            color=(0.5, 0.5, 0.5, 1)
        )
        self.role_display.bind(size=self.role_display.setter('text_size'))
        
        profile_info.add_widget(self.name_display)
        profile_info.add_widget(self.role_display)
        
        profile_row.add_widget(profile_image)
        profile_row.add_widget(profile_info)
        
        section.add_widget(title)
        section.add_widget(profile_row)
        
        return section
    
    def _create_info_section(self):
        """Create the user information section."""
        section = BoxLayout(orientation='vertical', size_hint=(1, 0.4), spacing=10)
        
        # Section title
        title = Label(
            text="Account Information",
            size_hint=(1, 0.2),
            halign='left',
            valign='middle',
            font_size='18sp',
            color=(0.3, 0.3, 0.3, 1)
        )
        title.bind(size=title.setter('text_size'))
        section.add_widget(title)
        
        # Username field
        username_row = BoxLayout(orientation='horizontal', size_hint=(1, 0.2))
        
        username_label = Label(
            text="Username",
            size_hint=(0.3, 1),
            halign='left',
            valign='middle',
            color=(0.5, 0.5, 0.5, 1)
        )
        username_label.bind(size=username_label.setter('text_size'))
        
        self.username_input = TextInput(
            text="johndoe",
            size_hint=(0.7, 0.8),
            pos_hint={'center_y': 0.5},
            multiline=False,
            readonly=True  # Username typically can't be changed
        )
        
        username_row.add_widget(username_label)
        username_row.add_widget(self.username_input)
        
        # Name field
        name_row = BoxLayout(orientation='horizontal', size_hint=(1, 0.2))
        
        name_label = Label(
            text="Full Name",
            size_hint=(0.3, 1),
            halign='left',
            valign='middle',
            color=(0.5, 0.5, 0.5, 1)
        )
        name_label.bind(size=name_label.setter('text_size'))
        
        self.name_input = TextInput(
            text="John Doe",
            size_hint=(0.7, 0.8),
            pos_hint={'center_y': 0.5},
            multiline=False
        )
        
        name_row.add_widget(name_label)
        name_row.add_widget(self.name_input)
        
        # Email field
        email_row = BoxLayout(orientation='horizontal', size_hint=(1, 0.2))
        
        email_label = Label(
            text="Email",
            size_hint=(0.3, 1),
            halign='left',
            valign='middle',
            color=(0.5, 0.5, 0.5, 1)
        )
        email_label.bind(size=email_label.setter('text_size'))
        
        self.email_input = TextInput(
            text="john.doe@example.com",
            size_hint=(0.7, 0.8),
            pos_hint={'center_y': 0.5},
            multiline=False
        )
        
        email_row.add_widget(email_label)
        email_row.add_widget(self.email_input)
        
        # Password change button
        password_row = BoxLayout(orientation='horizontal', size_hint=(1, 0.2))
        
        password_label = Label(
            text="Password",
            size_hint=(0.3, 1),
            halign='left',
            valign='middle',
            color=(0.5, 0.5, 0.5, 1)
        )
        password_label.bind(size=password_label.setter('text_size'))
        
        change_password_button = Button(
            text="Change Password",
            size_hint=(0.7, 0.8),
            pos_hint={'center_y': 0.5},
            background_normal='',
            background_color=(0.9, 0.9, 0.9, 1),
            color=(0.3, 0.3, 0.3, 1)
        )
        change_password_button.bind(on_press=self._on_change_password)
        
        password_row.add_widget(password_label)
        password_row.add_widget(change_password_button)
        
        section.add_widget(username_row)
        section.add_widget(name_row)
        section.add_widget(email_row)
        section.add_widget(password_row)
        
        return section
    
    def _create_role_section(self):
        """Create the role information section."""
        section = BoxLayout(orientation='vertical', size_hint=(1, 0.15), spacing=5)
        
        # Section title
        title = Label(
            text="Role Information",
            size_hint=(1, 0.4),
            halign='left',
            valign='middle',
            font_size='18sp',
            color=(0.3, 0.3, 0.3, 1)
        )
        title.bind(size=title.setter('text_size'))
        section.add_widget(title)
        
        # Role row
        role_row = BoxLayout(orientation='horizontal', size_hint=(1, 0.6))
        
        role_title = Label(
            text="Current Role",
            size_hint=(0.3, 1),
            halign='left',
            valign='middle',
            color=(0.5, 0.5, 0.5, 1)
        )
        role_title.bind(size=role_title.setter('text_size'))
        
        self.role_label = Label(
            text="Bookkeeper",
            size_hint=(0.7, 1),
            halign='left',
            valign='middle',
            color=(0, 0.6, 0.9, 1),
            font_size='16sp'
        )
        self.role_label.bind(size=self.role_label.setter('text_size'))
        
        role_row.add_widget(role_title)
        role_row.add_widget(self.role_label)
        
        section.add_widget(role_row)
        
        return section
    
    def _create_actions_section(self):
        """Create the actions section."""
        section = BoxLayout(orientation='vertical', size_hint=(1, 0.15), spacing=10)
        
        # Save button
        save_button = Button(
            text="Save Changes",
            size_hint=(1, 0.5),
            background_normal='',
            background_color=(0, 0.7, 0.4, 1),
            color=(1, 1, 1, 1)
        )
        save_button.bind(on_press=self._on_save_profile)
        
        # Logout button
        logout_button = Button(
            text="Logout",
            size_hint=(1, 0.5),
            background_normal='',
            background_color=(0.9, 0.3, 0.3, 1),
            color=(1, 1, 1, 1)
        )
        logout_button.bind(on_press=self._on_logout)
        
        section.add_widget(save_button)
        section.add_widget(logout_button)
        
        return section
    
    def _on_save_profile(self, instance):
        """Handle save profile button press."""
        if not self.api_client:
            return
        
        # Update display name
        self.name_display.text = self.name_input.text
        
        # In a real implementation, we would save profile data to the API
        # For now, we'll just print the data
        profile_data = {
            'username': self.username_input.text,
            'name': self.name_input.text,
            'email': self.email_input.text
        }
        
        print(f"Saving profile: {profile_data}")
    
    def _on_change_password(self, instance):
        """Handle change password button press."""
        # In a real implementation, this would open a password change dialog
        # For now, we'll just print a message
        print("Change password pressed")
    
    def _on_logout(self, instance):
        """Handle logout button press."""
        if not self.api_client:
            return
        
        # In a real implementation, this would log the user out
        # For now, we'll just print a message
        print("Logout pressed")
