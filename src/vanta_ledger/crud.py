from sqlalchemy.orm import Session
from .models.transaction import Expenditure
from sqlalchemy.future import select

# Function to create a new expenditure
def create_expenditure(db: Session, name: str, amount: float, description: str):
    db_expenditure = Expenditure(name=name, amount=amount, description=description)
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
