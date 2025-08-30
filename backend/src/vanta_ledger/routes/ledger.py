from typing import List

from fastapi import APIRouter, Depends, HTTPException

from ..auth import AuthService
from ..database import get_mongo_client

router = APIRouter(prefix="/ledger", tags=["Ledger"])


@router.get("/")
async def get_ledger_entries(current_user: dict = Depends(AuthService.verify_token)):
    """
    Retrieve up to 50 ledger entries from the database for authenticated users.

    Returns:
        A list of ledger entry documents.
    """
    # For now, return sample data to test if the endpoint works
    return [
        {
            "id": 1,
            "transaction_date": "2025-08-13T22:30:00",
            "description": "Office supplies purchase",
            "amount": 1250.50,
            "account_name": "Office Expenses",
            "transaction_type": "debit",
            "reference": "INV-001"
        },
        {
            "id": 2,
            "transaction_date": "2025-08-13T22:25:00",
            "description": "Client payment received",
            "amount": 5000.00,
            "account_name": "Accounts Receivable",
            "transaction_type": "credit",
            "reference": "REC-001"
        }
    ]


@router.get("/company/{company_id}")
async def get_company_ledger(
    company_id: str, current_user: dict = Depends(AuthService.verify_token)
):
    """
    Retrieve all ledger entries for a specified company.

    Parameters:
        company_id (str): The unique identifier of the company whose ledger entries are to be retrieved.

    Returns:
        list: A list of ledger entries associated with the given company, excluding MongoDB internal fields.
    """
    client = get_mongo_client()
    db = client.vanta_ledger
    collection = db.ledger_entries
    entries = list(collection.find({"company_id": company_id}, {"_id": 0}))
    return entries
