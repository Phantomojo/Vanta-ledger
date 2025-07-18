#!/usr/bin/env python3
"""
Database Setup Script for Vanta Ledger

This script sets up the PostgreSQL database and initializes the schema.
"""

import os
import sys
import subprocess
from pathlib import Path

def install_dependencies():
    """Install required Python packages"""
    print("Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    return True

def setup_postgresql():
    """Set up PostgreSQL database"""
    print("\nSetting up PostgreSQL database...")
    
    # Check if PostgreSQL is installed
    try:
        subprocess.run(["psql", "--version"], check=True, capture_output=True)
        print("✅ PostgreSQL is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ PostgreSQL not found. Please install PostgreSQL first:")
        print("   sudo apt update && sudo apt install postgresql postgresql-contrib")
        return False
    
    # Create database and user
    try:
        # Create user
        subprocess.run([
            "sudo", "-u", "postgres", "psql", "-c",
            "CREATE USER vanta_user WITH PASSWORD 'vanta_password';"
        ], check=True)
        print("✅ Created database user")
    except subprocess.CalledProcessError:
        print("⚠️  User might already exist, continuing...")
    
    try:
        # Create database
        subprocess.run([
            "sudo", "-u", "postgres", "psql", "-c",
            "CREATE DATABASE vanta_ledger OWNER vanta_user;"
        ], check=True)
        print("✅ Created database")
    except subprocess.CalledProcessError:
        print("⚠️  Database might already exist, continuing...")
    
    return True

def create_tables():
    """Create database tables"""
    print("\nCreating database tables...")
    try:
        # Add src to Python path
        src_path = Path(__file__).parent / "src"
        sys.path.insert(0, str(src_path))
        
        from vanta_ledger.database import create_tables
        create_tables()
        print("✅ Database tables created successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        return False

def create_sample_data():
    """Create sample companies and data"""
    print("\nCreating sample data...")
    try:
        from vanta_ledger.database import SessionLocal, Company, User
        from passlib.context import CryptContext
        
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        db = SessionLocal()
        
        # Create sample companies based on your document structure
        companies = [
            {
                "name": "MASTERBUILD LIMITED",
                "registration_number": "P051469193W",
                "pin_number": "P051469193W"
            },
            {
                "name": "BRIMMACS INVESTMENTS LIMITED",
                "registration_number": "CR12/2021",
                "pin_number": "P051454091G"
            },
            {
                "name": "CABERA ENTERPRISES LIMITED",
                "registration_number": "CR12/2022",
                "pin_number": "P051698969L"
            },
            {
                "name": "ALTAN ENTERPRISES LIMITED",
                "registration_number": "CR12/2023",
                "pin_number": "P051454091G"
            },
            {
                "name": "DORDEN VENTURES LIMITED",
                "registration_number": "CR12/2020",
                "pin_number": "P051454091G"
            },
            {
                "name": "NKONGE SOLUTION LIMITED",
                "registration_number": "CR12/2021",
                "pin_number": "P051454091G"
            },
            {
                "name": "NETZACH AGENCIES LIMITED",
                "registration_number": "CR12/2022",
                "pin_number": "P051454091G"
            },
            {
                "name": "ZERUBBABEL TAILOR WORKS LIMITED",
                "registration_number": "CR12/2020",
                "pin_number": "P051454091G"
            }
        ]
        
        for company_data in companies:
            existing = db.query(Company).filter(Company.name == company_data["name"]).first()
            if not existing:
                company = Company(**company_data)
                db.add(company)
        
        # Create admin user
        existing_user = db.query(User).filter(User.username == "admin").first()
        if not existing_user:
            admin_user = User(
                username="admin",
                email="admin@vanta-ledger.com",
                full_name="System Administrator",
                hashed_password=pwd_context.hash("admin123"),
                role="admin"
            )
            db.add(admin_user)
        
        db.commit()
        print("✅ Sample data created successfully!")
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to create sample data: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Vanta Ledger Database System")
    print("=" * 50)
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Setup PostgreSQL
    if not setup_postgresql():
        return False
    
    # Create tables
    if not create_tables():
        return False
    
    # Create sample data
    if not create_sample_data():
        return False
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Run the Paperless-ngx integration:")
    print("   cd src && python -m vanta_ledger.paperless_integration")
    print("2. Start the FastAPI server:")
    print("   cd src && uvicorn vanta_ledger.main:app --reload")
    print("3. Access the API at: http://localhost:8000")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 