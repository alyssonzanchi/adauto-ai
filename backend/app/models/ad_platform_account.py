"""
Ad Platform Account model.
"""
import datetime
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.enums import AdPlatform, ConnectionStatus


class AdPlatformAccount(Base):
    """Ad Platform Account model."""

    __tablename__ = "ad_platform_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Relationship
    dealership_id = Column(
        UUID(as_uuid=True),
        ForeignKey("dealerships.id", ondelete="CASCADE"),
        nullable=False
    )

    # Platform
    platform = Column(String(20), nullable=False)

    # Credentials
    account_id = Column(String(255), nullable=False)
    account_name = Column(String(255))
    business_id = Column(String(255))

    # OAuth tokens (encrypted)
    access_token = Column(Text)
    refresh_token = Column(Text)
    token_expires_at = Column(DateTime)

    # Configuration
    status = Column(String(20), default=ConnectionStatus.ACTIVE, nullable=False)
    auto_sync = Column(Boolean, default=True)
    sync_interval = Column(Integer, default=3600)

    # Platform metadata
    platform_data = Column(JSON)
    """
    {
        "facebook": {
            "account_id": "act_123456",
            "business_id": "123456",
            "currency": "BRL",
            "timezone": "America/Sao_Paulo"
        }
    }
    """

    # Metadata
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    last_sync_at = Column(DateTime)

    # Relationships
    dealership = relationship("Dealership", back_populates="ad_platform_accounts")

    def __repr__(self) -> str:
        return f"<AdPlatformAccount {self.platform} - {self.account_name} ({self.id})>"
