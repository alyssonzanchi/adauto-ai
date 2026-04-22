"""
Google Ads Account model.
"""
import datetime
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
    Text,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.enums import ConnectionStatus


class GoogleAccount(Base):
    """Google Ads Account model."""

    __tablename__ = "google_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Dealership relationship
    dealership_id = Column(
        UUID(as_uuid=True),
        ForeignKey("dealerships.id", ondelete="CASCADE"),
        nullable=False
    )

    # Google Ads account details
    google_account_id = Column(String(100), nullable=False, unique=True, index=True)
    google_account_name = Column(String(255), nullable=False)
    google_manager_id = Column(String(100))

    # Access token (encrypted)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=False)
    token_expires_at = Column(DateTime)

    # Connection status
    status = Column(String(20), default=ConnectionStatus.PENDING, nullable=False)
    last_synced_at = Column(DateTime)

    # Google metadata
    account_metadata = Column(JSON)
    """
    {
        "currency_code": "BRL",
        "time_zone": "America/Sao_Paulo",
        "tracking_url_template": "{lpurl}?utm_source=google",
        "final_url_suffix": "utm_source=google",
        "auto_tagging_enabled": true
    }
    """

    # Sync configuration
    auto_sync_enabled = Column(Boolean, default=True)
    sync_frequency_minutes = Column(String(20), default="60")  # 60 minutes default

    # Metadata
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    deleted_at = Column(DateTime)

    # Relationships
    dealership = relationship("Dealership", back_populates="google_accounts")

    def __repr__(self) -> str:
        return f"<GoogleAccount {self.google_account_name} ({self.google_account_id})>"
