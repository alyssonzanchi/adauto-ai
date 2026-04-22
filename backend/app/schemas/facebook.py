"""
Facebook integration schemas.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl

from app.models.enums import ConnectionStatus


class FacebookAccountBase(BaseModel):
    """Base Facebook account schema."""

    facebook_account_id: str = Field(..., description="Facebook Ad Account ID")
    facebook_account_name: str = Field(..., description="Facebook Ad Account name")
    facebook_business_id: Optional[str] = Field(None, description="Facebook Business ID")
    auto_sync_enabled: bool = Field(True, description="Enable automatic metrics sync")
    sync_frequency_minutes: str = Field("60", description="Sync frequency in minutes")


class FacebookAccountCreate(FacebookAccountBase):
    """Schema for creating Facebook account connection."""

    access_token: str = Field(..., description="Facebook access token")
    token_expires_at: Optional[datetime] = Field(None, description="Token expiration time")


class FacebookAccountResponse(FacebookAccountBase):
    """Schema for Facebook account response."""

    id: UUID
    dealership_id: UUID
    status: ConnectionStatus
    last_synced_at: Optional[datetime]
    account_metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FacebookOAuthURL(BaseModel):
    """Schema for OAuth URL response."""

    authorization_url: str = Field(..., description="Facebook OAuth authorization URL")
    state: str = Field(..., description="OAuth state parameter for CSRF protection")


class FacebookOAuthCallback(BaseModel):
    """Schema for OAuth callback."""

    code: str = Field(..., description="OAuth authorization code")
    state: str = Field(..., description="OAuth state parameter")


class FacebookTokenResponse(BaseModel):
    """Schema for Facebook token response."""

    id: UUID
    user_id: UUID
    dealership_id: UUID
    token_type: str
    granted_scopes: List[str]
    expires_at: Optional[datetime]
    is_active: bool
    created_at: datetime


class FacebookAdAccountInfo(BaseModel):
    """Schema for Facebook ad account information."""

    account_id: str
    account_name: str
    account_status: int
    currency: str
    timezone_name: str
    timezone_offset_hours_utc: int
    business_name: Optional[str] = None
    business_id: Optional[str] = None


class FacebookPublishRequest(BaseModel):
    """Schema for publishing ad to Facebook."""

    ad_id: UUID = Field(..., description="Internal ad ID")
    account_id: str = Field(..., description="Facebook Ad Account ID")
    campaign_name: str = Field(..., description="Campaign name")
    adset_name: str = Field(..., description="Ad set name")
    objective: str = Field(
        "OUTCOME_TRAFFIC",
        description="Facebook campaign objective"
    )
    status: str = Field("PAUSED", description="Initial ad status")


class FacebookPublishResponse(BaseModel):
    """Schema for Facebook publish response."""

    success: bool
    ad_id: UUID
    facebook_campaign_id: Optional[str] = None
    facebook_adset_id: Optional[str] = None
    facebook_ad_id: Optional[str] = None
    message: str
    errors: Optional[List[str]] = None


class FacebookMetricsSync(BaseModel):
    """Schema for metrics sync request."""

    account_id: str = Field(..., description="Facebook Ad Account ID")
    start_date: Optional[datetime] = Field(None, description="Start date for metrics")
    end_date: Optional[datetime] = Field(None, description="End date for metrics")
    ad_ids: Optional[List[str]] = Field(None, description="Specific ad IDs to sync")


class FacebookMetricsResponse(BaseModel):
    """Schema for Facebook metrics response."""

    success: bool
    account_id: str
    ads_updated: int
    period_start: datetime
    period_end: datetime
    message: str
