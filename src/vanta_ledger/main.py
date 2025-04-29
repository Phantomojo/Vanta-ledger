from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import crud, models, db
from fastapi.responses import JSONResponse

app = FastAPI()

# Dependency to get the database session
def get_db():
    db = db.database
    try:
        yield db
    finally:
        db.disconnect()

@app.on_event("startup")
async def startup():
    # Connect to the database
    await db.database.connect()

@app.on_event("shutdown")
async def shutdown():
    # Disconnect from the database
    await db.database.disconnect()

@app.post("/expenditures/", response_model=models.Expenditure)
async def create_expenditure(name: str, amount: float, description: str, db: Session = Depends(get_db)):
    return crud.create_expenditure(db=db, name=name, amount=amount, description=description)

@app.get("/expenditures/{expenditure_id}", response_model=models.Expenditure)
async def read_expenditure(expenditure_id: int, db: Session = Depends(get_db)):
    db_expenditure = crud.get_expenditure(db=db, expenditure_id=expenditure_id)
    if db_expenditure is None:
        raise HTTPException(status_code=404, detail="Expenditure not found")
    return db_expenditure

@app.get("/expenditures/", response_model=list[models.Expenditure])
async def read_expenditures(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    expenditures = crud.get_expenditures(db=db, skip=skip, limit=limit)
    return expenditures
