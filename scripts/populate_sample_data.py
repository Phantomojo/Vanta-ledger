#!/usr/bin/env python3
"""
Populate Sample Data Script
Adds sample data to the database for testing the frontend
"""

import sys
from pathlib import Path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from vanta_ledger.database_init import get_database_initializer
from vanta_ledger.models import Company, Project, LedgerEntry
from datetime import datetime, timedelta
import random
import logging
logger = logging.getLogger(__name__)

def populate_sample_data():
    """Populate database with sample data"""
    try:
        logger.info("🚀 Populating database with sample data...")
        db_init = get_database_initializer()
        session = db_init.SessionLocal()
        
        try:
            # Check if data already exists
            company_count = session.query(Company).count()
            if company_count > 0:
                logger.info(f"✅ Database already has {company_count} companies, skipping population")
                return True
            
            logger.info("📊 Creating sample companies...")
            
            # Sample companies
            companies = [
                Company(
                    name="Acme Corporation",
                    industry="Technology",
                    revenue=5000000.0,
                    registration_number="AC001",
                    company_type="business_partner",
                    status="active"
                ),
                Company(
                    name="Global Industries Ltd",
                    industry="Manufacturing",
                    revenue=12000000.0,
                    registration_number="GI002",
                    company_type="business_partner",
                    status="active"
                ),
                Company(
                    name="Tech Solutions Inc",
                    industry="Software",
                    revenue=8000000.0,
                    registration_number="TS003",
                    company_type="business_partner",
                    status="active"
                ),
                Company(
                    name="Green Energy Co",
                    industry="Renewable Energy",
                    revenue=3000000.0,
                    registration_number="GE004",
                    company_type="business_partner",
                    status="active"
                ),
                Company(
                    name="Financial Services Group",
                    industry="Banking",
                    revenue=25000000.0,
                    registration_number="FS005",
                    company_type="business_partner",
                    status="active"
                )
            ]
            
            for company in companies:
                session.add(company)
            session.commit()
            logger.info(f"✅ Created {len(companies)} sample companies")
            
            logger.info("📋 Creating sample projects...")
            
            # Sample projects
            projects = [
                Project(
                    name="Website Redesign",
                    status="active",
                    budget=50000.0,
                    description="Modernize company website with new design and features",
                    start_date=datetime.now() - timedelta(days=30),
                    end_date=datetime.now() + timedelta(days=60)
                ),
                Project(
                    name="Mobile App Development",
                    status="active",
                    budget=75000.0,
                    description="Develop iOS and Android mobile applications",
                    start_date=datetime.now() - timedelta(days=15),
                    end_date=datetime.now() + timedelta(days=90)
                ),
                Project(
                    name="Database Migration",
                    status="completed",
                    budget=25000.0,
                    description="Migrate from legacy database to new cloud solution",
                    start_date=datetime.now() - timedelta(days=90),
                    end_date=datetime.now() - timedelta(days=10)
                ),
                Project(
                    name="Security Audit",
                    status="on_hold",
                    budget=15000.0,
                    description="Comprehensive security assessment and recommendations",
                    start_date=datetime.now() - timedelta(days=45),
                    end_date=datetime.now() + timedelta(days=30)
                )
            ]
            
            for project in projects:
                session.add(project)
            session.commit()
            logger.info(f"✅ Created {len(projects)} sample projects")
            
            logger.info("💰 Creating sample ledger entries...")
            
            # Sample ledger entries
            ledger_entries = [
                LedgerEntry(
                    transaction_date=datetime.now() - timedelta(days=5),
                    description="Office supplies purchase",
                    amount=1250.50,
                    account_name="Office Expenses",
                    transaction_type="debit",
                    reference="INV-001"
                ),
                LedgerEntry(
                    transaction_date=datetime.now() - timedelta(days=3),
                    description="Client payment received",
                    amount=5000.00,
                    account_name="Accounts Receivable",
                    transaction_type="credit",
                    reference="REC-001"
                ),
                LedgerEntry(
                    transaction_date=datetime.now() - timedelta(days=1),
                    description="Software license renewal",
                    amount=2500.00,
                    account_name="Software Expenses",
                    transaction_type="debit",
                    reference="INV-002"
                ),
                LedgerEntry(
                    transaction_date=datetime.now(),
                    description="Bank interest earned",
                    amount=150.75,
                    account_name="Interest Income",
                    transaction_type="credit",
                    reference="INT-001"
                )
            ]
            
            for entry in ledger_entries:
                session.add(entry)
            session.commit()
            logger.info(f"✅ Created {len(ledger_entries)} sample ledger entries")
            
            logger.info("🎉 Database population completed successfully!")
            logger.info(f"   Companies: {session.query(Company).count()}")
            logger.info(f"   Projects: {session.query(Project).count()}")
            logger.info(f"   Ledger Entries: {session.query(LedgerEntry).count()}")
            
            return True
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"❌ Error populating database: {e}")
        return False

if __name__ == "__main__":
    populate_sample_data()
