import os
from fastapi import APIRouter, HTTPException, Depends, Security, status
from fastapi.security.api_key import APIKeyHeader, APIKey
from fastapi.responses import JSONResponse
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from vanta_ledger.db.session import get_db
from vanta_ledger.crud.transaction import create_transaction, get_transaction, get_transactions
from vanta_ledger.schemas.transaction import Transaction, TransactionCreate
from vanta_ledger.core.config import settings

API_KEY_NAME = "access_token"
import os

API_KEY = os.getenv("VANTALEDGER_API_KEY", settings.API_KEY)

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(status_code=403, detail="Could not validate credentials")

router = APIRouter()

@router.post("/verify")
async def verify_token(api_key: APIKey = Depends(get_api_key)):
    return JSONResponse(content={"message": "Token is valid"}, status_code=status.HTTP_200_OK)

@router.get("/transactions", response_model=List[Transaction])
async def get_transactions_endpoint(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), api_key: APIKey = Depends(get_api_key)):
    transactions = await get_transactions(db, skip=skip, limit=limit)
    return transactions

@router.get("/transactions/{transaction_id}", response_model=Transaction)
async def get_transaction_endpoint(transaction_id: int, db: AsyncSession = Depends(get_db), api_key: APIKey = Depends(get_api_key)):
    transaction = await get_transaction(db, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@router.post("/transactions", response_model=Transaction)
async def create_transaction_endpoint(transaction: TransactionCreate, db: AsyncSession = Depends(get_db), api_key: APIKey = Depends(get_api_key)):
    db_transaction = await create_transaction(db, amount=transaction.amount, type=transaction.type, description=transaction.description, date=transaction.date)
    return db_transaction

@router.delete("/transactions/{transaction_id}")
async def delete_transaction_endpoint(transaction_id: int, db: AsyncSession = Depends(get_db), api_key: APIKey = Depends(get_api_key)):
    db_transaction = await get_transaction(db, transaction_id)
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    await db.delete(db_transaction)
    await db.commit()
    return {"message": "Transaction deleted"}

@router.put("/transactions/{transaction_id}", response_model=Transaction)
async def update_transaction_endpoint(transaction_id: int, transaction: TransactionCreate, db: AsyncSession = Depends(get_db), api_key: APIKey = Depends(get_api_key)):
    updated_transaction = await update_transaction(db, transaction_id, amount=transaction.amount, type=transaction.type, description=transaction.description, date=transaction.date)
    if not updated_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return updated_transaction

@router.get("/logs")
async def get_logs(api_key: APIKey = Depends(get_api_key)):
    logs = [
        "2025-05-05 10:00:00 INFO User logged in",
        "2025-05-05 10:05:00 INFO Transaction created",
        "2025-05-05 10:10:00 ERROR Failed to update transaction",
    ]
    return {"logs": logs}
