from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey, Date
from sqlalchemy.orm import relationship
from . import Base
import datetime

class Project(Base):
    """
    Represents a project undertaken by a company.
    Each project is linked to a company and stores key info needed for tenders:
    - Name, client, value, dates, status, description.
    - This helps the family quickly find and present past/current projects when applying for new tenders.
    """
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    name = Column(String(255), nullable=False)
    client = Column(String(255))
    value = Column(Float)
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(String(50))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    company = relationship('Company', back_populates='projects')

# Add the reverse relationship in Company
from .company import Company
Company.projects = relationship('Project', order_by=Project.id, back_populates='company') 