"""
Theme initialization file for Vanta Ledger Enhanced.

This module initializes the theme package and provides access to theme components.
"""

from frontend.theme.colors import get_color_scheme
from frontend.theme.fonts import get_font_styles
from frontend.theme.styles import apply_theme_to_widget

__all__ = ['get_color_scheme', 'get_font_styles', 'apply_theme_to_widget']
