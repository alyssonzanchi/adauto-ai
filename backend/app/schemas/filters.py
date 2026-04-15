"""
Filter schemas.
"""
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from app.models.enums import UserRole, UserStatus, VehicleStatus


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


class VehicleFilter(BaseModel):
    """Schema for vehicle filtering."""

    search: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    year_min: Optional[int] = Field(None, ge=1900)
    year_max: Optional[int] = Field(None, le=2030)
    price_min: Optional[Decimal] = Field(None, ge=0)
    price_max: Optional[Decimal] = Field(None, ge=0)
    status: Optional[VehicleStatus] = None
