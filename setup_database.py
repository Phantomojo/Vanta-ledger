
#!/usr/bin/env python3
"""
Database Setup Script for Vanta Ledger Filing System

Sets up PostgreSQL database for comprehensive document management
and financial tracking for family construction business.
"""

import os
import sys
from pathlib import Path

# Add src to Python path for Replit environment
current_dir = Path(__file__).parent
src_path = current_dir / "src"
sys.path.insert(0, str(src_path))

# Set environment variables for database
os.environ.setdefault("DATABASE_URL", "postgresql://replit:password@db.postgres.replit.com:5432/replit")

def setup_filing_system():
    """Set up the comprehensive filing system database"""
    print("🗃️ Setting up Vanta Ledger Filing System Database...")
    
    try:
        from vanta_ledger.database import engine, SessionLocal, Base, Company, Project, Document, User
        from passlib.context import CryptContext
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created")
        
        # Create session
        db = SessionLocal()
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # Check if data already exists
        if db.query(Company).count() > 0:
            print("✅ Database already initialized with data")
            db.close()
            return
        
        # Create your actual family companies based on the documents
        companies = [
            Company(
                name="MASTERBUILD LIMITED",
                registration_number="P051469193W",
                pin_number="P051469193W",
                agpo_number="AGPO001",
                phone="+254700000001",
                email="masterbuild@familybusiness.co.ke",
                address="Nairobi, Kenya",
                is_active=True
            ),
            Company(
                name="BRIMMACS INVESTMENTS LIMITED", 
                registration_number="CR12/2021",
                pin_number="P051454091G",
                agpo_number="AGPO002",
                phone="+254700000002",
                email="brimmacs@familybusiness.co.ke",
                address="Nairobi, Kenya",
                is_active=True
            ),
            Company(
                name="CABERA ENTERPRISES LIMITED",
                registration_number="CR12/2022",
                pin_number="P051698969L",
                agpo_number="AGPO003",
                phone="+254700000003",
                email="cabera@familybusiness.co.ke", 
                address="Nairobi, Kenya",
                is_active=True
            ),
            Company(
                name="ALTAN ENTERPRISES LIMITED",
                registration_number="CR12/2023",
                pin_number="P051454091G",
                agpo_number="AGPO004",
                phone="+254700000004",
                email="altan@familybusiness.co.ke",
                address="Nairobi, Kenya",
                is_active=True
            ),
            Company(
                name="DORDEN VENTURES LIMITED",
                registration_number="CR12/2020",
                pin_number="P051454091G",
                agpo_number="AGPO005",
                phone="+254700000005", 
                email="dorden@familybusiness.co.ke",
                address="Nairobi, Kenya",
                is_active=True
            )
        ]
        
        for company in companies:
            db.add(company)
        
        # Create admin user for the filing system
        admin_user = User(
            username="admin",
            email="admin@familybusiness.co.ke",
            full_name="Family Business Administrator",
            hashed_password=pwd_context.hash("change_password_123"),
            role="admin",
            is_active=True
        )
        db.add(admin_user)
        
        # Create sample project categories for tender tracking
        sample_projects = [
            Project(
                name="Government Road Construction Tender",
                description="Main highway construction project",
                status="tendering",
                company_id=1,
                contract_value=5000000.00,
                project_type="road"
            ),
            Project(
                name="School Building Project",
                description="Primary school construction",
                status="active", 
                company_id=2,
                contract_value=2500000.00,
                project_type="building"
            ),
            Project(
                name="Water Pipeline Installation",
                description="Municipal water infrastructure",
                status="completed",
                company_id=3,
                contract_value=1800000.00,
                project_type="infrastructure"
            )
        ]
        
        for project in sample_projects:
            db.add(project)
        
        db.commit()
        print("✅ Filing system initialized successfully!")
        print("\n📊 Created:")
        print(f"   🏢 {len(companies)} Family Companies")
        print(f"   👤 1 Admin User")
        print(f"   📋 {len(sample_projects)} Sample Projects")
        print("\n🔑 Login Credentials:")
        print("   Username: admin")
        print("   Password: change_password_123")
        print("\n🎯 Next Steps:")
        print("   1. Start the backend: Click Run button")
        print("   2. Access API docs: http://localhost:5000/docs")
        print("   3. Start web dashboard for file management")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error setting up filing system: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    setup_filing_system()
