"""
Pydantic schemas for authentication
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Token data extracted from JWT"""
    user_id: int
    role: str


class UserLogin(BaseModel):
    """User login request schema"""
    username: str
    password: str


class UserRegister(BaseModel):
    """User registration request schema"""
    username: str
    email: EmailStr
    full_name: str
    password: str
    role: Optional[str] = "backend_developer"  # Default role


class UserResponse(BaseModel):
    """User response schema"""
    id: int
    username: str
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class PasswordChange(BaseModel):
    """Password change request schema"""
    current_password: str
    new_password: str