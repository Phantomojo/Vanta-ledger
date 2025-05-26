"""
Theme colors for Vanta Ledger Enhanced.

This module defines the color schemes used throughout the application.
"""

def get_color_scheme(dark_mode=False):
    """
    Get the application color scheme.
    
    Args:
        dark_mode (bool): Whether to use dark mode colors.
        
    Returns:
        dict: Dictionary containing color definitions.
    """
    if dark_mode:
        return {
            # Primary colors
            'primary': (0, 0.6, 0.9, 1),  # Blue
            'primary_dark': (0, 0.4, 0.7, 1),
            'primary_light': (0.4, 0.7, 1, 1),
            
            # Accent colors
            'accent': (0.9, 0.3, 0.5, 1),  # Pink
            'accent_dark': (0.7, 0.2, 0.4, 1),
            'accent_light': (1, 0.5, 0.7, 1),
            
            # Transaction type colors
            'income': (0, 0.7, 0.4, 1),  # Green
            'expense': (0.9, 0.3, 0.3, 1),  # Red
            
            # UI colors
            'background': (0.1, 0.1, 0.1, 1),
            'surface': (0.15, 0.15, 0.15, 1),
            'card': (0.2, 0.2, 0.2, 1),
            'divider': (0.3, 0.3, 0.3, 1),
            
            # Text colors
            'text_primary': (1, 1, 1, 1),
            'text_secondary': (0.8, 0.8, 0.8, 1),
            'text_hint': (0.6, 0.6, 0.6, 1),
            'text_disabled': (0.4, 0.4, 0.4, 1),
            
            # Status colors
            'success': (0, 0.8, 0.4, 1),
            'warning': (1, 0.8, 0, 1),
            'error': (1, 0.3, 0.3, 1),
            'info': (0.2, 0.7, 1, 1),
        }
    else:
        return {
            # Primary colors
            'primary': (0, 0.6, 0.9, 1),  # Blue
            'primary_dark': (0, 0.4, 0.7, 1),
            'primary_light': (0.4, 0.7, 1, 1),
            
            # Accent colors
            'accent': (0.9, 0.3, 0.5, 1),  # Pink
            'accent_dark': (0.7, 0.2, 0.4, 1),
            'accent_light': (1, 0.5, 0.7, 1),
            
            # Transaction type colors
            'income': (0, 0.7, 0.4, 1),  # Green
            'expense': (0.9, 0.3, 0.3, 1),  # Red
            
            # UI colors
            'background': (0.98, 0.98, 0.98, 1),
            'surface': (1, 1, 1, 1),
            'card': (0.95, 0.95, 0.95, 1),
            'divider': (0.9, 0.9, 0.9, 1),
            
            # Text colors
            'text_primary': (0.1, 0.1, 0.1, 1),
            'text_secondary': (0.4, 0.4, 0.4, 1),
            'text_hint': (0.6, 0.6, 0.6, 1),
            'text_disabled': (0.7, 0.7, 0.7, 1),
            
            # Status colors
            'success': (0, 0.8, 0.4, 1),
            'warning': (1, 0.8, 0, 1),
            'error': (1, 0.3, 0.3, 1),
            'info': (0.2, 0.7, 1, 1),
        }
