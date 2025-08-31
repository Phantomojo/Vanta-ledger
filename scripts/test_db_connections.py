#!/usr/bin/env python3
"""
Test database connections for Vanta Ledger
"""
import os
import sys
import urllib.parse
from dotenv import load_dotenv

def test_postgresql():
    """Test PostgreSQL connection"""
    try:
        import psycopg2
        load_dotenv()
        
        password = os.getenv('POSTGRES_PASSWORD')
        if not password:
            print("❌ POSTGRES_PASSWORD not found in .env file")
            return False
            
        # Decode URL-encoded password
        decoded_password = urllib.parse.unquote(password)
        
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='vanta_ledger',
            user='vanta_user',
            password=decoded_password
        )
        print("✅ PostgreSQL connection SUCCESS!")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ PostgreSQL connection FAILED: {e}")
        return False

def test_mongodb():
    """Test MongoDB connection"""
    try:
        import pymongo
        load_dotenv()
        
        # For now, connect without authentication since MongoDB is running in no-auth mode
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        # Test the connection
        client.admin.command('ping')
        print("✅ MongoDB connection SUCCESS! (no auth mode)")
        client.close()
        return True
    except Exception as e:
        print(f"❌ MongoDB connection FAILED: {e}")
        return False

def test_redis():
    """Test Redis connection"""
    try:
        import redis
        load_dotenv()
        
        password = os.getenv('REDIS_PASSWORD')
        if not password:
            print("❌ REDIS_PASSWORD not found in .env file")
            return False
            
        # Decode URL-encoded password
        decoded_password = urllib.parse.unquote(password)
        
        r = redis.Redis(
            host='localhost',
            port=6379,
            password=decoded_password,
            decode_responses=True
        )
        # Test the connection
        r.ping()
        print("✅ Redis connection SUCCESS!")
        r.close()
        return True
    except Exception as e:
        print(f"❌ Redis connection FAILED: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing Database Connections...")
    print("=" * 40)
    
    results = []
    results.append(test_postgresql())
    results.append(test_mongodb())
    results.append(test_redis())
    
    print("=" * 40)
    if all(results):
        print("🎉 All database connections successful!")
    else:
        print("⚠️  Some database connections failed. Check the errors above.")
