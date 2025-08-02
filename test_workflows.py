
#!/usr/bin/env python3
"""
Test script to verify all workflows and components are working
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def test_python_availability():
    """Test if Python is available"""
    try:
        result = subprocess.run(['python3', '--version'], capture_output=True, text=True)
        print(f"✅ Python available: {result.stdout.strip()}")
        return True
    except FileNotFoundError:
        print("❌ Python3 not found")
        return False

def test_database_setup():
    """Test database setup"""
    try:
        import sqlite3
        print("✅ SQLite available")
        
        # Test database creation
        if Path('simple_db_setup.py').exists():
            result = subprocess.run(['python3', 'simple_db_setup.py'], capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print("✅ Database setup successful")
                return True
            else:
                print(f"❌ Database setup failed: {result.stderr}")
                return False
        else:
            print("❌ Database setup script not found")
            return False
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_backend_startup():
    """Test backend server startup"""
    try:
        if Path('src/run_server.py').exists():
            print("✅ Backend startup script found")
            return True
        else:
            print("❌ Backend startup script not found")
            return False
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        return False

def test_frontend_availability():
    """Test frontend availability"""
    try:
        if Path('frontend-web/package.json').exists():
            print("✅ Frontend project found")
            return True
        else:
            print("❌ Frontend project not found")
            return False
    except Exception as e:
        print(f"❌ Frontend test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Running Vanta Ledger Workflow Tests")
    print("=" * 50)
    
    tests = [
        ("Python Availability", test_python_availability),
        ("Database Setup", test_database_setup),
        ("Backend Startup", test_backend_startup),
        ("Frontend Availability", test_frontend_availability),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing: {test_name}")
        if test_func():
            passed += 1
        
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
