#!/usr/bin/env python3
"""
Simple MongoDB connection test
"""
import pymongo

def test_mongodb_no_auth():
    """Test MongoDB connection without authentication"""
    try:
        # Try connecting without authentication first
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        # Test the connection
        client.admin.command('ping')
        print("✅ MongoDB connection SUCCESS (no auth)!")
        
        # Check what databases exist
        databases = client.list_database_names()
        print(f"📁 Available databases: {databases}")
        
        client.close()
        return True
    except Exception as e:
        print(f"❌ MongoDB connection FAILED: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing MongoDB Connection (No Auth)...")
    print("=" * 40)
    test_mongodb_no_auth()
