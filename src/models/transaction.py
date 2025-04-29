# src/models/transaction.py
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Transaction:
    id: int
    type: str  # "sale" or "expense"
    amount: float
    description: str
    timestamp: datetime
    user: str
