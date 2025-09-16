#!/usr/bin/env python3
"""
Hybrid Database System Setup for Vanta Ledger
============================================

Complete setup script for the hybrid database system with PostgreSQL and MongoDB.
This script will:
1. Start the database containers
2. Initialize the hybrid database schema
3. Populate with the 10 family companies
4. Create sample data for testing

Author: Vanta Ledger Team
"""

import os
import sys
import subprocess
import time
import requests
import json
from pathlib import Path
import logging
logger = logging.getLogger(__name__)

def run_command(command: str, cwd: str = None) -> bool:
    """Run a shell command and return success status"""
    try:
        logger.info(f"🔄 Running: {command}")
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info(f"✅ Success: {command}")
            return True
        else:
            logger.error(f"❌ Failed: {command}")
            logger.error(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Exception running {command}: {e}")
        return False

def wait_for_service(url: str, service_name: str, max_attempts: int = 30) -> bool:
    """Wait for a service to be ready"""
    logger.info(f"⏳ Waiting for {service_name} to be ready...")
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                logger.info(f"✅ {service_name} is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        logger.info(f"   Attempt {attempt + 1}/{max_attempts}...")
        time.sleep(2)
    
    logger.error(f"❌ {service_name} failed to start")
    return False

def setup_directories():
    """Create necessary directories"""
    directories = [
        "database/postgresql/init",
        "database/mongodb/init",
        "logs",
        "data/uploads",
        "data/processed_documents"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ Created directory: {directory}")

def create_postgresql_init_script():
    """Create PostgreSQL initialization script"""
    init_script = """
-- PostgreSQL initialization script for Vanta Ledger
-- This script runs when the PostgreSQL container starts

-- Create database if it doesn't exist
SELECT 'CREATE DATABASE vanta_ledger'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'vanta_ledger')\\gexec

-- Connect to the database
\\c vanta_ledger;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create custom functions
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'PostgreSQL database initialized successfully for Vanta Ledger';
END $$;
"""
    
    with open("database/postgresql/init/01-init.sql", "w") as f:
        f.write(init_script)
    
    logger.info("✅ Created PostgreSQL initialization script")

def create_mongodb_init_script():
    """Create MongoDB initialization script"""
    init_script = """
// MongoDB initialization script for Vanta Ledger
// This script runs when the MongoDB container starts

// Switch to the vanta_ledger database
use vanta_ledger;

// Create collections with proper validation
db.createCollection("companies", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["name", "registration_number"],
            properties: {
                name: { bsonType: "string" },
                registration_number: { bsonType: "string" },
                industry: { bsonType: "string" },
                status: { bsonType: "string" }
            }
        }
    }
});

db.createCollection("documents", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["filename", "file_path"],
            properties: {
                filename: { bsonType: "string" },
                file_path: { bsonType: "string" },
                document_type: { bsonType: "string" },
                company_id: { bsonType: "number" }
            }
        }
    }
});

db.createCollection("financial_extractions");
db.createCollection("document_analyses");

// Create indexes for performance
db.companies.createIndex({ "name": 1 });
db.companies.createIndex({ "registration_number": 1 }, { unique: true });
db.companies.createIndex({ "status": 1 });

db.documents.createIndex({ "company_id": 1 });
db.documents.createIndex({ "project_id": 1 });
db.documents.createIndex({ "document_type": 1 });
db.documents.createIndex({ "upload_date": -1 });
db.documents.createIndex({ "postgres_id": 1 }, { unique: true });

// Text search index for OCR content
db.documents.createIndex({ "ai_analysis.ocr_text": "text" });

logger.info("MongoDB database initialized successfully for Vanta Ledger");
"""
    
    with open("database/mongodb/init/01-init.js", "w") as f:
        f.write(init_script)
    
    logger.info("✅ Created MongoDB initialization script")

def start_database_containers():
    """Start the database containers using Docker Compose"""
    logger.info("🚀 Starting database containers...")
    
    # Stop any existing containers
    run_command("docker-compose -f database/docker-compose-hybrid.yml down")
    
    # Start containers
    success = run_command("docker-compose -f database/docker-compose-hybrid.yml up -d")
    
    if not success:
        logger.error("❌ Failed to start database containers")
        return False
    
    # Wait for services to be ready
    logger.info("⏳ Waiting for database services to be ready...")
    time.sleep(10)
    
    # Check PostgreSQL
    postgres_ready = wait_for_service("http://localhost:5432", "PostgreSQL", 30)
    
    # Check MongoDB
    mongo_ready = wait_for_service("http://localhost:27017", "MongoDB", 30)
    
    # Check Mongo Express
    mongo_express_ready = wait_for_service("http://localhost:8081", "Mongo Express", 20)
    
    # Check pgAdmin
    pgadmin_ready = wait_for_service("http://localhost:8080", "pgAdmin", 20)
    
    if all([postgres_ready, mongo_ready, mongo_express_ready, pgadmin_ready]):
        logger.info("✅ All database services are ready!")
        return True
    else:
        logger.error("❌ Some database services failed to start")
        return False

def run_hybrid_database_setup():
    """Run the hybrid database setup script"""
    logger.info("🔧 Running hybrid database setup...")
    
    # Install required Python packages
    logger.info("📦 Installing Python dependencies...")
    success = run_command("pip install -r backend/requirements-hybrid.txt")
    
    if not success:
        logger.error("❌ Failed to install Python dependencies")
        return False
    
    # Run the hybrid database setup
    success = run_command("python database/hybrid_database_setup.py")
    
    if not success:
        logger.error("❌ Failed to run hybrid database setup")
        return False
    
    logger.info("✅ Hybrid database setup completed successfully!")
    return True

def create_environment_file():
    """
    Create a `.env` file with environment variables for database connections, application settings, security, file storage, cache, and optional Redis configuration.
    """
    env_content = """# Vanta Ledger Hybrid Database Configuration

# Database URIs
POSTGRES_URI=postgresql://vanta_user:vanta_password@localhost:5432/vanta_ledger
MONGO_URI=mongodb://admin:${MONGO_INITDB_ROOT_PASSWORD}@localhost:27017/vanta_ledger

# Application Settings
DEBUG=True
HOST=0.0.0.0
PORT=8500

# Security
SECRET_KEY=${SECRET_KEY}
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Storage
UPLOAD_DIR=../data/uploads
PROCESSED_DOCUMENTS_DIR=../data/processed_documents

# Cache
CACHE_DURATION=300
DEFAULT_PAGE_SIZE=100
MAX_PAGE_SIZE=1000

# Redis (optional)
REDIS_URL=redis://localhost:6379
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    logger.info("✅ Created environment configuration file")

def display_setup_summary():
    """Display setup summary and next steps"""
    logger.info("\n")
    logger.info("🎉 HYBRID DATABASE SYSTEM SETUP COMPLETE!")
    logger.info("=")
    
    logger.info("\n📊 Database Services:")
    logger.info("   ✅ PostgreSQL: localhost:5432/vanta_ledger")
    logger.info("   ✅ MongoDB: localhost:27017/vanta_ledger")
    logger.info("   ✅ Mongo Express: http://localhost:8081")
    logger.info("   ✅ pgAdmin: http://localhost:8080")
    logger.info("   ✅ Redis: localhost:6379")
    
    logger.info("\n👥 The 10 Family Companies:")
    companies = [
        "1. ALTAN ENTERPRISES LIMITED",
        "2. DORDEN VENTURES LIMITED", 
        "3. AMROLAC COMPANY LIMITED",
        "4. RUCTUS GROUP LIMITED",
        "5. NIFTY VENTURES LIMITED",
        "6. YUMI VENTURES LIMITED",
        "7. SOLOPRIDE CONTRACTORS & GENERAL SUPPLIES LIMITED",
        "8. MEGUMI VENTURES LIMITED",
        "9. CADIMO LIMITED",
        "10. MOATENG LIMITED"
    ]
    
    for company in companies:
        logger.info(f"   {company}")
    
    logger.info("\n🔐 Admin Access:")
    logger.info("   Username: admin")
    logger.info("   Password: Check your .env file or use create_secure_admin.py")
    
    logger.info("\n🚀 Next Steps:")
    logger.info("   1. Start the backend: python backend/app/main.py")
    logger.info("   2. Start the frontend: cd frontend/frontend-web && npm run dev")
    logger.info("   3. Access the application: http://localhost:5173")
    logger.info("   4. View database management:")
    logger.info("      - MongoDB: http://localhost:8081")
    logger.info("      - PostgreSQL: http://localhost:8080")
    
    logger.info("\n📚 Documentation:")
    logger.info("   - API Documentation: http://localhost:8500/docs")
    logger.info("   - Database Schema: database/hybrid_database_setup.py")
    logger.info("   - Configuration: .env")
    
    logger.info("\n")

def main():
    """Main setup function"""
    logger.info("🚀 Vanta Ledger Hybrid Database System Setup")
    logger.info("=")
    
    try:
        # 1. Setup directories
        logger.info("\n📁 Setting up directories...")
        setup_directories()
        
        # 2. Create initialization scripts
        logger.info("\n📝 Creating database initialization scripts...")
        create_postgresql_init_script()
        create_mongodb_init_script()
        
        # 3. Start database containers
        logger.info("\n🐳 Starting database containers...")
        if not start_database_containers():
            logger.error("❌ Failed to start database containers")
            sys.exit(1)
        
        # 4. Run hybrid database setup
        logger.info("\n🔧 Running hybrid database setup...")
        if not run_hybrid_database_setup():
            logger.error("❌ Failed to run hybrid database setup")
            sys.exit(1)
        
        # 5. Create environment file
        logger.info("\n⚙️ Creating environment configuration...")
        create_environment_file()
        
        # 6. Display summary
        display_setup_summary()
        
    except KeyboardInterrupt:
        logger.info("\n❌ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 