"""
Google Ads integration schemas.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import ConnectionStatus


class GoogleAccountBase(BaseModel):
    """Base Google Ads account schema."""

    google_account_id: str = Field(..., description="Google Ads Customer ID")
    google_account_name: str = Field(..., description="Google Ads account name")
    google_manager_id: Optional[str] = Field(None, description="Google Manager ID")
    auto_sync_enabled: bool = Field(True, description="Enable automatic metrics sync")
    sync_frequency_minutes: str = Field("60", description="Sync frequency in minutes")


class GoogleAccountCreate(GoogleAccountBase):
    """Schema for creating Google Ads account connection."""

    access_token: str = Field(..., description="Google access token")
    refresh_token: str = Field(..., description="Google refresh token")
    token_expires_at: Optional[datetime] = Field(None, description="Token expiration time")


class GoogleAccountResponse(GoogleAccountBase):
    """Schema for Google Ads account response."""

    id: UUID
    dealership_id: UUID
    status: ConnectionStatus
    last_synced_at: Optional[datetime]
    account_metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GoogleOAuthURL(BaseModel):
    """Schema for OAuth URL response."""

    authorization_url: str = Field(..., description="Google OAuth authorization URL")
    state: str = Field(..., description="OAuth state parameter for CSRF protection")


class GoogleOAuthCallback(BaseModel):
    """Schema for OAuth callback."""

    code: str = Field(..., description="OAuth authorization code")
    state: str = Field(..., description="OAuth state parameter")


class GoogleTokenResponse(BaseModel):
    """Schema for Google token response."""

    id: UUID
    user_id: UUID
    dealership_id: UUID
    token_type: str
    granted_scopes: List[str]
    expires_at: Optional[datetime]
    is_active: bool
    created_at: datetime


class GoogleAdAccountInfo(BaseModel):
    """Schema for Google Ads account information."""

    customer_id: str
    account_name: str
    currency_code: str
    time_zone: str
    tracking_url_template: Optional[str] = None
    final_url_suffix: Optional[str] = None
    manager_id: Optional[str] = None


class GooglePublishRequest(BaseModel):
    """Schema for publishing ad to Google Ads."""

    ad_id: UUID = Field(..., description="Internal ad ID")
    customer_id: str = Field(..., description="Google Ads Customer ID")
    campaign_name: str = Field(..., description="Campaign name")
    ad_group_name: str = Field(..., description="Ad group name")
    budget_amount: float = Field(..., description="Daily budget amount")
    status: str = Field("PAUSED", description="Initial ad status")


class GooglePublishResponse(BaseModel):
    """Schema for Google publish response."""

    success: bool
    ad_id: UUID
    google_campaign_id: Optional[str] = None
    google_adgroup_id: Optional[str] = None
    google_ad_id: Optional[str] = None
    message: str
    errors: Optional[List[str]] = None


class GoogleMetricsSync(BaseModel):
    """Schema for metrics sync request."""

    customer_id: str = Field(..., description="Google Ads Customer ID")
    start_date: Optional[datetime] = Field(None, description="Start date for metrics")
    end_date: Optional[datetime] = Field(None, description="End date for metrics")
    ad_ids: Optional[List[str]] = Field(None, description="Specific ad IDs to sync")


class GoogleMetricsResponse(BaseModel):
    """Schema for Google metrics response."""

    success: bool
    customer_id: str
    ads_updated: int
    period_start: datetime
    period_end: datetime
    message: str
