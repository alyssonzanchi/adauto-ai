"""
Ad model.
"""
import datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import (
    ARRAY,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.enums import AdPlatform, AdStatus


class Ad(Base):
    """Ad model."""

    __tablename__ = "ads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Relationship
    vehicle_id = Column(
        UUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="CASCADE"),
        nullable=False
    )

    # Platform
    platform = Column(String(20), nullable=False)
    platform_ad_id = Column(String(255))

    # Status
    status = Column(String(20), default=AdStatus.DRAFT, nullable=False)

    # Content
    title = Column(String(500))
    description = Column(Text)
    headline = Column(String(255))
    call_to_action = Column(String(100))

    # Media
    images = Column(ARRAY(String))
    video_url = Column(String)

    # Targeting (JSONB)
    target_audience = Column(JSON)
    """
    {
        "age_min": 25,
        "age_max": 55,
        "genders": ["male", "female"],
        "locations": [
            {"city": "São Paulo", "radius": 30}
        ],
        "interests": ["automotive", "suv", "off-road"],
        "behaviors": ["car_buyers", "luxury_shoppers"],
        "custom_audiences": ["website_visitors", "lookalike_1"]
    }
    """

    # Budget
    budget_daily = Column(Numeric(10, 2))
    budget_total = Column(Numeric(10, 2))
    bid_amount = Column(Numeric(10, 2))
    bid_strategy = Column(String(50))

    # Dates
    start_date = Column(DateTime)
    end_date = Column(DateTime)

    # AI Generated
    ai_generated = Column(Boolean, default=False)
    ai_suggestions = Column(JSON)
    """
    {
        "headlines": ["Opção 1", "Opção 2", "Opção 3"],
        "descriptions": ["Desc 1", "Desc 2"],
        "ctas": ["Agendar Test-Drive", "Saber Mais"],
        "estimated_ctr": {"min": 0.035, "max": 0.041},
        "estimated_conversions": {"min": 35, "max": 55}
    }
    """

    # Performance aggregates
    total_impressions = Column(Integer, default=0)
    total_clicks = Column(Integer, default=0)
    total_spend = Column(Numeric(10, 2), default=Decimal("0.00"))
    total_conversions = Column(Integer, default=0)

    # Metadata
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    published_at = Column(DateTime)
    deleted_at = Column(DateTime)

    # Relationships
    vehicle = relationship("Vehicle", back_populates="ads")
    metrics = relationship("AdMetric", back_populates="ad", cascade="all, delete-orphan")
    optimizations = relationship("AdOptimization", back_populates="ad", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Ad {self.platform} - {self.title} ({self.id})>"
