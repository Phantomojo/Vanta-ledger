from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class LedgerBase(BaseModel):
    """
    Base schema for ledger entry data. Used for both creation and update.
    Ensures all key financial info is captured for tracking and reporting.
    """
    type: str  # income, expense, withdrawal
    amount: float
    date: date
    description: Optional[str] = None

class ProjectInfo(BaseModel):
    id: int
    name: str
    class Config:
        orm_mode = True

class CompanyInfo(BaseModel):
    id: int
    name: str
    class Config:
        orm_mode = True

class LedgerRead(LedgerBase):
    """
    Schema for reading ledger entry data, including project, company, and user info.
    Used in financial summaries, dashboards, and reports for tenders.
    """
    id: int
    company: CompanyInfo
    project: Optional[ProjectInfo] = None
    created_at: datetime
    uploaded_by: int

    class Config:
        orm_mode = True 