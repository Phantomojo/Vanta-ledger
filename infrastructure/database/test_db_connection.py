#!/usr/bin/env python3
"""
Test Database Connection Script
"""

import os
import psycopg2
from pymongo import MongoClient
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_postgresql():
    """Test PostgreSQL connection and basic operations"""
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='vanta_ledger',
            user='vanta_user',
            password=os.getenv('POSTGRES_PASSWORD', 'password')
        )
        
        # Test basic query
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            version = cur.fetchone()
            logger.info(f"✅ PostgreSQL connection successful: {version[0]}")
            
            # Check existing tables
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = cur.fetchall()
            logger.info(f"✅ Existing tables: {[table[0] for table in tables]}")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ PostgreSQL test failed: {e}")
        return False

def test_mongodb():
    """Test MongoDB connection and basic operations"""
    try:
        # Connect to MongoDB
        client = MongoClient(f'mongodb://admin:{os.getenv("MONGO_INITDB_ROOT_PASSWORD")}@localhost:27017/vanta_ledger?authSource=admin')
        db = client.vanta_ledger
        
        # Test basic operation
        collections = db.list_collection_names()
        logger.info(f"✅ MongoDB connection successful")
        logger.info(f"✅ Existing collections: {collections}")
        
        client.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ MongoDB test failed: {e}")
        return False

def main():
    """Run database connection tests"""
    logger.info("🧪 Testing Database Connections...")
    logger.info("=" * 50)
    
    postgres_ok = test_postgresql()
    mongo_ok = test_mongodb()
    
    if postgres_ok and mongo_ok:
        logger.info("🎉 All database connections successful!")
        return True
    else:
        logger.error("❌ Some database connections failed!")
        return False

if __name__ == "__main__":
    main() 