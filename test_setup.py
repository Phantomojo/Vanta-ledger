
#!/usr/bin/env python3
"""
Test script to verify the setup works
"""

import os
import sys

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import fastapi
        print("✅ FastAPI imported")
    except ImportError:
        print("❌ FastAPI not available")
        return False
        
    try:
        import sqlalchemy
        print("✅ SQLAlchemy imported")
    except ImportError:
        print("❌ SQLAlchemy not available")
        return False
        
    try:
        import uvicorn
        print("✅ Uvicorn imported")
    except ImportError:
        print("❌ Uvicorn not available")
        return False
        
    return True

def test_database_connection():
    """Test database connection"""
    print("🗄️ Testing database connection...")
    
    # Set up path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.join(current_dir, "src")
    sys.path.insert(0, src_path)
    
    try:
        from vanta_ledger.database import engine, SessionLocal
        
        # Test connection
        db = SessionLocal()
        db.execute(sqlalchemy.text("SELECT 1"))
        db.close()
        print("✅ Database connection successful")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🎯 Vanta Ledger Setup Test")
    print("=" * 40)
    
    if test_imports():
        if test_database_connection():
            print("\n🎉 All tests passed! System is ready.")
        else:
            print("\n⚠️ Database test failed. Run setup first.")
    else:
        print("\n❌ Import tests failed. Install dependencies first.")
