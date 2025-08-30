#!/usr/bin/env python3
"""
Test backend with no-auth MongoDB
"""
import os
import sys

# Override MongoDB URI to work without authentication
os.environ["MONGO_URI"] = "mongodb://localhost:27017/vanta_ledger"

def test_backend_import():
    """Test if the backend can be imported without MongoDB auth errors"""
    try:
        from src.vanta_ledger.main import app
        print("✅ Backend import successful without MongoDB auth errors!")
        return True
    except Exception as e:
        print(f"❌ Backend import failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing Backend Import (No MongoDB Auth)...")
    print("=" * 50)
    test_backend_import()
