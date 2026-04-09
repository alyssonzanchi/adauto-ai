"""
Authentication schemas.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """Schema for user registration."""

    name: str = Field(..., min_length=3, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    dealership_name: str = Field(..., min_length=3, max_length=255)
    dealership_document_id: str = Field(..., min_length=11, max_length=50)
    dealership_phone: Optional[str] = Field(None, max_length=20)
    dealership_email: EmailStr


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str = Field(..., min_length=1, max_length=100)


class Token(BaseModel):
    """Schema for token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class TokenPayload(BaseModel):
    """Schema for token payload."""

    sub: str  # user_id
    exp: Optional[datetime] = None
    type: str  # "access" or "refresh"
