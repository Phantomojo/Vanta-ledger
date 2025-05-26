"""
Form components for Vanta Ledger Enhanced.

This module provides reusable form input components with validation and styling.
"""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty

from frontend.theme.styles import apply_theme_to_widget
from frontend.utils.validators import validate_required, validate_amount, validate_date

class FormField(BoxLayout):
    """
    Base form field component with label and validation.
    
    Features:
    - Consistent styling
    - Built-in validation
    - Error message display
    - Required field indicator
    """
    
    label_text = StringProperty("")
    hint_text = StringProperty("")
    required = BooleanProperty(False)
    error_text = StringProperty("")
    
    def __init__(self, **kwargs):
        """Initialize the form field."""
        super(FormField, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 5
        self.size_hint = (1, None)
        self.height = 70
        
        # Create label row with required indicator
        label_row = BoxLayout(orientation='horizontal', size_hint=(1, 0.3))
        
        self.label = Label(
            text=self.label_text,
            size_hint=(0.9, 1),
            halign='left',
            valign='bottom',
            color=(0.5, 0.5, 0.5, 1)
        )
        self.label.bind(size=self.label.setter('text_size'))
        
        self.required_indicator = Label(
            text="*" if self.required else "",
            size_hint=(0.1, 1),
            halign='right',
            valign='bottom',
            color=(0.9, 0.3, 0.3, 1)
        )
        self.required_indicator.bind(size=self.required_indicator.setter('text_size'))
        
        label_row.add_widget(self.label)
        label_row.add_widget(self.required_indicator)
        
        # Add input (to be implemented by subclasses)
        self.input_container = BoxLayout(orientation='vertical', size_hint=(1, 0.4))
        
        # Error message
        self.error_label = Label(
            text=self.error_text,
            size_hint=(1, 0.3),
            halign='left',
            valign='top',
            color=(0.9, 0.3, 0.3, 1),
            font_size='12sp'
        )
        self.error_label.bind(size=self.error_label.setter('text_size'))
        
        # Add all components
        self.add_widget(label_row)
        self.add_widget(self.input_container)
        self.add_widget(self.error_label)
        
        # Bind properties
        self.bind(label_text=self._update_label)
        self.bind(required=self._update_required)
        self.bind(error_text=self._update_error)
    
    def _update_label(self, instance, value):
        """Update the label text."""
        self.label.text = value
    
    def _update_required(self, instance, value):
        """Update the required indicator."""
        self.required_indicator.text = "*" if value else ""
    
    def _update_error(self, instance, value):
        """Update the error message."""
        self.error_label.text = value
        
        # Adjust height based on error presence
        if value:
            self.height = 90
        else:
            self.height = 70
    
    def get_value(self):
        """Get the current value (to be implemented by subclasses)."""
        return None
    
    def set_value(self, value):
        """Set the value (to be implemented by subclasses)."""
        pass
    
    def validate(self):
        """Validate the field (to be implemented by subclasses)."""
        return True, None


class TextInputField(FormField):
    """Text input form field with validation."""
    
    validator = ObjectProperty(None)
    multiline = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        """Initialize the text input field."""
        super(TextInputField, self).__init__(**kwargs)
        
        # Create text input
        self.text_input = TextInput(
            hint_text=self.hint_text,
            multiline=self.multiline,
            size_hint=(1, 1)
        )
        
        # Apply styling
        apply_theme_to_widget(self.text_input, {}, style='input')
        
        # Add to container
        self.input_container.add_widget(self.text_input)
        
        # Bind hint text
        self.bind(hint_text=self._update_hint)
    
    def _update_hint(self, instance, value):
        """Update the hint text."""
        self.text_input.hint_text = value
    
    def get_value(self):
        """Get the current text value."""
        return self.text_input.text
    
    def set_value(self, value):
        """Set the text value."""
        self.text_input.text = str(value) if value is not None else ""
    
    def validate(self):
        """Validate the field using the provided validator."""
        # Clear previous error
        self.error_text = ""
        
        # Check if required
        if self.required:
            is_valid, result = validate_required(self.text_input.text, self.label_text)
            if not is_valid:
                self.error_text = result
                return False, None
        
        # Apply custom validator if provided
        if self.validator and self.text_input.text:
            is_valid, result = self.validator(self.text_input.text)
            if not is_valid:
                self.error_text = result
                return False, None
            return True, result
        
        return True, self.text_input.text


class AmountInputField(TextInputField):
    """Amount input field with currency validation."""
    
    currency_symbol = StringProperty("$")
    
    def __init__(self, **kwargs):
        """Initialize the amount input field."""
        # Set default validator for amounts
        kwargs['validator'] = validate_amount
        super(AmountInputField, self).__init__(**kwargs)
        
        # Set numeric keyboard
        self.text_input.input_type = 'number'
        self.text_input.input_filter = 'float'


class DateInputField(TextInputField):
    """Date input field with date validation."""
    
    date_format = StringProperty("%Y-%m-%d")
    
    def __init__(self, **kwargs):
        """Initialize the date input field."""
        # Create custom validator using the date format
        def date_validator(value):
            return validate_date(value, self.date_format)
        
        kwargs['validator'] = date_validator
        kwargs['hint_text'] = kwargs.get('hint_text', 'YYYY-MM-DD')
        
        super(DateInputField, self).__init__(**kwargs)


class DropdownField(FormField):
    """Dropdown selection field."""
    
    options = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        """Initialize the dropdown field."""
        super(DropdownField, self).__init__(**kwargs)
        
        # Create spinner
        self.spinner = Spinner(
            text=self.hint_text or "Select...",
            values=self.options or [],
            size_hint=(1, 1)
        )
        
        # Apply styling
        apply_theme_to_widget(self.spinner, {}, style='input')
        
        # Add to container
        self.input_container.add_widget(self.spinner)
        
        # Bind options and hint
        self.bind(options=self._update_options)
        self.bind(hint_text=self._update_hint)
    
    def _update_options(self, instance, value):
        """Update the dropdown options."""
        self.spinner.values = value or []
    
    def _update_hint(self, instance, value):
        """Update the hint text."""
        if not self.spinner.text or self.spinner.text == "Select...":
            self.spinner.text = value or "Select..."
    
    def get_value(self):
        """Get the current selected value."""
        return self.spinner.text if self.spinner.text != "Select..." else None
    
    def set_value(self, value):
        """Set the selected value."""
        if value is not None and str(value) in self.spinner.values:
            self.spinner.text = str(value)
        else:
            self.spinner.text = self.hint_text or "Select..."
    
    def validate(self):
        """Validate the field."""
        # Clear previous error
        self.error_text = ""
        
        # Check if required
        if self.required and (not self.spinner.text or self.spinner.text == "Select..."):
            self.error_text = f"{self.label_text} is required"
            return False, None
        
        return True, self.spinner.text


class FormActions(BoxLayout):
    """Form action buttons container."""
    
    submit_text = StringProperty("Submit")
    cancel_text = StringProperty("Cancel")
    on_submit = ObjectProperty(None)
    on_cancel = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        """Initialize the form actions."""
        super(FormActions, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.spacing = 10
        self.size_hint = (1, None)
        self.height = 50
        
        # Create buttons
        self.cancel_button = Button(
            text=self.cancel_text,
            size_hint=(0.5, 1)
        )
        apply_theme_to_widget(self.cancel_button, {}, style='secondary_button')
        self.cancel_button.bind(on_press=self._on_cancel_pressed)
        
        self.submit_button = Button(
            text=self.submit_text,
            size_hint=(0.5, 1)
        )
        apply_theme_to_widget(self.submit_button, {}, style='primary_button')
        self.submit_button.bind(on_press=self._on_submit_pressed)
        
        # Add buttons
        self.add_widget(self.cancel_button)
        self.add_widget(self.submit_button)
        
        # Bind properties
        self.bind(submit_text=self._update_submit_text)
        self.bind(cancel_text=self._update_cancel_text)
    
    def _update_submit_text(self, instance, value):
        """Update the submit button text."""
        self.submit_button.text = value
    
    def _update_cancel_text(self, instance, value):
        """Update the cancel button text."""
        self.cancel_button.text = value
    
    def _on_submit_pressed(self, instance):
        """Handle submit button press."""
        if self.on_submit:
            self.on_submit()
    
    def _on_cancel_pressed(self, instance):
        """Handle cancel button press."""
        if self.on_cancel:
            self.on_cancel()
