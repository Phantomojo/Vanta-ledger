#!/usr/bin/env python3
"""
Atomic Transaction Structure Test
Validates code structure and syntax without database connections
"""

import ast
import importlib.util
import os
import sys
from pathlib import Path

def test_file_structure():
    """Test that all required files exist"""
    print("🔍 Testing file structure...")
    
    required_files = [
        "backend/src/vanta_ledger/services/atomic_transaction_service.py",
        "backend/src/vanta_ledger/routes/atomic_transactions.py",
        "infrastructure/database/migrations/001_add_atomic_transactions.py",
        "tests/test_atomic_transactions.py",
        "docs/ATOMIC_TRANSACTIONS_GUIDE.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print("✅ All required files exist")
    return True

def test_python_syntax(file_path):
    """Test Python syntax of a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the AST to check syntax
        ast.parse(content)
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error in {file_path}: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return False

def test_import_structure():
    """Test import structure of atomic transaction service"""
    print("\n🔍 Testing import structure...")
    
    service_file = "backend/src/vanta_ledger/services/atomic_transaction_service.py"
    
    try:
        with open(service_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required imports
        required_imports = [
            "import json",
            "import logging",
            "from datetime import datetime",
            "from decimal import Decimal",
            "from typing import Any, Dict, List, Optional, Tuple",
            "from uuid import UUID, uuid4",
            "import redis",
            "from pymongo.collection import Collection",
            "from pymongo.database import Database",
            "from sqlalchemy import text",
            "from sqlalchemy.engine import Engine",
            "from ..database import get_mongo_client, get_postgres_engine",
            "from ..config import settings",
            "from ..models.financial_models import",
            "from ..utils.validation import input_validator"
        ]
        
        missing_imports = []
        for import_line in required_imports:
            if import_line not in content:
                missing_imports.append(import_line)
        
        if missing_imports:
            print(f"❌ Missing imports: {missing_imports}")
            return False
        
        print("✅ All required imports found")
        return True
        
    except Exception as e:
        print(f"❌ Error testing imports: {e}")
        return False

def test_class_structure():
    """Test class structure and methods"""
    print("\n🔍 Testing class structure...")
    
    service_file = "backend/src/vanta_ledger/services/atomic_transaction_service.py"
    
    try:
        with open(service_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required class and methods
        required_elements = [
            "class AtomicTransactionService:",
            "def __init__(self):",
            "async def create_atomic_transaction(",
            "async def rollback_transaction(",
            "async def get_transaction_status(",
            "def _validate_transaction(",
            "async def _execute_atomic_transaction(",
            "async def _execute_rollback(",
            "atomic_transaction_service = AtomicTransactionService()"
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in content:
                missing_elements.append(element)
        
        if missing_elements:
            print(f"❌ Missing class elements: {missing_elements}")
            return False
        
        print("✅ All required class elements found")
        return True
        
    except Exception as e:
        print(f"❌ Error testing class structure: {e}")
        return False

def test_api_routes():
    """Test API routes structure"""
    print("\n🔍 Testing API routes...")
    
    routes_file = "backend/src/vanta_ledger/routes/atomic_transactions.py"
    
    try:
        with open(routes_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required route elements
        required_elements = [
            "router = APIRouter(prefix=\"/atomic-transactions\", tags=[\"Atomic Transactions\"])",
            "@router.post(\"/\", response_model=AtomicTransactionResponse)",
            "@router.get(\"/{transaction_id}\", response_model=TransactionStatusResponse)",
            "@router.post(\"/{transaction_id}/rollback\")",
            "@router.get(\"/groups/list\")",
            "@router.post(\"/validate\")",
            "@router.get(\"/health\")",
            "class AtomicTransactionRequest(BaseModel):",
            "class AtomicTransactionResponse(BaseModel):",
            "class TransactionStatusResponse(BaseModel):"
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in content:
                missing_elements.append(element)
        
        if missing_elements:
            print(f"❌ Missing route elements: {missing_elements}")
            return False
        
        print("✅ All required route elements found")
        return True
        
    except Exception as e:
        print(f"❌ Error testing routes: {e}")
        return False

def test_database_migration():
    """Test database migration structure"""
    print("\n🔍 Testing database migration...")
    
    migration_file = "infrastructure/database/migrations/001_add_atomic_transactions.py"
    
    try:
        with open(migration_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required migration elements
        required_elements = [
            "def upgrade(engine: Engine):",
            "def downgrade(engine: Engine):",
            "def verify_migration(engine: Engine) -> bool:",
            "CREATE TABLE IF NOT EXISTS atomic_transactions",
            "CREATE TABLE IF NOT EXISTS transaction_groups",
            "ADD COLUMN IF NOT EXISTS atomic_transaction_id",
            "CREATE INDEX IF NOT EXISTS idx_atomic_transactions"
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in content:
                missing_elements.append(element)
        
        if missing_elements:
            print(f"❌ Missing migration elements: {missing_elements}")
            return False
        
        print("✅ All required migration elements found")
        return True
        
    except Exception as e:
        print(f"❌ Error testing migration: {e}")
        return False

def test_main_integration():
    """Test main.py integration"""
    print("\n🔍 Testing main.py integration...")
    
    main_file = "backend/src/vanta_ledger/main.py"
    
    try:
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required integration elements
        required_elements = [
            "from .routes.atomic_transactions import router as atomic_transactions_router",
            "app.include_router(atomic_transactions_router)"
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in content:
                missing_elements.append(element)
        
        if missing_elements:
            print(f"❌ Missing main.py integration: {missing_elements}")
            return False
        
        print("✅ Main.py integration found")
        return True
        
    except Exception as e:
        print(f"❌ Error testing main.py integration: {e}")
        return False

def test_documentation():
    """Test documentation completeness"""
    print("\n🔍 Testing documentation...")
    
    doc_file = "docs/ATOMIC_TRANSACTIONS_GUIDE.md"
    
    try:
        with open(doc_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required documentation sections
        required_sections = [
            "# 🔄 Atomic Transactions Guide",
            "## 📋 Overview",
            "## 🏗️ Architecture",
            "## 🚀 Usage Examples",
            "## 🔍 API Reference",
            "## 🛡️ Error Handling",
            "## 🧪 Testing"
        ]
        
        missing_sections = []
        for section in required_sections:
            if section not in content:
                missing_sections.append(section)
        
        if missing_sections:
            print(f"❌ Missing documentation sections: {missing_sections}")
            return False
        
        print("✅ All required documentation sections found")
        return True
        
    except Exception as e:
        print(f"❌ Error testing documentation: {e}")
        return False

def main():
    """Run all structure tests"""
    print("🚀 Starting Atomic Transaction Structure Tests")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Python Syntax - Service", lambda: test_python_syntax("backend/src/vanta_ledger/services/atomic_transaction_service.py")),
        ("Python Syntax - Routes", lambda: test_python_syntax("backend/src/vanta_ledger/routes/atomic_transactions.py")),
        ("Python Syntax - Migration", lambda: test_python_syntax("infrastructure/database/migrations/001_add_atomic_transactions.py")),
        ("Python Syntax - Tests", lambda: test_python_syntax("tests/test_atomic_transactions.py")),
        ("Import Structure", test_import_structure),
        ("Class Structure", test_class_structure),
        ("API Routes", test_api_routes),
        ("Database Migration", test_database_migration),
        ("Main Integration", test_main_integration),
        ("Documentation", test_documentation)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 STRUCTURE TEST RESULTS")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All structure tests passed! Atomic transaction implementation is ready.")
        return True
    else:
        print("❌ Some structure tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
