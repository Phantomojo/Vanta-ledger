#!/usr/bin/env python3
"""
Setup initial data for Vanta Ledger
Creates default users and companies for the system
"""

import sys
import os
from pathlib import Path
from getpass import getpass
import json
import uuid

# Add the src directory to Python path
src_path = (Path(__file__).parent / "src").resolve()
if src_path.exists() and str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from vanta_ledger.database import SessionLocal, create_tables
from vanta_ledger.models.user_models import UserDB
from vanta_ledger.models.company import Company
from vanta_ledger.auth import get_password_hash


def get_initial_passwords():
    """Fetch initial passwords from environment, error if missing/weak."""
    admin_password = os.getenv("ADMIN_PASSWORD")
    auntie_password = os.getenv("AUNTIE_PASSWORD")
    if not admin_password or len(admin_password) < 12:
        raise RuntimeError("ADMIN_PASSWORD must be set and at least 12 characters")
    if not auntie_password or len(auntie_password) < 12:
        raise RuntimeError("AUNTIE_PASSWORD must be set and at least 12 characters")
    return admin_password, auntie_password


def setup_initial_data():
    """Setup initial data for the system"""
    
    admin_password, auntie_password = get_initial_passwords()
    print("✅ Initial passwords loaded from environment.")
    
    # Create database tables
    print("📊 Creating database tables...")
    create_tables()
    
    db = SessionLocal()
    
    try:
        with db.begin():
            # Check if admin user already exists
            admin_user = db.query(UserDB).filter(UserDB.username == "admin").first()
            if not admin_user:
                print("👤 Creating admin user...")
                admin_user = UserDB(
                    id=str(uuid.uuid4()),
                    username="admin",
                    email="admin@vantaledger.com",
                    hashed_password=get_password_hash(admin_password),
                    role="admin"
                )
                db.add(admin_user)
                print(f"✅ Admin user created (username: admin)")
            
            # Check if Auntie Nyaruai user exists
            auntie_user = db.query(UserDB).filter(UserDB.username == "auntie_nyaruai").first()
            if not auntie_user:
                print("👤 Creating Auntie Nyaruai user...")
                auntie_user = UserDB(
                    id=str(uuid.uuid4()),
                    username="auntie_nyaruai",
                    email="ruth.nyaruai@company.com",
                    hashed_password=get_password_hash(auntie_password),
                    role="admin"
                )
                db.add(auntie_user)
                print(f"✅ Auntie Nyaruai user created (username: auntie_nyaruai)")
            
            # Create default companies using enhanced model structure
            companies_data = [
                {
                    "name": "Solopride Contractors & General Supplies Ltd",
                    "registration_number": "C123456",
                    "industry": "Construction & General Supplies",
                    "company_type": "core_family",
                    "status": "active",
                    "address": json.dumps({
                        "street": "P.O BOX 1092",
                        "city": "NANYUKI",
                        "country": "Kenya"
                    }),
                    "contact_info": json.dumps({
                        "phone": "+254729631861",
                        "email": "info@solopride.com"
                    }),
                    "tax_info": json.dumps({
                        "tax_id": "KE123456789",
                        "vat_number": "KEVAT001",
                        "pin_number": "P123456789A"
                    })
                },
                {
                    "name": "Company 2",
                    "registration_number": "C789012",
                    "industry": "General Business",
                    "company_type": "business_partner",
                    "status": "active",
                    "address": json.dumps({
                        "street": "Nairobi",
                        "city": "Nairobi",
                        "country": "Kenya"
                    }),
                    "contact_info": json.dumps({
                        "phone": "+254700000000",
                        "email": "info@company2.com"
                    }),
                    "tax_info": json.dumps({
                        "tax_id": "KE987654321",
                        "vat_number": "KEVAT002",
                        "pin_number": "P987654321B"
                    })
                },
                {
                    "name": "Company 3",
                    "registration_number": "C345678",
                    "industry": "Trading & Services",
                    "company_type": "subsidiary",
                    "status": "active",
                    "address": json.dumps({
                        "street": "Mombasa",
                        "city": "Mombasa",
                        "country": "Kenya"
                    }),
                    "contact_info": json.dumps({
                        "phone": "+254711111111",
                        "email": "info@company3.com"
                    }),
                    "tax_info": json.dumps({
                        "tax_id": "KE456789123",
                        "vat_number": "KEVAT003",
                        "pin_number": "P456789123C"
                    })
                }
            ]
            
            for company_data in companies_data:
                existing_company = db.query(Company).filter(Company.name == company_data["name"]).first()
                if not existing_company:
                    print(f"🏢 Creating company: {company_data['name']}")
                    company = Company(**company_data)
                    db.add(company)
                    print(f"✅ Company created: {company_data['name']}")
        print("🎉 Initial data setup completed successfully!")
        print("\n📋 Default Users:")
        print(f"   - Admin: admin")
        print(f"   - Auntie Nyaruai: auntie_nyaruai")
        print("\n🏢 Default Companies:")
        print("   - Solopride Contractors & General Supplies Ltd")
        print("   - Company 2")
        print("   - Company 3")
        
    except Exception as e:
        print(f"❌ Error setting up initial data: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    setup_initial_data() 