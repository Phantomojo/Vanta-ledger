#!/usr/bin/env python3
"""
Code Quality Fix Script for Vanta Ledger
Addresses all linting, formatting, and import issues
"""

import os
import sys
from pathlib import Path

def fix_imports():
    """Fix missing imports in various files"""
    logger.info("🔧 Fixing missing imports...")
    
    # Fix test_db_connection.py
    db_test_file = Path("infrastructure/database/test_db_connection.py")
    if db_test_file.exists():
        content = db_test_file.read_text()
        if "import os" not in content:
            content = content.replace(
                "import psycopg2",
                "import os\nimport psycopg2"
            )
            db_test_file.write_text(content)
            logger.info("  ✅ Fixed imports in test_db_connection.py")
    
    # Fix test_auth.py
    auth_test_file = Path("tests/test_auth.py")
    if auth_test_file.exists():
        content = auth_test_file.read_text()
        if "from src.vanta_ledger.config import settings" not in content:
            content = content.replace(
                "from src.vanta_ledger.utils.password import get_password_hash",
                "from src.vanta_ledger.utils.password import get_password_hash\nfrom src.vanta_ledger.config import settings"
            )
            auth_test_file.write_text(content)
            logger.info("  ✅ Fixed imports in test_auth.py")
    
    # Fix test_users.py
    users_test_file = Path("tests/test_users.py")
    if users_test_file.exists():
        content = users_test_file.read_text()
        if "from tests.conftest import override_get_db" not in content:
            content = content.replace(
                "from src.vanta_ledger import models, schemas",
                "from src.vanta_ledger import models, schemas\nfrom tests.conftest import override_get_db"
            )
            users_test_file.write_text(content)
            logger.info("  ✅ Fixed imports in test_users.py")

def fix_indentation():
    """Fix indentation issues"""
    logger.info("🔧 Fixing indentation issues...")
    
    # Fix enhanced_hybrid_database_setup.py
    db_setup_file = Path("infrastructure/database/enhanced_hybrid_database_setup.py")
    if db_setup_file.exists():
        content = db_setup_file.read_text()
        # Fix the indentation issues
        content = content.replace("    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')", "POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')")
        content = content.replace("    MONGO_PASSWORD = os.getenv('MONGO_ROOT_PASSWORD')", "MONGO_PASSWORD = os.getenv('MONGO_ROOT_PASSWORD')")
        db_setup_file.write_text(content)
        logger.info("  ✅ Fixed indentation in enhanced_hybrid_database_setup.py")

def fix_formatting():
    """Fix code formatting issues"""
    logger.info("🔧 Fixing code formatting...")
    
    # Fix database.py formatting
    db_file = Path("backend/src/vanta_ledger/database.py")
    if db_file.exists():
        content = db_file.read_text()
        # Fix the long line issue
        content = content.replace(
            'raise RuntimeError("PostgreSQL driver not available or connection failed") from e',
            'raise RuntimeError(\n            "PostgreSQL driver not available or connection failed"\n        ) from e'
        )
        db_file.write_text(content)
        logger.info("  ✅ Fixed formatting in database.py")

def add_missing_docstrings():
    """Add missing docstrings to improve documentation quality"""
    logger.info("📚 Adding missing docstrings...")
    
    # Add docstrings to key functions
    files_to_check = [
        "backend/src/vanta_ledger/routes/companies.py",
        "backend/src/vanta_ledger/routes/ledger.py",
        "backend/src/vanta_ledger/routes/users.py"
    ]
    
    for file_path in files_to_check:
        path = Path(file_path)
        if path.exists():
            content = path.read_text()
            # Add module docstring if missing
            if not content.startswith('"""'):
                content = f'"""\n{path.stem.title()} API Routes\nREST endpoints for {path.stem.replace("_", " ")} management\n"""\n\n{content}'
                path.write_text(content)
                logger.info(f"  ✅ Added docstring to {file_path}")

def create_test_files():
    """Create missing test files to improve test coverage"""
    logger.info("🧪 Creating missing test files...")
    
    # Create basic test files for new routes
    test_files = {
        "tests/test_atomic_transactions.py": '''"""Tests for atomic transaction endpoints."""

import pytest
from fastapi import status

def test_create_atomic_transaction(client, auth_headers):
    """Test creating an atomic transaction."""
    transaction_data = {
        "description": "Test transaction",
        "entries": [
            {"account_id": "1", "debit": 100.0, "credit": 0.0},
            {"account_id": "2", "debit": 0.0, "credit": 100.0}
        ]
    }
    
    response = client.post(
        "/atomic-transactions/",
        json=transaction_data,
        headers=auth_headers,
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "transaction_id" in data
    assert data["status"] == "completed"
''',
        "tests/test_semantic_search.py": '''"""Tests for semantic search endpoints."""

import pytest
from fastapi import status

def test_semantic_search(client, auth_headers):
    """Test semantic search functionality."""
    search_data = {
        "query": "invoice over 1000",
        "company_id": "test-company-id"
    }
    
    response = client.post(
        "/semantic-search/search",
        json=search_data,
        headers=auth_headers,
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "results" in data
    assert "query" in data
''',
        "tests/test_advanced_documents.py": '''"""Tests for advanced document processing endpoints."""

import pytest
from fastapi import status
import logging
logger = logging.getLogger(__name__)

def test_process_document_advanced(client, auth_headers):
    """Test advanced document processing."""
    processing_data = {
        "document_id": "test-doc-id",
        "processing_options": {
            "process_handwritten": True,
            "enable_layout_analysis": True
        }
    }
    
    response = client.post(
        "/advanced-documents/process",
        json=processing_data,
        headers=auth_headers,
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "analysis_id" in data
    assert data["status"] == "completed"
'''
    }
    
    for file_path, content in test_files.items():
        path = Path(file_path)
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            logger.info(f"  ✅ Created {file_path}")

def main():
    """Run all code quality fixes"""
    logger.info("🔧 Vanta Ledger Code Quality Fix Script")
    logger.info("=")
    
    try:
        fix_imports()
        fix_indentation()
        fix_formatting()
        add_missing_docstrings()
        create_test_files()
        
        logger.info("\n")
        logger.info("🎉 All code quality fixes completed!")
        logger.info("✅ Ready to run tests and checks")
        
    except Exception as e:
        logger.error(f"❌ Error during fixes: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
