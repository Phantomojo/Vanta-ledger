"""
Shared financial calculation utilities for Vanta Ledger.
Provides common financial calculation functions to reduce code duplication.
"""

from decimal import Decimal
from typing import Dict, Any


def calculate_financial_totals(values: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate total and balance due for financial documents (invoices, bills, etc.).
    
    This function calculates:
    - total_amount = subtotal + tax_amount - discount_amount
    - balance_due = total_amount - paid_amount
    
    Args:
        values: Dictionary containing the financial values with keys:
            - subtotal: The subtotal amount
            - tax_amount: The tax amount (optional, defaults to 0)
            - discount_amount: The discount amount (optional, defaults to 0)
            - paid_amount: The amount paid (optional, defaults to 0)
    
    Returns:
        Dictionary with updated total_amount and balance_due values
    """
    subtotal = values.get("subtotal", Decimal("0"))
    tax = values.get("tax_amount", Decimal("0"))
    discount = values.get("discount_amount", Decimal("0"))
    paid = values.get("paid_amount", Decimal("0"))

    total = subtotal + tax - discount
    balance = total - paid

    values["total_amount"] = total
    values["balance_due"] = balance

    return values
