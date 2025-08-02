
#!/usr/bin/env python3
"""
Simplified Database Setup for Replit Environment
"""

import os
import sys

def setup_environment():
    """Setup environment variables and paths"""
    # Set database URL for local SQLite (fallback)
    if not os.getenv("DATABASE_URL"):
        os.environ["DATABASE_URL"] = "sqlite:///./vanta_ledger.db"
    
    # Add src to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.join(current_dir, "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

def create_basic_tables():
    """Create basic database tables"""
    print("🗃️ Setting up Vanta Ledger Database...")
    
    try:
        # Import after setting up paths
        from vanta_ledger.database import Base, engine, SessionLocal
        from vanta_ledger.database import Company, Project, Document, User
        
        # Create all tables
        print("📋 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        
        # Create a session and add sample data
        db = SessionLocal()
        
        # Check if we already have data
        if db.query(Company).count() > 0:
            print("✅ Database already has data")
            db.close()
            return True
            
        # Add sample companies
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
            )
        ]
        
        for company in companies:
            db.add(company)
            
        # Add admin user
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        admin_user = User(
            username="admin",
            email="admin@familybusiness.co.ke",
            full_name="System Administrator",
            hashed_password=pwd_context.hash("admin123"),
            role="admin",
            is_active=True
        )
        db.add(admin_user)
        
        # Add sample project
        sample_project = Project(
            name="Government Tender Project",
            description="Sample construction project",
            status="tendering",
            company_id=1,
            contract_value=5000000.00,
            project_type="construction"
        )
        db.add(sample_project)
        
        db.commit()
        db.close()
        
        print("✅ Sample data created!")
        print("🔑 Admin Login: admin / admin123")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("🔧 Installing dependencies...")
        return False
    except Exception as e:
        print(f"❌ Database setup error: {e}")
        return False

if __name__ == "__main__":
    setup_environment()
    if create_basic_tables():
        print("🎯 Database setup complete! Ready to start the API.")
    else:
        print("❌ Database setup failed. Check the error messages above.")
