"""
Ad schemas.
"""
from decimal import Decimal
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import AdPlatform, AdStatus


class AdBase(BaseModel):
    """Base ad schema."""

    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    headline: Optional[str] = Field(None, max_length=255)
    call_to_action: Optional[str] = Field(None, max_length=100)
    platform: AdPlatform
    budget_daily: Optional[Decimal] = Field(None, ge=0)
    budget_total: Optional[Decimal] = Field(None, ge=0)
    bid_amount: Optional[Decimal] = Field(None, ge=0)
    bid_strategy: Optional[str] = Field(None, max_length=50)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    target_audience: Optional[Dict[str, Any]] = None
    images: Optional[List[str]] = None
    video_url: Optional[str] = None


class AdCreate(AdBase):
    """Schema for creating ad."""

    vehicle_id: UUID


class AdUpdate(BaseModel):
    """Schema for updating ad."""

    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    headline: Optional[str] = Field(None, max_length=255)
    call_to_action: Optional[str] = Field(None, max_length=100)
    status: Optional[AdStatus] = None
    budget_daily: Optional[Decimal] = Field(None, ge=0)
    budget_total: Optional[Decimal] = Field(None, ge=0)
    bid_amount: Optional[Decimal] = Field(None, ge=0)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    target_audience: Optional[Dict[str, Any]] = None
    images: Optional[List[str]] = None


class AdResponse(AdBase):
    """Schema for ad response."""

    id: UUID
    vehicle_id: UUID
    status: AdStatus
    platform_ad_id: Optional[str] = None
    ai_generated: bool
    ai_suggestions: Optional[Dict[str, Any]] = None
    total_impressions: int
    total_clicks: int
    total_spend: Decimal
    total_conversions: int
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None

    class Config:
        """Pydantic config."""

        from_attributes = True


class AdStatusUpdate(BaseModel):
    """Schema for status updates."""

    status: AdStatus
    reason: Optional[str] = None


class AdFilter(BaseModel):
    """Schema for ad filtering."""

    search: Optional[str] = None
    platform: Optional[AdPlatform] = None
    status: Optional[AdStatus] = None
    vehicle_id: Optional[UUID] = None
    start_date_min: Optional[datetime] = None
    start_date_max: Optional[datetime] = None
    ai_generated: Optional[bool] = None


class AdPreviewRequest(BaseModel):
    """Schema for ad preview generation."""

    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    headline: Optional[str] = Field(None, max_length=255)
    call_to_action: Optional[str] = Field(None, max_length=100)
    images: Optional[List[str]] = None
    platform: AdPlatform = AdPlatform.FACEBOOK


class AdPreviewResponse(BaseModel):
    """Schema for ad preview response."""

    preview_url: str
    preview_html: str
    estimated_ctr: Optional[Dict[str, float]] = None
    estimated_impressions: Optional[int] = None
