from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey, Date, Boolean, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
import datetime
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://vanta_user:vanta_password@localhost/vanta_ledger")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Company(Base):
    """Companies in the family business group"""
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    registration_number = Column(String(100), unique=True)
    pin_number = Column(String(50))
    agpo_number = Column(String(50))
    phone = Column(String(20))
    email = Column(String(255))
    address = Column(Text)
    created_at = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    projects = relationship("Project", back_populates="company")
    documents = relationship("Document", back_populates="company")
    ledger_entries = relationship("LedgerEntry", back_populates="company")

class Project(Base):
    """Construction and tender projects"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    tender_number = Column(String(100))
    client_name = Column(String(255))
    contract_value = Column(Float)
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(String(50), default="active")  # active, completed, cancelled
    location = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="projects")
    documents = relationship("Document", back_populates="project")
    ledger_entries = relationship("LedgerEntry", back_populates="project")
    subcontractors = relationship("Subcontractor", back_populates="project")

class Document(Base):
    """Documents from Paperless-ngx and manual uploads"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    paperless_id = Column(Integer, unique=True)  # ID from Paperless-ngx
    company_id = Column(Integer, ForeignKey("companies.id"))
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    
    # Document metadata
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255))
    file_path = Column(String(512))
    file_size = Column(Integer)  # in bytes
    mime_type = Column(String(100))
    
    # Paperless-ngx data
    paperless_title = Column(String(255))
    paperless_correspondent = Column(String(255))
    paperless_tags = Column(JSON)  # Array of tags
    paperless_created = Column(DateTime)
    paperless_added = Column(DateTime)
    paperless_modified = Column(DateTime)
    
    # Document classification
    doc_type = Column(String(100))  # NCA Certificate, Tax Compliance, etc.
    doc_category = Column(String(100))  # statutory, financial, tender, contract
    expiry_date = Column(Date)
    
    # OCR and content
    ocr_text = Column(Text)
    ocr_confidence = Column(Float)
    
    # Business metadata
    amount = Column(Float)  # If document contains financial amounts
    currency = Column(String(10), default="KES")
    notes = Column(Text)
    
    # Audit fields
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    company = relationship("Company", back_populates="documents")
    project = relationship("Project", back_populates="documents")
    creator = relationship("User", back_populates="created_documents")

class LedgerEntry(Base):
    """Financial transactions and ledger entries"""
    __tablename__ = "ledger_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    
    # Transaction details
    date = Column(Date, nullable=False)
    description = Column(Text, nullable=False)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String(50), nullable=False)  # income, expense, withdrawal
    category = Column(String(100))  # materials, labor, equipment, etc.
    
    # Payment details
    payment_method = Column(String(50))
    reference_number = Column(String(100))
    bank_account = Column(String(100))
    
    # Audit fields
    created_at = Column(DateTime, default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    company = relationship("Company", back_populates="ledger_entries")
    project = relationship("Project", back_populates="ledger_entries")
    document = relationship("Document")
    creator = relationship("User", back_populates="created_entries")

class Subcontractor(Base):
    """Subcontractors and suppliers"""
    __tablename__ = "subcontractors"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    name = Column(String(255), nullable=False)
    contact_person = Column(String(255))
    phone = Column(String(20))
    email = Column(String(255))
    services = Column(Text)  # What they provide
    contract_value = Column(Float)
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="subcontractors")

class User(Base):
    """System users (family members and staff)"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="user")  # admin, user, viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    created_documents = relationship("Document", back_populates="creator")
    created_entries = relationship("LedgerEntry", back_populates="creator")

class DocumentAnalysis(Base):
    """Analysis and extracted data from documents"""
    __tablename__ = "document_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    
    # Extracted data
    extracted_amounts = Column(JSON)  # Array of amounts found
    extracted_dates = Column(JSON)  # Array of dates found
    extracted_companies = Column(JSON)  # Array of company names found
    extracted_addresses = Column(JSON)  # Array of addresses found
    
    # Analysis metadata
    analysis_date = Column(DateTime, default=func.now())
    confidence_score = Column(Float)
    analysis_method = Column(String(100))  # OCR, AI, manual
    
    # Relationships
    document = relationship("Document")

# Create all tables
def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

# Initialize database
if __name__ == "__main__":
    create_tables()
    print("Database tables created successfully!") 