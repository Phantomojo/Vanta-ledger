"""
Data formatting utilities for Vanta Ledger Enhanced.

This module provides helper functions for formatting data for display.
"""
from datetime import datetime

def format_currency(amount, currency_symbol="$"):
    """
    Format a number as currency.
    
    Args:
        amount (float): The amount to format
        currency_symbol (str): The currency symbol to use
        
    Returns:
        str: Formatted currency string
    """
    return f"{currency_symbol}{amount:,.2f}"

def format_date(date_str, input_format="%Y-%m-%d", output_format="%b %d, %Y"):
    """
    Format a date string for display.
    
    Args:
        date_str (str): The date string to format
        input_format (str): The format of the input date string
        output_format (str): The desired output format
        
    Returns:
        str: Formatted date string
    """
    try:
        date_obj = datetime.strptime(date_str, input_format)
        return date_obj.strftime(output_format)
    except (ValueError, TypeError):
        return date_str

def format_percentage(value, decimal_places=1):
    """
    Format a decimal as a percentage.
    
    Args:
        value (float): The value to format (e.g., 0.75 for 75%)
        decimal_places (int): Number of decimal places
        
    Returns:
        str: Formatted percentage string
    """
    return f"{value * 100:.{decimal_places}f}%"

def truncate_text(text, max_length=30, ellipsis="..."):
    """
    Truncate text to a maximum length.
    
    Args:
        text (str): The text to truncate
        max_length (int): Maximum length before truncation
        ellipsis (str): String to append to truncated text
        
    Returns:
        str: Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    return text[:max_length - len(ellipsis)] + ellipsis

def format_transaction_type(type_str):
    """
    Format transaction type for display.
    
    Args:
        type_str (str): The transaction type ('sale', 'expenditure', etc.)
        
    Returns:
        str: Formatted transaction type
    """
    type_map = {
        'sale': 'Income',
        'expenditure': 'Expense',
        'transfer': 'Transfer',
        'investment': 'Investment',
        'loan': 'Loan'
    }
    
    return type_map.get(type_str.lower(), type_str.capitalize())

def format_owner_name(owner_data):
    """
    Format owner name for display.
    
    Args:
        owner_data (dict): Owner data dictionary
        
    Returns:
        str: Formatted owner name
    """
    if not owner_data:
        return "Unknown Owner"
    
    first_name = owner_data.get('first_name', '')
    last_name = owner_data.get('last_name', '')
    
    if first_name and last_name:
        return f"{first_name} {last_name}"
    elif owner_data.get('name'):
        return owner_data['name']
    elif owner_data.get('username'):
        return owner_data['username']
    else:
        return f"Owner {owner_data.get('id', 'Unknown')}"
