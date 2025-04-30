from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from enum import Enum
from datetime import date
from threading import Lock

# Define the data models
class TransactionType(str, Enum):
    SALE = "sale"
    EXPENDITURE = "expenditure"

class Transaction(BaseModel):
    id: int
    description: str
    type: TransactionType
    date: date

# Initialize the router
router = APIRouter()

# Thread-safe transactions storage
transactions_db = {}
transactions_lock = Lock()

# Route to get all transactions
@router.get("/transactions", response_model=List[Transaction])
def get_transactions():
    with transactions_lock:
        return list(transactions_db.values())

# Route to create a new transaction
@router.post("/transactions", response_model=Transaction)
def create_transaction(transaction: Transaction):
    with transactions_lock:
        new_id = max(transactions_db.keys(), default=0) + 1
        transaction_with_id = transaction.copy(update={"id": new_id})
        transactions_db[new_id] = transaction_with_id
        return transaction_with_id

# Route to update a transaction
@router.put("/transactions/{transaction_id}", response_model=Transaction)
def update_transaction(transaction_id: int, transaction: Transaction):
    with transactions_lock:
        if transaction_id in transactions_db:
            updated_transaction = transaction.copy(update={"id": transaction_id})
            transactions_db[transaction_id] = updated_transaction
            return updated_transaction
        raise HTTPException(status_code=404, detail="Transaction not found")

# Route to delete a transaction
@router.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: int):
    with transactions_lock:
        if transaction_id in transactions_db:
            del transactions_db[transaction_id]
            return {"detail": "Transaction deleted"}
        else:
            raise HTTPException(status_code=404, detail="Transaction not found")
