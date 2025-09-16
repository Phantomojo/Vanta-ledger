#!/usr/bin/env python3
"""
Enhanced Hybrid Database Setup for Vanta Ledger
===============================================

Sets up both PostgreSQL (for structured financial data) and MongoDB (for document storage)
with ALL 29 companies discovered in the data, network analysis capabilities, and enhanced
document processing schema.

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
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, Float, DateTime, Date, Text, Boolean, DECIMAL, JSON
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

# Get credentials from environment variables with defaults
POSTGRES_USER = os.getenv('POSTGRES_USER', 'vanta_user')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'vanta_ledger')
MONGO_USER = os.getenv('MONGO_ROOT_USERNAME', 'admin')
MONGO_PASSWORD = os.getenv('MONGO_ROOT_PASSWORD')
MONGO_DB = os.getenv('MONGO_DATABASE', 'vanta_ledger')

# Debug: Print connection info (without password)
logger.info(f"PostgreSQL: {POSTGRES_USER}@{POSTGRES_DB}")
logger.info(f"MongoDB: {MONGO_USER}@{MONGO_DB}")

POSTGRES_URI = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost/{POSTGRES_DB}"
MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@localhost:27017/{MONGO_DB}?authSource=admin"

# ALL 29 Companies (10 Original + 19 Additional)
ALL_COMPANIES = [
    # Original 10 Vanta Ledger Companies
    {
        "name": "ALTAN ENTERPRISES LIMITED",
        "registration_number": "ALTAN001",
        "industry": "Construction & Engineering",
        "address": "Nairobi, Kenya",
        "phone": "+254700000001",
        "email": "info@altanenterprises.com",
        "tax_id": "KE123456789",
        "vat_number": "KEVAT001",
        "company_type": "core_family",
        "status": "active"
    },
    {
        "name": "DORDEN VENTURES LIMITED",
        "registration_number": "DORDEN002",
        "industry": "Construction & Supply",
        "address": "Nairobi, Kenya",
        "phone": "+254700000002",
        "email": "info@dordenventures.com",
        "tax_id": "KE123456790",
        "vat_number": "KEVAT002",
        "company_type": "core_family",
        "status": "active"
    },
    {
        "name": "AMROLAC COMPANY LIMITED",
        "registration_number": "AMROLAC003",
        "industry": "Construction & Services",
        "address": "Nairobi, Kenya",
        "phone": "+254700000003",
        "email": "info@amrolac.com",
        "tax_id": "KE123456791",
        "vat_number": "KEVAT003",
        "company_type": "core_family",
        "status": "active"
    },
    {
        "name": "RUCTUS GROUP LIMITED",
        "registration_number": "RUCTUS004",
        "industry": "Construction & Development",
        "address": "Nairobi, Kenya",
        "phone": "+254700000004",
        "email": "info@ructusgroup.com",
        "tax_id": "KE123456792",
        "vat_number": "KEVAT004",
        "company_type": "core_family",
        "status": "active"
    },
    {
        "name": "NIFTY VENTURES LIMITED",
        "registration_number": "NIFTY005",
        "industry": "Construction & Trading",
        "address": "Nairobi, Kenya",
        "phone": "+254700000005",
        "email": "info@niftyventures.com",
        "tax_id": "KE123456793",
        "vat_number": "KEVAT005",
        "company_type": "core_family",
        "status": "active"
    },
    {
        "name": "YUMI VENTURES LIMITED",
        "registration_number": "YUMI006",
        "industry": "Construction & Supplies",
        "address": "Nairobi, Kenya",
        "phone": "+254700000006",
        "email": "info@yumiventures.com",
        "tax_id": "KE123456794",
        "vat_number": "KEVAT006",
        "company_type": "core_family",
        "status": "active"
    },
    {
        "name": "SOLOPRIDE CONTRACTORS & GENERAL SUPPLIES LIMITED",
        "registration_number": "SOLOPRIDE007",
        "industry": "Construction & General Supplies",
        "address": "Nairobi, Kenya",
        "phone": "+254700000007",
        "email": "info@solopride.com",
        "tax_id": "KE123456795",
        "vat_number": "KEVAT007",
        "company_type": "core_family",
        "status": "active"
    },
    {
        "name": "MEGUMI VENTURES LIMITED",
        "registration_number": "MEGUMI008",
        "industry": "Construction & Services",
        "address": "Nairobi, Kenya",
        "phone": "+254700000008",
        "email": "info@megumiventures.com",
        "tax_id": "KE123456796",
        "vat_number": "KEVAT008",
        "company_type": "core_family",
        "status": "active"
    },
    {
        "name": "CADIMO LIMITED",
        "registration_number": "CADIMO009",
        "industry": "Construction & Development",
        "address": "Nairobi, Kenya",
        "phone": "+254700000009",
        "email": "info@cadimo.com",
        "tax_id": "KE123456797",
        "vat_number": "KEVAT009",
        "company_type": "core_family",
        "status": "active"
    },
    {
        "name": "MOATENG LIMITED",
        "registration_number": "MOATENG010",
        "industry": "Construction & Engineering",
        "address": "Nairobi, Kenya",
        "phone": "+254700000010",
        "email": "info@moateng.com",
        "tax_id": "KE123456798",
        "vat_number": "KEVAT010",
        "company_type": "core_family",
        "status": "active"
    },
    
    # Additional 19 Companies Discovered
    {
        "name": "NKONGE SOLUTION LIMITED",
        "registration_number": "NKONGE011",
        "industry": "Construction & Solutions",
        "address": "Nairobi, Kenya",
        "phone": "+254700000011",
        "email": "info@nkongesolution.com",
        "tax_id": "KE123456799",
        "vat_number": "KEVAT011",
        "company_type": "business_partner",
        "status": "active"
    },
    {
        "name": "CABERA SOLUTIONS LIMITED",
        "registration_number": "CABERA012",
        "industry": "Solutions Provider",
        "address": "Nairobi, Kenya",
        "phone": "+254700000012",
        "email": "info@caberasolutions.com",
        "tax_id": "KE123456800",
        "vat_number": "KEVAT012",
        "company_type": "business_partner",
        "status": "active"
    },
    {
        "name": "NETZACH AGENCIES LIMITED",
        "registration_number": "NETZACH013",
        "industry": "Agency Services",
        "address": "Nairobi, Kenya",
        "phone": "+254700000013",
        "email": "info@netzachagencies.com",
        "tax_id": "KE123456801",
        "vat_number": "KEVAT013",
        "company_type": "business_partner",
        "status": "active"
    },
    {
        "name": "BRIMMACS INVESTMENTS LIMITED",
        "registration_number": "BRIMMACS014",
        "industry": "Investment Company",
        "address": "Nairobi, Kenya",
        "phone": "+254700000014",
        "email": "info@brimmacsinvestments.com",
        "tax_id": "KE123456802",
        "vat_number": "KEVAT014",
        "company_type": "business_partner",
        "status": "active"
    },
    {
        "name": "COLESON SOLUTIONS LIMITED",
        "registration_number": "COLESON015",
        "industry": "Solutions Provider",
        "address": "Nairobi, Kenya",
        "phone": "+254700000015",
        "email": "info@colesonsolutions.com",
        "tax_id": "KE123456803",
        "vat_number": "KEVAT015",
        "company_type": "business_partner",
        "status": "active"
    },
    {
        "name": "DYLENE ENTERPRISES LIMITED",
        "registration_number": "DYLENE016",
        "industry": "Enterprise Services",
        "address": "Nairobi, Kenya",
        "phone": "+254700000016",
        "email": "info@dyleneenterprises.com",
        "tax_id": "KE123456804",
        "vat_number": "KEVAT016",
        "company_type": "business_partner",
        "status": "active"
    },
    {
        "name": "STARVELS ENTERPRISES LIMITED",
        "registration_number": "STARVELS017",
        "industry": "Enterprise Services",
        "address": "Nairobi, Kenya",
        "phone": "+254700000017",
        "email": "info@starvelsenterprises.com",
        "tax_id": "KE123456805",
        "vat_number": "KEVAT017",
        "company_type": "business_partner",
        "status": "active"
    },
    {
        "name": "PUMUNDUMA LIMITED",
        "registration_number": "PUMUNDUMA018",
        "industry": "Limited Company",
        "address": "Nairobi, Kenya",
        "phone": "+254700000018",
        "email": "info@pumunduma.com",
        "tax_id": "KE123456806",
        "vat_number": "KEVAT018",
        "company_type": "subsidiary",
        "status": "active"
    },
    {
        "name": "WEDOCAX LIMITED",
        "registration_number": "WEDOCAX019",
        "industry": "Limited Company",
        "address": "Nairobi, Kenya",
        "phone": "+254700000019",
        "email": "info@wedocax.com",
        "tax_id": "KE123456807",
        "vat_number": "KEVAT019",
        "company_type": "subsidiary",
        "status": "active"
    },
    {
        "name": "MASTERBUILD LIMITED",
        "registration_number": "MASTERBUILD020",
        "industry": "Construction Company",
        "address": "Nairobi, Kenya",
        "phone": "+254700000020",
        "email": "info@masterbuild.com",
        "tax_id": "KE123456808",
        "vat_number": "KEVAT020",
        "company_type": "business_partner",
        "status": "active"
    },
    {
        "name": "PASAKIS LIMITED",
        "registration_number": "PASAKIS021",
        "industry": "Limited Company",
        "address": "Nairobi, Kenya",
        "phone": "+254700000021",
        "email": "info@pasakis.com",
        "tax_id": "KE123456809",
        "vat_number": "KEVAT021",
        "company_type": "subsidiary",
        "status": "active"
    },
    {
        "name": "WILLMAT LIMITED",
        "registration_number": "WILLMAT022",
        "industry": "Limited Company",
        "address": "Nairobi, Kenya",
        "phone": "+254700000022",
        "email": "info@willmat.com",
        "tax_id": "KE123456810",
        "vat_number": "KEVAT022",
        "company_type": "subsidiary",
        "status": "active"
    },
    {
        "name": "DAMAGIS LIMITED",
        "registration_number": "DAMAGIS023",
        "industry": "Limited Company",
        "address": "Nairobi, Kenya",
        "phone": "+254700000023",
        "email": "info@damagis.com",
        "tax_id": "KE123456811",
        "vat_number": "KEVAT023",
        "company_type": "subsidiary",
        "status": "active"
    },
    {
        "name": "CHAJORUMA LIMITED",
        "registration_number": "CHAJORUMA024",
        "industry": "Limited Company",
        "address": "Nairobi, Kenya",
        "phone": "+254700000024",
        "email": "info@chajoruma.com",
        "tax_id": "KE123456812",
        "vat_number": "KEVAT024",
        "company_type": "subsidiary",
        "status": "active"
    },
    {
        "name": "ARXANE LIMITED",
        "registration_number": "ARXANE025",
        "industry": "Limited Company",
        "address": "Nairobi, Kenya",
        "phone": "+254700000025",
        "email": "info@arxane.com",
        "tax_id": "KE123456813",
        "vat_number": "KEVAT025",
        "company_type": "subsidiary",
        "status": "active"
    },
    {
        "name": "MOREMEX LIMITED",
        "registration_number": "MOREMEX026",
        "industry": "Limited Company",
        "address": "Nairobi, Kenya",
        "phone": "+254700000026",
        "email": "info@moremex.com",
        "tax_id": "KE123456814",
        "vat_number": "KEVAT026",
        "company_type": "subsidiary",
        "status": "active"
    },
    {
        "name": "TWIN EIGHT LIMITED",
        "registration_number": "TWINEIGHT027",
        "industry": "Limited Company",
        "address": "Nairobi, Kenya",
        "phone": "+254700000027",
        "email": "info@twinight.com",
        "tax_id": "KE123456815",
        "vat_number": "KEVAT027",
        "company_type": "subsidiary",
        "status": "active"
    },
    {
        "name": "ADIMU ENTERPRISES LIMITED",
        "registration_number": "ADIMU028",
        "industry": "Enterprise Services",
        "address": "Nairobi, Kenya",
        "phone": "+254700000028",
        "email": "info@adimuenterprises.com",
        "tax_id": "KE123456816",
        "vat_number": "KEVAT028",
        "company_type": "business_partner",
        "status": "active"
    },
    {
        "name": "KICUNA LIMITED",
        "registration_number": "KICUNA029",
        "industry": "Limited Company",
        "address": "Nairobi, Kenya",
        "phone": "+254700000029",
        "email": "info@kicuna.com",
        "tax_id": "KE123456817",
        "vat_number": "KEVAT029",
        "company_type": "subsidiary",
        "status": "active"
    }
]

class EnhancedHybridDatabaseManager:
    """Enhanced database manager with network analysis and document processing capabilities"""
    
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
    
    def create_enhanced_postgresql_schema(self):
        """Create enhanced PostgreSQL schema with network analysis capabilities"""
        try:
            with self.postgres_engine.begin() as conn:
                # Enhanced Companies table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS companies (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        registration_number VARCHAR(100) UNIQUE NOT NULL,
                        industry VARCHAR(100),
                        address JSONB,
                        contact_info JSONB,
                        tax_info JSONB,
                        company_type VARCHAR(50) DEFAULT 'business_partner',
                        status VARCHAR(50) DEFAULT 'active',
                        network_centrality_score FLOAT DEFAULT 0.0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Enhanced Projects table
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
                        project_type VARCHAR(100),
                        location VARCHAR(255),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Company Relationships table for network analysis
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS company_relationships (
                        id SERIAL PRIMARY KEY,
                        company_a_id INTEGER REFERENCES companies(id) NOT NULL,
                        company_b_id INTEGER REFERENCES companies(id) NOT NULL,
                        relationship_type VARCHAR(100) NOT NULL,
                        relationship_strength FLOAT DEFAULT 1.0,
                        description TEXT,
                        evidence_documents JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(company_a_id, company_b_id, relationship_type)
                    )
                """))
                
                # Enhanced Users table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(100) UNIQUE NOT NULL,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        role VARCHAR(50) DEFAULT 'user',
                        company_id INTEGER REFERENCES companies(id),
                        permissions JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP
                    )
                """))
                
                # Enhanced Ledger entries table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS ledger_entries (
                        id SERIAL PRIMARY KEY,
                        company_id INTEGER REFERENCES companies(id) NOT NULL,
                        project_id INTEGER REFERENCES projects(id),
                        related_company_id INTEGER REFERENCES companies(id),
                        entry_type VARCHAR(50) NOT NULL CHECK (entry_type IN ('income', 'expense', 'transfer', 'withdrawal', 'investment', 'loan')),
                        category VARCHAR(100),
                        subcategory VARCHAR(100),
                        description TEXT,
                        amount DECIMAL(15,2) NOT NULL,
                        currency VARCHAR(3) DEFAULT 'KES',
                        reference_number VARCHAR(100),
                        transaction_date DATE NOT NULL,
                        approval_status VARCHAR(50) DEFAULT 'pending',
                        approved_by INTEGER REFERENCES users(id),
                        metadata JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Enhanced Documents table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS documents (
                        id SERIAL PRIMARY KEY,
                        company_id INTEGER REFERENCES companies(id),
                        project_id INTEGER REFERENCES projects(id),
                        document_type VARCHAR(100),
                        document_category VARCHAR(100),
                        filename VARCHAR(255) NOT NULL,
                        original_path VARCHAR(500) NOT NULL,
                        file_size BIGINT,
                        mime_type VARCHAR(100),
                        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        uploader_id INTEGER REFERENCES users(id),
                        mongo_document_id VARCHAR(50),
                        processing_status VARCHAR(50) DEFAULT 'pending',
                        extracted_data JSONB,
                        ai_analysis JSONB,
                        status VARCHAR(50) DEFAULT 'active'
                    )
                """))
                
                # Document Categories table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS document_categories (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        description TEXT,
                        parent_id INTEGER REFERENCES document_categories(id),
                        company_id INTEGER REFERENCES companies(id),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Network Analysis Results table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS network_analysis (
                        id SERIAL PRIMARY KEY,
                        analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        analysis_type VARCHAR(100) NOT NULL,
                        company_id INTEGER REFERENCES companies(id),
                        centrality_metrics JSONB,
                        relationship_metrics JSONB,
                        financial_metrics JSONB,
                        risk_assessment JSONB,
                        recommendations JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Analytics Dashboard table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS analytics_dashboard (
                        id SERIAL PRIMARY KEY,
                        dashboard_name VARCHAR(255) NOT NULL,
                        dashboard_type VARCHAR(100) NOT NULL,
                        company_id INTEGER REFERENCES companies(id),
                        data_sources JSONB,
                        metrics JSONB,
                        filters JSONB,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Create enhanced indexes
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(name)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_companies_type ON companies(company_type)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_companies_registration ON companies(registration_number)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_projects_company ON projects(company_id)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_relationships_company_a ON company_relationships(company_a_id)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_relationships_company_b ON company_relationships(company_b_id)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_ledger_company ON ledger_entries(company_id)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_ledger_project ON ledger_entries(project_id)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_ledger_date ON ledger_entries(transaction_date)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_ledger_type ON ledger_entries(entry_type)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_documents_company ON documents(company_id)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_documents_category ON documents(document_category)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(processing_status)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_network_analysis_company ON network_analysis(company_id)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_analytics_company ON analytics_dashboard(company_id)"))
                
            logger.info("✅ Enhanced PostgreSQL schema created successfully")
            
        except Exception as e:
            logger.error(f"❌ Enhanced PostgreSQL schema creation failed: {e}")
            raise
    
    def create_enhanced_mongodb_collections(self):
        """Create enhanced MongoDB collections with document processing capabilities"""
        try:
            # Enhanced collections
            companies_collection = self.mongo_db.companies
            projects_collection = self.mongo_db.projects
            documents_collection = self.mongo_db.documents
            financial_extractions_collection = self.mongo_db.financial_extractions
            network_analysis_collection = self.mongo_db.network_analysis
            document_processing_collection = self.mongo_db.document_processing
            analytics_collection = self.mongo_db.analytics
            
            # Create indexes for performance
            companies_collection.create_index([("name", 1)])
            companies_collection.create_index([("registration_number", 1)])
            companies_collection.create_index([("company_type", 1)])
            
            projects_collection.create_index([("company_id", 1)])
            projects_collection.create_index([("status", 1)])
            
            documents_collection.create_index([("company_id", 1)])
            documents_collection.create_index([("document_type", 1)])
            documents_collection.create_index([("processing_status", 1)])
            documents_collection.create_index([("upload_date", -1)])
            
            financial_extractions_collection.create_index([("company_id", 1)])
            financial_extractions_collection.create_index([("document_id", 1)])
            financial_extractions_collection.create_index([("extraction_date", -1)])
            
            network_analysis_collection.create_index([("company_id", 1)])
            network_analysis_collection.create_index([("analysis_date", -1)])
            
            document_processing_collection.create_index([("document_id", 1)])
            document_processing_collection.create_index([("status", 1)])
            
            analytics_collection.create_index([("company_id", 1)])
            analytics_collection.create_index([("dashboard_type", 1)])
            
            logger.info("✅ Enhanced MongoDB collections created successfully")
            
        except Exception as e:
            logger.error(f"❌ Enhanced MongoDB collections creation failed: {e}")
            raise
    
    def populate_all_companies(self):
        """Populate all 29 companies in both databases"""
        try:
            # Populate PostgreSQL
            with self.postgres_engine.begin() as conn:
                for company in ALL_COMPANIES:
                    conn.execute(text("""
                        INSERT INTO companies (name, registration_number, industry, address, contact_info, tax_info, company_type, status)
                        VALUES (:name, :reg_num, :industry, :address, :contact_info, :tax_info, :company_type, :status)
                        ON CONFLICT (registration_number) DO UPDATE SET
                        name = EXCLUDED.name,
                        industry = EXCLUDED.industry,
                        address = EXCLUDED.address,
                        contact_info = EXCLUDED.contact_info,
                        tax_info = EXCLUDED.tax_info,
                        company_type = EXCLUDED.company_type,
                        status = EXCLUDED.status,
                        updated_at = CURRENT_TIMESTAMP
                    """), {
                        'name': company['name'],
                        'reg_num': company['registration_number'],
                        'industry': company['industry'],
                        'address': json.dumps({'address': company['address']}),
                        'contact_info': json.dumps({
                            'phone': company['phone'],
                            'email': company['email']
                        }),
                        'tax_info': json.dumps({
                            'tax_id': company['tax_id'],
                            'vat_number': company['vat_number']
                        }),
                        'company_type': company['company_type'],
                        'status': company['status']
                    })
            
            # Populate MongoDB
            companies_collection = self.mongo_db.companies
            for company in ALL_COMPANIES:
                company_doc = {
                    'name': company['name'],
                    'registration_number': company['registration_number'],
                    'industry': company['industry'],
                    'address': company['address'],
                    'contact_info': {
                        'phone': company['phone'],
                        'email': company['email']
                    },
                    'tax_info': {
                        'tax_id': company['tax_id'],
                        'vat_number': company['vat_number']
                    },
                    'company_type': company['company_type'],
                    'status': company['status'],
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                }
                
                companies_collection.update_one(
                    {'registration_number': company['registration_number']},
                    {'$set': company_doc},
                    upsert=True
                )
            
            logger.info(f"✅ Successfully populated all {len(ALL_COMPANIES)} companies")
            
        except Exception as e:
            logger.error(f"❌ Company population failed: {e}")
            raise
    
    def create_network_relationships(self):
        """Create initial network relationships based on company types"""
        try:
            with self.postgres_engine.begin() as conn:
                # Get all companies
                companies = conn.execute(text("SELECT id, name, company_type FROM companies")).fetchall()
                
                # Create relationships based on company types
                for company in companies:
                    company_id = company[0]
                    company_name = company[1]
                    company_type = company[2]
                    
                    # Core family companies are connected to each other
                    if company_type == 'core_family':
                        for other_company in companies:
                            if (other_company[0] != company_id and 
                                other_company[2] == 'core_family'):
                                conn.execute(text("""
                                    INSERT INTO company_relationships 
                                    (company_a_id, company_b_id, relationship_type, relationship_strength, description)
                                    VALUES (:a_id, :b_id, :rel_type, :strength, :desc)
                                    ON CONFLICT (company_a_id, company_b_id, relationship_type) DO NOTHING
                                """), {
                                    'a_id': company_id,
                                    'b_id': other_company[0],
                                    'rel_type': 'family_connection',
                                    'strength': 0.9,
                                    'desc': f'Family business connection between {company_name} and {other_company[1]}'
                                })
                    
                    # Business partners are connected to core family companies
                    elif company_type == 'business_partner':
                        for other_company in companies:
                            if other_company[2] == 'core_family':
                                conn.execute(text("""
                                    INSERT INTO company_relationships 
                                    (company_a_id, company_b_id, relationship_type, relationship_strength, description)
                                    VALUES (:a_id, :b_id, :rel_type, :strength, :desc)
                                    ON CONFLICT (company_a_id, company_b_id, relationship_type) DO NOTHING
                                """), {
                                    'a_id': company_id,
                                    'b_id': other_company[0],
                                    'rel_type': 'business_partnership',
                                    'strength': 0.7,
                                    'desc': f'Business partnership between {company_name} and {other_company[1]}'
                                })
                    
                    # Subsidiaries are connected to core family companies
                    elif company_type == 'subsidiary':
                        for other_company in companies:
                            if other_company[2] == 'core_family':
                                conn.execute(text("""
                                    INSERT INTO company_relationships 
                                    (company_a_id, company_b_id, relationship_type, relationship_strength, description)
                                    VALUES (:a_id, :b_id, :rel_type, :strength, :desc)
                                    ON CONFLICT (company_a_id, company_b_id, relationship_type) DO NOTHING
                                """), {
                                    'a_id': company_id,
                                    'b_id': other_company[0],
                                    'rel_type': 'subsidiary_connection',
                                    'strength': 0.8,
                                    'desc': f'Subsidiary relationship between {company_name} and {other_company[1]}'
                                })
            
            logger.info("✅ Network relationships created successfully")
            
        except Exception as e:
            logger.error(f"❌ Network relationships creation failed: {e}")
            raise
    
    def setup_enhanced_system(self):
        """Set up the complete enhanced hybrid system"""
        try:
            logger.info("🚀 Setting up Enhanced Vanta Ledger Hybrid System...")
            
            # Connect to databases
            self.connect_databases()
            
            # Create schemas
            self.create_enhanced_postgresql_schema()
            self.create_enhanced_mongodb_collections()
            
            # Populate data
            self.populate_all_companies()
            self.create_network_relationships()
            
            logger.info("✅ Enhanced Vanta Ledger system setup complete!")
            logger.info(f"📊 Total companies in system: {len(ALL_COMPANIES)}")
            logger.info("🔗 Network analysis ready")
            logger.info("📄 Document processing ready")
            logger.info("📈 Analytics dashboard ready")
            
        except Exception as e:
            logger.error(f"❌ Enhanced system setup failed: {e}")
            raise

def main():
    """Main function to run the enhanced setup"""
    try:
        manager = EnhancedHybridDatabaseManager()
        manager.setup_enhanced_system()
        
        logger.info("\n🎉 Enhanced Vanta Ledger Database Setup Complete!")
        logger.info("=")
        logger.info(f"📊 Companies: {len(ALL_COMPANIES)} total")
        logger.info("🔗 Network Analysis: Ready")
        logger.info("📄 Document Processing: Ready")
        logger.info("📈 Analytics: Ready")
        logger.info("=")
        
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 