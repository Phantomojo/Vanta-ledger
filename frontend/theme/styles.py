"""
Theme styles for Vanta Ledger Enhanced.

This module provides functions to apply theme styles to widgets.
"""
from kivy.graphics import Color, RoundedRectangle, Rectangle

def apply_theme_to_widget(widget, colors, style='default', radius=None):
    """
    Apply theme styling to a widget.
    
    Args:
        widget: The Kivy widget to style
        colors: Dictionary of colors from get_color_scheme()
        style: Style to apply ('default', 'card', 'button', 'input', etc.)
        radius: Corner radius for rounded elements (default depends on style)
    
    Returns:
        The styled widget
    """
    # Clear any existing canvas instructions
    widget.canvas.before.clear()
    
    # Apply style based on type
    if style == 'card':
        _apply_card_style(widget, colors, radius or 10)
    elif style == 'button':
        _apply_button_style(widget, colors, radius or 5)
    elif style == 'primary_button':
        _apply_primary_button_style(widget, colors, radius or 5)
    elif style == 'secondary_button':
        _apply_secondary_button_style(widget, colors, radius or 5)
    elif style == 'danger_button':
        _apply_danger_button_style(widget, colors, radius or 5)
    elif style == 'input':
        _apply_input_style(widget, colors, radius or 5)
    elif style == 'header':
        _apply_header_style(widget, colors)
    elif style == 'divider':
        _apply_divider_style(widget, colors)
    else:  # default
        _apply_default_style(widget, colors)
    
    # Bind position and size updates
    widget.bind(pos=_update_canvas_pos, size=_update_canvas_size)
    
    return widget

def _apply_default_style(widget, colors):
    """Apply default style to widget."""
    with widget.canvas.before:
        Color(*colors['background'])
        widget.bg_rect = Rectangle(pos=widget.pos, size=widget.size)

def _apply_card_style(widget, colors, radius):
    """Apply card style to widget."""
    with widget.canvas.before:
        Color(*colors['card'])
        widget.bg_rect = RoundedRectangle(pos=widget.pos, size=widget.size, radius=[radius])
        
        # Add subtle shadow effect (in a real implementation, this would be more sophisticated)
        Color(0, 0, 0, 0.1)
        widget.shadow_rect = RoundedRectangle(
            pos=(widget.pos[0] + 2, widget.pos[1] - 2),
            size=widget.size,
            radius=[radius]
        )

def _apply_button_style(widget, colors, radius):
    """Apply button style to widget."""
    with widget.canvas.before:
        Color(*colors['surface'])
        widget.bg_rect = RoundedRectangle(pos=widget.pos, size=widget.size, radius=[radius])
    
    # Set text color
    widget.color = colors['text_primary']

def _apply_primary_button_style(widget, colors, radius):
    """Apply primary button style to widget."""
    with widget.canvas.before:
        Color(*colors['primary'])
        widget.bg_rect = RoundedRectangle(pos=widget.pos, size=widget.size, radius=[radius])
    
    # Set text color to white for contrast
    widget.color = (1, 1, 1, 1)

def _apply_secondary_button_style(widget, colors, radius):
    """Apply secondary button style to widget."""
    with widget.canvas.before:
        Color(*colors['accent'])
        widget.bg_rect = RoundedRectangle(pos=widget.pos, size=widget.size, radius=[radius])
    
    # Set text color to white for contrast
    widget.color = (1, 1, 1, 1)

def _apply_danger_button_style(widget, colors, radius):
    """Apply danger button style to widget."""
    with widget.canvas.before:
        Color(*colors['error'])
        widget.bg_rect = RoundedRectangle(pos=widget.pos, size=widget.size, radius=[radius])
    
    # Set text color to white for contrast
    widget.color = (1, 1, 1, 1)

def _apply_input_style(widget, colors, radius):
    """Apply input field style to widget."""
    with widget.canvas.before:
        # Background
        Color(*colors['surface'])
        widget.bg_rect = RoundedRectangle(pos=widget.pos, size=widget.size, radius=[radius])
        
        # Border
        Color(*colors['divider'])
        widget.border_rect = RoundedRectangle(
            pos=widget.pos,
            size=widget.size,
            radius=[radius]
        )
    
    # Set text color
    widget.foreground_color = colors['text_primary']
    widget.hint_text_color = colors['text_hint']

def _apply_header_style(widget, colors):
    """Apply header style to widget."""
    with widget.canvas.before:
        Color(*colors['surface'])
        widget.bg_rect = Rectangle(pos=widget.pos, size=widget.size)
        
        # Bottom border
        Color(*colors['divider'])
        widget.border_rect = Rectangle(
            pos=(widget.pos[0], widget.pos[1]),
            size=(widget.size[0], 1)
        )

def _apply_divider_style(widget, colors):
    """Apply divider style to widget."""
    with widget.canvas.before:
        Color(*colors['divider'])
        widget.bg_rect = Rectangle(pos=widget.pos, size=widget.size)

def _update_canvas_pos(instance, value):
    """Update the position of canvas elements when widget position changes."""
    if hasattr(instance, 'bg_rect'):
        instance.bg_rect.pos = instance.pos
    
    if hasattr(instance, 'shadow_rect'):
        instance.shadow_rect.pos = (instance.pos[0] + 2, instance.pos[1] - 2)
    
    if hasattr(instance, 'border_rect'):
        instance.border_rect.pos = instance.pos

def _update_canvas_size(instance, value):
    """Update the size of canvas elements when widget size changes."""
    if hasattr(instance, 'bg_rect'):
        instance.bg_rect.size = instance.size
    
    if hasattr(instance, 'shadow_rect'):
        instance.shadow_rect.size = instance.size
    
    if hasattr(instance, 'border_rect'):
        if instance.height > 2:  # For headers with bottom border
            instance.border_rect.size = (instance.width, 1)
        else:  # For dividers
            instance.border_rect.size = instance.size
