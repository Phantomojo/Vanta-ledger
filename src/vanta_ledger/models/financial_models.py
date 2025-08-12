#!/usr/bin/env python3
"""
Financial Management Models
Comprehensive financial models for GL, AP/AR, budgeting, and cash flow management
"""

import json
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, root_validator, validator


class AccountType(str, Enum):
    """Chart of accounts types"""

    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"


class TransactionType(str, Enum):
    """Transaction types"""

    DEBIT = "debit"
    CREDIT = "credit"


class PaymentStatus(str, Enum):
    """Payment status"""

    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class InvoiceStatus(str, Enum):
    """Invoice status"""

    DRAFT = "draft"
    SENT = "sent"
    VIEWED = "viewed"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class BudgetType(str, Enum):
    """Budget types"""

    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    PROJECT = "project"


class Currency(str, Enum):
    """Supported currencies"""

    KES = "KES"  # Kenyan Shilling
    USD = "USD"  # US Dollar
    EUR = "EUR"  # Euro
    GBP = "GBP"  # British Pound


class ChartOfAccounts(BaseModel):
    """Chart of accounts model"""

    id: UUID = Field(default_factory=uuid4)
    account_code: str = Field(..., min_length=1, max_length=20)
    account_name: str = Field(..., min_length=1, max_length=100)
    account_type: AccountType
    parent_account_id: Optional[UUID] = None
    description: Optional[str] = Field(None, max_length=500)
    is_active: bool = Field(default=True)
    is_system: bool = Field(default=False)
    created_by: UUID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    modified_at: Optional[datetime] = None

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat(), UUID: lambda v: str(v)}

    @validator("account_code")
    def validate_account_code(cls, v):
        """Validate account code format"""
        if not v.replace("-", "").replace(".", "").isalnum():
            raise ValueError(
                "Account code must be alphanumeric with optional hyphens and dots"
            )
        return v.upper()


class JournalEntry(BaseModel):
    """Journal entry model"""

    id: UUID = Field(default_factory=uuid4)
    entry_number: str = Field(..., min_length=1, max_length=50)
    entry_date: datetime
    reference: Optional[str] = Field(None, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    total_debit: Decimal = Field(..., decimal_places=2)
    total_credit: Decimal = Field(..., decimal_places=2)
    currency: Currency = Field(default=Currency.KES)
    exchange_rate: Decimal = Field(default=Decimal("1.00"), decimal_places=4)
    is_posted: bool = Field(default=False)
    posted_at: Optional[datetime] = None
    created_by: UUID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    modified_at: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
            Decimal: lambda v: str(v),
        }

    @root_validator(skip_on_failure=True)
    def validate_balanced_entry(cls, values):
        """Ensure debits equal credits"""
        total_debit = values.get("total_debit", Decimal("0"))
        total_credit = values.get("total_credit", Decimal("0"))

        if abs(total_debit - total_credit) > Decimal("0.01"):
            raise ValueError("Journal entry must be balanced (debits = credits)")

        return values


class JournalEntryLine(BaseModel):
    """Journal entry line item"""

    id: UUID = Field(default_factory=uuid4)
    journal_entry_id: UUID
    account_id: UUID
    description: str = Field(..., min_length=1, max_length=200)
    debit_amount: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    credit_amount: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    line_number: int = Field(..., ge=1)

    class Config:
        json_encoders = {UUID: lambda v: str(v), Decimal: lambda v: str(v)}

    @root_validator(skip_on_failure=True)
    def validate_line_amounts(cls, values):
        """Ensure either debit or credit, not both"""
        debit = values.get("debit_amount", Decimal("0"))
        credit = values.get("credit_amount", Decimal("0"))

        if debit > 0 and credit > 0:
            raise ValueError("Line item cannot have both debit and credit amounts")

        if debit == 0 and credit == 0:
            raise ValueError("Line item must have either debit or credit amount")

        return values


class AccountBalance(BaseModel):
    """Account balance model"""

    id: UUID = Field(default_factory=uuid4)
    account_id: UUID
    period_start: datetime
    period_end: datetime
    opening_balance: Decimal = Field(..., decimal_places=2)
    total_debits: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    total_credits: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    closing_balance: Decimal = Field(..., decimal_places=2)
    currency: Currency = Field(default=Currency.KES)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
            Decimal: lambda v: str(v),
        }


class Invoice(BaseModel):
    """Invoice model for accounts receivable"""

    id: UUID = Field(default_factory=uuid4)
    invoice_number: str = Field(..., min_length=1, max_length=50)
    customer_id: UUID
    invoice_date: datetime
    due_date: datetime
    status: InvoiceStatus = Field(default=InvoiceStatus.DRAFT)
    subtotal: Decimal = Field(..., decimal_places=2)
    tax_amount: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    discount_amount: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    total_amount: Decimal = Field(..., decimal_places=2)
    paid_amount: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    balance_due: Decimal = Field(..., decimal_places=2)
    currency: Currency = Field(default=Currency.KES)
    exchange_rate: Decimal = Field(default=Decimal("1.00"), decimal_places=4)
    notes: Optional[str] = Field(None, max_length=1000)
    terms: Optional[str] = Field(None, max_length=500)
    created_by: UUID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    modified_at: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
            Decimal: lambda v: str(v),
        }

    @root_validator(skip_on_failure=True)
    def calculate_totals(cls, values):
        """Calculate total and balance due"""
        subtotal = values.get("subtotal", Decimal("0"))
        tax = values.get("tax_amount", Decimal("0"))
        discount = values.get("discount_amount", Decimal("0"))
        paid = values.get("paid_amount", Decimal("0"))

        total = subtotal + tax - discount
        balance = total - paid

        values["total_amount"] = total
        values["balance_due"] = balance

        return values


class InvoiceLine(BaseModel):
    """Invoice line item"""

    id: UUID = Field(default_factory=uuid4)
    invoice_id: UUID
    item_description: str = Field(..., min_length=1, max_length=200)
    quantity: Decimal = Field(..., decimal_places=2, gt=0)
    unit_price: Decimal = Field(..., decimal_places=2, ge=0)
    tax_rate: Decimal = Field(default=Decimal("0.00"), decimal_places=4)
    line_total: Decimal = Field(..., decimal_places=2)
    line_number: int = Field(..., ge=1)

    class Config:
        json_encoders = {UUID: lambda v: str(v), Decimal: lambda v: str(v)}

    @root_validator(skip_on_failure=True)
    def calculate_line_total(cls, values):
        """Calculate line total"""
        quantity = values.get("quantity", Decimal("0"))
        unit_price = values.get("unit_price", Decimal("0"))

        line_total = quantity * unit_price
        values["line_total"] = line_total

        return values


class Bill(BaseModel):
    """Bill model for accounts payable"""

    id: UUID = Field(default_factory=uuid4)
    bill_number: str = Field(..., min_length=1, max_length=50)
    vendor_id: UUID
    bill_date: datetime
    due_date: datetime
    status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    subtotal: Decimal = Field(..., decimal_places=2)
    tax_amount: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    discount_amount: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    total_amount: Decimal = Field(..., decimal_places=2)
    paid_amount: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    balance_due: Decimal = Field(..., decimal_places=2)
    currency: Currency = Field(default=Currency.KES)
    exchange_rate: Decimal = Field(default=Decimal("1.00"), decimal_places=4)
    notes: Optional[str] = Field(None, max_length=1000)
    terms: Optional[str] = Field(None, max_length=500)
    created_by: UUID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    modified_at: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
            Decimal: lambda v: str(v),
        }

    @root_validator(skip_on_failure=True)
    def calculate_totals(cls, values):
        """Calculate total and balance due"""
        subtotal = values.get("subtotal", Decimal("0"))
        tax = values.get("tax_amount", Decimal("0"))
        discount = values.get("discount_amount", Decimal("0"))
        paid = values.get("paid_amount", Decimal("0"))

        total = subtotal + tax - discount
        balance = total - paid

        values["total_amount"] = total
        values["balance_due"] = balance

        return values


class Payment(BaseModel):
    """Payment model"""

    id: UUID = Field(default_factory=uuid4)
    payment_number: str = Field(..., min_length=1, max_length=50)
    payment_date: datetime
    payment_type: str = Field(
        ..., min_length=1, max_length=50
    )  # cash, bank, card, etc.
    reference_number: Optional[str] = Field(None, max_length=100)
    amount: Decimal = Field(..., decimal_places=2, gt=0)
    currency: Currency = Field(default=Currency.KES)
    exchange_rate: Decimal = Field(default=Decimal("1.00"), decimal_places=4)
    notes: Optional[str] = Field(None, max_length=500)
    created_by: UUID
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
            Decimal: lambda v: str(v),
        }


class PaymentAllocation(BaseModel):
    """Payment allocation to invoices/bills"""

    id: UUID = Field(default_factory=uuid4)
    payment_id: UUID
    invoice_id: Optional[UUID] = None  # For AR payments
    bill_id: Optional[UUID] = None  # For AP payments
    amount_allocated: Decimal = Field(..., decimal_places=2, gt=0)
    allocation_date: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
            Decimal: lambda v: str(v),
        }

    @root_validator(skip_on_failure=True)
    def validate_allocation(cls, values):
        """Ensure payment is allocated to either invoice or bill, not both"""
        invoice_id = values.get("invoice_id")
        bill_id = values.get("bill_id")

        if invoice_id and bill_id:
            raise ValueError("Payment allocation cannot be to both invoice and bill")

        if not invoice_id and not bill_id:
            raise ValueError("Payment allocation must be to either invoice or bill")

        return values


class Budget(BaseModel):
    """Budget model"""

    id: UUID = Field(default_factory=uuid4)
    budget_name: str = Field(..., min_length=1, max_length=100)
    budget_type: BudgetType
    start_date: datetime
    end_date: datetime
    total_budget: Decimal = Field(..., decimal_places=2)
    currency: Currency = Field(default=Currency.KES)
    description: Optional[str] = Field(None, max_length=500)
    is_active: bool = Field(default=True)
    created_by: UUID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    modified_at: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
            Decimal: lambda v: str(v),
        }


class BudgetLine(BaseModel):
    """Budget line item"""

    id: UUID = Field(default_factory=uuid4)
    budget_id: UUID
    account_id: UUID
    budget_amount: Decimal = Field(..., decimal_places=2)
    actual_amount: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    variance: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    variance_percentage: Decimal = Field(default=Decimal("0.00"), decimal_places=2)

    class Config:
        json_encoders = {UUID: lambda v: str(v), Decimal: lambda v: str(v)}

    @root_validator(skip_on_failure=True)
    def calculate_variance(cls, values):
        """Calculate variance and percentage"""
        budget = values.get("budget_amount", Decimal("0"))
        actual = values.get("actual_amount", Decimal("0"))

        variance = actual - budget
        variance_pct = (variance / budget * 100) if budget > 0 else Decimal("0")

        values["variance"] = variance
        values["variance_percentage"] = variance_pct

        return values


class CashFlow(BaseModel):
    """Cash flow model"""

    id: UUID = Field(default_factory=uuid4)
    period_start: datetime
    period_end: datetime
    opening_balance: Decimal = Field(..., decimal_places=2)
    cash_inflows: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    cash_outflows: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    net_cash_flow: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    closing_balance: Decimal = Field(..., decimal_places=2)
    currency: Currency = Field(default=Currency.KES)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
            Decimal: lambda v: str(v),
        }

    @root_validator(skip_on_failure=True)
    def calculate_net_flow(cls, values):
        """Calculate net cash flow and closing balance"""
        inflows = values.get("cash_inflows", Decimal("0"))
        outflows = values.get("cash_outflows", Decimal("0"))
        opening = values.get("opening_balance", Decimal("0"))

        net_flow = inflows - outflows
        closing = opening + net_flow

        values["net_cash_flow"] = net_flow
        values["closing_balance"] = closing

        return values


class FinancialReport(BaseModel):
    """Financial report model"""

    id: UUID = Field(default_factory=uuid4)
    report_name: str = Field(..., min_length=1, max_length=100)
    report_type: str = Field(
        ..., min_length=1, max_length=50
    )  # P&L, Balance Sheet, Cash Flow
    report_date: datetime
    period_start: datetime
    period_end: datetime
    report_data: Dict[str, Any] = Field(default_factory=dict)
    currency: Currency = Field(default=Currency.KES)
    generated_by: UUID
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat(), UUID: lambda v: str(v)}


class Customer(BaseModel):
    """Customer model"""

    id: UUID = Field(default_factory=uuid4)
    customer_code: str = Field(..., min_length=1, max_length=20)
    customer_name: str = Field(..., min_length=1, max_length=100)
    contact_person: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)
    tax_id: Optional[str] = Field(None, max_length=50)
    credit_limit: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    payment_terms: Optional[str] = Field(None, max_length=100)
    is_active: bool = Field(default=True)
    created_by: UUID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    modified_at: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
            Decimal: lambda v: str(v),
        }


class Vendor(BaseModel):
    """Vendor model"""

    id: UUID = Field(default_factory=uuid4)
    vendor_code: str = Field(..., min_length=1, max_length=20)
    vendor_name: str = Field(..., min_length=1, max_length=100)
    contact_person: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)
    tax_id: Optional[str] = Field(None, max_length=50)
    payment_terms: Optional[str] = Field(None, max_length=100)
    is_active: bool = Field(default=True)
    created_by: UUID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    modified_at: Optional[datetime] = None

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat(), UUID: lambda v: str(v)}
