import os

from fastapi import APIRouter, HTTPException, Depends, status, Body
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from vanta_ledger.db.session import get_db
from vanta_ledger.crud.transaction import create_transaction, get_transaction, get_transactions, update_transaction
from vanta_ledger.schemas.transaction import Transaction, TransactionCreate
from vanta_ledger.core.config import settings

router = APIRouter()

@router.post("/users/register", status_code=201)
async def register_user(username: str = Body(...), password: str = Body(...), db: AsyncSession = Depends(get_db)):
    # Registration without authentication
    from vanta_ledger.crud.user import create_user, get_user_by_username, UserRole
    existing_user = await get_user_by_username(db, username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    user = await create_user(db, username=username, password=password, role=UserRole.user)
    return {"username": user.username, "role": user.role.value}

@router.get("/ledger/summary")
async def get_ledger_summary(db: AsyncSession = Depends(get_db)):
    from vanta_ledger.services.finance import calculate_totals
    summary = await calculate_totals(db)
    return summary

@router.get("/transactions", response_model=List[Transaction])
async def get_transactions_endpoint(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    transactions = await get_transactions(db, skip=skip, limit=limit)
    return transactions

@router.get("/transactions/{transaction_id}", response_model=Transaction)
async def get_transaction_endpoint(transaction_id: int, db: AsyncSession = Depends(get_db)):
    transaction = await get_transaction(db, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@router.post("/transactions", response_model=Transaction)
async def create_transaction_endpoint(transaction: TransactionCreate, db: AsyncSession = Depends(get_db)):
    db_transaction = await create_transaction(db, amount=transaction.amount, type=transaction.type, description=transaction.description, date=transaction.date)
    return db_transaction

@router.put("/transactions/{transaction_id}", response_model=Transaction)
async def update_transaction_endpoint(transaction_id: int, transaction: TransactionCreate, db: AsyncSession = Depends(get_db)):
    updated_transaction = await update_transaction(db, transaction_id, amount=transaction.amount, type=transaction.type, description=transaction.description, date=transaction.date)
    if not updated_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return updated_transaction

@router.delete("/transactions/{transaction_id}")
async def delete_transaction_endpoint(transaction_id: int, db: AsyncSession = Depends(get_db)):
    db_transaction = await get_transaction(db, transaction_id)
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    await db.delete(db_transaction)
    await db.commit()
    return {"message": "Transaction deleted"}

@router.get("/settings")
async def get_settings():
    return {
        "currency": settings.LEDGER_DEFAULT_CURRENCY,
        "allowNegativeBalance": settings.LEDGER_ALLOW_NEGATIVE_BALANCE,
    }

@router.post("/settings")
async def update_settings(new_settings: dict):
    # For simplicity, settings are static in config; this is a placeholder for future persistence
    return {"message": "Settings update not implemented"}

import io
import csv
from fastapi.responses import StreamingResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import pandas as pd

@router.get("/export/csv")
async def export_transactions_csv(db: AsyncSession = Depends(get_db)):
    transactions = await get_transactions(db, skip=0, limit=1000)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Type", "Amount", "Description", "Date"])
    for tx in transactions:
        writer.writerow([tx.id, tx.type, tx.amount, tx.description, tx.date])
    output.seek(0)
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=transactions.csv"})

@router.get("/export/excel")
async def export_transactions_excel(db: AsyncSession = Depends(get_db)):
    transactions = await get_transactions(db, skip=0, limit=1000)
    data = [{
        "ID": tx.id,
        "Type": tx.type,
        "Amount": tx.amount,
        "Description": tx.description,
        "Date": tx.date
    } for tx in transactions]
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Transactions')
    output.seek(0)
    headers = {
        "Content-Disposition": "attachment; filename=transactions.xlsx"
    }
    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers=headers)

@router.get("/export/pdf")
async def export_transactions_pdf(db: AsyncSession = Depends(get_db)):
    transactions = await get_transactions(db, skip=0, limit=1000)
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 40
    p.setFont("Helvetica-Bold", 14)
    p.drawString(30, y, "Transactions Report")
    y -= 30
    p.setFont("Helvetica", 10)
    headers = ["ID", "Type", "Amount", "Description", "Date"]
    x_positions = [30, 80, 150, 220, 400]
    for i, header in enumerate(headers):
        p.drawString(x_positions[i], y, header)
    y -= 20
    for tx in transactions:
        if y < 40:
            p.showPage()
            y = height - 40
        p.drawString(x_positions[0], y, str(tx.id))
        p.drawString(x_positions[1], y, tx.type)
        p.drawString(x_positions[2], y, f"{tx.amount:.2f}")
        p.drawString(x_positions[3], y, tx.description or "")
        p.drawString(x_positions[4], y, tx.date.strftime("%Y-%m-%d"))
        y -= 15
    p.save()
    buffer.seek(0)
    headers = {
        "Content-Disposition": "attachment; filename=transactions.pdf"
    }
    return StreamingResponse(buffer, media_type="application/pdf", headers=headers)
