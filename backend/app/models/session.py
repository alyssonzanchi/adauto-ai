"""
Session model.
"""
import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, JSON, String, UUID as SQLUUID
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Session(Base):
    """Session model."""

    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Relationship
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    # Token
    token = Column(String(255), unique=True, nullable=False)

    # Session info
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    device_type = Column(String(50))

    # Location
    location = Column(JSON)
    """
    {
        "country": "BR",
        "state": "SP",
        "city": "São Paulo"
    }
    """

    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    last_activity = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User")

    def __repr__(self) -> str:
        return f"<Session {self.user_id} - {self.device_type}>"
