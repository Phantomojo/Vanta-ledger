"""Pytest configuration and fixtures for testing Vanta Ledger."""

import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from src.vanta_ledger.auth import get_password_hash
from src.vanta_ledger.config import settings
from src.vanta_ledger.database_init import DatabaseInitializer
from src.vanta_ledger.main import app
from src.vanta_ledger.models import user_models
from src.vanta_ledger.models.user_models import Base

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override the get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Create a mock get_db function for testing
def get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def client() -> Generator:
    """
    Create a test client that can be used to interact with the application.
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create a test client
    with TestClient(app) as test_client:
        yield test_client

    # Clean up
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Generator:
    """
    Create a new database session with a rollback at the end of the test.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def test_user(db_session) -> user_models.UserDB:
    """
    Create a test user.
    """
    import uuid
    from datetime import datetime

    user_data = {
        "id": str(uuid.uuid4()),
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": get_password_hash("testpassword123"),
        "is_active": True,
        "role": "user",
        "created_at": datetime.utcnow(),
    }
    user = user_models.UserDB(**user_data)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_superuser(db_session) -> user_models.UserDB:
    """
    Create a test superuser.
    """
    import uuid
    from datetime import datetime

    user_data = {
        "id": str(uuid.uuid4()),
        "username": "admin",
        "email": "admin@example.com",
        "hashed_password": get_password_hash("adminpassword123"),
        "is_active": True,
        "role": "admin",
        "created_at": datetime.utcnow(),
    }
    user = user_models.UserDB(**user_data)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_headers(client, test_user) -> Dict[str, str]:
    """
    Get authentication headers for the test user.
    """
    login_data = {
        "username": test_user.username,
        "password": "testpassword123",
    }
    response = client.post(
        "/auth/token",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def admin_auth_headers(client, test_superuser) -> Dict[str, str]:
    """
    Get authentication headers for the admin user.
    """
    login_data = {
        "username": test_superuser.username,
        "password": "adminpassword123",
    }
    response = client.post(
        "/auth/token",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def pytest_configure(config):
    """Configure pytest for the test suite."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m "not slow"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
