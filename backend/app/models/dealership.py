"""
Dealership model.
"""
import datetime
from uuid import uuid4

from sqlalchemy import JSON, Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.enums import DealershipStatus


class Dealership(Base):
    """Dealership model."""

    __tablename__ = "dealerships"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    trade_name = Column(String(255))
    document_id = Column(String(50), unique=True, nullable=False)
    state_registration = Column(String(50))

    # Contact
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20))
    whatsapp = Column(String(20))
    website = Column(String(255))

    # Address (JSONB for flexibility)
    address = Column(JSON)
    """
    Format:
    {
        "street": "Rua Exemplo",
        "number": "123",
        "complement": "Sala 1",
        "neighborhood": "Centro",
        "city": "São Paulo",
        "state": "SP",
        "zip_code": "01234-567",
        "country": "BR",
        "latitude": -23.5505,
        "longitude": -46.6333
    }
    """

    # Configuration
    status = Column(
        String(20),
        default=DealershipStatus.ACTIVE,
        nullable=False
    )
    settings = Column(JSON, default={})
    """
    {
        "timezone": "America/Sao_Paulo",
        "currency": "BRL",
        "notifications_enabled": true,
        "auto_optimization": true,
        "max_daily_budget": 1000
    }
    """

    # Metadata
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    deleted_at = Column(DateTime)

    # Relationships
    users = relationship("User", back_populates="dealership", cascade="all, delete-orphan")
    vehicles = relationship("Vehicle", back_populates="dealership", cascade="all, delete-orphan")
    ad_platform_accounts = relationship("AdPlatformAccount", back_populates="dealership", cascade="all, delete-orphan")
    facebook_accounts = relationship("FacebookAccount", back_populates="dealership", cascade="all, delete-orphan")
    google_accounts = relationship("GoogleAccount", back_populates="dealership", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Dealership {self.name} ({self.id})>"
