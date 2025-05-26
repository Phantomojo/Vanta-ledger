"""
Dialog components for Vanta Ledger Enhanced.

This module provides reusable dialog and notification components.
"""
from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from kivy.animation import Animation
from kivy.clock import Clock

from frontend.theme.styles import apply_theme_to_widget

class Dialog(ModalView):
    """
    Base dialog component with customizable content.
    
    Features:
    - Consistent styling
    - Animation effects
    - Customizable content
    - Backdrop overlay
    """
    
    title = StringProperty("")
    
    def __init__(self, **kwargs):
        """Initialize the dialog."""
        super(Dialog, self).__init__(**kwargs)
        self.size_hint = (0.8, None)
        self.height = 300
        self.auto_dismiss = True
        
        # Main layout
        self.layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # Title
        self.title_label = Label(
            text=self.title,
            size_hint=(1, 0.2),
            halign='left',
            valign='middle',
            font_size='18sp',
            color=(0.3, 0.3, 0.3, 1)
        )
        self.title_label.bind(size=self.title_label.setter('text_size'))
        
        # Content container (to be filled by subclasses)
        self.content_container = BoxLayout(orientation='vertical', size_hint=(1, 0.6))
        
        # Buttons container (to be filled by subclasses)
        self.buttons_container = BoxLayout(orientation='horizontal', size_hint=(1, 0.2), spacing=10)
        
        # Add components to layout
        self.layout.add_widget(self.title_label)
        self.layout.add_widget(self.content_container)
        self.layout.add_widget(self.buttons_container)
        
        # Add layout to dialog
        self.add_widget(self.layout)
        
        # Bind properties
        self.bind(title=self._update_title)
    
    def _update_title(self, instance, value):
        """Update the dialog title."""
        self.title_label.text = value
    
    def open(self, *args, **kwargs):
        """Open the dialog with animation."""
        self.opacity = 0
        super(Dialog, self).open(*args, **kwargs)
        
        # Fade in animation
        anim = Animation(opacity=1, duration=0.2)
        anim.start(self)
    
    def dismiss(self, *args, **kwargs):
        """Dismiss the dialog with animation."""
        # Fade out animation
        anim = Animation(opacity=0, duration=0.2)
        anim.bind(on_complete=lambda *x: super(Dialog, self).dismiss(*args, **kwargs))
        anim.start(self)


class AlertDialog(Dialog):
    """Alert dialog with message and confirmation button."""
    
    message = StringProperty("")
    button_text = StringProperty("OK")
    on_confirm = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        """Initialize the alert dialog."""
        super(AlertDialog, self).__init__(**kwargs)
        
        # Message label
        self.message_label = Label(
            text=self.message,
            size_hint=(1, 1),
            halign='center',
            valign='middle',
            color=(0.3, 0.3, 0.3, 1)
        )
        self.message_label.bind(size=self.message_label.setter('text_size'))
        
        # Confirm button
        self.confirm_button = Button(
            text=self.button_text,
            size_hint=(1, 1)
        )
        apply_theme_to_widget(self.confirm_button, {}, style='primary_button')
        self.confirm_button.bind(on_press=self._on_confirm)
        
        # Add components
        self.content_container.add_widget(self.message_label)
        self.buttons_container.add_widget(self.confirm_button)
        
        # Bind properties
        self.bind(message=self._update_message)
        self.bind(button_text=self._update_button_text)
    
    def _update_message(self, instance, value):
        """Update the message text."""
        self.message_label.text = value
    
    def _update_button_text(self, instance, value):
        """Update the button text."""
        self.confirm_button.text = value
    
    def _on_confirm(self, instance):
        """Handle confirm button press."""
        if self.on_confirm:
            self.on_confirm()
        self.dismiss()


class ConfirmDialog(Dialog):
    """Confirmation dialog with yes/no buttons."""
    
    message = StringProperty("")
    confirm_text = StringProperty("Yes")
    cancel_text = StringProperty("No")
    on_confirm = ObjectProperty(None)
    on_cancel = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        """Initialize the confirmation dialog."""
        super(ConfirmDialog, self).__init__(**kwargs)
        
        # Message label
        self.message_label = Label(
            text=self.message,
            size_hint=(1, 1),
            halign='center',
            valign='middle',
            color=(0.3, 0.3, 0.3, 1)
        )
        self.message_label.bind(size=self.message_label.setter('text_size'))
        
        # Cancel button
        self.cancel_button = Button(
            text=self.cancel_text,
            size_hint=(0.5, 1)
        )
        apply_theme_to_widget(self.cancel_button, {}, style='secondary_button')
        self.cancel_button.bind(on_press=self._on_cancel)
        
        # Confirm button
        self.confirm_button = Button(
            text=self.confirm_text,
            size_hint=(0.5, 1)
        )
        apply_theme_to_widget(self.confirm_button, {}, style='primary_button')
        self.confirm_button.bind(on_press=self._on_confirm)
        
        # Add components
        self.content_container.add_widget(self.message_label)
        self.buttons_container.add_widget(self.cancel_button)
        self.buttons_container.add_widget(self.confirm_button)
        
        # Bind properties
        self.bind(message=self._update_message)
        self.bind(confirm_text=self._update_confirm_text)
        self.bind(cancel_text=self._update_cancel_text)
    
    def _update_message(self, instance, value):
        """Update the message text."""
        self.message_label.text = value
    
    def _update_confirm_text(self, instance, value):
        """Update the confirm button text."""
        self.confirm_button.text = value
    
    def _update_cancel_text(self, instance, value):
        """Update the cancel button text."""
        self.cancel_button.text = value
    
    def _on_confirm(self, instance):
        """Handle confirm button press."""
        if self.on_confirm:
            self.on_confirm()
        self.dismiss()
    
    def _on_cancel(self, instance):
        """Handle cancel button press."""
        if self.on_cancel:
            self.on_cancel()
        self.dismiss()


class Toast(BoxLayout):
    """
    Toast notification that appears briefly and disappears.
    
    Features:
    - Auto-dismiss after timeout
    - Different styles for success, error, info
    - Animation effects
    """
    
    message = StringProperty("")
    duration = NumericProperty(3)  # seconds
    type = StringProperty("info")  # info, success, error
    
    def __init__(self, **kwargs):
        """Initialize the toast notification."""
        super(Toast, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint = (None, None)
        self.width = 300
        self.height = 50
        self.opacity = 0
        self.pos_hint = {'center_x': 0.5, 'y': 0.1}
        
        # Apply styling based on type
        bg_color = (0.2, 0.7, 1, 1)  # info (blue)
        if self.type == 'success':
            bg_color = (0, 0.8, 0.4, 1)  # success (green)
        elif self.type == 'error':
            bg_color = (0.9, 0.3, 0.3, 1)  # error (red)
        
        # Background
        with self.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(*bg_color)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[25])
        
        # Bind position and size updates
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        # Message label
        self.message_label = Label(
            text=self.message,
            size_hint=(1, 1),
            halign='center',
            valign='middle',
            color=(1, 1, 1, 1)
        )
        self.add_widget(self.message_label)
        
        # Bind properties
        self.bind(message=self._update_message)
    
    def _update_bg(self, instance, value):
        """Update the background rectangle position and size."""
        self.bg.pos = self.pos
        self.bg.size = self.size
    
    def _update_message(self, instance, value):
        """Update the message text."""
        self.message_label.text = value
    
    def show(self):
        """Show the toast with animation."""
        # Fade in animation
        anim_in = Animation(opacity=1, duration=0.3)
        
        # Wait
        anim_wait = Animation(opacity=1, duration=self.duration)
        
        # Fade out animation
        anim_out = Animation(opacity=0, duration=0.3)
        anim_out.bind(on_complete=self._remove_self)
        
        # Chain animations
        anim = anim_in + anim_wait + anim_out
        anim.start(self)
    
    def _remove_self(self, *args):
        """Remove the toast from its parent."""
        if self.parent:
            self.parent.remove_widget(self)


def show_toast(parent, message, type="info", duration=3):
    """
    Show a toast notification.
    
    Args:
        parent: Parent widget to add the toast to
        message: Message to display
        type: Toast type ('info', 'success', 'error')
        duration: Display duration in seconds
    """
    toast = Toast(message=message, type=type, duration=duration)
    parent.add_widget(toast)
    toast.show()


def show_alert(title, message, button_text="OK", on_confirm=None):
    """
    Show an alert dialog.
    
    Args:
        title: Dialog title
        message: Message to display
        button_text: Text for the confirm button
        on_confirm: Callback for confirm button press
    """
    dialog = AlertDialog(
        title=title,
        message=message,
        button_text=button_text,
        on_confirm=on_confirm
    )
    dialog.open()


def show_confirm(title, message, confirm_text="Yes", cancel_text="No", 
                on_confirm=None, on_cancel=None):
    """
    Show a confirmation dialog.
    
    Args:
        title: Dialog title
        message: Message to display
        confirm_text: Text for the confirm button
        cancel_text: Text for the cancel button
        on_confirm: Callback for confirm button press
        on_cancel: Callback for cancel button press
    """
    dialog = ConfirmDialog(
        title=title,
        message=message,
        confirm_text=confirm_text,
        cancel_text=cancel_text,
        on_confirm=on_confirm,
        on_cancel=on_cancel
    )
    dialog.open()
