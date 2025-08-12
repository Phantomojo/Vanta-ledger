"""Tests for database models."""

from datetime import datetime, timedelta

import pytest
from sqlalchemy.exc import IntegrityError

from src.vanta_ledger import models
from src.vanta_ledger.database import Base, get_db
from src.vanta_ledger.utils.password import get_password_hash


def test_user_model(db_session):
    """Test the User model."""
    # Create a test user
    user = models.User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        full_name="Test User",
        is_active=True,
        is_superuser=False,
    )

    # Add to database
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Test attributes
    assert user.email == "test@example.com"
    assert user.full_name == "Test User"
    assert user.is_active is True
    assert user.is_superuser is False
    assert isinstance(user.created_at, datetime)
    assert isinstance(user.updated_at, datetime)

    # Test password verification
    assert user.verify_password("testpassword") is True
    assert user.verify_password("wrongpassword") is False

    # Test string representation
    assert str(user) == f"<User {user.email}>"


def test_user_model_unique_email(db_session):
    """Test that email must be unique."""
    # Create first user
    user1 = models.User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        full_name="Test User 1",
    )
    db_session.add(user1)
    db_session.commit()

    # Try to create user with same email
    user2 = models.User(
        email="test@example.com",  # Same email
        hashed_password=get_password_hash("anotherpassword"),
        full_name="Test User 2",
    )
    db_session.add(user2)

    # Should raise integrity error
    with pytest.raises(IntegrityError):
        db_session.commit()

    # Rollback the failed transaction
    db_session.rollback()


def test_user_model_required_fields(db_session):
    """Test that required fields are enforced."""
    # Missing email
    with pytest.raises(IntegrityError):
        user = models.User(
            hashed_password=get_password_hash("testpassword"),
            full_name="Test User",
        )
        db_session.add(user)
        db_session.commit()

    db_session.rollback()

    # Missing password
    with pytest.raises(IntegrityError):
        user = models.User(
            email="test@example.com",
            full_name="Test User",
        )
        db_session.add(user)
        db_session.commit()

    db_session.rollback()


def test_user_model_default_values(db_session):
    """Test default values for User model."""
    user = models.User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
    )

    assert user.full_name is None
    assert user.is_active is True  # Default from model
    assert user.is_superuser is False  # Default from model
    assert user.created_at is not None
    assert user.updated_at is not None


def test_user_model_timestamps(db_session):
    """Test that created_at and updated_at timestamps work correctly."""
    # Create user
    user = models.User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
    )
    db_session.add(user)
    db_session.commit()

    created_at = user.created_at
    updated_at = user.updated_at

    # Update user
    user.full_name = "Updated Name"
    db_session.commit()
    db_session.refresh(user)

    # Created at should not change
    assert user.created_at == created_at
    # Updated at should be newer
    assert user.updated_at > updated_at


def test_user_model_deactivate(db_session):
    """Test deactivating a user."""
    user = models.User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()

    # Deactivate
    user.is_active = False
    db_session.commit()
    db_session.refresh(user)

    assert user.is_active is False


def test_user_model_superuser(db_session):
    """Test superuser flag."""
    user = models.User(
        email="admin@example.com",
        hashed_password=get_password_hash("adminpassword"),
        is_superuser=True,
    )
    db_session.add(user)
    db_session.commit()

    assert user.is_superuser is True
