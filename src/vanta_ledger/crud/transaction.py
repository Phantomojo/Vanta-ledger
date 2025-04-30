from sqlalchemy.orm import Session
from vanta_ledger.models.transaction import Expenditure

# Function to create a new expenditure
def create_expenditure(db: Session, amount: float, type: str, description: str, date=None):
    db_expenditure = Expenditure(amount=amount, type=type, description=description)
    if date:
        db_expenditure.date = date
    db.add(db_expenditure)
    db.commit()
    db.refresh(db_expenditure)
    return db_expenditure

# Function to get an expenditure by ID
def get_expenditure(db: Session, expenditure_id: int):
    return db.query(Expenditure).filter(Expenditure.id == expenditure_id).first()

# Function to get all expenditures
def get_expenditures(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Expenditure).offset(skip).limit(limit).all()
