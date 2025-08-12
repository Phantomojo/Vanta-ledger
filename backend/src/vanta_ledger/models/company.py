#!/usr/bin/env python3
"""
Enhanced Company Models for Vanta Ledger
Defines comprehensive company data models matching the remote repository schema
"""

from sqlalchemy import Column, String, DateTime, Text, Float
from sqlalchemy.sql import func
import uuid
import json

# Import Base from user_models to ensure all models use the same Base
from .user_models import Base

class Company(Base):
    """Enhanced company model matching remote repository schema"""
    
    __tablename__ = "companies"
    
    # Primary key and basic info
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, unique=True)
    registration_number = Column(String(100), unique=True, nullable=False)
    
    # Core company information
    industry = Column(String(100))
    company_type = Column(String(50), default="business_partner")  # core_family, business_partner, subsidiary
    status = Column(String(50), default="active")
    
    # Flexible data storage using JSONB-like approach (SQLite compatible)
    address = Column(Text)  # JSON string for address data
    contact_info = Column(Text)  # JSON string for contact information
    tax_info = Column(Text)  # JSON string for tax information
    
    # Network analysis capabilities
    network_centrality_score = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Company(name='{self.name}', registration_number='{self.registration_number}', type='{self.company_type}')>"
    
    def get_address(self) -> dict:
        """Get address as dictionary"""
        try:
            return json.loads(self.address) if self.address else {}
        except (json.JSONDecodeError, TypeError):
            return {}
    
    def set_address(self, address_data: dict):
        """Set address from dictionary"""
        self.address = json.dumps(address_data) if address_data else None
    
    def get_contact_info(self) -> dict:
        """Get contact info as dictionary"""
        try:
            return json.loads(self.contact_info) if self.contact_info else {}
        except (json.JSONDecodeError, TypeError):
            return {}
    
    def set_contact_info(self, contact_data: dict):
        """Set contact info from dictionary"""
        self.contact_info = json.dumps(contact_data) if contact_data else None
    
    def get_tax_info(self) -> dict:
        """Get tax info as dictionary"""
        try:
            return json.loads(self.tax_info) if self.tax_info else {}
        except (json.JSONDecodeError, TypeError):
            return {}
    
    def set_tax_info(self, tax_data: dict):
        """Set tax info from dictionary"""
        self.tax_info = json.dumps(tax_data) if tax_data else None
    
    def to_dict(self):
        """Convert company to dictionary with parsed JSON fields"""
        return {
            "id": self.id,
            "name": self.name,
            "registration_number": self.registration_number,
            "industry": self.industry,
            "company_type": self.company_type,
            "status": self.status,
            "address": self.get_address(),
            "contact_info": self.get_contact_info(),
            "tax_info": self.get_tax_info(),
            "network_centrality_score": self.network_centrality_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_simple_dict(self):
        """Convert to simple dictionary for basic operations"""
        return {
            "id": self.id,
            "name": self.name,
            "registration_number": self.registration_number,
            "industry": self.industry,
            "company_type": self.company_type,
            "status": self.status
        }
