from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..auth import AuthService
from ..database import get_mongo_client

router = APIRouter(prefix='/ledger', tags=['Ledger'])

@router.get('/')
async def get_ledger_entries(current_user: dict = Depends(AuthService.verify_token)):
    client = get_mongo_client()
    db = client.vanta_ledger
    collection = db.ledger_entries
    entries = list(collection.find({}, {'_id': 0}).limit(50))
    return entries

@router.get('/company/{company_id}')
async def get_company_ledger(company_id: str, current_user: dict = Depends(AuthService.verify_token)):
    client = get_mongo_client()
    db = client.vanta_ledger
    collection = db.ledger_entries
    entries = list(collection.find({'company_id': company_id}, {'_id': 0}))
    return entries
