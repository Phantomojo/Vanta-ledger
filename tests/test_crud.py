"""Tests for CRUD operations."""

import pytest
from sqlalchemy.orm import Session

from src.vanta_ledger import crud, models, schemas
from src.vanta_ledger.utils.password import get_password_hash


def test_get_user(db_session: Session):
    """Test retrieving a user by ID."""
    # Create a test user
    user = models.User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        full_name="Test User",
    )
    db_session.add(user)
    db_session.commit()

    # Retrieve the user
    db_user = crud.user.get(db=db_session, id=user.id)
    assert db_user is not None
    assert db_user.email == "test@example.com"
    assert db_user.full_name == "Test User"
    assert db_user.is_active is True
    assert db_user.is_superuser is False


def test_get_user_by_email(db_session: Session):
    """Test retrieving a user by email."""
    # Create a test user
    user = models.User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
    )
    db_session.add(user)
    db_session.commit()

    # Retrieve the user by email
    db_user = crud.user.get_by_email(db=db_session, email="test@example.com")
    assert db_user is not None
    assert db_user.email == "test@example.com"


def test_get_nonexistent_user(db_session: Session):
    """Test retrieving a user that doesn't exist."""
    db_user = crud.user.get(db=db_session, id=999)
    assert db_user is None

    db_user = crud.user.get_by_email(db=db_session, email="nonexistent@example.com")
    assert db_user is None


def test_get_users(db_session: Session):
    """Test retrieving multiple users."""
    # Create test users
    user1 = models.User(
        email="user1@example.com",
        hashed_password=get_password_hash("password1"),
    )
    user2 = models.User(
        email="user2@example.com",
        hashed_password=get_password_hash("password2"),
    )
    db_session.add_all([user1, user2])
    db_session.commit()

    # Get all users
    users = crud.user.get_multi(db=db_session)
    assert len(users) >= 2
    assert any(u.email == "user1@example.com" for u in users)
    assert any(u.email == "user2@example.com" for u in users)


def test_create_user(db_session: Session):
    """Test creating a new user."""
    user_in = schemas.UserCreate(
        email="new@example.com",
        password="securepassword123",
        full_name="New User",
    )
    user = crud.user.create(db=db_session, obj_in=user_in)

    assert user.email == "new@example.com"
    assert user.full_name == "New User"
    assert hasattr(user, "hashed_password")
    assert user.is_active is True
    assert user.is_superuser is False

    # Verify password was hashed
    assert user.verify_password("securepassword123") is True
    assert user.verify_password("wrongpassword") is False


def test_create_superuser(db_session: Session):
    """Test creating a superuser."""
    user_in = schemas.UserCreate(
        email="admin@example.com",
        password="adminpassword123",
        full_name="Admin User",
    )
    user = crud.user.create(db=db_session, obj_in=user_in, is_superuser=True)

    assert user.email == "admin@example.com"
    assert user.is_superuser is True


def test_update_user(db_session: Session):
    """Test updating a user."""
    # Create a test user
    user = models.User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        full_name="Original Name",
    )
    db_session.add(user)
    db_session.commit()

    # Update the user
    user_update = schemas.UserUpdate(
        full_name="Updated Name",
        email="updated@example.com",
    )
    updated_user = crud.user.update(db=db_session, db_obj=user, obj_in=user_update)

    assert updated_user.full_name == "Updated Name"
    assert updated_user.email == "updated@example.com"
    assert updated_user.updated_at > user.updated_at


def test_update_user_password(db_session: Session):
    """Test updating a user's password."""
    # Create a test user
    user = models.User(
        email="test@example.com",
        hashed_password=get_password_hash("oldpassword"),
    )
    db_session.add(user)
    db_session.commit()

    # Update the password
    user_update = schemas.UserUpdate(password="newsecurepassword123")
    updated_user = crud.user.update(db=db_session, db_obj=user, obj_in=user_update)

    # Verify the password was updated
    assert updated_user.verify_password("newsecurepassword123") is True
    assert updated_user.verify_password("oldpassword") is False


def test_authenticate_user(db_session: Session):
    """Test user authentication."""
    # Create a test user
    user = models.User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
    )
    db_session.add(user)
    db_session.commit()

    # Test successful authentication
    authenticated_user = crud.user.authenticate(
        db=db_session, email="test@example.com", password="testpassword"
    )
    assert authenticated_user is not None
    assert authenticated_user.email == "test@example.com"

    # Test wrong password
    failed_auth = crud.user.authenticate(
        db=db_session, email="test@example.com", password="wrongpassword"
    )
    assert failed_auth is False

    # Test non-existent user
    non_existent = crud.user.authenticate(
        db=db_session, email="nonexistent@example.com", password="doesntmatter"
    )
    assert non_existent is False

    # Test inactive user
    user.is_active = False
    db_session.commit()

    inactive_auth = crud.user.authenticate(
        db=db_session, email="test@example.com", password="testpassword"
    )
    assert inactive_auth is False


def test_remove_user(db_session: Session):
    """Test removing a user."""
    # Create a test user
    user = models.User(
        email="delete@example.com",
        hashed_password=get_password_hash("testpassword"),
    )
    db_session.add(user)
    db_session.commit()

    # Remove the user
    crud.user.remove(db=db_session, id=user.id)

    # Verify the user was deleted
    deleted_user = crud.user.get(db=db_session, id=user.id)
    assert deleted_user is None
