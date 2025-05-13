import os
from fastapi import APIRouter, HTTPException, Depends, Security, status, Body
from fastapi.security.api_key import APIKeyHeader, APIKey
from fastapi.responses import JSONResponse
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from vanta_ledger.db.session import get_db
from vanta_ledger.crud.transaction import create_transaction, get_transaction, get_transactions, update_transaction
from vanta_ledger.schemas.transaction import Transaction, TransactionCreate
from vanta_ledger.core.config import settings
from vanta_ledger.models.user import UserRole
from vanta_ledger.crud.user import create_user, authenticate_user, get_user_by_username
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security.oauth2 import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta

API_KEY_NAME = "access_token"
import os

API_KEY = os.getenv("API_KEY", "supersecretadmintoken")

SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

router = APIRouter()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user=Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    # Deprecated: keep for backward compatibility with API_KEY
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(status_code=403, detail="Could not validate credentials")

@router.post("/verify")
async def verify_token(api_key: APIKey = Depends(get_api_key)):
    return JSONResponse(content={"message": "Token is valid"}, status_code=status.HTTP_200_OK)

@router.post("/users/register", status_code=201)
async def register_user(username: str = Body(...), password: str = Body(...), db: AsyncSession = Depends(get_db)):
    existing_user = await get_user_by_username(db, username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    user = await create_user(db, username=username, password=password, role=UserRole.user)
    return {"username": user.username, "role": user.role.value}

@router.post("/users/login")
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=dict)
async def read_users_me(current_user=Depends(get_current_active_user)):
    return {"username": current_user.username, "role": current_user.role.value, "is_active": current_user.is_active}

@router.get("/ledger/summary")
async def get_ledger_summary(db: AsyncSession = Depends(get_db), api_key: APIKey = Depends(get_api_key)):
    from vanta_ledger.services.finance import calculate_totals
    summary = await calculate_totals(db)
    return summary

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

@router.put("/transactions/{transaction_id}", response_model=Transaction)
async def update_transaction_endpoint(transaction_id: int, transaction: TransactionCreate, db: AsyncSession = Depends(get_db), api_key: APIKey = Depends(get_api_key)):
    updated_transaction = await update_transaction(db, transaction_id, amount=transaction.amount, type=transaction.type, description=transaction.description, date=transaction.date)
    if not updated_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return updated_transaction

@router.delete("/transactions/{transaction_id}")
async def delete_transaction_endpoint(transaction_id: int, db: AsyncSession = Depends(get_db), api_key: APIKey = Depends(get_api_key)):
    db_transaction = await get_transaction(db, transaction_id)
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    await db.delete(db_transaction)
    await db.commit()
    return {"message": "Transaction deleted"}

@router.get("/settings")
async def get_settings(api_key: APIKey = Depends(get_api_key)):
    from vanta_ledger.core.config import settings
    return {
        "currency": settings.LEDGER_DEFAULT_CURRENCY,
        "allowNegativeBalance": settings.LEDGER_ALLOW_NEGATIVE_BALANCE,
    }

@router.post("/settings")
async def update_settings(new_settings: dict, api_key: APIKey = Depends(get_api_key)):
    # For simplicity, settings are static in config; this is a placeholder for future persistence
    return {"message": "Settings update not implemented"}

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

import io
import csv
from fastapi.responses import StreamingResponse
from fastapi import Response
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import pandas as pd

@router.get("/export/csv")
async def export_transactions_csv(api_key: APIKey = Depends(get_api_key), db: AsyncSession = Depends(get_db)):
    transactions = await get_transactions(db, skip=0, limit=1000)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Type", "Amount", "Description", "Date"])
    for tx in transactions:
        writer.writerow([tx.id, tx.type, tx.amount, tx.description, tx.date])
    output.seek(0)
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=transactions.csv"})

@router.get("/export/excel")
async def export_transactions_excel(api_key: APIKey = Depends(get_api_key), db: AsyncSession = Depends(get_db)):
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
async def export_transactions_pdf(api_key: APIKey = Depends(get_api_key), db: AsyncSession = Depends(get_db)):
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
