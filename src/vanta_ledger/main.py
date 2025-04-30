from fastapi import FastAPI, Depends, HTTPException
from pydantic import conint
from sqlalchemy.orm import Session
from vanta_ledger import crud, models, db
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

# Dependency to get the database session
def get_db():
    if not hasattr(db, 'database') or db.database is None:
        raise RuntimeError("Database is not properly initialized.")
    database = db.database
    try:
        if db.is_connected:
            db.disconnect()
    finally:
        db.disconnect()
from contextlib import asynccontextmanager
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to the database
    await db.database.connect()
    try:
        yield
    finally:
        # Disconnect from the database
        await db.database.disconnect()

class ExpenditureCreate(BaseModel):
    name: str
    amount: float
    description: str

@app.post(
    "/expenditures/",
    response_model=models.Expenditure,
    summary="Create a new expenditure",
    description="This endpoint allows you to create a new expenditure by providing its name, amount, and description."
)
async def create_expenditure(expenditure: ExpenditureCreate, db: Session = Depends(get_db)):
    return crud.create_expenditure(db=db, name=expenditure.name, amount=expenditure.amount, description=expenditure.description)
@app.get(
    "/expenditures/{expenditure_id}",
    response_model=models.Expenditure,
    summary="Retrieve an expenditure by ID",
    description="Fetch a specific expenditure from the database using its unique ID."
)
async def read_expenditure(expenditure_id: int, db: Session = Depends(get_db)):
    db_expenditure = crud.get_expenditure(db=db, expenditure_id=expenditure_id)
    if db_expenditure is None:
        raise HTTPException(status_code=404, detail="Expenditure not found")
    return db_expenditure

from fastapi import Query

@app.get(
    "/expenditures/",
    response_model=list[models.Expenditure],
    summary="Retrieve a list of expenditures",
    description="This endpoint retrieves a list of expenditures with optional pagination using skip and limit parameters."
)
async def read_expenditures(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1), db: Session = Depends(get_db)):
    expenditures = crud.get_expenditures(db=db, skip=skip, limit=limit)
    return expenditures

from fastapi import Query

# (Removed duplicate and incomplete function definitions)
