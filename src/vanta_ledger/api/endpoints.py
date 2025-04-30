from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi.security.api_key import APIKeyHeader, APIKey
from pydantic import BaseModel
from typing import List
from enum import Enum
from datetime import date
from sqlalchemy.orm import Session
from vanta_ledger.db.session import get_db
from vanta_ledger.crud.transaction import create_expenditure, get_expenditure, get_expenditures
from vanta_ledger.models.transaction import Expenditure

API_KEY_NAME = "access_token"
API_KEY = "supersecretadmintoken"  # This should be stored securely in env variables

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(status_code=403, detail="Could not validate credentials")

# Define the data models
class TransactionType(str, Enum):
    sale = "sale"
    expenditure = "expenditure"

class TransactionBase(BaseModel):
    description: str
    type: TransactionType
    amount: float
    date: date

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int

    class Config:
        orm_mode = True

# Initialize the router
router = APIRouter()

# Route to get all transactions
@router.get("/transactions", response_model=List[Transaction])
def get_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), api_key: APIKey = Depends(get_api_key)):
    expenditures = get_expenditures(db, skip=skip, limit=limit)
    return expenditures

# Route to create a new transaction
@router.post("/transactions", response_model=Transaction)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db), api_key: APIKey = Depends(get_api_key)):
    db_transaction = create_expenditure(db, amount=transaction.amount, type=transaction.type, description=transaction.description, date=transaction.date)
    return db_transaction

# Route to update a transaction
@router.put("/transactions/{transaction_id}", response_model=Transaction)
def update_transaction(transaction_id: int, transaction: TransactionUpdate, db: Session = Depends(get_db), api_key: APIKey = Depends(get_api_key)):
    db_transaction = get_expenditure(db, transaction_id)
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db_transaction.amount = transaction.amount
    db_transaction.type = transaction.type
    db_transaction.description = transaction.description
    db_transaction.date = transaction.date
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

# Route to delete a transaction
@router.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: int, db: Session = Depends(get_db), api_key: APIKey = Depends(get_api_key)):
    db_transaction = get_expenditure(db, transaction_id)
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(db_transaction)
    db.commit()
    return {"detail": "Transaction deleted"}
