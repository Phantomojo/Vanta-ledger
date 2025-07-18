from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class DocumentBase(BaseModel):
    """
    Base schema for document data. Used for both creation and update.
    Ensures all key document info is captured for compliance and tendering.
    """
    filename: str
    doc_type: Optional[str] = None
    notes: Optional[str] = None
    expiry_date: Optional[date] = None

class DocumentCreate(DocumentBase):
    """
    Schema for uploading a new document or version.
    Links the document to a project and company, and stores the file path.
    """
    project_id: Optional[int] = None
    company_id: Optional[int] = None
    file_path: str
    version_number: int = 1
    uploader_id: int

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

class DocumentRead(DocumentBase):
    """
    Schema for reading document data, including project, company, and version info.
    Used in document lists, detail views, and version history for tenders and audits.
    """
    id: int
    project: Optional[ProjectInfo] = None
    company: Optional[CompanyInfo] = None
    file_path: str
    version_number: int
    uploader_id: int
    uploaded_at: datetime

    class Config:
        orm_mode = True 