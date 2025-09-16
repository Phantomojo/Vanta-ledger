"""Test the database models."""

import pytest
from datetime import datetime
import uuid


def test_user_model_creation(db_session, test_user_data):
    """Test creating a user model."""
    from vanta_ledger.models.user_models import UserDB
    
    user = UserDB(**test_user_data)
    db_session.add(user)
    db_session.commit()
    
    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.role == "user"
    assert user.is_active is True


def test_company_model_creation(db_session, test_company_data):
    """Test creating a company model."""
    from vanta_ledger.models.company import Company
    
    company = Company(**test_company_data)
    db_session.add(company)
    db_session.commit()
    
    assert company.id is not None
    assert company.name == "Test Company"
    assert company.registration_number == "TEST123"
    assert company.status == "active"


def test_project_model_creation(db_session, test_company_data, test_user_data):
    """Test creating a project model."""
    from vanta_ledger.models.project_models import Project
    from vanta_ledger.models.company import Company
    from vanta_ledger.models.user_models import UserDB
    
    # Create company and user first
    company = Company(**test_company_data)
    user = UserDB(**test_user_data)
    db_session.add(company)
    db_session.add(user)
    db_session.commit()
    
    project_data = {
        "name": "Test Project",
        "description": "A test project",
        "project_code": "TEST001",
        "company_id": company.id,
        "created_by": user.id,
        "status": "active",
        "budget": 10000.0
    }
    
    project = Project(**project_data)
    db_session.add(project)
    db_session.commit()
    
    assert project.id is not None
    assert project.name == "Test Project"
    assert project.project_code == "TEST001"
    assert project.budget == 10000.0


def test_ledger_entry_model_creation(db_session, test_company_data, test_user_data):
    """Test creating a ledger entry model."""
    from vanta_ledger.models.project_models import LedgerEntry
    from vanta_ledger.models.company import Company
    from vanta_ledger.models.user_models import UserDB
    
    # Create company and user first
    company = Company(**test_company_data)
    user = UserDB(**test_user_data)
    db_session.add(company)
    db_session.add(user)
    db_session.commit()
    
    entry_data = {
        "entry_number": "ENT001",
        "description": "Test expense",
        "transaction_type": "expense",
        "amount": 100.0,
        "company_id": company.id,
        "created_by": user.id,
        "transaction_date": datetime.now()
    }
    
    entry = LedgerEntry(**entry_data)
    db_session.add(entry)
    db_session.commit()
    
    assert entry.id is not None
    assert entry.entry_number == "ENT001"
    assert entry.amount == 100.0
    assert entry.transaction_type == "expense"


def test_user_to_dict(db_session, test_user_data):
    """Test user to_dict method."""
    from vanta_ledger.models.user_models import UserDB
    
    user = UserDB(**test_user_data)
    db_session.add(user)
    db_session.commit()
    
    user_dict = user.to_dict()
    
    assert isinstance(user_dict, dict)
    assert user_dict["username"] == "testuser"
    assert user_dict["email"] == "test@example.com"
    assert "id" in user_dict
    assert "created_at" in user_dict


def test_company_to_dict(db_session, test_company_data):
    """Test company to_dict method."""
    from vanta_ledger.models.company import Company
    
    company = Company(**test_company_data)
    db_session.add(company)
    db_session.commit()
    
    company_dict = company.to_dict()
    
    assert isinstance(company_dict, dict)
    assert company_dict["name"] == "Test Company"
    assert company_dict["registration_number"] == "TEST123"
    assert "id" in company_dict
    assert "created_at" in company_dict