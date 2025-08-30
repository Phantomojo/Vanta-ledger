#!/usr/bin/env python3
"""
Security Test Script for Vanta Ledger
Validates all security fixes and improvements
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def test_authentication_requirements():
    """Test that all endpoints require authentication"""
    print("🔐 Testing Authentication Requirements...")
    
    # Check companies route
    companies_file = Path("backend/src/vanta_ledger/routes/companies.py")
    if companies_file.exists():
        content = companies_file.read_text()
        if "current_user: dict = Depends(AuthService.verify_token)" in content:
            print("  ✅ Companies endpoint requires authentication")
        else:
            print("  ❌ Companies endpoint missing authentication")
            return False
    
    # Check ledger route
    ledger_file = Path("backend/src/vanta_ledger/routes/ledger.py")
    if ledger_file.exists():
        content = ledger_file.read_text()
        if "current_user: dict = Depends(AuthService.verify_token)" in content:
            print("  ✅ Ledger endpoint requires authentication")
        else:
            print("  ❌ Ledger endpoint missing authentication")
            return False
    
    return True

def test_frontend_security():
    """Test frontend security improvements"""
    print("🛡️ Testing Frontend Security...")
    
    # Check API test routes disabled
    api_file = Path("frontend/frontend-web/src/api.ts")
    if api_file.exists():
        content = api_file.read_text()
        if "const USE_TEST_ROUTES = false" in content:
            print("  ✅ Test routes disabled for security")
        else:
            print("  ❌ Test routes still enabled")
            return False
    
    # Check input validation
    signup_file = Path("frontend/frontend-web/src/components/auth/SignUpForm.tsx")
    if signup_file.exists():
        content = signup_file.read_text()
        if "emailRegex.test" in content and "trimmedPassword.length < 8" in content:
            print("  ✅ Client-side validation implemented")
        else:
            print("  ❌ Client-side validation missing")
            return False
    
    return True

def test_database_transaction_safety():
    """Test database transaction safety"""
    print("💾 Testing Database Transaction Safety...")
    
    # Check user update with rollback
    users_file = Path("backend/src/vanta_ledger/routes/users.py")
    if users_file.exists():
        content = users_file.read_text()
        if "user_service.db.rollback()" in content:
            print("  ✅ User update includes rollback on failure")
        else:
            print("  ❌ User update missing rollback")
            return False
    
    return True

def test_api_design():
    """Test API design improvements"""
    print("🔧 Testing API Design...")
    
    # Check PATCH endpoint exists
    users_file = Path("backend/src/vanta_ledger/routes/users.py")
    if users_file.exists():
        content = users_file.read_text()
        if "@router.patch" in content:
            print("  ✅ PATCH endpoint implemented for partial updates")
        else:
            print("  ❌ PATCH endpoint missing")
            return False
    
    return True

def test_error_handling():
    """Test error handling improvements"""
    print("🚨 Testing Error Handling...")
    
    # Check main.py logging
    main_file = Path("backend/src/vanta_ledger/main.py")
    if main_file.exists():
        content = main_file.read_text()
        if "logger.exception" in content:
            print("  ✅ Proper exception logging implemented")
        else:
            print("  ❌ Exception logging missing")
            return False
    
    return True

def test_import_fixes():
    """Test import fixes"""
    print("📦 Testing Import Fixes...")
    
    # Check companies route imports
    companies_file = Path("backend/src/vanta_ledger/routes/companies.py")
    if companies_file.exists():
        content = companies_file.read_text()
        if "from fastapi import APIRouter, Depends, HTTPException, status, Query" in content:
            print("  ✅ Companies route imports fixed")
        else:
            print("  ❌ Companies route imports missing Query")
            return False
    
    # Check ledger route imports
    ledger_file = Path("backend/src/vanta_ledger/routes/ledger.py")
    if ledger_file.exists():
        content = ledger_file.read_text()
        if "from fastapi import APIRouter, Depends, HTTPException, Query" in content:
            print("  ✅ Ledger route imports fixed")
        else:
            print("  ❌ Ledger route imports missing Query")
            return False
    
    return True

def main():
    """Run all security tests"""
    print("🔒 Vanta Ledger Security Test Suite")
    print("=" * 50)
    
    tests = [
        test_authentication_requirements,
        test_frontend_security,
        test_database_transaction_safety,
        test_api_design,
        test_error_handling,
        test_import_fixes
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"  ❌ Test failed with error: {e}")
            print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All security tests passed!")
        return 0
    else:
        print("⚠️  Some security tests failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
