"""
Ad Optimization model.
"""
import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.enums import OptimizationType


class AdOptimization(Base):
    """Ad Optimization model."""

    __tablename__ = "ad_optimizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Relationship
    ad_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ads.id", ondelete="CASCADE"),
        nullable=False
    )

    # Type
    type = Column(String(20), nullable=False)

    # Description
    description = Column(Text)

    # Action taken (JSONB)
    action_taken = Column(JSON)
    """
    {
        "field": "budget_daily",
        "old_value": 100,
        "new_value": 150,
        "reason": "ctr_above_threshold"
    }
    """

    # Result (JSONB)
    result = Column(JSON)
    """
    {
        "previous_ctr": 0.025,
        "new_ctr": 0.032,
        "improvement": 0.28,
        "status": "successful"
    }
    """

    # Timestamp
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    ad = relationship("Ad", back_populates="optimizations")

    def __repr__(self) -> str:
        return f"<AdOptimization {self.type} ({self.id})>"
