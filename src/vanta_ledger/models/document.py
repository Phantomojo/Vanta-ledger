from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Date
from sqlalchemy.orm import relationship
from . import Base
import datetime

class Document(Base):
    """
    Represents a document (e.g., letter, certificate, contract) for a project or company.
    - Each document is versioned, so the family can always find the latest (and past) versions for tenders, audits, or compliance.
    - Linked to a project and company for easy organization.
    - Stores file path for local storage, and metadata for search/filtering.
    """
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    version_number = Column(Integer, nullable=False, default=1)
    uploader_id = Column(Integer, ForeignKey('users.id'))
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)
    notes = Column(Text)
    doc_type = Column(String(100))  # e.g., 'NCA Certificate', 'Tax Compliance', etc.
    expiry_date = Column(Date)

    project = relationship('Project', backref='documents')
    company = relationship('Company', backref='documents')
    uploader = relationship('User', backref='uploaded_documents') 