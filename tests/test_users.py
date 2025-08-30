"""Tests for user management endpoints."""

import pytest
from fastapi import status
from sqlalchemy.orm import Session

from src.vanta_ledger import models, schemas
from tests.conftest import override_get_db


def test_create_user(client, admin_auth_headers, db_session):
    """Test creating a new user as admin."""
    user_data = {
        "email": "newuser@example.com",
        "password": "SecurePass123!",
        "full_name": "New User",
        "is_active": True,
        "is_superuser": False,
    }

    response = client.post(
        "/api/v1/users/",
        json=user_data,
        headers=admin_auth_headers,
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert data["is_active"] == user_data["is_active"]
    assert data["is_superuser"] == user_data["is_superuser"]
    assert "id" in data
    assert "hashed_password" not in data

    # Verify user was created in the database
    db_user = (
        db_session.query(models.User)
        .filter(models.User.email == user_data["email"])
        .first()
    )
    assert db_user is not None
    assert db_user.email == user_data["email"]
    assert db_user.full_name == user_data["full_name"]
    assert db_user.is_active == user_data["is_active"]
    assert db_user.is_superuser == user_data["is_superuser"]


def test_create_user_unauthorized(client, auth_headers):
    """Test creating a user without admin privileges."""
    user_data = {
        "email": "newuser@example.com",
        "password": "SecurePass123!",
        "full_name": "New User",
        "is_active": True,
    }

    response = client.post(
        "/api/v1/users/",
        json=user_data,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_read_users(client, admin_auth_headers, test_user, test_superuser):
    """Test reading users as admin."""
    response = client.get(
        "/api/v1/users/",
        headers=admin_auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2  # At least the test user and superuser

    # Check that passwords are not included
    for user in data:
        assert "hashed_password" not in user

    # Check that both test users are in the response
    emails = {user["email"] for user in data}
    assert test_user.email in emails
    assert test_superuser.email in emails


def test_read_users_unauthorized(client, auth_headers):
    """Test reading users without admin privileges."""
    response = client.get(
        "/api/v1/users/",
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_read_user_me(client, auth_headers, test_user):
    """Test reading the current user's profile."""
    response = client.get(
        "/api/v1/users/me",
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == test_user.email
    assert data["full_name"] == test_user.full_name
    assert "hashed_password" not in data


def test_read_user_by_id(client, admin_auth_headers, test_user):
    """Test reading a user by ID as admin."""
    response = client.get(
        f"/api/v1/users/{test_user.id}",
        headers=admin_auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_user.id
    assert data["email"] == test_user.email
    assert "hashed_password" not in data


def test_read_user_by_id_unauthorized(client, auth_headers, test_user):
    """Test reading another user's profile without admin privileges."""
    # First, create another test user
    other_user = models.User(
        email="other@example.com",
        hashed_password="hashed_password",
        full_name="Other User",
    )
    db = next(override_get_db())
    db.add(other_user)
    db.commit()
    db.refresh(other_user)

    # Try to access the other user's profile
    response = client.get(
        f"/api/v1/users/{other_user.id}",
        headers=auth_headers,
    )

    # Should be forbidden (can only access own profile)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_user_me(client, auth_headers, test_user):
    """Test updating the current user's profile."""
    update_data = {
        "full_name": "Updated Name",
        "email": "updated@example.com",
    }

    response = client.put(
        "/api/v1/users/me",
        json=update_data,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == update_data["email"]
    assert data["full_name"] == update_data["full_name"]

    # Verify the user was updated in the database
    db = next(override_get_db())
    db_user = db.query(models.User).filter(models.User.id == test_user.id).first()
    assert db_user.email == update_data["email"]
    assert db_user.full_name == update_data["full_name"]


def test_update_user_password(client, auth_headers, test_user):
    """Test updating the current user's password."""
    update_data = {
        "current_password": "testpassword123",
        "new_password": "NewSecurePass123!",
    }

    response = client.put(
        "/api/v1/users/me/password",
        json=update_data,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK

    # Verify the password was updated by trying to log in with the new password
    login_data = {
        "username": test_user.email,
        "password": update_data["new_password"],
    }
    login_response = client.post(
        "/api/v1/auth/token",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login_response.status_code == status.HTTP_200_OK


def test_delete_user_me(client, auth_headers, test_user):
    """Test deleting the current user's account."""
    response = client.delete(
        "/api/v1/users/me",
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify the user was deactivated in the database
    db = next(override_get_db())
    db_user = db.query(models.User).filter(models.User.id == test_user.id).first()
    assert db_user.is_active is False
