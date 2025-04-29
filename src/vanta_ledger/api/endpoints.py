from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

# Define the data models
class Transaction(BaseModel):
    id: int
    description: str
    amount: float
    type: str  # 'sale' or 'expenditure'
    date: str

# Initialize the router
router = APIRouter()

# Sample data
transactions_db = []

# Route to get all transactions
@router.get("/transactions", response_model=List[Transaction])
def get_transactions():
    return transactions_db

# Route to create a new transaction
@router.post("/transactions", response_model=Transaction)
def create_transaction(transaction: Transaction):
    transactions_db.append(transaction)
    return transaction

# Route to update a transaction
@router.put("/transactions/{transaction_id}", response_model=Transaction)
def update_transaction(transaction_id: int, transaction: Transaction):
    for idx, trans in enumerate(transactions_db):
        if trans.id == transaction_id:
            transactions_db[idx] = transaction
            return transaction
    return {"message": "Transaction not found"}

# Route to delete a transaction
@router.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: int):
    global transactions_db
    transactions_db = [trans for trans in transactions_db if trans.id != transaction_id]
    return {"message": "Transaction deleted"}
