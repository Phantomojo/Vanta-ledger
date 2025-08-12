"""Tests for configuration settings."""
import os
from unittest.mock import patch

import pytest

from src.vanta_ledger.config import settings, Settings


def test_settings_defaults():
    """Test that default settings are loaded correctly."""
    # Create a new settings instance to test defaults
    test_settings = Settings()
    
    # Test some default values
    assert test_settings.PROJECT_NAME == "Vanta Ledger"
    assert test_settings.API_V1_STR == "/api/v1"
    assert test_settings.ALGORITHM == "HS256"
    assert test_settings.ACCESS_TOKEN_EXPIRE_MINUTES == 10080  # 7 days
    assert test_settings.SECURITY_BCRYPT_ROUNDS == 12
    assert test_settings.MIN_PASSWORD_LENGTH == 12
    assert test_settings.UPLOAD_FOLDER == "./uploads"
    assert test_settings.DEBUG is False


def test_environment_variables_override():
    """Test that environment variables override defaults."""
    # Set some environment variables
    os.environ["PROJECT_NAME"] = "Test App"
    os.environ["DEBUG"] = "true"
    os.environ["DATABASE_URL"] = "sqlite:///test.db"
    
    # Create a new settings instance
    test_settings = Settings()
    
    # Test that environment variables override defaults
    assert test_settings.PROJECT_NAME == "Test App"
    assert test_settings.DEBUG is True
    assert test_settings.DATABASE_URL == "sqlite:///test.db"
    
    # Clean up
    del os.environ["PROJECT_NAME"]
    del os.environ["DEBUG"]
    del os.environ["DATABASE_URL"]


def test_settings_validation():
    """Test that settings validation works as expected."""
    # Test with invalid values
    with pytest.raises(ValueError):
        Settings(MIN_PASSWORD_LENGTH=3)  # Too short
    
    with pytest.raises(ValueError):
        Settings(ACCESS_TOKEN_EXPIRE_MINUTES=0)  # Must be positive
    
    with pytest.raises(ValueError):
        Settings(SECURITY_BCRYPT_ROUNDS=3)  # Too few rounds
    
    # Test with valid values
    try:
        Settings(
            MIN_PASSWORD_LENGTH=16,
            ACCESS_TOKEN_EXPIRE_MINUTES=60,
            SECURITY_BCRYPT_ROUNDS=14,
        )
    except ValueError:
        pytest.fail("Valid settings should not raise ValueError")


def test_settings_instance():
    """Test that the settings instance is properly configured."""
    assert isinstance(settings, Settings)
    assert hasattr(settings, "SECRET_KEY")
    assert hasattr(settings, "DATABASE_URL")
    assert hasattr(settings, "REDIS_URL")
    assert hasattr(settings, "SMTP_HOST")
    assert hasattr(settings, "SMTP_PORT")
    assert hasattr(settings, "EMAILS_FROM_EMAIL")


def test_settings_database_url_construction():
    """Test that database URL is constructed correctly from components."""
    # Test with all components
    test_settings = Settings(
        POSTGRES_SERVER="localhost",
        POSTGRES_USER="testuser",
        POSTGRES_PASSWORD="testpass",
        POSTGRES_DB="testdb",
    )
    assert test_settings.DATABASE_URL == "postgresql://testuser:testpass@localhost/testdb"
    
    # Test with SQLite
    test_settings = Settings(SQLITE_DB="test.db")
    assert test_settings.DATABASE_URL == "sqlite:///test.db"


def test_settings_redis_url_construction():
    """Test that Redis URL is constructed correctly from components."""
    # Test with all components
    test_settings = Settings(
        REDIS_HOST="localhost",
        REDIS_PORT=6379,
        REDIS_PASSWORD="redispass",
        REDIS_DB=1,
    )
    assert test_settings.REDIS_URL == "redis://:redispass@localhost:6379/1"
    
    # Test without password
    test_settings = Settings(
        REDIS_HOST="localhost",
        REDIS_PORT=6379,
        REDIS_DB=0,
    )
    assert test_settings.REDIS_URL == "redis://localhost:6379/0"


def test_settings_cors_origins():
    """Test that CORS origins are parsed correctly."""
    # Test with a single origin
    test_settings = Settings(BACKEND_CORS_ORIGINS=["http://localhost:3000"])
    assert test_settings.BACKEND_CORS_ORIGINS == ["http://localhost:3000"]
    
    # Test with multiple origins
    test_settings = Settings(BACKEND_CORS_ORIGINS=["http://localhost:3000", "https://example.com"])
    assert test_settings.BACKEND_CORS_ORIGINS == ["http://localhost:3000", "https://example.com"]
    
    # Test with a JSON string
    test_settings = Settings(BACKEND_CORS_ORIGINS='["http://localhost:3000"]')
    assert test_settings.BACKEND_CORS_ORIGINS == ["http://localhost:3000"]


def test_settings_env_file_loading(tmp_path):
    """Test that settings are loaded from a .env file."""
    # Create a temporary .env file
    env_file = tmp_path / ".env"
    env_file.write_text("""
    PROJECT_NAME=Test App
    DEBUG=true
    SECRET_KEY=test-secret-key
    """)
    
    # Create settings with the .env file
    with patch.dict(os.environ, {"ENV_FILE": str(env_file)}):
        test_settings = Settings()
        
        # Test that values from .env file are loaded
        assert test_settings.PROJECT_NAME == "Test App"
        assert test_settings.DEBUG is True
        assert test_settings.SECRET_KEY == "test-secret-key"
        
        # Test that other values still have defaults
        assert test_settings.API_V1_STR == "/api/v1"
