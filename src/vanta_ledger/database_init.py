#!/usr/bin/env python3
"""
Secure Database Initialization Module
Creates database tables and initial admin user using environment variables
"""

import os
import uuid
import logging
from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from .models.user_models import Base, UserDB
from .auth import AuthService
from .config import settings

logger = logging.getLogger(__name__)

class DatabaseInitializer:
    """Handles secure database initialization"""
    
    def __init__(self):
        """Initialize database connection"""
        if not settings.POSTGRES_URI:
            raise ValueError("POSTGRES_URI must be set in environment variables")
        
        self.engine = create_engine(settings.POSTGRES_URI)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def create_tables(self):
        """Create all database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("✅ Database tables created successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create database tables: {e}")
            return False
    
    def create_initial_admin(self) -> bool:
        """
        Create initial admin user using environment variables
        Requires ADMIN_USERNAME, ADMIN_EMAIL, and ADMIN_PASSWORD to be set
        """
        try:
            # Get admin credentials from environment
            admin_username = os.getenv("ADMIN_USERNAME", "admin")
            admin_email = os.getenv("ADMIN_EMAIL", "admin@vantaledger.com")
            admin_password = os.getenv("ADMIN_PASSWORD")
            
            if not admin_password:
                logger.error("❌ ADMIN_PASSWORD environment variable must be set")
                return False
            
            if len(admin_password) < 8:
                logger.error("❌ ADMIN_PASSWORD must be at least 8 characters long")
                return False
            
            # Create session
            session = self.SessionLocal()
            
            try:
                # Check if admin user already exists
                existing_admin = session.query(UserDB).filter(UserDB.username == admin_username).first()
                if existing_admin:
                    logger.info(f"✅ Admin user '{admin_username}' already exists")
                    return True
                
                # Create new admin user
                user_id = str(uuid.uuid4())
                hashed_password = AuthService.get_password_hash(admin_password)
                
                admin_user = UserDB(
                    id=user_id,
                    username=admin_username,
                    email=admin_email,
                    hashed_password=hashed_password,
                    is_active=True,
                    role="admin",
                    created_at=datetime.utcnow()
                )
                
                session.add(admin_user)
                session.commit()
                
                logger.info(f"✅ Admin user '{admin_username}' created successfully")
                logger.info(f"   Email: {admin_email}")
                logger.info(f"   Role: admin")
                logger.warning("⚠️  Please change the admin password after first login")
                
                return True
                
            except Exception as e:
                session.rollback()
                logger.error(f"❌ Failed to create admin user: {e}")
                return False
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"❌ Admin user creation failed: {e}")
            return False
    
    def initialize_database(self) -> bool:
        """
        Complete database initialization
        Creates tables and initial admin user
        """
        logger.info("🚀 Initializing database...")
        
        # Create tables
        if not self.create_tables():
            return False
        
        # Create initial admin user
        if not self.create_initial_admin():
            logger.warning("⚠️  Admin user creation failed - you may need to create one manually")
            return False
        
        logger.info("✅ Database initialization completed successfully")
        return True
    
    def health_check(self) -> bool:
        """Check database connectivity"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"❌ Database health check failed: {e}")
            return False

# Global instance
_db_initializer: Optional[DatabaseInitializer] = None

def get_database_initializer() -> DatabaseInitializer:
    """Get or create database initializer instance"""
    global _db_initializer
    if _db_initializer is None:
        _db_initializer = DatabaseInitializer()
    return _db_initializer

def initialize_database() -> bool:
    """Initialize database tables and admin user"""
    return get_database_initializer().initialize_database()

def create_admin_user() -> bool:
    """Create initial admin user"""
    return get_database_initializer().create_initial_admin()
