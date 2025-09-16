#!/usr/bin/env python3
"""
Create admin user for Vanta Ledger
"""

import os
import sys
import getpass
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from vanta_ledger.services.user_service import get_user_service, init_user_service
from vanta_ledger.models.user_models import UserCreate
from vanta_ledger.database import get_db_session
import logging
logger = logging.getLogger(__name__)

def create_admin_user():
    """
    Creates an admin user with secure credentials in the Vanta Ledger system.
    
    Returns:
        The created admin user object if successful, or None if user creation fails.
    """
    try:
        # Get admin credentials from environment or prompt securely
        username = os.getenv("ADMIN_USERNAME", "admin")
        email = os.getenv("ADMIN_EMAIL", "admin@vanta.com")
        password = os.getenv("ADMIN_PASSWORD")
        
        if not password:
            # Prompt without echo; fail in non-interactive environments
            try:
                password = getpass.getpass("Enter admin password: ")
            except Exception:
                raise RuntimeError("ADMIN_PASSWORD not set and no TTY available for prompting")
        
        role = os.getenv("ADMIN_ROLE", "admin")
        
        # Initialize database session and user service
        session = get_db_session()
        init_user_service(session)
        user_service = get_user_service()
        
        # Create admin user
        admin_data = UserCreate(
            username=username,
            email=email,
            password=password,
            role=role
        )
        
        user = user_service.create_user(admin_data)
        logger.info("✅ Admin user created successfully!")
        logger.info(f"   Username: {username}")
        logger.info(f"   Email: {email}")
        logger.info(f"   Role: {role}")
        # Note: password intentionally not printed
        
        return user
        
    except Exception as e:
        logger.error(f"❌ Error creating admin user: {e}")
        return None

if __name__ == "__main__":
    create_admin_user() 