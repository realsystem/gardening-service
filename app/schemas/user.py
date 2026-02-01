"""User schemas"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.user import UnitSystem


class UserCreate(BaseModel):
    """Schema for creating a new user"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    zip_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserProfileUpdate(BaseModel):
    """Schema for updating user profile"""
    display_name: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    gardening_preferences: Optional[str] = None
    zip_code: Optional[str] = Field(None, max_length=10)
    unit_system: Optional[UnitSystem] = None


class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    email: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    city: Optional[str] = None
    gardening_preferences: Optional[str] = None
    zip_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    usda_zone: Optional[str] = None
    unit_system: UnitSystem = UnitSystem.METRIC
    is_admin: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"
