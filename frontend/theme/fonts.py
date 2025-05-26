"""
Font styles for Vanta Ledger Enhanced.

This module defines the typography styles used throughout the application.
"""

def get_font_styles(dark_mode=False):
    """
    Get the application font styles.
    
    Args:
        dark_mode (bool): Whether to use dark mode text colors.
        
    Returns:
        dict: Dictionary containing font style definitions.
    """
    # Base text color depends on dark mode
    text_primary = (1, 1, 1, 1) if dark_mode else (0.1, 0.1, 0.1, 1)
    text_secondary = (0.8, 0.8, 0.8, 1) if dark_mode else (0.4, 0.4, 0.4, 1)
    text_hint = (0.6, 0.6, 0.6, 1) if dark_mode else (0.6, 0.6, 0.6, 1)
    
    return {
        # Headings
        'h1': {
            'font_size': '28sp',
            'color': text_primary,
            'bold': True
        },
        'h2': {
            'font_size': '24sp',
            'color': text_primary,
            'bold': True
        },
        'h3': {
            'font_size': '20sp',
            'color': text_primary,
            'bold': True
        },
        'h4': {
            'font_size': '18sp',
            'color': text_primary,
            'bold': False
        },
        'h5': {
            'font_size': '16sp',
            'color': text_primary,
            'bold': True
        },
        
        # Body text
        'body1': {
            'font_size': '16sp',
            'color': text_primary,
            'bold': False
        },
        'body2': {
            'font_size': '14sp',
            'color': text_primary,
            'bold': False
        },
        
        # Special text styles
        'caption': {
            'font_size': '12sp',
            'color': text_secondary,
            'bold': False
        },
        'button': {
            'font_size': '16sp',
            'color': text_primary,
            'bold': True
        },
        'label': {
            'font_size': '14sp',
            'color': text_secondary,
            'bold': False
        },
        'hint': {
            'font_size': '14sp',
            'color': text_hint,
            'bold': False
        },
        
        # Financial text
        'amount_large': {
            'font_size': '32sp',
            'color': text_primary,
            'bold': True
        },
        'amount_medium': {
            'font_size': '24sp',
            'color': text_primary,
            'bold': True
        },
        'amount_small': {
            'font_size': '18sp',
            'color': text_primary,
            'bold': True
        },
        
        # Status text
        'success': {
            'font_size': '14sp',
            'color': (0, 0.8, 0.4, 1),  # Green
            'bold': False
        },
        'warning': {
            'font_size': '14sp',
            'color': (1, 0.8, 0, 1),  # Yellow
            'bold': False
        },
        'error': {
            'font_size': '14sp',
            'color': (1, 0.3, 0.3, 1),  # Red
            'bold': False
        },
        'info': {
            'font_size': '14sp',
            'color': (0.2, 0.7, 1, 1),  # Blue
            'bold': False
        }
    }
