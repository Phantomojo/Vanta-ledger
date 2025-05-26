"""
Owner management screen for Vanta Ledger Enhanced.

This module provides the owner management screen for the bookkeeper role.
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.properties import ObjectProperty

from frontend.components.forms import (
    TextInputField, AmountInputField, FormActions
)
from frontend.components.dialogs import (
    show_alert, show_confirm, show_toast
)
from frontend.models.owner import Owner

class OwnerCard(BoxLayout):
    """
    Card component for displaying owner information.
    
    Features:
    - Owner details display
    - Edit and delete actions
    - Ownership percentage indicator
    """
    
    owner_id = ObjectProperty(None)
    name = ObjectProperty(None)
    email = ObjectProperty(None)
    ownership_percentage = ObjectProperty(None)
    on_edit = ObjectProperty(None)
    on_delete = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        """Initialize the owner card."""
        super(OwnerCard, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = 150
        self.padding = 10
        self.spacing = 5
        
        # Apply card styling
        with self.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(0.95, 0.95, 0.95, 1)  # Light gray background
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[10])
        
        # Bind position and size updates
        self.bind(pos=self._update_rect, size=self._update_rect)
        
        # Header row with name and actions
        header_row = BoxLayout(orientation='horizontal', size_hint=(1, 0.3))
        
        self.name_label = Label(
            text=self.name or "Unknown Owner",
            size_hint=(0.7, 1),
            halign='left',
            valign='middle',
            color=(0.2, 0.2, 0.2, 1),
            font_size='18sp',
            bold=True
        )
        self.name_label.bind(size=self.name_label.setter('text_size'))
        
        actions_layout = BoxLayout(orientation='horizontal', size_hint=(0.3, 1), spacing=5)
        
        edit_button = Button(
            text="Edit",
            size_hint=(0.5, 0.8),
            pos_hint={'center_y': 0.5},
            background_normal='',
            background_color=(0, 0.6, 0.9, 1),
            color=(1, 1, 1, 1)
        )
        edit_button.bind(on_press=self._on_edit_pressed)
        
        delete_button = Button(
            text="Delete",
            size_hint=(0.5, 0.8),
            pos_hint={'center_y': 0.5},
            background_normal='',
            background_color=(0.9, 0.3, 0.3, 1),
            color=(1, 1, 1, 1)
        )
        delete_button.bind(on_press=self._on_delete_pressed)
        
        actions_layout.add_widget(edit_button)
        actions_layout.add_widget(delete_button)
        
        header_row.add_widget(self.name_label)
        header_row.add_widget(actions_layout)
        
        # Details rows
        email_row = BoxLayout(orientation='horizontal', size_hint=(1, 0.2))
        
        email_label = Label(
            text="Email:",
            size_hint=(0.3, 1),
            halign='left',
            valign='middle',
            color=(0.5, 0.5, 0.5, 1)
        )
        email_label.bind(size=email_label.setter('text_size'))
        
        self.email_value = Label(
            text=self.email or "N/A",
            size_hint=(0.7, 1),
            halign='left',
            valign='middle',
            color=(0.3, 0.3, 0.3, 1)
        )
        self.email_value.bind(size=self.email_value.setter('text_size'))
        
        email_row.add_widget(email_label)
        email_row.add_widget(self.email_value)
        
        # Ownership percentage row
        ownership_row = BoxLayout(orientation='horizontal', size_hint=(1, 0.2))
        
        ownership_label = Label(
            text="Ownership:",
            size_hint=(0.3, 1),
            halign='left',
            valign='middle',
            color=(0.5, 0.5, 0.5, 1)
        )
        ownership_label.bind(size=ownership_label.setter('text_size'))
        
        self.ownership_value = Label(
            text=f"{self.ownership_percentage:.1f}%" if self.ownership_percentage is not None else "0.0%",
            size_hint=(0.7, 1),
            halign='left',
            valign='middle',
            color=(0, 0.6, 0.9, 1),
            font_size='16sp',
            bold=True
        )
        self.ownership_value.bind(size=self.ownership_value.setter('text_size'))
        
        ownership_row.add_widget(ownership_label)
        ownership_row.add_widget(self.ownership_value)
        
        # Ownership percentage bar
        percentage_bar = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        
        with percentage_bar.canvas:
            from kivy.graphics import Color, Rectangle
            Color(0.9, 0.9, 0.9, 1)  # Background color
            self.bar_bg = Rectangle(pos=percentage_bar.pos, size=percentage_bar.size)
            
            # Filled portion
            percentage = self.ownership_percentage or 0
            width = percentage_bar.width * (percentage / 100)
            Color(0, 0.6, 0.9, 1)  # Fill color
            self.bar_fill = Rectangle(pos=percentage_bar.pos, size=(width, percentage_bar.height))
        
        percentage_bar.bind(pos=self._update_bar, size=self._update_bar)
        
        # Add all rows to layout
        self.add_widget(header_row)
        self.add_widget(email_row)
        self.add_widget(ownership_row)
        self.add_widget(percentage_bar)
        
        # Bind properties
        self.bind(name=self._update_name)
        self.bind(email=self._update_email)
        self.bind(ownership_percentage=self._update_ownership)
    
    def _update_rect(self, instance, value):
        """Update the background rectangle position and size."""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def _update_bar(self, instance, value):
        """Update the percentage bar position and size."""
        instance.canvas.before.clear()
        with instance.canvas:
            from kivy.graphics import Color, Rectangle
            Color(0.9, 0.9, 0.9, 1)  # Background color
            self.bar_bg = Rectangle(pos=instance.pos, size=instance.size)
            
            # Filled portion
            percentage = self.ownership_percentage or 0
            width = instance.width * (percentage / 100)
            Color(0, 0.6, 0.9, 1)  # Fill color
            self.bar_fill = Rectangle(pos=instance.pos, size=(width, instance.height))
    
    def _update_name(self, instance, value):
        """Update the name label."""
        self.name_label.text = value or "Unknown Owner"
    
    def _update_email(self, instance, value):
        """Update the email value."""
        self.email_value.text = value or "N/A"
    
    def _update_ownership(self, instance, value):
        """Update the ownership percentage value and bar."""
        self.ownership_value.text = f"{value:.1f}%" if value is not None else "0.0%"
        
        # Update bar fill width
        if hasattr(self, 'bar_fill') and hasattr(self, 'bar_bg'):
            percentage = value or 0
            parent = self.bar_fill.parent
            if parent:
                self.bar_fill.size = (parent.width * (percentage / 100), self.bar_fill.height)
    
    def _on_edit_pressed(self, instance):
        """Handle edit button press."""
        if self.on_edit:
            self.on_edit(self.owner_id)
    
    def _on_delete_pressed(self, instance):
        """Handle delete button press."""
        if self.on_delete:
            self.on_delete(self.owner_id)


class OwnerForm(BoxLayout):
    """Form for adding or editing an owner."""
    
    owner = ObjectProperty(None)
    on_save = ObjectProperty(None)
    on_cancel = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        """Initialize the owner form."""
        super(OwnerForm, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 10
        self.padding = 15
        
        # Name field
        self.name_field = TextInputField(
            label_text="Full Name",
            hint_text="Enter owner's full name",
            required=True
        )
        
        # Email field
        self.email_field = TextInputField(
            label_text="Email",
            hint_text="Enter owner's email address",
            required=True,
            validator=lambda email: (
                True, email
            ) if '@' in email else (
                False, "Please enter a valid email address"
            )
        )
        
        # Phone field
        self.phone_field = TextInputField(
            label_text="Phone",
            hint_text="Enter owner's phone number"
        )
        
        # Ownership percentage field
        self.ownership_field = AmountInputField(
            label_text="Ownership Percentage",
            hint_text="Enter ownership percentage (0-100)",
            required=True,
            validator=lambda value: (
                True, float(value)
            ) if 0 <= float(value) <= 100 else (
                False, "Percentage must be between 0 and 100"
            )
        )
        
        # Form actions
        self.form_actions = FormActions(
            submit_text="Save Owner",
            cancel_text="Cancel",
            on_submit=self._on_submit,
            on_cancel=self._on_cancel
        )
        
        # Add fields to layout
        self.add_widget(self.name_field)
        self.add_widget(self.email_field)
        self.add_widget(self.phone_field)
        self.add_widget(self.ownership_field)
        self.add_widget(self.form_actions)
        
        # Load owner data if provided
        if self.owner:
            self._load_owner_data()
        
        # Bind owner property
        self.bind(owner=self._load_owner_data)
    
    def _load_owner_data(self, *args):
        """Load owner data into form fields."""
        if not self.owner:
            return
        
        self.name_field.set_value(self.owner.name)
        self.email_field.set_value(self.owner.email)
        self.phone_field.set_value(self.owner.phone)
        self.ownership_field.set_value(str(self.owner.ownership_percentage))
    
    def _on_submit(self):
        """Handle form submission."""
        # Validate all fields
        name_valid, name = self.name_field.validate()
        email_valid, email = self.email_field.validate()
        phone_valid, phone = self.phone_field.validate()
        ownership_valid, ownership = self.ownership_field.validate()
        
        if not all([name_valid, email_valid, phone_valid, ownership_valid]):
            return
        
        # Create or update owner
        if self.owner:
            # Update existing owner
            owner = self.owner
            owner.name = name
            owner.email = email
            owner.phone = phone
            owner.ownership_percentage = ownership
        else:
            # Create new owner
            owner = Owner(
                name=name,
                email=email,
                phone=phone,
                ownership_percentage=ownership
            )
        
        # Call save callback
        if self.on_save:
            self.on_save(owner)
    
    def _on_cancel(self):
        """Handle form cancellation."""
        if self.on_cancel:
            self.on_cancel()


class OwnersScreen(Screen):
    """
    Owner management screen for the bookkeeper role.
    
    Features:
    - List of company owners
    - Add, edit, and delete owners
    - Ownership percentage visualization
    - Validation of total ownership (100%)
    """
    
    api_client = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        """Initialize the owners screen."""
        super(OwnersScreen, self).__init__(**kwargs)
        
        # Main layout
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=15)
        
        # Add header section
        self.header_section = self._create_header_section()
        self.layout.add_widget(self.header_section)
        
        # Add owners list section
        self.owners_section = self._create_owners_section()
        self.layout.add_widget(self.owners_section)
        
        # Add form container (initially hidden)
        self.form_container = BoxLayout(orientation='vertical', size_hint=(1, 0))
        self.layout.add_widget(self.form_container)
        
        self.add_widget(self.layout)
        
        # Initialize owner form
        self.owner_form = None
        self.editing_owner_id = None
    
    def on_enter(self):
        """Called when the screen is entered."""
        # Get API client from app
        if not self.api_client and hasattr(self.manager.parent.parent, 'api_client'):
            self.api_client = self.manager.parent.parent.api_client
        
        # Load data
        self.load_data()
    
    def load_data(self):
        """Load owners data."""
        if not self.api_client:
            return
        
        # Get owners
        owners = self.api_client.get_owners()
        self._update_owners_list(owners)
    
    def _create_header_section(self):
        """Create the header section with title and add button."""
        section = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        
        title = Label(
            text="Company Owners",
            size_hint=(0.7, 1),
            halign='left',
            valign='middle',
            font_size='22sp',
            color=(0.3, 0.3, 0.3, 1)
        )
        title.bind(size=title.setter('text_size'))
        
        add_button = Button(
            text="+ Add Owner",
            size_hint=(0.3, 0.8),
            pos_hint={'center_y': 0.5},
            background_normal='',
            background_color=(0, 0.7, 0.4, 1),
            color=(1, 1, 1, 1)
        )
        add_button.bind(on_press=self._on_add_owner)
        
        section.add_widget(title)
        section.add_widget(add_button)
        
        return section
    
    def _create_owners_section(self):
        """Create the owners list section."""
        section = BoxLayout(orientation='vertical', size_hint=(1, 0.9))
        
        # Owners list
        self.owners_layout = BoxLayout(orientation='vertical', spacing=10, size_hint=(1, 1))
        
        # Wrap in scroll view
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.owners_layout)
        
        section.add_widget(scroll)
        return section
    
    def _update_owners_list(self, owners):
        """Update the owners list with data."""
        self.owners_layout.clear_widgets()
        
        if not owners:
            empty_label = Label(
                text="No owners found. Add your first company owner.",
                size_hint=(1, 1),
                halign='center',
                valign='middle',
                color=(0.5, 0.5, 0.5, 1)
            )
            empty_label.bind(size=empty_label.setter('text_size'))
            self.owners_layout.add_widget(empty_label)
            return
        
        # Check total ownership
        total_ownership = sum(owner.get('ownership_percentage', 0) for owner in owners)
        if abs(total_ownership - 100.0) > 0.1:
            warning = Label(
                text=f"Warning: Total ownership is {total_ownership:.1f}%, not 100%",
                size_hint=(1, None),
                height=30,
                halign='center',
                valign='middle',
                color=(0.9, 0.5, 0, 1)
            )
            warning.bind(size=warning.setter('text_size'))
            self.owners_layout.add_widget(warning)
        
        # Add owner cards
        for owner in owners:
            card = OwnerCard(
                owner_id=owner.get('id', ''),
                name=owner.get('name', ''),
                email=owner.get('email', ''),
                ownership_percentage=owner.get('ownership_percentage', 0),
                on_edit=self._on_edit_owner,
                on_delete=self._on_delete_owner
            )
            self.owners_layout.add_widget(card)
    
    def _show_owner_form(self, owner=None):
        """Show the owner form for adding or editing."""
        # Hide any existing form
        self._hide_owner_form()
        
        # Create new form
        self.owner_form = OwnerForm(
            owner=owner,
            on_save=self._on_save_owner,
            on_cancel=self._hide_owner_form
        )
        
        # Show form container
        self.form_container.add_widget(self.owner_form)
        self.form_container.size_hint = (1, 0.8)
        
        # Hide owners list
        self.owners_section.size_hint = (1, 0)
    
    def _hide_owner_form(self, *args):
        """Hide the owner form."""
        if self.owner_form:
            self.form_container.remove_widget(self.owner_form)
            self.owner_form = None
        
        # Reset container size
        self.form_container.size_hint = (1, 0)
        
        # Show owners list
        self.owners_section.size_hint = (1, 0.9)
        
        # Clear editing state
        self.editing_owner_id = None
    
    def _on_add_owner(self, instance):
        """Handle add owner button press."""
        self._show_owner_form()
    
    def _on_edit_owner(self, owner_id):
        """Handle edit owner action."""
        if not self.api_client:
            return
        
        # Get owner details
        owner = self.api_client.get_owner(owner_id)
        if not owner:
            show_alert("Error", "Owner not found")
            return
        
        # Set editing state
        self.editing_owner_id = owner_id
        
        # Show form with owner data
        self._show_owner_form(owner)
    
    def _on_delete_owner(self, owner_id):
        """Handle delete owner action."""
        if not self.api_client:
            return
        
        # Confirm deletion
        show_confirm(
            "Delete Owner",
            "Are you sure you want to delete this owner? This action cannot be undone.",
            confirm_text="Delete",
            cancel_text="Cancel",
            on_confirm=lambda: self._confirm_delete_owner(owner_id)
        )
    
    def _confirm_delete_owner(self, owner_id):
        """Confirm and process owner deletion."""
        if not self.api_client:
            return
        
        # Delete owner
        success = self.api_client.delete_owner(owner_id)
        
        if success:
            show_toast(self, "Owner deleted successfully", type="success")
            self.load_data()
        else:
            show_alert("Error", "Failed to delete owner")
    
    def _on_save_owner(self, owner):
        """Handle owner save action."""
        if not self.api_client:
            return
        
        if self.editing_owner_id:
            # Update existing owner
            success = self.api_client.update_owner(self.editing_owner_id, owner.to_dict())
            message = "Owner updated successfully"
        else:
            # Create new owner
            success = self.api_client.create_owner(owner.to_dict())
            message = "Owner added successfully"
        
        if success:
            show_toast(self, message, type="success")
            self._hide_owner_form()
            self.load_data()
        else:
            show_alert("Error", "Failed to save owner")
