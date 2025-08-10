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
    assert Path("src/vanta_ledger").exists(), "src/vanta_ledger directory should exist"
    assert Path("src/vanta_ledger/main.py").exists(), "main.py should be in src/vanta_ledger"
    assert Path("src/vanta_ledger/config.py").exists(), "config.py should be in src/vanta_ledger"
    assert Path("src/vanta_ledger/auth.py").exists(), "auth.py should be in src/vanta_ledger"
    assert not Path("backend/app").exists(), "backend/app should be moved to src/vanta_ledger"
    for p in ["routes", "services", "models", "utils"]:
        assert Path(f"src/vanta_ledger/{p}").exists(), f"{p} directory should exist"


def test_setup_py_fixes():
    setup_py = Path("setup.py").read_text()
    assert "from setuptools import setup" in setup_py
    assert "setup()" in setup_py
    assert "def run_command" not in setup_py


def test_pyproject_toml_fixes():
    py = Path("pyproject.toml").read_text()
    assert 'where = ["src"]' in py


def test_user_management_implementation():
    assert Path("src/vanta_ledger/models/user_models.py").exists()
    assert Path("src/vanta_ledger/services/user_service.py").exists()
    auth_content = Path("src/vanta_ledger/auth.py").read_text()
    assert "get_user_service" in auth_content


def test_security_improvements():
    auth_content = Path("src/vanta_ledger/auth.py").read_text()
    assert "admin123" not in auth_content
    config_content = Path("src/vanta_ledger/config.py").read_text()
    assert "os.getenv" in config_content or "settings" in config_content
    assert "CryptContext" in auth_content
    assert "bcrypt" in auth_content


def test_dependency_management_fixes():
    for f in [
        "backend/requirements.in",
        "backend/requirements-dev.in",
        "backend/requirements-llm.in",
        "backend/requirements.txt",
        "backend/requirements-dev.txt",
        "backend/requirements-llm.txt",
    ]:
        assert Path(f).exists(), f"{f} should exist"


def test_api_structure_improvements():
    routes_dir = Path("src/vanta_ledger/routes")
    assert routes_dir.exists(), "routes directory should exist"
    main_content = Path("src/vanta_ledger/main.py").read_text()
    assert len(main_content.split('\n')) < 500
    assert "from .routes" in main_content


def test_database_integration():
    assert Path("scripts/init_database.py").exists(), "Database initialization script should exist"
    user_models_content = Path("src/vanta_ledger/models/user_models.py").read_text()
    assert "UserDB" in user_models_content
    assert "Base" in user_models_content


def test_import_structure():
    try:
        from vanta_ledger.config import settings
        assert settings is not None
        from vanta_ledger.main import app
        assert app is not None
        from vanta_ledger.auth import AuthService
        assert AuthService is not None
        from vanta_ledger.models import user_models
        assert user_models is not None
        from vanta_ledger.services import user_service
        assert user_service is not None
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")


def test_audit_report_exists():
    assert Path("AUDIT_REPORT.md").exists(), "AUDIT_REPORT.md should exist"
    audit_content = Path("AUDIT_REPORT.md").read_text()
    assert "Security Vulnerabilities" in audit_content
    assert "Dependency Management" in audit_content
    assert "API Structure" in audit_content
    assert "Project Setup" in audit_content


def test_new_setup_script():
    assert Path("scripts/setup_project.py").exists(), "New setup script should exist"
    setup_script_content = Path("scripts/setup_project.py").read_text()
    assert "Modern Python Layout" in setup_script_content
    assert "pip install -e .[dev]" in setup_script_content


def test_alembic_wrapper():
    assert Path("scripts/run_alembic.sh").exists(), "Alembic wrapper script should exist"
    alembic_wrapper_content = Path("scripts/run_alembic.sh").read_text()
    assert "DATABASE_URL" in alembic_wrapper_content
    assert ".env" in alembic_wrapper_content

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 