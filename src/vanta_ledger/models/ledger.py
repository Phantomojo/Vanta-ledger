from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from . import Base
import datetime

class LedgerEntry(Base):
    """
    Represents a financial transaction (income, expense, or owner withdrawal) for a project or company.
    - Lets the family track all money in/out for each project and company.
    - Used for financial summaries, audits, and tender reporting.
    """
    __tablename__ = 'ledger_entries'
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'))
    type = Column(String(50), nullable=False)  # income/expense/withdrawal
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    uploaded_by = Column(Integer, ForeignKey('users.id'))

    company = relationship('Company', backref='ledger_entries')
    project = relationship('Project', backref='ledger_entries')
    uploader = relationship('User', backref='ledger_entries_uploaded') 