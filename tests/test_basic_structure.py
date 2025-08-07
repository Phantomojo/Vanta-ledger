#!/usr/bin/env python3
"""
Basic structure test to verify the project setup works correctly
"""

import pytest
import sys
from pathlib import Path

def test_project_structure():
    """Test that the project structure is correct"""
    # Check that src/vanta_ledger exists
    assert Path("src/vanta_ledger").exists(), "src/vanta_ledger directory should exist"
    
    # Check that main modules exist
    assert Path("src/vanta_ledger/main.py").exists(), "main.py should exist"
    assert Path("src/vanta_ledger/config.py").exists(), "config.py should exist"
    assert Path("src/vanta_ledger/auth.py").exists(), "auth.py should exist"
    
    # Check that subdirectories exist
    assert Path("src/vanta_ledger/routes").exists(), "routes directory should exist"
    assert Path("src/vanta_ledger/services").exists(), "services directory should exist"
    assert Path("src/vanta_ledger/models").exists(), "models directory should exist"
    assert Path("src/vanta_ledger/utils").exists(), "utils directory should exist"

def test_basic_imports():
    """Test that basic imports work"""
    try:
        from vanta_ledger.config import settings
        assert settings is not None, "Settings should be importable"
    except ImportError as e:
        pytest.fail(f"Failed to import settings: {e}")

def test_main_app_import():
    """Test that the main app can be imported"""
    try:
        from vanta_ledger.main import app
        assert app is not None, "Main app should be importable"
    except ImportError as e:
        pytest.fail(f"Failed to import main app: {e}")

def test_auth_import():
    """Test that auth module can be imported"""
    try:
        from vanta_ledger.auth import AuthService
        assert AuthService is not None, "AuthService should be importable"
    except ImportError as e:
        pytest.fail(f"Failed to import AuthService: {e}")

def test_models_import():
    """Test that models can be imported"""
    try:
        from vanta_ledger.models import document_models, financial_models
        assert document_models is not None, "document_models should be importable"
        assert financial_models is not None, "financial_models should be importable"
    except ImportError as e:
        pytest.fail(f"Failed to import models: {e}")

def test_utils_import():
    """Test that utils can be imported"""
    try:
        from vanta_ledger.utils import validation, file_utils
        assert validation is not None, "validation should be importable"
        assert file_utils is not None, "file_utils should be importable"
    except ImportError as e:
        pytest.fail(f"Failed to import utils: {e}")

def test_routes_import():
    """Test that routes can be imported"""
    try:
        from vanta_ledger.routes import auth, documents, companies
        assert auth is not None, "auth routes should be importable"
        assert documents is not None, "documents routes should be importable"
        assert companies is not None, "companies routes should be importable"
    except ImportError as e:
        pytest.fail(f"Failed to import routes: {e}")

def test_services_import():
    """Test that services can be imported"""
    try:
        from vanta_ledger.services import document_processor, ai_analytics_service
        assert document_processor is not None, "document_processor should be importable"
        assert ai_analytics_service is not None, "ai_analytics_service should be importable"
    except ImportError as e:
        pytest.fail(f"Failed to import services: {e}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 