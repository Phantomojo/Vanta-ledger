from sqlalchemy.orm import Session
from vanta_ledger.models.transaction import Transaction

# Function to create a new transaction
def create_transaction(db: Session, amount: float, type: str, description: str, date=None):
    db_transaction = Transaction(amount=amount, type=type, description=description)
    if date:
        db_transaction.date = date
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

# Function to get a transaction by ID
def get_transaction(db: Session, transaction_id: int):
    return db.query(Transaction).filter(Transaction.id == transaction_id).first()

# Function to get all transactions
def get_transactions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Transaction).offset(skip).limit(limit).all()
