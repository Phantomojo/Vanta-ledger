"""Simplified pytest configuration for basic testing."""

import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the backend/src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent / "backend" / "src"))

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    from vanta_ledger.models.user_models import Base
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Drop all tables
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_user_data():
    """Sample user data for testing."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": "hashed_password_here",
        "first_name": "Test",
        "last_name": "User",
        "role": "user"
    }


@pytest.fixture(scope="function")
def test_company_data():
    """Sample company data for testing."""
    return {
        "name": "Test Company",
        "registration_number": "TEST123",
        "industry": "Technology",
        "company_type": "business_partner",
        "status": "active"
    }
