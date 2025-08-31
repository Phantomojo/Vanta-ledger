import os
#!/usr/bin/env python3
"""
Financial Management API Routes
Comprehensive financial management endpoints for GL, AP/AR, and accounting
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

from ..auth import User, get_current_user
from ..models.financial_models import (
    AccountType,
    ChartOfAccounts,
    Currency,
    Customer,
    Invoice,
    InvoiceLine,
    InvoiceStatus,
    JournalEntry,
    JournalEntryLine,
    PaymentStatus,
    Vendor,
)
from ..services.financial_service import financial_service
from ..utils.validation import input_validator

router = APIRouter(prefix="/api/v2/financial", tags=["Financial Management"])

# ============================================================================
# CHART OF ACCOUNTS ENDPOINTS
# ============================================================================


@router.post("/accounts")
async def create_account(
    account_data: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_user),
):
    """Create a new chart of accounts entry"""
    try:
        account = financial_service.create_account(account_data, current_user.id)
        return {
            "success": True,
            "account": account.dict(),
            "message": "Account created successfully",
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create account: {str(e)}",
        )


@router.get("/accounts")
async def list_accounts(
    account_type: Optional[str] = Query(None, description="Filter by account type"),
    include_inactive: bool = Query(False, description="Include inactive accounts"),
    current_user: User = Depends(get_current_user),
):
    """List chart of accounts"""
    try:
        account_type_enum = None
        if account_type:
            try:
                account_type_enum = AccountType(account_type)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid account type: {account_type}",
                )

        accounts = financial_service.get_accounts(account_type_enum, include_inactive)
        return {"success": True, "accounts": [account.dict() for account in accounts]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list accounts: {str(e)}",
        )


@router.get("/accounts/types")
async def get_account_types():
    """Get all available account types"""
    return {"success": True, "account_types": [at.value for at in AccountType]}


# ============================================================================
# JOURNAL ENTRIES ENDPOINTS
# ============================================================================


@router.post("/journal-entries")
async def create_journal_entry(
    entry_data: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_user),
):
    """Create a new journal entry"""
    try:
        entry = financial_service.create_journal_entry(entry_data, current_user.id)
        return {
            "success": True,
            "journal_entry": entry.dict(),
            "message": "Journal entry created successfully",
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create journal entry: {str(e)}",
        )


@router.get("/journal-entries")
async def list_journal_entries(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    is_posted: Optional[bool] = Query(None, description="Filter by posted status"),
    current_user: User = Depends(get_current_user),
):
    """List journal entries with filtering and pagination"""
    try:
        entries, total_count = financial_service.get_journal_entries(
            page, limit, is_posted
        )

        return {
            "success": True,
            "journal_entries": [entry.dict() for entry in entries],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_count,
                "total_pages": (total_count + limit - 1) // limit,
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list journal entries: {str(e)}",
        )


@router.get("/journal-entries/{entry_id}")
async def get_journal_entry(
    entry_id: str, current_user: User = Depends(get_current_user)
):
    """Get journal entry by ID"""
    try:
        entry_uuid = input_validator.validate_uuid(entry_id, "entry_id")

        # Get journal entry
        entry_data = financial_service.journal_entries.find_one(
            {"_id": str(entry_uuid)}
        )
        if not entry_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Journal entry not found"
            )

        entry = JournalEntry(**entry_data)

        # Get entry lines
        lines_data = financial_service.journal_entry_lines.find(
            {"journal_entry_id": str(entry_uuid)}
        )
        lines = [JournalEntryLine(**line_data) for line_data in lines_data]

        return {
            "success": True,
            "journal_entry": entry.dict(),
            "lines": [line.dict() for line in lines],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get journal entry: {str(e)}",
        )


# ============================================================================
# INVOICE ENDPOINTS (ACCOUNTS RECEIVABLE)
# ============================================================================


@router.post("/invoices")
async def create_invoice(
    invoice_data: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_user),
):
    """Create a new invoice"""
    try:
        invoice = financial_service.create_invoice(invoice_data, current_user.id)
        return {
            "success": True,
            "invoice": invoice.dict(),
            "message": "Invoice created successfully",
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create invoice: {str(e)}",
        )


@router.get("/invoices")
async def list_invoices(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    customer_id: Optional[str] = Query(None, description="Filter by customer ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    current_user: User = Depends(get_current_user),
):
    """List invoices with filtering and pagination"""
    try:
        customer_uuid = None
        if customer_id:
            customer_uuid = input_validator.validate_uuid(customer_id, "customer_id")

        status_enum = None
        if status:
            try:
                status_enum = InvoiceStatus(status)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid invoice status: {status}",
                )

        invoices, total_count = financial_service.get_invoices(
            customer_uuid, status_enum, page, limit
        )

        return {
            "success": True,
            "invoices": [invoice.dict() for invoice in invoices],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_count,
                "total_pages": (total_count + limit - 1) // limit,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list invoices: {str(e)}",
        )


@router.get("/invoices/{invoice_id}")
async def get_invoice(invoice_id: str, current_user: User = Depends(get_current_user)):
    """Get invoice by ID"""
    try:
        invoice_uuid = input_validator.validate_uuid(invoice_id, "invoice_id")

        # Get invoice
        invoice_data = financial_service.invoices.find_one({"_id": str(invoice_uuid)})
        if not invoice_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found"
            )

        invoice = Invoice(**invoice_data)

        # Get invoice lines
        lines_data = financial_service.invoice_lines.find(
            {"invoice_id": str(invoice_uuid)}
        )
        lines = [InvoiceLine(**line_data) for line_data in lines_data]

        return {
            "success": True,
            "invoice": invoice.dict(),
            "lines": [line.dict() for line in lines],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get invoice: {str(e)}",
        )


@router.get("/invoices/statuses")
async def get_invoice_statuses():
    """Get all available invoice statuses"""
    return {
        "success": True,
        "invoice_statuses": [status.value for status in InvoiceStatus],
    }


# ============================================================================
# CUSTOMER ENDPOINTS
# ============================================================================


@router.post("/customers")
async def create_customer(
    customer_data: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_user),
):
    """Create a new customer"""
    try:
        customer = financial_service.create_customer(customer_data, current_user.id)
        return {
            "success": True,
            "customer": customer.dict(),
            "message": "Customer created successfully",
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create customer: {str(e)}",
        )


@router.get("/customers")
async def list_customers(
    include_inactive: bool = Query(False, description="Include inactive customers"),
    current_user: User = Depends(get_current_user),
):
    """List customers"""
    try:
        customers = financial_service.get_customers(include_inactive)
        return {
            "success": True,
            "customers": [customer.dict() for customer in customers],
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list customers: {str(e)}",
        )


@router.get("/customers/{customer_id}")
async def get_customer(
    customer_id: str, current_user: User = Depends(get_current_user)
):
    """Get customer by ID"""
    try:
        customer_uuid = input_validator.validate_uuid(customer_id, "customer_id")

        customer_data = financial_service.customers.find_one(
            {"_id": str(customer_uuid)}
        )
        if not customer_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found"
            )

        customer = Customer(**customer_data)

        return {"success": True, "customer": customer.dict()}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get customer: {str(e)}",
        )


# ============================================================================
# FINANCIAL STATISTICS ENDPOINTS
# ============================================================================


@router.get("/statistics/overview")
async def get_financial_statistics(current_user: User = Depends(get_current_user)):
    """Get comprehensive financial statistics"""
    try:
        stats = financial_service.get_financial_statistics(current_user.id)

        return {"success": True, "statistics": stats}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get financial statistics: {str(e)}",
        )


@router.get("/statistics/accounts")
async def get_account_statistics(current_user: User = Depends(get_current_user)):
    """Get account-related statistics"""
    try:
        stats = financial_service.get_financial_statistics(current_user.id)

        return {
            "success": True,
            "account_statistics": {
                "total_accounts": stats.get("total_accounts", 0),
                "accounts_by_type": stats.get("accounts_by_type", {}),
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get account statistics: {str(e)}",
        )


@router.get("/statistics/invoices")
async def get_invoice_statistics(current_user: User = Depends(get_current_user)):
    """Get invoice-related statistics"""
    try:
        stats = financial_service.get_financial_statistics(current_user.id)

        return {
            "success": True,
            "invoice_statistics": {
                "total_invoices": stats.get("total_invoices", 0),
                "invoices_by_status": stats.get("invoices_by_status", {}),
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get invoice statistics: {str(e)}",
        )


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================


@router.get("/currencies")
async def get_currencies():
    """Get all supported currencies"""
    return {"success": True, "currencies": [currency.value for currency in Currency]}


@router.get("/payment-statuses")
async def get_payment_statuses():
    """Get all payment statuses"""
    return {
        "success": True,
        "payment_statuses": [status.value for status in PaymentStatus],
    }


@router.post("/validate-account-code")
async def validate_account_code(
    account_code: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
):
    """Validate account code format and uniqueness"""
    try:
        # Check format
        if not account_code.replace("-", "").replace(".", "").isalnum():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account code must be alphanumeric with optional hyphens and dots",
            )

        # Check uniqueness
        existing_account = financial_service.chart_of_accounts.find_one(
            {"account_code": account_code.upper()}
        )
        if existing_account:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Account code '{account_code}' already exists",
            )

        return {
            "success": True,
            "valid": True,
            "message": "Account code is valid and available",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate account code: {str(e)}",
        )


@router.post("/validate-customer-code")
async def validate_customer_code(
    customer_code: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
):
    """Validate customer code uniqueness"""
    try:
        existing_customer = financial_service.customers.find_one(
            {"customer_code": customer_code}
        )
        if existing_customer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Customer code '{customer_code}' already exists",
            )

        return {"success": True, "valid": True, "message": "Customer code is available"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate customer code: {str(e)}",
        )
