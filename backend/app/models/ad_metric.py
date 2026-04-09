"""
Ad Metric model.
"""
import datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    Numeric,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.enums import AdPlatform


class AdMetric(Base):
    """Ad Metric model."""

    __tablename__ = "ad_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Relationship
    ad_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ads.id", ondelete="CASCADE"),
        nullable=False
    )

    # Date
    date = Column(Date, nullable=False)

    # Platform
    platform = Column(String(20), nullable=False)

    # Basic metrics
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    ctr = Column(Numeric(5, 4))

    # Cost metrics
    spend = Column(Numeric(10, 2), default=Decimal("0.00"))
    cost_per_click = Column(Numeric(10, 2))
    cost_per_thousand = Column(Numeric(10, 2))
    cost_per_conversion = Column(Numeric(10, 2))

    # Conversion metrics
    conversions = Column(Integer, default=0)
    conversion_rate = Column(Numeric(5, 4))
    qualified_leads = Column(Integer, default=0)

    # Revenue and ROI
    revenue = Column(Numeric(12, 2))
    roi = Column(Numeric(10, 2))
    roas = Column(Numeric(10, 2))

    # Engagement
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    saves = Column(Integer, default=0)

    # Raw data from API
    raw_data = Column(JSON)

    # Metadata
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    ad = relationship("Ad", back_populates="metrics")

    def __repr__(self) -> str:
        return f"<AdMetric {self.platform} - {self.date} ({self.ad_id})>"
