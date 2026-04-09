"""
User model.
"""
import datetime
from uuid import uuid4

from sqlalchemy import JSON, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.enums import UserRole, UserStatus


class User(Base):
    """User model."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Relationship
    dealership_id = Column(
        UUID(as_uuid=True),
        ForeignKey("dealerships.id", ondelete="CASCADE"),
        nullable=False
    )

    # Personal info
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20))

    # Authentication
    password_hash = Column(String(255), nullable=False)
    last_login = Column(DateTime)

    # Permissions
    role = Column(String(20), default=UserRole.USER, nullable=False)
    permissions = Column(JSON, default=[])
    """
    ["vehicles:create", "vehicles:edit", "ads:publish", "metrics:view"]
    """

    # Status
    status = Column(String(20), default=UserStatus.ACTIVE, nullable=False)

    # Metadata
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    deleted_at = Column(DateTime)

    # Relationships
    dealership = relationship("Dealership", back_populates="users")

    def __repr__(self) -> str:
        return f"<User {self.name} ({self.email})>"
