"""
Setup Initial Data Module

This module provides functionality for setting up initial data for the system.
"""

import os
import uuid
from sqlalchemy.orm import Session
from src.vanta_ledger.models.user import UserDB
from src.vanta_ledger.utils.auth import get_password_hash
from src.vanta_ledger.database import SessionLocal, create_tables


def get_initial_passwords():
    """Get initial passwords from environment variables."""
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
    auntie_password = os.getenv("AUNTIE_PASSWORD", "auntie123")
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
                # Create admin user
                admin_user = UserDB(
                    id=str(uuid.uuid4()),
                    username="admin",
                    email="admin@vantaledger.com",
                    hashed_password=get_password_hash(admin_password),
                    role="admin",
                )
                db.add(admin_user)
                print("✅ Admin user created successfully.")

            # Check if auntie user already exists
            auntie_user = db.query(UserDB).filter(UserDB.username == "auntie").first()

            if not auntie_user:
                # Create auntie user
                auntie_user = UserDB(
                    id=str(uuid.uuid4()),
                    username="auntie",
                    email="auntie@vantaledger.com",
                    hashed_password=get_password_hash(auntie_password),
                    role="user",
                )
                db.add(auntie_user)
                print("✅ Auntie user created successfully.")

            print("🎉 Initial data setup completed successfully!")

    except Exception as e:
        print(f"❌ Error setting up initial data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    setup_initial_data() 