from pydantic import BaseModel
from datetime import datetime

class Transaction(BaseModel):
    id: int
    amount: float
    type: str  # 'sale' or 'expense'
    description: str
    date: datetime
