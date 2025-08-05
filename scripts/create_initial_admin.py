#!/usr/bin/env python3
"""
Script to create an initial admin user with a secure password.
This should be run during the first deployment.
"""
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

import getpass
from sqlalchemy.orm import Session

from src.vanta_ledger.database import SessionLocal, engine
from src.vanta_ledger import models, schemas, crud
from src.vanta_ledger.config import settings

def init_db(db: Session) -> None:
    """Initialize the database with the first admin user."""
    # Create all tables
    models.Base.metadata.create_all(bind=engine)
    
    # Check if admin user already exists
    admin = crud.user.get_by_email(db, email=settings.FIRST_SUPERUSER)
    if admin:
        print(f"Admin user {settings.FIRST_SUPERUSER} already exists.")
        return
    
    # Prompt for admin password
    while True:
        password = getpass.getpass("Enter admin password: ")
        password_confirm = getpass.getpass("Confirm admin password: ")
        
        if password != password_confirm:
            print("Passwords do not match. Please try again.")
            continue
            
        # Validate password strength
        from src.vanta_ledger.utils.password import validate_password_strength
        is_valid, message = validate_password_strength(password)
        if not is_valid:
            print(f"Password is not strong enough: {message}")
            print(f"Password must be at least {settings.MIN_PASSWORD_LENGTH} characters long and include:")
            print("- Uppercase letters")
            print("- Lowercase letters")
            print("- Numbers")
            print("- Special characters")
            continue
            
        break
    
    # Create admin user
    user_in = schemas.UserCreate(
        email=settings.FIRST_SUPERUSER,
        password=password,
        full_name="Admin User",
        is_superuser=True,
    )
    
    # Create the user
    user = crud.user.create(db, obj_in=user_in)
    print(f"Admin user {user.email} created successfully!")

def main():
    """Main entry point."""
    print("Setting up initial admin user...")
    db = SessionLocal()
    try:
        init_db(db)
    except Exception as e:
        print(f"Error setting up admin user: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
