from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models
from ..schemas.ledger import LedgerCreate, LedgerRead
from sqlalchemy import func

router = APIRouter(prefix="/ledger", tags=["ledger"])

@router.get("/", response_model=List[LedgerRead])
def list_ledger_entries(db: Session = Depends(get_db)):
    """
    List all ledger entries in the system.
    Lets the family see every financial transaction for reporting and audits.
    """
    return db.query(models.LedgerEntry).all()

@router.get("/{entry_id}", response_model=LedgerRead)
def get_ledger_entry(entry_id: int, db: Session = Depends(get_db)):
    """
    Get details for a single ledger entry.
    Useful for reviewing or correcting financial records.
    """
    entry = db.query(models.LedgerEntry).get(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Ledger entry not found")
    return entry

@router.get("/project/{project_id}", response_model=List[LedgerRead])
def list_project_ledger(project_id: int, db: Session = Depends(get_db)):
    """
    List all ledger entries for a specific project.
    Lets the family track all money in/out for each project, for tendering and review.
    """
    return db.query(models.LedgerEntry).filter(models.LedgerEntry.project_id == project_id).all()

@router.get("/company/{company_id}", response_model=List[LedgerRead])
def list_company_ledger(company_id: int, db: Session = Depends(get_db)):
    """
    List all ledger entries for a specific company.
    Useful for company-wide financial summaries and audits.
    """
    return db.query(models.LedgerEntry).filter(models.LedgerEntry.company_id == company_id).all()

@router.post("/", response_model=LedgerRead)
def add_ledger_entry(entry: LedgerCreate, db: Session = Depends(get_db)):
    """
    Add a new ledger entry (income, expense, withdrawal).
    Lets the family record every transaction for accurate reporting and compliance.
    """
    db_entry = models.LedgerEntry(**entry.dict())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

@router.put("/{entry_id}", response_model=LedgerRead)
def update_ledger_entry(entry_id: int, entry: LedgerCreate, db: Session = Depends(get_db)):
    """
    Update an existing ledger entry.
    Keeps financial records accurate and up to date.
    """
    db_entry = db.query(models.LedgerEntry).get(entry_id)
    if not db_entry:
        raise HTTPException(status_code=404, detail="Ledger entry not found")
    for key, value in entry.dict().items():
        setattr(db_entry, key, value)
    db.commit()
    db.refresh(db_entry)
    return db_entry

@router.delete("/{entry_id}")
def delete_ledger_entry(entry_id: int, db: Session = Depends(get_db)):
    """
    Delete a ledger entry (if entered in error or no longer needed).
    Keeps the financial records clean and relevant.
    """
    db_entry = db.query(models.LedgerEntry).get(entry_id)
    if not db_entry:
        raise HTTPException(status_code=404, detail="Ledger entry not found")
    db.delete(db_entry)
    db.commit()
    return {"ok": True}

@router.get("/summary/{project_id}")
def project_ledger_summary(project_id: int, db: Session = Depends(get_db)):
    """
    Get a summary of income, expenses, and balance for a project.
    Lets the family quickly see project profitability for tenders and management.
    """
    income = db.query(func.sum(models.LedgerEntry.amount)).filter(models.LedgerEntry.project_id == project_id, models.LedgerEntry.type == 'income').scalar() or 0
    expenses = db.query(func.sum(models.LedgerEntry.amount)).filter(models.LedgerEntry.project_id == project_id, models.LedgerEntry.type == 'expense').scalar() or 0
    withdrawals = db.query(func.sum(models.LedgerEntry.amount)).filter(models.LedgerEntry.project_id == project_id, models.LedgerEntry.type == 'withdrawal').scalar() or 0
    balance = income - expenses - withdrawals
    return {
        "income": income,
        "expenses": expenses,
        "withdrawals": withdrawals,
        "balance": balance
    } 