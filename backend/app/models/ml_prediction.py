"""
ML Prediction model.
"""
import datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    JSON,
    Numeric,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.enums import PredictionType


class MLPrediction(Base):
    """ML Prediction model."""

    __tablename__ = "ml_predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Relationships
    vehicle_id = Column(
        UUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="CASCADE")
    )
    ad_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ads.id", ondelete="CASCADE")
    )

    # Type
    prediction_type = Column(String(20), nullable=False)

    # Prediction
    predicted_value = Column(Numeric(10, 2))
    confidence = Column(Numeric(5, 4))

    # Features used
    features = Column(JSON)
    """
    {
        "price": 135000,
        "mileage": 15000,
        "year": 2024,
        "brand_score": 0.85,
        "historical_ctr": 0.035
    }
    """

    # Model info
    model_version = Column(String(50), nullable=False)
    model_type = Column(String(50))

    # Prediction evaluation
    actual_value = Column(Numeric(10, 2))
    error = Column(Numeric(10, 2))

    # Metadata
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    vehicle = relationship("Vehicle")
    ad = relationship("Ad")

    def __repr__(self) -> str:
        return f"<MLPrediction {self.prediction_type} ({self.id})>"
