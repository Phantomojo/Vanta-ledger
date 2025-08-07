#!/usr/bin/env python3
"""
Secure Authentication Module
Handles user authentication, password hashing, JWT tokens, and token blacklisting
"""

import os
import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import redis
from .config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token security
security = HTTPBearer()

# Redis client for token blacklisting
redis_client = redis.Redis.from_url(settings.REDIS_URI, decode_responses=True)

class User:
    """User model for authentication"""
    def __init__(self, id: str, username: str, email: str, hashed_password: str, 
                 is_active: bool = True, role: str = "user"):
        self.id = id
        self.username = username
        self.email = email
        self.hashed_password = hashed_password
        self.is_active = is_active
        self.role = role

class AuthService:
    """Authentication service with secure practices"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Generate password hash"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token with JTI for blacklisting"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # Add JWT ID for blacklisting
        to_encode.update({
            "exp": expire,
            "jti": str(uuid.uuid4()),
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({
            "exp": expire,
            "jti": str(uuid.uuid4()),
            "iat": datetime.utcnow(),
            "type": "refresh"
        })
        
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            
            # Check if token is blacklisted
            if AuthService.is_token_blacklisted(payload.get("jti")):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has been revoked"
                )
            
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
    
    @staticmethod
    def blacklist_token(jti: str, expires_in: int = None) -> bool:
        """Add token to blacklist"""
        try:
            if expires_in is None:
                # Default to token expiration time
                expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            
            redis_client.setex(f"blacklist:{jti}", expires_in, "1")
            return True
        except Exception as e:
            logger.error(f"Error blacklisting token: {str(e)}")
            return False
    
    @staticmethod
    def is_token_blacklisted(jti: str) -> bool:
        """Check if token is blacklisted"""
        try:
            return redis_client.exists(f"blacklist:{jti}") > 0
        except Exception as e:
            logger.error(f"Error checking token blacklist: {str(e)}")
            return False

# User management functions (to be implemented with database)
async def get_user_by_username(username: str) -> Optional[User]:
    """Get user by username from database"""
    # TODO: Implement a proper database query to fetch users.
    # The hardcoded 'admin' user has been removed for security reasons.
    # A real implementation should query a database like this:
    # user_data = await db.users.find_one({"username": username})
    # if user_data:
    #     return User(**user_data)
    return None

async def get_user_by_id(user_id: str) -> Optional[User]:
    """Get user by ID from database"""
    # TODO: Implement database query
    return None

async def create_user(username: str, email: str, password: str, role: str = "user") -> User:
    """Create new user with hashed password"""
    # TODO: Implement database insertion
    user_id = str(uuid.uuid4())
    hashed_password = AuthService.get_password_hash(password)
    
    user = User(
        id=user_id,
        username=username,
        email=email,
        hashed_password=hashed_password,
        role=role
    )
    
    # TODO: Save to database
    return user

# Dependency for getting current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user"""
    try:
        payload = AuthService.verify_token(credentials.credentials)
        username: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        user = await get_user_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

# Role-based access control
def require_role(required_role: str):
    """Decorator for role-based access control"""
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker 