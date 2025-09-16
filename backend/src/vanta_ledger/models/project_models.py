#!/usr/bin/env python3
"""
Project and Ledger Models for Vanta Ledger
Defines SQLAlchemy models for project management and ledger entries
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from datetime import datetime

# Import Base from user_models to ensure all models use the same Base
from .user_models import Base


class Project(Base):
    """Project model for managing business projects"""
    
    __tablename__ = "projects"
    
    # Primary key and basic info
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    project_code = Column(String(50), unique=True, nullable=False, index=True)
    
    # Project details
    status = Column(String(50), default="active")  # active, completed, cancelled, on_hold
    priority = Column(String(20), default="medium")  # low, medium, high, critical
    project_type = Column(String(50))  # internal, client, research, maintenance
    
    # Relationships
    company_id = Column(String(36), ForeignKey('companies.id'), nullable=False)
    created_by = Column(String(36), ForeignKey('users.id'), nullable=False)
    assigned_to = Column(String(36), ForeignKey('users.id'))
    
    # Financial information
    budget = Column(Float, default=0.0)
    actual_cost = Column(Float, default=0.0)
    currency = Column(String(3), default="USD")
    
    # Timestamps
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Additional fields
    notes = Column(Text)
    tags = Column(Text)  # JSON string for project tags
    extra_data = Column(Text)  # JSON string for additional project data
    
    def __repr__(self):
        return f"<Project(id='{self.id}', name='{self.name}', status='{self.status}')>"
    
    def to_dict(self):
        """Convert project to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'project_code': self.project_code,
            'status': self.status,
            'priority': self.priority,
            'project_type': self.project_type,
            'company_id': self.company_id,
            'created_by': self.created_by,
            'assigned_to': self.assigned_to,
            'budget': self.budget,
            'actual_cost': self.actual_cost,
            'currency': self.currency,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'notes': self.notes,
            'tags': self.tags,
            'extra_data': self.extra_data
        }


class LedgerEntry(Base):
    """Ledger entry model for financial transactions"""
    
    __tablename__ = "ledger_entries"
    
    # Primary key and basic info
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entry_number = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)
    
    # Transaction details
    transaction_type = Column(String(50), nullable=False)  # income, expense, transfer, adjustment
    category = Column(String(100))  # office_supplies, travel, software, etc.
    subcategory = Column(String(100))
    
    # Financial information
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    exchange_rate = Column(Float, default=1.0)
    base_amount = Column(Float)  # Amount in base currency
    
    # Relationships
    company_id = Column(String(36), ForeignKey('companies.id'), nullable=False)
    project_id = Column(String(36), ForeignKey('projects.id'))
    created_by = Column(String(36), ForeignKey('users.id'), nullable=False)
    
    # Transaction details
    transaction_date = Column(DateTime(timezone=True), nullable=False)
    due_date = Column(DateTime(timezone=True))
    payment_method = Column(String(50))  # cash, bank_transfer, credit_card, check
    reference_number = Column(String(100))
    
    # Status and approval
    status = Column(String(50), default="pending")  # pending, approved, rejected, paid
    is_recurring = Column(Boolean, default=False)
    recurring_frequency = Column(String(20))  # daily, weekly, monthly, yearly
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    approved_at = Column(DateTime(timezone=True))
    paid_at = Column(DateTime(timezone=True))
    
    # Additional fields
    notes = Column(Text)
    attachments = Column(Text)  # JSON string for file attachments
    tags = Column(Text)  # JSON string for entry tags
    extra_data = Column(Text)  # JSON string for additional entry data
    
    def __repr__(self):
        return f"<LedgerEntry(id='{self.id}', entry_number='{self.entry_number}', amount='{self.amount}')>"
    
    def to_dict(self):
        """Convert ledger entry to dictionary"""
        return {
            'id': self.id,
            'entry_number': self.entry_number,
            'description': self.description,
            'transaction_type': self.transaction_type,
            'category': self.category,
            'subcategory': self.subcategory,
            'amount': self.amount,
            'currency': self.currency,
            'exchange_rate': self.exchange_rate,
            'base_amount': self.base_amount,
            'company_id': self.company_id,
            'project_id': self.project_id,
            'created_by': self.created_by,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'payment_method': self.payment_method,
            'reference_number': self.reference_number,
            'status': self.status,
            'is_recurring': self.is_recurring,
            'recurring_frequency': self.recurring_frequency,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None,
            'notes': self.notes,
            'attachments': self.attachments,
            'tags': self.tags,
            'extra_data': self.extra_data
        }
