"""
User schemas.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import UserRole, UserStatus


class UserBase(BaseModel):
    """Base user schema."""

    name: str = Field(..., min_length=3, max_length=255)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    role: UserRole = UserRole.USER


class UserResponse(UserBase):
    """Schema for user response."""

    id: UUID
    dealership_id: UUID
    status: UserStatus
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class UserUpdate(BaseModel):
    """Schema for user update."""

    name: Optional[str] = Field(None, min_length=3, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None


class UserChangePassword(BaseModel):
    """Schema for changing password."""

    old_password: str = Field(..., min_length=1, max_length=100)
    new_password: str = Field(..., min_length=8, max_length=100)
