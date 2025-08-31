import os
#!/usr/bin/env python3
"""
Financial Management Service
Core financial management for GL, AP/AR, and basic accounting
"""

import json
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID, uuid4

import redis
# from pymongo import MongoClient
from ..database import get_mongo_client
from pymongo.collection import Collection
from pymongo.database import Database

from ..config import settings
from ..models.financial_models import (
    AccountBalance,
    AccountType,
    Bill,
    ChartOfAccounts,
    Currency,
    Customer,
    Invoice,
    InvoiceLine,
    InvoiceStatus,
    JournalEntry,
    JournalEntryLine,
    Payment,
    PaymentAllocation,
    PaymentStatus,
    Vendor,
)
from ..utils.validation import input_validator

logger = logging.getLogger(__name__)


class FinancialService:
    """Core financial management service"""

    def __init__(self):
        # Database connections
        self.mongo_client = get_mongo_client()
        self.db: Database = self.mongo_client[settings.DATABASE_NAME]
        self.redis_client = redis.Redis.from_url(
            settings.REDIS_URI, decode_responses=True
        )

        # Collections
        self.chart_of_accounts: Collection = self.db.chart_of_accounts
        self.journal_entries: Collection = self.db.journal_entries
        self.journal_entry_lines: Collection = self.db.journal_entry_lines
        self.account_balances: Collection = self.db.account_balances
        self.invoices: Collection = self.db.invoices
        self.invoice_lines: Collection = self.db.invoice_lines
        self.bills: Collection = self.db.bills
        self.payments: Collection = self.db.payments
        self.payment_allocations: Collection = self.db.payment_allocations
        self.customers: Collection = self.db.customers
        self.vendors: Collection = self.db.vendors

        # Create indexes
        self._create_indexes()

        # Initialize default chart of accounts
        self._initialize_default_accounts()

    def _create_indexes(self):
        """Create database indexes for optimal performance"""
        try:
            # Chart of accounts indexes
            self.chart_of_accounts.create_index([("account_code", 1)], unique=True)
            self.chart_of_accounts.create_index([("account_type", 1)])

            # Journal entries indexes
            self.journal_entries.create_index([("entry_number", 1)], unique=True)
            self.journal_entries.create_index([("entry_date", -1)])
            self.journal_entries.create_index([("is_posted", 1)])

            # Invoice indexes
            self.invoices.create_index([("invoice_number", 1)], unique=True)
            self.invoices.create_index([("customer_id", 1)])
            self.invoices.create_index([("status", 1)])

            # Bill indexes
            self.bills.create_index([("bill_number", 1)], unique=True)
            self.bills.create_index([("vendor_id", 1)])
            self.bills.create_index([("status", 1)])

            # Customer/Vendor indexes
            self.customers.create_index([("customer_code", 1)], unique=True)
            self.vendors.create_index([("vendor_code", 1)], unique=True)

            logger.info("Financial database indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating financial indexes: {str(e)}")

    def _initialize_default_accounts(self):
        """Initialize default chart of accounts"""
        try:
            default_accounts = [
                # Assets
                {
                    "code": "1000",
                    "name": "Cash and Cash Equivalents",
                    "type": AccountType.ASSET,
                },
                {
                    "code": "1100",
                    "name": "Accounts Receivable",
                    "type": AccountType.ASSET,
                },
                {"code": "1200", "name": "Inventory", "type": AccountType.ASSET},
                {"code": "1300", "name": "Fixed Assets", "type": AccountType.ASSET},
                # Liabilities
                {
                    "code": "2000",
                    "name": "Accounts Payable",
                    "type": AccountType.LIABILITY,
                },
                {
                    "code": "2100",
                    "name": "Accrued Expenses",
                    "type": AccountType.LIABILITY,
                },
                {
                    "code": "2200",
                    "name": "Short-term Loans",
                    "type": AccountType.LIABILITY,
                },
                # Equity
                {"code": "3000", "name": "Owner's Equity", "type": AccountType.EQUITY},
                {
                    "code": "3100",
                    "name": "Retained Earnings",
                    "type": AccountType.EQUITY,
                },
                # Revenue
                {"code": "4000", "name": "Sales Revenue", "type": AccountType.REVENUE},
                {
                    "code": "4100",
                    "name": "Service Revenue",
                    "type": AccountType.REVENUE,
                },
                # Expenses
                {
                    "code": "5000",
                    "name": "Cost of Goods Sold",
                    "type": AccountType.EXPENSE,
                },
                {
                    "code": "5100",
                    "name": "Operating Expenses",
                    "type": AccountType.EXPENSE,
                },
                {
                    "code": "5200",
                    "name": "Payroll Expenses",
                    "type": AccountType.EXPENSE,
                },
            ]

            for account_data in default_accounts:
                if not self.chart_of_accounts.find_one(
                    {"account_code": account_data["code"]}
                ):
                    account = ChartOfAccounts(
                        account_code=account_data["code"],
                        account_name=account_data["name"],
                        account_type=account_data["type"],
                        is_system=True,
                        created_by=uuid4(),  # System user
                    )
                    self.chart_of_accounts.insert_one(account.dict())

            logger.info("Default chart of accounts initialized")
        except Exception as e:
            logger.error(f"Error initializing default accounts: {str(e)}")

    # Chart of Accounts Management
    def create_account(
        self, account_data: Dict[str, Any], user_id: UUID
    ) -> ChartOfAccounts:
        """Create a new chart of accounts entry"""
        try:
            account_data = input_validator.validate_json_payload(
                account_data,
                required_fields=["account_code", "account_name", "account_type"],
            )

            # Check if account code already exists
            existing_account = self.chart_of_accounts.find_one(
                {"account_code": account_data["account_code"]}
            )
            if existing_account:
                raise ValueError(
                    f"Account code '{account_data['account_code']}' already exists"
                )

            account = ChartOfAccounts(
                account_code=account_data["account_code"],
                account_name=account_data["account_name"],
                account_type=AccountType(account_data["account_type"]),
                parent_account_id=account_data.get("parent_account_id"),
                description=account_data.get("description"),
                created_by=user_id,
            )

            self.chart_of_accounts.insert_one(account.dict())
            logger.info(f"Account created: {account.account_code}")
            return account

        except Exception as e:
            logger.error(f"Error creating account: {str(e)}")
            raise

    def get_accounts(
        self, account_type: Optional[AccountType] = None, include_inactive: bool = False
    ) -> List[ChartOfAccounts]:
        """Get chart of accounts"""
        try:
            query = {}
            if account_type:
                query["account_type"] = account_type.value
            if not include_inactive:
                query["is_active"] = True

            cursor = self.chart_of_accounts.find(query).sort("account_code", 1)
            return [ChartOfAccounts(**account_data) for account_data in cursor]

        except Exception as e:
            logger.error(f"Error getting accounts: {str(e)}")
            raise

    # Journal Entry Management
    def create_journal_entry(
        self, entry_data: Dict[str, Any], user_id: UUID
    ) -> JournalEntry:
        """Create a new journal entry"""
        try:
            entry_data = input_validator.validate_json_payload(
                entry_data,
                required_fields=["entry_number", "entry_date", "description", "lines"],
            )

            # Create journal entry
            entry = JournalEntry(
                entry_number=entry_data["entry_number"],
                entry_date=datetime.fromisoformat(entry_data["entry_date"]),
                reference=entry_data.get("reference"),
                description=entry_data["description"],
                total_debit=Decimal("0"),
                total_credit=Decimal("0"),
                currency=Currency(entry_data.get("currency", "KES")),
                exchange_rate=Decimal(str(entry_data.get("exchange_rate", "1.00"))),
                created_by=user_id,
            )

            # Process lines and calculate totals
            lines = entry_data["lines"]
            total_debit = Decimal("0")
            total_credit = Decimal("0")

            for i, line_data in enumerate(lines, 1):
                line = JournalEntryLine(
                    journal_entry_id=entry.id,
                    account_id=UUID(line_data["account_id"]),
                    description=line_data["description"],
                    debit_amount=Decimal(str(line_data.get("debit_amount", "0"))),
                    credit_amount=Decimal(str(line_data.get("credit_amount", "0"))),
                    line_number=i,
                )

                total_debit += line.debit_amount
                total_credit += line.credit_amount

                # Save line
                self.journal_entry_lines.insert_one(line.dict())

            # Update entry totals
            entry.total_debit = total_debit
            entry.total_credit = total_credit

            # Save entry
            self.journal_entries.insert_one(entry.dict())

            logger.info(f"Journal entry created: {entry.entry_number}")
            return entry

        except Exception as e:
            logger.error(f"Error creating journal entry: {str(e)}")
            raise

    def get_journal_entries(
        self, page: int = 1, limit: int = 20, is_posted: Optional[bool] = None
    ) -> Tuple[List[JournalEntry], int]:
        """Get journal entries with filtering and pagination"""
        try:
            query = {}
            if is_posted is not None:
                query["is_posted"] = is_posted

            total_count = self.journal_entries.count_documents(query)
            skip = (page - 1) * limit

            cursor = (
                self.journal_entries.find(query)
                .sort("entry_date", -1)
                .skip(skip)
                .limit(limit)
            )
            entries = [JournalEntry(**entry_data) for entry_data in cursor]

            return entries, total_count

        except Exception as e:
            logger.error(f"Error getting journal entries: {str(e)}")
            raise

    # Invoice Management (Accounts Receivable)
    def create_invoice(self, invoice_data: Dict[str, Any], user_id: UUID) -> Invoice:
        """Create a new invoice"""
        try:
            invoice_data = input_validator.validate_json_payload(
                invoice_data,
                required_fields=[
                    "invoice_number",
                    "customer_id",
                    "invoice_date",
                    "due_date",
                    "lines",
                ],
            )

            # Calculate totals from lines
            subtotal = Decimal("0")
            tax_amount = Decimal("0")

            for line_data in invoice_data["lines"]:
                line_total = Decimal(str(line_data["quantity"])) * Decimal(
                    str(line_data["unit_price"])
                )
                subtotal += line_total

                if "tax_rate" in line_data:
                    tax_rate = Decimal(str(line_data["tax_rate"]))
                    tax_amount += line_total * (tax_rate / Decimal("100"))

            # Create invoice
            invoice = Invoice(
                invoice_number=invoice_data["invoice_number"],
                customer_id=UUID(invoice_data["customer_id"]),
                invoice_date=datetime.fromisoformat(invoice_data["invoice_date"]),
                due_date=datetime.fromisoformat(invoice_data["due_date"]),
                status=InvoiceStatus(invoice_data.get("status", "draft")),
                subtotal=subtotal,
                tax_amount=tax_amount,
                discount_amount=Decimal(str(invoice_data.get("discount_amount", "0"))),
                currency=Currency(invoice_data.get("currency", "KES")),
                exchange_rate=Decimal(str(invoice_data.get("exchange_rate", "1.00"))),
                notes=invoice_data.get("notes"),
                terms=invoice_data.get("terms"),
                created_by=user_id,
            )

            # Save invoice
            self.invoices.insert_one(invoice.dict())

            # Save invoice lines
            for i, line_data in enumerate(invoice_data["lines"], 1):
                line = InvoiceLine(
                    invoice_id=invoice.id,
                    item_description=line_data["item_description"],
                    quantity=Decimal(str(line_data["quantity"])),
                    unit_price=Decimal(str(line_data["unit_price"])),
                    tax_rate=Decimal(str(line_data.get("tax_rate", "0"))),
                    line_number=i,
                )

                self.invoice_lines.insert_one(line.dict())

            logger.info(f"Invoice created: {invoice.invoice_number}")
            return invoice

        except Exception as e:
            logger.error(f"Error creating invoice: {str(e)}")
            raise

    def get_invoices(
        self,
        customer_id: Optional[UUID] = None,
        status: Optional[InvoiceStatus] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[Invoice], int]:
        """Get invoices with filtering and pagination"""
        try:
            query = {}
            if customer_id:
                query["customer_id"] = str(customer_id)
            if status:
                query["status"] = status.value

            total_count = self.invoices.count_documents(query)
            skip = (page - 1) * limit

            cursor = (
                self.invoices.find(query)
                .sort("invoice_date", -1)
                .skip(skip)
                .limit(limit)
            )
            invoices = [Invoice(**invoice_data) for invoice_data in cursor]

            return invoices, total_count

        except Exception as e:
            logger.error(f"Error getting invoices: {str(e)}")
            raise

    # Customer Management
    def create_customer(self, customer_data: Dict[str, Any], user_id: UUID) -> Customer:
        """Create a new customer"""
        try:
            customer_data = input_validator.validate_json_payload(
                customer_data, required_fields=["customer_code", "customer_name"]
            )

            # Check if customer code already exists
            existing_customer = self.customers.find_one(
                {"customer_code": customer_data["customer_code"]}
            )
            if existing_customer:
                raise ValueError(
                    f"Customer code '{customer_data['customer_code']}' already exists"
                )

            customer = Customer(
                customer_code=customer_data["customer_code"],
                customer_name=customer_data["customer_name"],
                contact_person=customer_data.get("contact_person"),
                email=customer_data.get("email"),
                phone=customer_data.get("phone"),
                address=customer_data.get("address"),
                tax_id=customer_data.get("tax_id"),
                credit_limit=Decimal(str(customer_data.get("credit_limit", "0"))),
                payment_terms=customer_data.get("payment_terms"),
                created_by=user_id,
            )

            self.customers.insert_one(customer.dict())
            logger.info(f"Customer created: {customer.customer_code}")
            return customer

        except Exception as e:
            logger.error(f"Error creating customer: {str(e)}")
            raise

    def get_customers(self, include_inactive: bool = False) -> List[Customer]:
        """Get customers"""
        try:
            query = {}
            if not include_inactive:
                query["is_active"] = True

            cursor = self.customers.find(query).sort("customer_name", 1)
            return [Customer(**customer_data) for customer_data in cursor]

        except Exception as e:
            logger.error(f"Error getting customers: {str(e)}")
            raise

    # Financial Statistics
    def get_financial_statistics(self, user_id: UUID) -> Dict[str, Any]:
        """Get comprehensive financial statistics"""
        try:
            stats = {}

            # Account statistics
            stats["total_accounts"] = self.chart_of_accounts.count_documents(
                {"is_active": True}
            )
            stats["accounts_by_type"] = {}
            for account_type in AccountType:
                count = self.chart_of_accounts.count_documents(
                    {"account_type": account_type.value, "is_active": True}
                )
                stats["accounts_by_type"][account_type.value] = count

            # Invoice statistics
            stats["total_invoices"] = self.invoices.count_documents({})
            stats["invoices_by_status"] = {}
            for status in InvoiceStatus:
                count = self.invoices.count_documents({"status": status.value})
                stats["invoices_by_status"][status.value] = count

            # Journal entry statistics
            stats["total_journal_entries"] = self.journal_entries.count_documents({})
            stats["posted_entries"] = self.journal_entries.count_documents(
                {"is_posted": True}
            )
            stats["unposted_entries"] = self.journal_entries.count_documents(
                {"is_posted": False}
            )

            # Customer statistics
            stats["total_customers"] = self.customers.count_documents(
                {"is_active": True}
            )

            return stats

        except Exception as e:
            logger.error(f"Error getting financial statistics: {str(e)}")
            raise


# Global instance
financial_service = FinancialService()
