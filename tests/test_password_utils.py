"""Tests for password utilities."""

import pytest

from src.vanta_ledger.utils.password import (
    PasswordError,
    generate_secure_password,
    get_password_hash,
    validate_password_strength,
    verify_password,
)


def test_validate_password_strength_success():
    """Test password strength validation with a strong password."""
    password = "SecurePass123!@#"
    is_valid, message = validate_password_strength(password)
    assert is_valid is True
    assert message == ""


def test_validate_password_strength_too_short():
    """Test password strength validation with a too short password."""
    password = "Short1!"
    is_valid, message = validate_password_strength(password)
    assert is_valid is False
    assert "at least 12 characters" in message


def test_validate_password_strength_missing_uppercase():
    """Test password strength validation with missing uppercase."""
    password = "lowercase123!"
    is_valid, message = validate_password_strength(password)
    assert is_valid is False
    assert "uppercase" in message.lower()


def test_validate_password_strength_missing_number():
    """Test password strength validation with missing number."""
    password = "NoNumber!@#"
    is_valid, message = validate_password_strength(password)
    assert is_valid is False
    assert "number" in message.lower()


def test_validate_password_strength_missing_special_char():
    """Test password strength validation with missing special character."""
    password = "NoSpecialChar123"
    is_valid, message = validate_password_strength(password)
    assert is_valid is False
    assert "special character" in message.lower()


def test_validate_password_strength_common_password():
    """Test password strength validation with common password."""
    password = "password123"
    is_valid, message = validate_password_strength(password)
    assert is_valid is False
    assert "common" in message.lower() or "guessable" in message.lower()


def test_password_hashing():
    """Test password hashing and verification."""
    password = "TestPassword123!@#"
    hashed = get_password_hash(password)

    # Should verify correctly
    assert verify_password(password, hashed) is True

    # Wrong password should not verify
    assert verify_password("wrongpassword", hashed) is False


def test_generate_secure_password():
    """Test secure password generation."""
    # Test default length
    password = generate_secure_password()
    assert len(password) >= 12  # Default minimum length

    # Test custom length
    password = generate_secure_password(16)
    assert len(password) == 16

    # Test password strength
    is_valid, _ = validate_password_strength(password)
    assert is_valid is True


@pytest.mark.parametrize(
    "password,expected_valid",
    [
        ("Short1!", False),  # Too short
        ("longenoughbutnouppercase1!", False),  # No uppercase
        ("LONGENOUGHBUTNOLOWERCASE1!", False),  # No lowercase
        ("NoNumber!@#", False),  # No number
        ("NoSpecialChar123", False),  # No special char
        ("SecurePass123!@#", True),  # Valid
        ("Another$ecure123", True),  # Valid with different special char
    ],
)
def test_password_validation_cases(password, expected_valid):
    """Test various password validation cases."""
    is_valid, _ = validate_password_strength(password)
    assert is_valid == expected_valid
