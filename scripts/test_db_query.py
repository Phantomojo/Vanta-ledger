#!/usr/bin/env python3
"""
Test Database Query Script
Tests the database query directly to debug the 422 error
"""

import sys
from pathlib import Path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from vanta_ledger.database import get_postgres_connection

def test_companies_query():
    """Test the companies query directly"""
    try:
        print("🔍 Testing companies query directly...")
        
        conn = get_postgres_connection()
        cursor = conn.cursor()
        
        try:
            # Test the exact query from the route
            print("📊 Testing COUNT query...")
            cursor.execute("SELECT COUNT(*) FROM companies")
            total_count = cursor.fetchone()[0]
            print(f"✅ Total companies: {total_count}")
            
            print("📋 Testing SELECT query...")
            cursor.execute(
                "SELECT postgres_id, name, industry, revenue FROM companies ORDER BY name LIMIT 5 OFFSET 0"
            )
            companies = cursor.fetchall()
            print(f"✅ Found {len(companies)} companies:")
            
            for company in companies:
                print(f"   - ID: {company[0]}, Name: {company[1]}, Industry: {company[2]}, Revenue: {company[3]}")
                
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        print(f"❌ Error testing query: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_companies_query()
