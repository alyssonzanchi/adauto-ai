"""
Filter schemas.
"""
from typing import Optional
from pydantic import BaseModel, Field

from app.models.enums import UserRole, UserStatus


class UserFilter(BaseModel):
    """Schema for user filtering."""

    email: Optional[str] = None
    name: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    dealership_id: Optional[str] = None


class DealershipFilter(BaseModel):
    """Schema for dealership filtering."""

    name: Optional[str] = None
    email: Optional[str] = None
    document_id: Optional[str] = None
    status: Optional[str] = None
