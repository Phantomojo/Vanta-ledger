from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class ProjectBase(BaseModel):
    """
    Base schema for project data. Used for both creation and update.
    This ensures all key project info is captured for tendering and reporting.
    """
    name: str
    client: Optional[str] = None
    value: Optional[float] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    """
    Schema for creating a new project. All fields except name are optional.
    This lets the family quickly add new projects as soon as they start work or win a tender.
    """
    company_id: int

class CompanyInfo(BaseModel):
    """
    Minimal company info for project read responses.
    This helps heads see which company owns each project at a glance.
    """
    id: int
    name: str

    class Config:
        orm_mode = True

class ProjectRead(ProjectBase):
    """
    Schema for reading project data, including company info and timestamps.
    Used in project lists, detail views, and reports for tenders.
    """
    id: int
    company: CompanyInfo
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True 