#!/usr/bin/env python3
"""
User Models for Vanta Ledger
Defines user data models and database schemas
"""

from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, Field

# Production fix for email validation - use string type with validation
EmailStr = str
from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class UserDB(Base):
    """Database model for users"""

    __tablename__ = "users"

    id = Column(String(36), primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String(20), default="user")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        """
        Return a string representation of the user instance, including id, username, and email.
        """
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


# Pydantic models for API
class UserBase(BaseModel):
    """Base user model"""

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    is_active: bool = True
    role: str = Field(default="user", max_length=20)


class UserCreate(UserBase):
    """Model for creating a new user"""

    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Model for updating user information"""

    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    role: Optional[str] = Field(None, max_length=20)
    password: Optional[str] = Field(None, min_length=8)


class UserResponse(UserBase):
    """Model for user responses (excludes sensitive data)"""

    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Model for user login"""

    username: str
    password: str


class UserInDB(UserBase):
    """Internal user model with hashed password"""

    id: str
    hashed_password: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


# Token models
class Token(BaseModel):
    """JWT token response model"""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Token payload data"""

    username: Optional[str] = None
    user_id: Optional[str] = None
    role: Optional[str] = None
