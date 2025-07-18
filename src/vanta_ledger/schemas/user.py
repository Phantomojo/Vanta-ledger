from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """
    Base schema for user data. Used for both creation and update.
    Ensures all key user info is captured for authentication and access control.
    """
    name: str
    email: EmailStr
    role: str

class UserCreate(UserBase):
    """
    Schema for registering a new user. Includes password.
    Lets the family add new members securely.
    """
    password: str

class UserRead(UserBase):
    """
    Schema for reading user data, including ID and timestamps.
    Used in user lists and profile views.
    """
    id: int
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    """
    Schema for user login (email and password).
    Used for authentication.
    """
    email: EmailStr
    password: str 