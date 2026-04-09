"""
Dealership schemas.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import DealershipStatus


class DealershipBase(BaseModel):
    """Base dealership schema."""

    name: str = Field(..., min_length=3, max_length=255)
    trade_name: Optional[str] = Field(None, max_length=255)
    document_id: str = Field(..., min_length=11, max_length=50)
    state_registration: Optional[str] = Field(None, max_length=50)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    whatsapp: Optional[str] = Field(None, max_length=20)
    website: Optional[str] = Field(None, max_length=255)


class DealershipCreate(DealershipBase):
    """Schema for dealership creation."""

    address: Optional[dict] = None
    settings: Optional[dict] = None


class DealershipUpdate(BaseModel):
    """Schema for dealership update."""

    name: Optional[str] = Field(None, min_length=3, max_length=255)
    trade_name: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    whatsapp: Optional[str] = Field(None, max_length=20)
    website: Optional[str] = Field(None, max_length=255)
    address: Optional[dict] = None
    settings: Optional[dict] = None
    status: Optional[DealershipStatus] = None


class DealershipResponse(DealershipBase):
    """Schema for dealership response."""

    id: UUID
    status: DealershipStatus
    address: Optional[dict] = None
    settings: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True
