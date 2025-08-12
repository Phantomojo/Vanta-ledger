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
        A list of ledger entry documents, excluding the MongoDB internal `_id` field.
    """
    client = get_mongo_client()
    db = client.vanta_ledger
    collection = db.ledger_entries
    entries = list(collection.find({}, {"_id": 0}).limit(50))
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
