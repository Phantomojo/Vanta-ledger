from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

from ..auth import AuthService
from ..database import get_mongo_client

router = APIRouter(prefix="/ledger", tags=["Ledger"])


@router.get("/")
async def get_ledger_entries(
    company_id: str = Query(..., description="Company ID to filter ledger entries"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of entries to return"),
    current_user: dict = Depends(AuthService.verify_token)
):
    """
    Retrieve ledger entries from the database for authenticated users.

    Parameters:
        company_id (str): The company ID to filter entries by
        limit (int): Maximum number of entries to return (1-100)

    Returns:
        A list of ledger entry documents for the specified company.
    """
    client = get_mongo_client()
    db = client.vanta_ledger
    collection = db.ledger_entries
    
    # Get entries for the specified company, sorted by transaction date
    entries = list(
        collection.find(
            {"company_id": company_id}, 
            {"_id": 0}
        ).sort("transaction_date", -1).limit(limit)
    )
    
    return entries


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
