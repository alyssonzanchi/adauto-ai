"""
Google Ads Token model for OAuth flow.
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
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class GoogleToken(Base):
    """Google Ads OAuth Token model."""

    __tablename__ = "google_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # User relationship (who authorized)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    # Dealership relationship
    dealership_id = Column(
        UUID(as_uuid=True),
        ForeignKey("dealerships.id", ondelete="CASCADE"),
        nullable=False
    )

    # OAuth tokens
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=False)
    token_type = Column(String(50), default="Bearer")  # Bearer
    expires_in = Column(String(50))  # seconds from Google
    granted_scopes = Column(Text)
    """
    Space-separated list of granted scopes:
    "https://www.googleapis.com/auth/adwords"
    """

    # Token metadata
    expires_at = Column(DateTime)
    issued_at = Column(DateTime)

    # Status
    is_active = Column(Boolean, default=True)
    revoked_at = Column(DateTime)

    # Metadata
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", backref="google_tokens")
    dealership = relationship("Dealership", backref="google_tokens")

    def __repr__(self) -> str:
        return f"<GoogleToken user={self.user_id} active={self.is_active}>"

    @property
    def is_valid(self) -> bool:
        """Check if token is valid and not expired."""
        if not self.is_active or self.revoked_at:
            return False
        if self.expires_at and self.expires_at < datetime.datetime.utcnow():
            return False
        return True

    @property
    def needs_refresh(self) -> bool:
        """Check if token needs refresh (expires in less than 5 minutes)."""
        if not self.is_valid:
            return False
        if not self.expires_at:
            return False
        return self.expires_at < datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
