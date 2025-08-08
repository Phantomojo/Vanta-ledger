#!/usr/bin/env python3
"""
Basic structure test to verify the project setup works correctly
"""

import pytest
import sys
from pathlib import Path

def test_project_structure():
    """
    Verify that the essential directories and files for the vanta_ledger project exist in the expected locations.
    """
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
    """
    Verify that the `settings` object can be imported from `vanta_ledger.config`.
    
    Fails the test if the import is unsuccessful or if `settings` is not defined.
    """
    try:
        from vanta_ledger.config import settings
        assert settings is not None, "Settings should be importable"
    except ImportError as e:
        pytest.fail(f"Failed to import settings: {e}")

def test_main_app_import():
    """
    Verify that the main application object can be imported from the vanta_ledger.main module.
    
    Fails the test if the import is unsuccessful or if the app object is not defined.
    """
    try:
        from vanta_ledger.main import app
        assert app is not None, "Main app should be importable"
    except ImportError as e:
        pytest.fail(f"Failed to import main app: {e}")

def test_auth_import():
    """
    Verify that the AuthService class can be imported from the vanta_ledger.auth module.
    
    Fails the test if the import is unsuccessful.
    """
    try:
        from vanta_ledger.auth import AuthService
        assert AuthService is not None, "AuthService should be importable"
    except ImportError as e:
        pytest.fail(f"Failed to import AuthService: {e}")

def test_models_import():
    """
    Verify that the `document_models` and `financial_models` modules can be imported from `vanta_ledger.models`.
    
    Fails the test if either module cannot be imported.
    """
    try:
        from vanta_ledger.models import document_models, financial_models
        assert document_models is not None, "document_models should be importable"
        assert financial_models is not None, "financial_models should be importable"
    except ImportError as e:
        pytest.fail(f"Failed to import models: {e}")

def test_utils_import():
    """
    Verify that the `validation` and `file_utils` modules in `vanta_ledger.utils` can be imported successfully.
    
    Fails the test if either module cannot be imported.
    """
    try:
        from vanta_ledger.utils import validation, file_utils
        assert validation is not None, "validation should be importable"
        assert file_utils is not None, "file_utils should be importable"
    except ImportError as e:
        pytest.fail(f"Failed to import utils: {e}")

def test_routes_import():
    """
    Verify that the `auth`, `documents`, and `companies` route modules in `vanta_ledger.routes` can be imported successfully.
    
    Fails the test if any of the specified route modules cannot be imported.
    """
    try:
        from vanta_ledger.routes import auth, documents, companies
        assert auth is not None, "auth routes should be importable"
        assert documents is not None, "documents routes should be importable"
        assert companies is not None, "companies routes should be importable"
    except ImportError as e:
        pytest.fail(f"Failed to import routes: {e}")

def test_services_import():
    """
    Verify that the `document_processor` and `ai_analytics_service` modules can be imported from `vanta_ledger.services`.
    
    Fails the test if either module cannot be imported.
    """
    try:
        from vanta_ledger.services import document_processor, ai_analytics_service
        assert document_processor is not None, "document_processor should be importable"
        assert ai_analytics_service is not None, "ai_analytics_service should be importable"
    except ImportError as e:
        pytest.fail(f"Failed to import services: {e}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 