#!/usr/bin/env python3
"""
Secure Admin User Creation Script
Uses environment variables for credentials - no hardcoded secrets
"""

import os
import sys
import getpass
from pathlib import Path
import logging
logger = logging.getLogger(__name__)

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def create_secure_admin():
    """Create admin user using secure environment variables"""
    
    logger.info("🔐 Vanta Ledger - Secure Admin User Creation")
    logger.info("=")
    
    # Check if admin credentials are set in environment
    admin_username = os.getenv("ADMIN_USERNAME")
    admin_email = os.getenv("ADMIN_EMAIL") 
    admin_password = os.getenv("ADMIN_PASSWORD")
    
    # If not in environment, prompt securely
    if not admin_username:
        admin_username = input("Enter admin username (default: admin): ").strip() or "admin"
    
    if not admin_email:
        admin_email = input("Enter admin email (default: admin@vantaledger.com): ").strip() or "admin@vantaledger.com"
    
    if not admin_password:
        logger.info("\n⚠️  Admin password not found in ADMIN_PASSWORD environment variable")
        admin_password = getpass.getpass("Enter secure admin password (min 8 characters): ")
        
        if len(admin_password) < 8:
            logger.info("❌ Password must be at least 8 characters long")
            return False
    
    # Set environment variables for the initialization
    os.environ["ADMIN_USERNAME"] = admin_username
    os.environ["ADMIN_EMAIL"] = admin_email
    os.environ["ADMIN_PASSWORD"] = admin_password
    
    try:
        # Import and run database initialization
        from vanta_ledger.database_init import get_database_initializer
        
        db_init = get_database_initializer()
        
        logger.info("\n📊 Creating database tables...")
        if not db_init.create_tables():
            logger.error("❌ Failed to create database tables")
            return False
        
        logger.info("👤 Creating admin user...")
        if not db_init.create_initial_admin():
            logger.error("❌ Failed to create admin user")
            return False
        
        logger.info("\n✅ Admin user created successfully!")
        logger.info(f"   Username: {admin_username}")
        logger.info(f"   Email: {admin_email}")
        logger.info("   Role: admin")
        logger.info("\n🔒 Security Notes:")
        logger.info("   - Password is securely hashed in database")
        logger.info("   - Change password after first login")
        logger.info("   - Clear ADMIN_PASSWORD environment variable")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Clear any existing password from environment after use
    try:
        success = create_secure_admin()
        sys.exit(0 if success else 1)
    finally:
        # Clear the password from environment for security
        if "ADMIN_PASSWORD" in os.environ:
            del os.environ["ADMIN_PASSWORD"]
