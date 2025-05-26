"""
Utility functions for form validation and data formatting.

This module provides helper functions for validating user input and formatting data.
"""
import re
from datetime import datetime

def validate_amount(amount_str):
    """
    Validate that the input is a valid currency amount.
    
    Args:
        amount_str (str): The amount string to validate
        
    Returns:
        tuple: (is_valid, value_or_error_message)
    """
    # Remove currency symbols and commas
    cleaned = re.sub(r'[^\d.-]', '', amount_str)
    
    try:
        value = float(cleaned)
        return True, value
    except ValueError:
        return False, "Please enter a valid amount"

def validate_date(date_str, format='%Y-%m-%d'):
    """
    Validate that the input is a valid date in the specified format.
    
    Args:
        date_str (str): The date string to validate
        format (str): The expected date format
        
    Returns:
        tuple: (is_valid, date_object_or_error_message)
    """
    try:
        date_obj = datetime.strptime(date_str, format)
        return True, date_obj
    except ValueError:
        return False, f"Please enter a valid date in {format} format"

def validate_required(value, field_name="This field"):
    """
    Validate that the input is not empty.
    
    Args:
        value (str): The value to validate
        field_name (str): Name of the field for error message
        
    Returns:
        tuple: (is_valid, value_or_error_message)
    """
    if value and value.strip():
        return True, value.strip()
    return False, f"{field_name} is required"

def validate_email(email):
    """
    Validate that the input is a valid email address.
    
    Args:
        email (str): The email to validate
        
    Returns:
        tuple: (is_valid, email_or_error_message)
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return True, email
    return False, "Please enter a valid email address"

def format_currency(amount, currency="$"):
    """
    Format a number as currency.
    
    Args:
        amount (float): The amount to format
        currency (str): The currency symbol
        
    Returns:
        str: Formatted currency string
    """
    return f"{currency}{amount:,.2f}"

def format_date(date_obj, format='%Y-%m-%d'):
    """
    Format a date object as a string.
    
    Args:
        date_obj (datetime): The date to format
        format (str): The output format
        
    Returns:
        str: Formatted date string
    """
    return date_obj.strftime(format)

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
