#!/usr/bin/env python3
"""
Setup initial data for Vanta Ledger
Creates default users and companies for the system
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from vanta_ledger.database import SessionLocal, create_tables
from vanta_ledger.models.user import User
from vanta_ledger.models.company import Company
from vanta_ledger.auth import get_password_hash

def setup_initial_data():
    """Setup initial data for the system"""
    
    # Get passwords from environment or use defaults
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
    auntie_password = os.getenv("AUNTIE_PASSWORD", "auntie123")
    
    # Create database tables
    print("📊 Creating database tables...")
    create_tables()
    
    db = SessionLocal()
    
    try:
        # Check if admin user already exists
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            print("👤 Creating admin user...")
            admin_user = User(
                username="admin",
                name="System Administrator",
                email="admin@vantaledger.com",
                hashed_password=get_password_hash(admin_password),
                role="admin"
            )
            db.add(admin_user)
            print(f"✅ Admin user created (username: admin, password: {admin_password})")
        
        # Check if Auntie Nyaruai user exists
        auntie_user = db.query(User).filter(User.username == "auntie_nyaruai").first()
        if not auntie_user:
            print("👤 Creating Auntie Nyaruai user...")
            auntie_user = User(
                username="auntie_nyaruai",
                name="Ruth Nyaruai",
                email="ruth.nyaruai@company.com",
                hashed_password=get_password_hash(auntie_password),
                role="admin"
            )
            db.add(auntie_user)
            print(f"✅ Auntie Nyaruai user created (username: auntie_nyaruai, password: {auntie_password})")
        
        # Create default companies
        companies_data = [
            {
                "name": "Solopride Contractors & General Supplies Ltd",
                "registration_number": "C123456",
                "pin_number": "P123456789A",
                "phone": "+254729631861",
                "email": "info@solopride.com",
                "address": "P.O BOX 1092, NANYUKI"
            },
            {
                "name": "Company 2",
                "registration_number": "C789012",
                "pin_number": "P987654321B",
                "phone": "+254700000000",
                "email": "info@company2.com",
                "address": "Nairobi, Kenya"
            },
            {
                "name": "Company 3",
                "registration_number": "C345678",
                "pin_number": "P456789123C",
                "phone": "+254711111111",
                "email": "info@company3.com",
                "address": "Mombasa, Kenya"
            }
        ]
        
        for company_data in companies_data:
            existing_company = db.query(Company).filter(Company.name == company_data["name"]).first()
            if not existing_company:
                print(f"🏢 Creating company: {company_data['name']}")
                company = Company(**company_data)
                db.add(company)
                print(f"✅ Company created: {company_data['name']}")
        
        db.commit()
        print("🎉 Initial data setup completed successfully!")
        print("\n📋 Default Users:")
        print(f"   - Admin: admin / {admin_password}")
        print(f"   - Auntie Nyaruai: auntie_nyaruai / {auntie_password}")
        print("\n🏢 Default Companies:")
        print("   - Solopride Contractors & General Supplies Ltd")
        print("   - Company 2")
        print("   - Company 3")
        
    except Exception as e:
        print(f"❌ Error setting up initial data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    setup_initial_data() 