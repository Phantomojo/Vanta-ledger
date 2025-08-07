#!/usr/bin/env python3
"""
Test Jules Audit Fixes
Comprehensive test to verify all fixes from the Jules audit are working
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

def test_project_structure_fixes():
    """Test that the project structure fixes are implemented correctly"""
    # Check src/vanta_ledger structure
    assert Path("src/vanta_ledger").exists(), "src/vanta_ledger directory should exist"
    assert Path("src/vanta_ledger/main.py").exists(), "main.py should be in src/vanta_ledger"
    assert Path("src/vanta_ledger/config.py").exists(), "config.py should be in src/vanta_ledger"
    assert Path("src/vanta_ledger/auth.py").exists(), "auth.py should be in src/vanta_ledger"
    
    # Check that backend/app is moved
    assert not Path("backend/app").exists(), "backend/app should be moved to src/vanta_ledger"
    
    # Check subdirectories
    assert Path("src/vanta_ledger/routes").exists(), "routes directory should exist"
    assert Path("src/vanta_ledger/services").exists(), "services directory should exist"
    assert Path("src/vanta_ledger/models").exists(), "models directory should exist"
    assert Path("src/vanta_ledger/utils").exists(), "utils directory should exist"

def test_setup_py_fixes():
    """Test that setup.py has been fixed"""
    setup_py_content = Path("setup.py").read_text()
    
    # Check that setup.py is minimal and correct
    assert "from setuptools import setup" in setup_py_content
    assert "setup()" in setup_py_content
    
    # Check that the old non-standard setup.py content is removed
    assert "def run_command" not in setup_py_content
    assert "def check_python_version" not in setup_py_content
    assert "def create_directories" not in setup_py_content

def test_pyproject_toml_fixes():
    """Test that pyproject.toml has been updated for src layout"""
    pyproject_content = Path("pyproject.toml").read_text()
    
    # Check that setuptools is configured for src layout
    assert 'where = ["src"]' in pyproject_content
    assert 'where = ["backend"]' not in pyproject_content

def test_user_management_implementation():
    """Test that user management system is implemented"""
    # Check that user models exist
    assert Path("src/vanta_ledger/models/user_models.py").exists(), "user_models.py should exist"
    
    # Check that user service exists
    assert Path("src/vanta_ledger/services/user_service.py").exists(), "user_service.py should exist"
    
    # Check that auth.py has been updated
    auth_content = Path("src/vanta_ledger/auth.py").read_text()
    assert "TODO: Implement" not in auth_content, "TODO comments should be removed"
    assert "get_user_service" in auth_content, "User service should be integrated"

def test_security_improvements():
    """Test that security improvements are implemented"""
    # Check that hardcoded credentials are removed
    auth_content = Path("src/vanta_ledger/auth.py").read_text()
    assert "admin123" not in auth_content, "Hardcoded admin123 should be removed"
    
    # Check that environment variables are used
    config_content = Path("src/vanta_ledger/config.py").read_text()
    assert "os.getenv" in config_content or "settings" in config_content, "Environment variables should be used"
    
    # Check that secure password hashing is implemented
    assert "CryptContext" in auth_content, "Secure password hashing should be implemented"
    assert "bcrypt" in auth_content, "bcrypt should be used for password hashing"

def test_dependency_management_fixes():
    """Test that dependency management is improved"""
    # Check that pip-tools files exist
    assert Path("backend/requirements.in").exists(), "requirements.in should exist"
    assert Path("backend/requirements-dev.in").exists(), "requirements-dev.in should exist"
    assert Path("backend/requirements-llm.in").exists(), "requirements-llm.in should exist"
    
    # Check that generated requirements files exist
    assert Path("backend/requirements.txt").exists(), "requirements.txt should exist"
    assert Path("backend/requirements-dev.txt").exists(), "requirements-dev.txt should exist"
    assert Path("backend/requirements-llm.txt").exists(), "requirements-llm.txt should exist"

def test_api_structure_improvements():
    """Test that API structure has been improved"""
    # Check that routes are properly organized
    routes_dir = Path("src/vanta_ledger/routes")
    assert routes_dir.exists(), "routes directory should exist"
    
    # Check that main.py is cleaner
    main_content = Path("src/vanta_ledger/main.py").read_text()
    assert len(main_content.split('\n')) < 300, "main.py should be much smaller after refactoring"
    
    # Check that routes are imported
    assert "from .routes" in main_content, "Routes should be imported from separate modules"

def test_database_integration():
    """Test that database integration is properly implemented"""
    # Check that database initialization script exists
    assert Path("scripts/init_database.py").exists(), "Database initialization script should exist"
    
    # Check that user models have proper database integration
    user_models_content = Path("src/vanta_ledger/models/user_models.py").read_text()
    assert "UserDB" in user_models_content, "UserDB model should exist"
    assert "Base" in user_models_content, "SQLAlchemy Base should be imported"

def test_import_structure():
    """Test that imports work correctly with the new structure"""
    try:
        # Test basic imports
        from vanta_ledger.config import settings
        assert settings is not None
        
        from vanta_ledger.main import app
        assert app is not None
        
        from vanta_ledger.auth import AuthService
        assert AuthService is not None
        
        # Test model imports
        from vanta_ledger.models import user_models
        assert user_models is not None
        
        # Test service imports
        from vanta_ledger.services import user_service
        assert user_service is not None
        
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")

def test_audit_report_exists():
    """Test that the audit report exists and is comprehensive"""
    assert Path("AUDIT_REPORT.md").exists(), "AUDIT_REPORT.md should exist"
    
    audit_content = Path("AUDIT_REPORT.md").read_text()
    
    # Check that audit report covers key areas
    assert "Security Vulnerabilities" in audit_content
    assert "Dependency Management" in audit_content
    assert "API Structure" in audit_content
    assert "Project Setup" in audit_content

def test_new_setup_script():
    """Test that the new setup script exists"""
    assert Path("scripts/setup_project.py").exists(), "New setup script should exist"
    
    setup_script_content = Path("scripts/setup_project.py").read_text()
    assert "Modern Python Layout" in setup_script_content
    assert "pip install -e .[dev]" in setup_script_content

def test_alembic_wrapper():
    """Test that the alembic wrapper script exists"""
    assert Path("scripts/run_alembic.sh").exists(), "Alembic wrapper script should exist"
    
    alembic_wrapper_content = Path("scripts/run_alembic.sh").read_text()
    assert "DATABASE_URL" in alembic_wrapper_content
    assert ".env" in alembic_wrapper_content

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 