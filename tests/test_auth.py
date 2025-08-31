"""Tests for authentication endpoints."""

import pytest
from fastapi import status
from sqlalchemy.orm import Session

from src.vanta_ledger import crud, models, schemas
from src.vanta_ledger.utils.password import get_password_hash
from src.vanta_ledger.config import settings


def test_login_success(client, test_user):
    """Test successful login."""
    login_data = {
        "username": test_user.email,
        "password": "testpassword123",
    }
    response = client.post(
        "/api/v1/auth/token",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_invalid_username(client):
    """Test login with invalid username."""
    login_data = {
        "username": "nonexistent@example.com",
        "password": "wrongpassword",
    }
    response = client.post(
        "/api/v1/auth/token",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "detail" in response.json()
    assert "Incorrect username or password" in response.json()["detail"]


def test_login_invalid_password(client, test_user):
    """Test login with invalid password."""
    login_data = {
        "username": test_user.email,
        "password": "wrongpassword",
    }
    response = client.post(
        "/api/v1/auth/token",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "detail" in response.json()
    assert "Incorrect username or password" in response.json()["detail"]


def test_register_success(client, db_session):
    """Test successful user registration."""
    user_data = {
        "email": "newuser@example.com",
        "password": "SecurePass123!",
        "full_name": "New User",
    }

    # First, ensure registration is enabled
    settings.ENABLE_REGISTRATION = True

    response = client.post(
        "/api/v1/auth/register",
        json=user_data,
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
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
    assert db_user.is_active is True
    assert db_user.is_superuser is False


def test_register_duplicate_email(client, test_user):
    """Test registration with duplicate email."""
    user_data = {
        "email": test_user.email,  # Already exists
        "password": "SecurePass123!",
        "full_name": "Duplicate User",
    }

    settings.ENABLE_REGISTRATION = True

    response = client.post(
        "/api/v1/auth/register",
        json=user_data,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "detail" in response.json()
    assert "Email already registered" in response.json()["detail"]


def test_register_weak_password(client):
    """Test registration with weak password."""
    user_data = {
        "email": "weakpass@example.com",
        "password": "weak",  # Too short
        "full_name": "Weak Password User",
    }

    settings.ENABLE_REGISTRATION = True

    response = client.post(
        "/api/v1/auth/register",
        json=user_data,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "detail" in response.json()
    assert "Password must be at least" in response.json()["detail"][0]["msg"]


def test_register_disabled(client, settings):
    """Test registration when it's disabled."""
    settings.ENABLE_REGISTRATION = False

    user_data = {
        "email": "newuser@example.com",
        "password": "SecurePass123!",
        "full_name": "New User",
    }

    response = client.post(
        "/api/v1/auth/register",
        json=user_data,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "detail" in response.json()
    assert "Registration is disabled" in response.json()["detail"]


def test_get_current_user(client, auth_headers):
    """Test getting current user with valid token."""
    response = client.get(
        "/api/v1/users/me",
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "email" in data
    assert "full_name" in data
    assert "is_active" in data
    assert "is_superuser" in data
    assert "hashed_password" not in data


def test_get_current_user_unauthorized(client):
    """Test getting current user without authentication."""
    response = client.get("/api/v1/users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user_invalid_token(client):
    """Test getting current user with invalid token."""
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer invalidtoken"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
