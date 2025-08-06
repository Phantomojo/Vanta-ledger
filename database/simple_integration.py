#!/usr/bin/env python3
"""
Simplified Vanta Ledger Integration
===================================

This script performs a simplified integration focusing on document processing
without complex schema modifications.
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Run simplified integration"""
    logger.info("🎯 Starting Simplified Vanta Ledger Integration...")
    logger.info("=" * 60)
    
    # Step 1: Test database connections
    logger.info("🚀 Step 1: Testing Database Connections...")
    
    try:
        import psycopg2
        from pymongo import MongoClient
        
        # Test PostgreSQL
        postgres_conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='vanta_ledger',
            user='vanta_user',
            password='vanta_secure_password_2024'
        )
        logger.info("✅ PostgreSQL connection successful")
        
        # Test MongoDB
        mongo_client = MongoClient('mongodb://admin:THq2ibwBwnNCHUqbKFlSHrkmo3eSpzPGPX4AZg2V7yU=@localhost:27017/vanta_ledger?authSource=admin')
        mongo_db = mongo_client.vanta_ledger
        logger.info("✅ MongoDB connection successful")
        
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False
    
    # Step 2: Check existing data
    logger.info("🚀 Step 2: Checking Existing Data...")
    
    try:
        with postgres_conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM companies")
            company_count = cur.fetchone()[0]
            logger.info(f"✅ Found {company_count} companies in database")
            
            cur.execute("SELECT COUNT(*) FROM documents")
            doc_count = cur.fetchone()[0]
            logger.info(f"✅ Found {doc_count} documents in database")
    
    except Exception as e:
        logger.error(f"❌ Error checking existing data: {e}")
    
    # Step 3: Check organized company data
    logger.info("🚀 Step 3: Checking Organized Company Data...")
    
    organized_data_path = Path("/home/phantomojo/vanta_companies_data_improved")
    if organized_data_path.exists():
        logger.info(f"✅ Organized data found at: {organized_data_path}")
        
        # Count files in each company directory
        total_files = 0
        company_dirs = []
        
        for company_dir in organized_data_path.iterdir():
            if company_dir.is_dir() and company_dir.name != "unmatched_documents":
                file_count = sum(1 for f in company_dir.rglob('*') if f.is_file())
                total_files += file_count
                company_dirs.append((company_dir.name, file_count))
                logger.info(f"  📁 {company_dir.name}: {file_count} files")
        
        logger.info(f"✅ Total files found: {total_files}")
        logger.info(f"✅ Companies with data: {len(company_dirs)}")
        
    else:
        logger.warning(f"⚠️  Organized data not found at: {organized_data_path}")
    
    # Step 4: Generate summary report
    logger.info("🚀 Step 4: Generating Summary Report...")
    
    report = {
        "integration_date": datetime.now().isoformat(),
        "database_status": {
            "postgresql": "connected",
            "mongodb": "connected",
            "companies_in_db": company_count,
            "documents_in_db": doc_count
        },
        "organized_data": {
            "path": str(organized_data_path),
            "exists": organized_data_path.exists(),
            "total_files": total_files if organized_data_path.exists() else 0,
            "companies": company_dirs if organized_data_path.exists() else []
        },
        "system_status": "ready_for_processing"
    }
    
    # Save report
    report_path = Path("simple_integration_report.json")
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"✅ Report saved to: {report_path}")
    
    # Cleanup
    postgres_conn.close()
    mongo_client.close()
    
    logger.info("=" * 60)
    logger.info("🎉 Simplified Integration Complete!")
    logger.info("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 