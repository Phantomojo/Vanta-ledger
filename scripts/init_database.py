#!/usr/bin/env python3
"""
Database Initialization Script
Sets up the database tables and creates initial admin user
"""

import os
import sys
import logging
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from vanta_ledger.models.user_models import Base, UserDB
from vanta_ledger.services.user_service import UserService
from vanta_ledger.models.user_models import UserCreate
from vanta_ledger.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_database_engine():
    """
    Create and return a SQLAlchemy database engine using the application's PostgreSQL URI.
    
    Returns:
        engine: A SQLAlchemy Engine instance connected to the configured PostgreSQL database.
    
    Raises:
        Exception: If the engine creation fails.
    """
    try:
        # Extract database URL from PostgreSQL URI
        db_url = settings.POSTGRES_URI.replace("postgresql://", "postgresql://")
        engine = create_engine(db_url)
        return engine
    except Exception as e:
        logger.error(f"Failed to create database engine: {e}")
        raise

def create_tables(engine):
    """
    Create all database tables defined in the application's ORM metadata using the provided SQLAlchemy engine.
    
    Parameters:
        engine: SQLAlchemy engine instance used to connect to the target database.
    """
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        raise

def create_initial_admin_user(session):
    """
    Creates an initial admin user if one does not already exist.
    
    Uses environment variables to avoid hardcoded credentials.
    Requires ADMIN_PASSWORD to be provided via environment.
    """
    try:
        user_service = UserService(session)
        
        # Check if admin user already exists
        existing_admin = user_service.get_user_by_username("admin")
        if existing_admin:
            logger.info("✅ Admin user already exists")
            return existing_admin
        
        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        admin_email = os.getenv("ADMIN_EMAIL", "admin@vantaledger.com")
        admin_password = os.getenv("ADMIN_PASSWORD")
        
        if not admin_password or len(admin_password) < 12:
            raise RuntimeError("ADMIN_PASSWORD must be set and at least 12 characters for initial admin creation")
        
        # Create admin user
        admin_data = UserCreate(
            username=admin_username,
            email=admin_email,
            password=admin_password,
            role="admin"
        )
        
        admin_user = user_service.create_user(admin_data)
        logger.info("✅ Initial admin user created successfully")
        logger.info(f"   Username: {admin_user.username}")
        logger.info(f"   Email: {admin_user.email}")
        logger.info(f"   Role: {admin_user.role}")
        logger.warning("⚠️  Ensure the admin password is rotated and stored securely.")
        
        return admin_user
        
    except Exception as e:
        logger.error(f"Failed to create admin user: {e}")
        raise

def test_database_connection(engine):
    """
    Checks if the database connection is operational by executing a simple test query.
    
    Parameters:
        engine: SQLAlchemy engine instance used to connect to the database.
    
    Returns:
        bool: True if the connection is successful, False otherwise.
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            logger.info("✅ Database connection successful")
            return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

def main():
    """
    Orchestrates the database initialization process for the Vanta Ledger application.
    
    This function tests the database connection, creates the necessary tables, and sets up an initial admin user using secure environment-provided credentials.
    """
    logger.info("🚀 Initializing Vanta Ledger Database")
    logger.info("=" * 50)
    
    try:
        # Test database connection
        if not test_database_connection(create_database_engine()):
            logger.error("❌ Database connection failed. Please check your configuration.")
            sys.exit(1)
        
        # Create engine and session
        engine = create_database_engine()
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()
        
        # Create tables
        create_tables(engine)
        
        # Create initial admin user (requires ADMIN_PASSWORD)
        create_initial_admin_user(session)
        
        # Close session
        session.close()
        
        logger.info("🎉 Database initialization completed successfully!")
        logger.info("\n📋 Next Steps:")
        logger.info("1. Start the application")
        logger.info("2. Configure RBAC and rotate admin credentials if needed")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 