from pydantic import BaseModel
from enum import Enum
from datetime import date

class TransactionType(str, Enum):
    sale = "sale"
    expenditure = "expenditure"

class TransactionBase(BaseModel):
    description: str
    type: TransactionType
    amount: float
    date: date

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int

    class Config:
        orm_mode = True
