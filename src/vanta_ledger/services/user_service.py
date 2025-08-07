#!/usr/bin/env python3
"""
User Service for Vanta Ledger
Handles user database operations and business logic
"""

import uuid
import logging
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from ..models.user_models import UserDB, UserCreate, UserUpdate, UserResponse
from ..auth import AuthService
from ..config import settings

logger = logging.getLogger(__name__)

class UserService:
    """Service for user management operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_id(self, user_id: str) -> Optional[UserDB]:
        """Get user by ID"""
        try:
            return self.db.query(UserDB).filter(UserDB.id == user_id).first()
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {str(e)}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[UserDB]:
        """Get user by username"""
        try:
            return self.db.query(UserDB).filter(UserDB.username == username).first()
        except Exception as e:
            logger.error(f"Error getting user by username {username}: {str(e)}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[UserDB]:
        """Get user by email"""
        try:
            return self.db.query(UserDB).filter(UserDB.email == email).first()
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {str(e)}")
            return None
    
    def get_users(self, skip: int = 0, limit: int = 100) -> List[UserDB]:
        """Get list of users with pagination"""
        try:
            return self.db.query(UserDB).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting users: {str(e)}")
            return []
    
    def create_user(self, user_data: UserCreate) -> Optional[UserDB]:
        """Create a new user"""
        try:
            # Check if username already exists
            if self.get_user_by_username(user_data.username):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already registered"
                )
            
            # Check if email already exists
            if self.get_user_by_email(user_data.email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            # Create new user
            user_id = str(uuid.uuid4())
            hashed_password = AuthService.get_password_hash(user_data.password)
            
            db_user = UserDB(
                id=user_id,
                username=user_data.username,
                email=user_data.email,
                hashed_password=hashed_password,
                is_active=user_data.is_active,
                role=user_data.role
            )
            
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            
            logger.info(f"Created new user: {user_data.username}")
            return db_user
            
        except HTTPException:
            raise
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Database integrity error creating user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User creation failed - duplicate data"
            )
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[UserDB]:
        """Update user information"""
        try:
            db_user = self.get_user_by_id(user_id)
            if not db_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Update fields if provided
            if user_data.username is not None:
                # Check if new username already exists
                existing_user = self.get_user_by_username(user_data.username)
                if existing_user and existing_user.id != user_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Username already taken"
                    )
                db_user.username = user_data.username
            
            if user_data.email is not None:
                # Check if new email already exists
                existing_user = self.get_user_by_email(user_data.email)
                if existing_user and existing_user.id != user_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already taken"
                    )
                db_user.email = user_data.email
            
            if user_data.is_active is not None:
                db_user.is_active = user_data.is_active
            
            if user_data.role is not None:
                db_user.role = user_data.role
            
            if user_data.password is not None:
                db_user.hashed_password = AuthService.get_password_hash(user_data.password)
            
            db_user.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(db_user)
            
            logger.info(f"Updated user: {db_user.username}")
            return db_user
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user"""
        try:
            db_user = self.get_user_by_id(user_id)
            if not db_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            self.db.delete(db_user)
            self.db.commit()
            
            logger.info(f"Deleted user: {db_user.username}")
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    def update_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp"""
        try:
            db_user = self.get_user_by_id(user_id)
            if not db_user:
                return False
            
            db_user.last_login = datetime.utcnow()
            self.db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating last login for user {user_id}: {str(e)}")
            return False
    
    def verify_user_credentials(self, username: str, password: str) -> Optional[UserDB]:
        """Verify user credentials and return user if valid"""
        try:
            user = self.get_user_by_username(username)
            if not user:
                return None
            
            if not user.is_active:
                return None
            
            if not AuthService.verify_password(password, user.hashed_password):
                return None
            
            # Update last login
            self.update_last_login(user.id)
            
            return user
            
        except Exception as e:
            logger.error(f"Error verifying credentials for user {username}: {str(e)}")
            return None

# Global user service instance (to be initialized with database session)
user_service: Optional[UserService] = None

def get_user_service() -> UserService:
    """Get the global user service instance"""
    if user_service is None:
        raise RuntimeError("User service not initialized")
    return user_service

def init_user_service(db: Session):
    """Initialize the global user service with database session"""
    global user_service
    user_service = UserService(db) 