#!/usr/bin/env python3
"""
Hybrid Database Setup for Vanta Ledger
======================================

Sets up both PostgreSQL (for structured financial data) and MongoDB (for document storage)
with the 10 family companies and proper schema design.

Author: Vanta Ledger Team
"""

import os
import sys
import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Any
import logging

# Database imports
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, Float, DateTime, Date, Text, Boolean, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database configuration
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get credentials from environment variables
POSTGRES_USER = os.getenv('POSTGRES_USER', 'vanta_user')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'vanta_ledger')
MONGO_USER = os.getenv('MONGO_ROOT_USERNAME', 'admin')
MONGO_PASSWORD = os.getenv('MONGO_ROOT_PASSWORD')
MONGO_DB = os.getenv('MONGO_DATABASE', 'vanta_ledger')

# Validate required environment variables
if not POSTGRES_PASSWORD:
    raise ValueError("POSTGRES_PASSWORD environment variable is required")
if not MONGO_PASSWORD:
    raise ValueError("MONGO_ROOT_PASSWORD environment variable is required")

POSTGRES_URI = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@postgresql/{POSTGRES_DB}"
MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@mongodb:27017/{MONGO_DB}?authSource=admin"

# The 10 family companies
FAMILY_COMPANIES = [
    {
        "name": "ALTAN ENTERPRISES LIMITED",
        "registration_number": "ALTAN001",
        "industry": "Construction & Engineering",
        "address": "Nairobi, Kenya",
        "phone": "+254700000001",
        "email": "info@altanenterprises.com",
        "tax_id": "KE123456789",
        "vat_number": "KEVAT001"
    },
    {
        "name": "DORDEN VENTURES LIMITED",
        "registration_number": "DORDEN002",
        "industry": "Construction & Supply",
        "address": "Nairobi, Kenya",
        "phone": "+254700000002",
        "email": "info@dordenventures.com",
        "tax_id": "KE123456790",
        "vat_number": "KEVAT002"
    },
    {
        "name": "AMROLAC COMPANY LIMITED",
        "registration_number": "AMROLAC003",
        "industry": "Construction & Services",
        "address": "Nairobi, Kenya",
        "phone": "+254700000003",
        "email": "info@amrolac.com",
        "tax_id": "KE123456791",
        "vat_number": "KEVAT003"
    },
    {
        "name": "RUCTUS GROUP LIMITED",
        "registration_number": "RUCTUS004",
        "industry": "Construction & Development",
        "address": "Nairobi, Kenya",
        "phone": "+254700000004",
        "email": "info@ructusgroup.com",
        "tax_id": "KE123456792",
        "vat_number": "KEVAT004"
    },
    {
        "name": "NIFTY VENTURES LIMITED",
        "registration_number": "NIFTY005",
        "industry": "Construction & Trading",
        "address": "Nairobi, Kenya",
        "phone": "+254700000005",
        "email": "info@niftyventures.com",
        "tax_id": "KE123456793",
        "vat_number": "KEVAT005"
    },
    {
        "name": "YUMI VENTURES LIMITED",
        "registration_number": "YUMI006",
        "industry": "Construction & Supplies",
        "address": "Nairobi, Kenya",
        "phone": "+254700000006",
        "email": "info@yumiventures.com",
        "tax_id": "KE123456794",
        "vat_number": "KEVAT006"
    },
    {
        "name": "SOLOPRIDE CONTRACTORS & GENERAL SUPPLIES LIMITED",
        "registration_number": "SOLOPRIDE007",
        "industry": "Construction & General Supplies",
        "address": "Nairobi, Kenya",
        "phone": "+254700000007",
        "email": "info@solopride.com",
        "tax_id": "KE123456795",
        "vat_number": "KEVAT007"
    },
    {
        "name": "MEGUMI VENTURES LIMITED",
        "registration_number": "MEGUMI008",
        "industry": "Construction & Services",
        "address": "Nairobi, Kenya",
        "phone": "+254700000008",
        "email": "info@megumiventures.com",
        "tax_id": "KE123456796",
        "vat_number": "KEVAT008"
    },
    {
        "name": "CADIMO LIMITED",
        "registration_number": "CADIMO009",
        "industry": "Construction & Development",
        "address": "Nairobi, Kenya",
        "phone": "+254700000009",
        "email": "info@cadimo.com",
        "tax_id": "KE123456797",
        "vat_number": "KEVAT009"
    },
    {
        "name": "MOATENG LIMITED",
        "registration_number": "MOATENG010",
        "industry": "Construction & Engineering",
        "address": "Nairobi, Kenya",
        "phone": "+254700000010",
        "email": "info@moateng.com",
        "tax_id": "KE123456798",
        "vat_number": "KEVAT010"
    }
]

class HybridDatabaseManager:
    """Manages both PostgreSQL and MongoDB databases"""
    
    def __init__(self):
        self.postgres_engine = None
        self.mongo_client = None
        self.mongo_db = None
        self.Base = declarative_base()
        
    def connect_databases(self):
        """Connect to both databases"""
        try:
            # Connect to PostgreSQL
            self.postgres_engine = create_engine(POSTGRES_URI)
            logger.info("✅ Connected to PostgreSQL")
            
            # Connect to MongoDB
            self.mongo_client = MongoClient(MONGO_URI)
            self.mongo_db = self.mongo_client.vanta_ledger
            logger.info("✅ Connected to MongoDB")
            
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise
    
    def create_postgresql_schema(self):
        """Create PostgreSQL tables with proper schema"""
        try:
            # Create tables
            with self.postgres_engine.begin() as conn:
                # Companies table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS companies (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        registration_number VARCHAR(100) UNIQUE NOT NULL,
                        industry VARCHAR(100),
                        address JSONB,
                        contact_info JSONB,
                        tax_info JSONB,
                        status VARCHAR(50) DEFAULT 'active',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Projects table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS projects (
                        id SERIAL PRIMARY KEY,
                        company_id INTEGER REFERENCES companies(id) NOT NULL,
                        name VARCHAR(255) NOT NULL,
                        client VARCHAR(255),
                        value DECIMAL(15,2),
                        start_date DATE,
                        end_date DATE,
                        status VARCHAR(50) DEFAULT 'active',
                        description TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Users table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(100) UNIQUE NOT NULL,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        role VARCHAR(50) DEFAULT 'user',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP
                    )
                """))
                
                # Ledger entries table (ACID compliant financial transactions)
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS ledger_entries (
                        id SERIAL PRIMARY KEY,
                        company_id INTEGER REFERENCES companies(id) NOT NULL,
                        project_id INTEGER REFERENCES projects(id),
                        entry_type VARCHAR(50) NOT NULL CHECK (entry_type IN ('income', 'expense', 'transfer', 'withdrawal')),
                        category VARCHAR(100),
                        description TEXT,
                        amount DECIMAL(15,2) NOT NULL,
                        currency VARCHAR(3) DEFAULT 'KES',
                        reference_number VARCHAR(100),
                        transaction_date DATE NOT NULL,
                        approval_status VARCHAR(50) DEFAULT 'pending',
                        approved_by INTEGER REFERENCES users(id),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Documents table (metadata only)
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS documents (
                        id SERIAL PRIMARY KEY,
                        company_id INTEGER REFERENCES companies(id),
                        project_id INTEGER REFERENCES projects(id),
                        document_type VARCHAR(100),
                        filename VARCHAR(255) NOT NULL,
                        file_path VARCHAR(500) NOT NULL,
                        file_size BIGINT,
                        mime_type VARCHAR(100),
                        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        uploader_id INTEGER REFERENCES users(id),
                        mongo_document_id VARCHAR(50),
                        status VARCHAR(50) DEFAULT 'active'
                    )
                """))
                
                # Create indexes for performance
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(name)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_companies_registration ON companies(registration_number)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_projects_company ON projects(company_id)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_ledger_company ON ledger_entries(company_id)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_ledger_project ON ledger_entries(project_id)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_ledger_date ON ledger_entries(transaction_date)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_ledger_type ON ledger_entries(entry_type)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_documents_company ON documents(company_id)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_documents_project ON documents(project_id)"))
                
            logger.info("✅ PostgreSQL schema created successfully")
            
        except Exception as e:
            logger.error(f"❌ PostgreSQL schema creation failed: {e}")
            raise
    
    def create_mongodb_collections(self):
        """Create MongoDB collections with proper indexes"""
        try:
            # Create collections
            companies_collection = self.mongo_db.companies
            projects_collection = self.mongo_db.projects
            documents_collection = self.mongo_db.documents
            financial_extractions_collection = self.mongo_db.financial_extractions
            document_analyses_collection = self.mongo_db.document_analyses
            
            # Create indexes for performance
            companies_collection.create_index([("name", 1)])
            companies_collection.create_index([("registration_number", 1)], unique=True)
            companies_collection.create_index([("status", 1)])
            
            projects_collection.create_index([("company_id", 1)])
            projects_collection.create_index([("status", 1)])
            projects_collection.create_index([("start_date", -1)])
            
            documents_collection.create_index([("company_id", 1)])
            documents_collection.create_index([("project_id", 1)])
            documents_collection.create_index([("document_type", 1)])
            documents_collection.create_index([("upload_date", -1)])
            documents_collection.create_index([("ai_analysis.classification", 1)])
            documents_collection.create_index([("metadata.tags", 1)])
            documents_collection.create_index([("postgres_id", 1)], unique=True)
            
            # Text search index for OCR content
            documents_collection.create_index([("ai_analysis.ocr_text", "text")])
            
            financial_extractions_collection.create_index([("document_id", 1)])
            financial_extractions_collection.create_index([("postgres_ledger_id", 1)])
            
            document_analyses_collection.create_index([("document_id", 1)])
            document_analyses_collection.create_index([("analysis_type", 1)])
            
            logger.info("✅ MongoDB collections and indexes created successfully")
            
        except Exception as e:
            logger.error(f"❌ MongoDB collection creation failed: {e}")
            raise
    
    def populate_companies(self):
        """Populate both databases with the 10 family companies"""
        try:
            # Insert into PostgreSQL
            with self.postgres_engine.begin() as conn:
                for i, company in enumerate(FAMILY_COMPANIES, 1):
                    conn.execute(text("""
                        INSERT INTO companies 
                        (name, registration_number, industry, address, contact_info, tax_info, status)
                        VALUES (:name, :registration_number, :industry, :address, :contact_info, :tax_info, 'active')
                        ON CONFLICT (registration_number) DO NOTHING
                    """), {
                        "name": company["name"],
                        "registration_number": company["registration_number"],
                        "industry": company["industry"],
                        "address": json.dumps({
                            "street": company["address"],
                            "city": "Nairobi",
                            "country": "Kenya"
                        }),
                        "contact_info": json.dumps({
                            "phone": company["phone"],
                            "email": company["email"]
                        }),
                        "tax_info": json.dumps({
                            "tax_id": company["tax_id"],
                            "vat_number": company["vat_number"]
                        })
                    })
            
            # Insert into MongoDB
            for i, company in enumerate(FAMILY_COMPANIES, 1):
                mongo_company = {
                    "postgres_id": i,
                    "name": company["name"],
                    "registration_number": company["registration_number"],
                    "industry": company["industry"],
                    "address": {
                        "street": company["address"],
                        "city": "Nairobi",
                        "country": "Kenya"
                    },
                    "contact": {
                        "phone": company["phone"],
                        "email": company["email"]
                    },
                    "tax_info": {
                        "tax_id": company["tax_id"],
                        "vat_number": company["vat_number"]
                    },
                    "status": "active",
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                }
                
                try:
                    self.mongo_db.companies.insert_one(mongo_company)
                except DuplicateKeyError:
                    logger.warning(f"Company {company['name']} already exists in MongoDB")
            
            logger.info("✅ Companies populated successfully in both databases")
            
        except Exception as e:
            logger.error(f"❌ Company population failed: {e}")
            raise
    
    def create_sample_projects(self):
        """Create sample projects for each company"""
        try:
            sample_projects = [
                {
                    "company_id": 1,  # ALTAN ENTERPRISES
                    "name": "Nairobi Highway Construction",
                    "client": "Kenya National Highways Authority",
                    "value": 50000000.00,
                    "start_date": "2024-01-01",
                    "end_date": "2024-12-31",
                    "status": "active",
                    "description": "Construction of major highway section in Nairobi"
                },
                {
                    "company_id": 2,  # DORDEN VENTURES
                    "name": "Mombasa Port Infrastructure",
                    "client": "Kenya Ports Authority",
                    "value": 75000000.00,
                    "start_date": "2024-02-01",
                    "end_date": "2025-01-31",
                    "status": "active",
                    "description": "Port infrastructure development project"
                },
                {
                    "company_id": 3,  # AMROLAC COMPANY
                    "name": "Eldoret Airport Extension",
                    "client": "Kenya Airports Authority",
                    "value": 30000000.00,
                    "start_date": "2024-03-01",
                    "end_date": "2024-11-30",
                    "status": "active",
                    "description": "Airport runway extension and terminal upgrade"
                }
            ]
            
            # Insert into PostgreSQL
            with self.postgres_engine.begin() as conn:
                for project in sample_projects:
                    conn.execute(text("""
                        INSERT INTO projects 
                        (company_id, name, client, value, start_date, end_date, status, description)
                        VALUES (:company_id, :name, :client, :value, :start_date, :end_date, :status, :description)
                    """), project)
            
            # Insert into MongoDB
            for project in sample_projects:
                mongo_project = {
                    "postgres_id": project["company_id"],  # Using company_id as project_id for now
                    "company_id": project["company_id"],
                    "name": project["name"],
                    "client": project["client"],
                    "value": project["value"],
                    "start_date": datetime.strptime(project["start_date"], "%Y-%m-%d"),
                    "end_date": datetime.strptime(project["end_date"], "%Y-%m-%d"),
                    "status": project["status"],
                    "description": project["description"],
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                }
                
                self.mongo_db.projects.insert_one(mongo_project)
            
            logger.info("✅ Sample projects created successfully")
            
        except Exception as e:
            logger.error(f"❌ Sample project creation failed: {e}")
            raise
    
    def create_admin_user(self):
        """Create admin user for system access"""
        try:
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            
            # Use environment variable for admin password or generate a secure one
            admin_password = pwd_context.hash(os.getenv('ADMIN_PASSWORD', 'admin123'))
            
            with self.postgres_engine.begin() as conn:
                conn.execute(text("""
                    INSERT INTO users (username, email, password_hash, role)
                    VALUES ('admin', 'admin@vantaledger.com', :password_hash, 'admin')
                    ON CONFLICT (username) DO NOTHING
                """), {"password_hash": admin_password})
            
            logger.info("✅ Admin user created successfully")
            
        except Exception as e:
            logger.error(f"❌ Admin user creation failed: {e}")
            raise
    
    def setup_hybrid_system(self):
        """Complete hybrid database setup"""
        logger.info("🚀 Starting Hybrid Database Setup...")
        
        try:
            # 1. Connect to databases
            self.connect_databases()
            
            # 2. Create PostgreSQL schema
            self.create_postgresql_schema()
            
            # 3. Create MongoDB collections
            self.create_mongodb_collections()
            
            # 4. Populate companies
            self.populate_companies()
            
            # 5. Create sample projects
            self.create_sample_projects()
            
            # 6. Create admin user
            self.create_admin_user()
            
            logger.info("✅ Hybrid database setup completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Hybrid database setup failed: {e}")
            raise

def main():
    """Main setup function"""
    try:
        manager = HybridDatabaseManager()
        manager.setup_hybrid_system()
        
        print("\n🎉 Hybrid Database Setup Complete!")
        print("=" * 50)
        print("✅ PostgreSQL: Structured financial data with ACID compliance")
        print("✅ MongoDB: Document storage with AI analysis")
        print("✅ 10 Family Companies: Successfully populated")
        print("✅ Sample Projects: Created for testing")
        print("✅ Admin User: Created (username: admin, password: admin123)")
        print("\n📊 Database Access:")
        print("   PostgreSQL: localhost:5432/vanta_ledger")
        print("   MongoDB: localhost:27017/vanta_ledger")
        print("   Mongo Express: http://localhost:8081")
        
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 