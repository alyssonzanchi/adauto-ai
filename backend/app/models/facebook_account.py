"""
Facebook Account model.
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


class FacebookAccount(Base):
    """Facebook Ad Account model."""

    __tablename__ = "facebook_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Dealership relationship
    dealership_id = Column(
        UUID(as_uuid=True),
        ForeignKey("dealerships.id", ondelete="CASCADE"),
        nullable=False
    )

    # Facebook account details
    facebook_account_id = Column(String(100), nullable=False, unique=True, index=True)
    facebook_account_name = Column(String(255), nullable=False)
    facebook_business_id = Column(String(100))

    # Access token (encrypted)
    access_token = Column(Text, nullable=False)
    token_expires_at = Column(DateTime)

    # Connection status
    status = Column(String(20), default=ConnectionStatus.PENDING, nullable=False)
    last_synced_at = Column(DateTime)

    # Facebook metadata
    account_metadata = Column(JSON)
    """
    {
        "currency": "BRL",
        "timezone_name": "America/Sao_Paulo",
        "timezone_offset_hours_utc": -3,
        "capabilities": ["CUSTOM_AUDIENCES", "LOOKALIKE_AUDIENCES"],
        "balance": {"amount": 100.00, "currency": "USD"}
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
    dealership = relationship("Dealership", back_populates="facebook_accounts")

    def __repr__(self) -> str:
        return f"<FacebookAccount {self.facebook_account_name} ({self.facebook_account_id})>"
