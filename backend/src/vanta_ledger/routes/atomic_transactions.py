#!/usr/bin/env python3
"""
Atomic Transactions API Routes
REST endpoints for atomic multi-posting transactions
"""

import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from ..auth import get_current_user
from ..models.user_models import User
from ..services.atomic_transaction_service import atomic_transaction_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/atomic-transactions", tags=["Atomic Transactions"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================


class TransactionLine(BaseModel):
    """Transaction line model"""
    account_id: str = Field(..., description="Account ID for the transaction line")
    description: str = Field(..., description="Description of the transaction line")
    debit_amount: str = Field("0.00", description="Debit amount")
    credit_amount: str = Field("0.00", description="Credit amount")
    line_number: int = Field(1, description="Line number in the transaction")


class AtomicTransactionRequest(BaseModel):
    """Request model for creating atomic transactions"""
    transactions: List[Dict[str, Any]] = Field(..., description="List of transactions to execute atomically")
    group_name: Optional[str] = Field(None, description="Optional group name for transaction grouping")
    description: Optional[str] = Field(None, description="Optional description for the transaction group")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class AtomicTransactionResponse(BaseModel):
    """Response model for atomic transactions"""
    success: bool
    atomic_transaction_id: str
    transaction_group_id: str
    status: str
    total_debit: str
    total_credit: str
    transaction_count: int
    message: str


class TransactionStatusResponse(BaseModel):
    """Response model for transaction status"""
    atomic_transaction_id: str
    status: str
    company_id: str
    transaction_group_id: str
    created_at: str
    completed_at: Optional[str]
    rolled_back_at: Optional[str]
    metadata: Dict[str, Any]
    journal_entries: List[Dict[str, Any]]
    journal_entry_count: int


class TransactionGroupResponse(BaseModel):
    """Response model for transaction groups"""
    id: str
    name: str
    description: Optional[str]
    company_id: str
    status: str
    created_at: str
    metadata: Dict[str, Any]


# ============================================================================
# ATOMIC TRANSACTION ENDPOINTS
# ============================================================================


@router.post("/", response_model=AtomicTransactionResponse)
async def create_atomic_transaction(
    request: AtomicTransactionRequest = Body(...),
    current_user: User = Depends(get_current_user),
    company_id: str = Query(..., description="Company ID for the transaction"),
):
    """
    Create an atomic transaction across multiple accounts/companies
    
    This endpoint enables atomic multi-posting transactions inspired by Formance Ledger.
    All transactions in the group will either succeed completely or fail completely.
    """
    try:
        # Validate company access
        if not current_user.has_company_access(company_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to specified company"
            )

        # Create atomic transaction
        result = await atomic_transaction_service.create_atomic_transaction(
            transactions=request.transactions,
            company_id=UUID(company_id),
            metadata=request.metadata,
            group_name=request.group_name,
            description=request.description,
        )

        return AtomicTransactionResponse(
            success=result["success"],
            atomic_transaction_id=result["atomic_transaction_id"],
            transaction_group_id=result["transaction_group_id"],
            status=result["status"],
            total_debit=result["total_debit"],
            total_credit=result["total_credit"],
            transaction_count=result["transaction_count"],
            message="Atomic transaction created successfully",
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error creating atomic transaction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create atomic transaction: {str(e)}"
        )


@router.get("/{transaction_id}", response_model=TransactionStatusResponse)
async def get_atomic_transaction_status(
    transaction_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Get the status and details of an atomic transaction
    """
    try:
        # Validate transaction ID format
        try:
            UUID(transaction_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid transaction ID format"
            )

        # Get transaction status
        status_data = await atomic_transaction_service.get_transaction_status(
            UUID(transaction_id)
        )

        # Check if user has access to the company
        if not current_user.has_company_access(status_data["company_id"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this transaction"
            )

        return TransactionStatusResponse(**status_data)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction not found: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error getting transaction status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get transaction status: {str(e)}"
        )


@router.post("/{transaction_id}/rollback")
async def rollback_atomic_transaction(
    transaction_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Rollback an atomic transaction
    
    This will create reversal entries for all journal entries in the transaction.
    """
    try:
        # Validate transaction ID format
        try:
            UUID(transaction_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid transaction ID format"
            )

        # Get transaction to check company access
        status_data = await atomic_transaction_service.get_transaction_status(
            UUID(transaction_id)
        )

        # Check if user has access to the company
        if not current_user.has_company_access(status_data["company_id"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this transaction"
            )

        # Check if transaction can be rolled back
        if status_data["status"] != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Transaction cannot be rolled back. Current status: {status_data['status']}"
            )

        # Execute rollback
        success = await atomic_transaction_service.rollback_transaction(
            UUID(transaction_id)
        )

        if success:
            return {
                "success": True,
                "message": f"Atomic transaction {transaction_id} rolled back successfully",
                "transaction_id": transaction_id,
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to rollback transaction"
            )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction not found: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rolling back transaction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to rollback transaction: {str(e)}"
        )


@router.get("/groups/list")
async def list_transaction_groups(
    current_user: User = Depends(get_current_user),
    company_id: str = Query(..., description="Company ID to list groups for"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of groups to return"),
):
    """
    List transaction groups for a company
    """
    try:
        # Validate company access
        if not current_user.has_company_access(company_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to specified company"
            )

        # List transaction groups
        groups = await atomic_transaction_service.list_transaction_groups(
            company_id=UUID(company_id),
            status=status,
            limit=limit,
        )

        return {
            "success": True,
            "transaction_groups": groups,
            "total_count": len(groups),
            "company_id": company_id,
        }

    except Exception as e:
        logger.error(f"Error listing transaction groups: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list transaction groups: {str(e)}"
        )


# ============================================================================
# VALIDATION ENDPOINTS
# ============================================================================


@router.post("/validate")
async def validate_atomic_transaction(
    request: AtomicTransactionRequest = Body(...),
    current_user: User = Depends(get_current_user),
):
    """
    Validate an atomic transaction without executing it
    
    This endpoint allows users to validate transaction structure and balance
    before actually creating the transaction.
    """
    try:
        # Validate transactions structure
        validation_results = []
        total_debit = 0
        total_credit = 0

        for i, transaction in enumerate(request.transactions):
            try:
                # Validate transaction structure
                validated_tx = atomic_transaction_service._validate_transaction(
                    transaction, i
                )
                
                # Calculate totals
                debit = float(validated_tx.get("debit_amount", "0"))
                credit = float(validated_tx.get("credit_amount", "0"))
                total_debit += debit
                total_credit += credit

                validation_results.append({
                    "transaction_index": i,
                    "valid": True,
                    "description": validated_tx["description"],
                    "debit_amount": validated_tx["debit_amount"],
                    "credit_amount": validated_tx["credit_amount"],
                    "line_count": len(validated_tx.get("lines", [])),
                })

            except Exception as e:
                validation_results.append({
                    "transaction_index": i,
                    "valid": False,
                    "error": str(e),
                })

        # Check overall balance
        is_balanced = abs(total_debit - total_credit) < 0.01  # Allow for rounding

        return {
            "success": True,
            "is_valid": all(r["valid"] for r in validation_results) and is_balanced,
            "is_balanced": is_balanced,
            "total_debit": str(total_debit),
            "total_credit": str(total_credit),
            "validation_results": validation_results,
            "transaction_count": len(request.transactions),
        }

    except Exception as e:
        logger.error(f"Error validating atomic transaction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate transaction: {str(e)}"
        )


# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================


@router.get("/health")
async def atomic_transaction_health_check():
    """
    Health check for atomic transaction service
    """
    try:
        # Basic health check
        return {
            "service": "atomic_transaction_service",
            "status": "healthy",
            "version": "1.0.0",
            "features": [
                "atomic_multi_posting",
                "cross_company_transfers",
                "rollback_mechanisms",
                "audit_trails",
            ],
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Atomic transaction service is unhealthy"
        )
