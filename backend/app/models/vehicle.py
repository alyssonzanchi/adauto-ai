"""
Vehicle model.
"""
import datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import (
    ARRAY,
    JSON,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.enums import BodyType, FuelType, TransmissionType, VehicleStatus


class Vehicle(Base):
    """Vehicle model."""

    __tablename__ = "vehicles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Relationship
    dealership_id = Column(
        UUID(as_uuid=True),
        ForeignKey("dealerships.id", ondelete="CASCADE"),
        nullable=False
    )

    # Basic info
    title = Column(String(500), nullable=False)
    description = Column(Text)

    # Vehicle characteristics
    brand = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    model_year = Column(Integer)
    version = Column(String(100))

    # Specifications
    color = Column(String(50))
    mileage = Column(Integer)
    mileage_unit = Column(String(10), default="km")
    plate = Column(String(20))
    chassis = Column(String(50), unique=True)
    doors = Column(Integer)
    seats = Column(Integer)

    # Types
    fuel_type = Column(String(20))
    transmission = Column(String(20))
    body_type = Column(String(20))

    # Price
    price = Column(Numeric(12, 2), nullable=False)
    price_market = Column(Numeric(12, 2))
    price_score = Column(Integer)
    price_position = Column(String(20))

    # Features (JSONB)
    features = Column(JSON, default={})
    """
    {
        "security": ["airbags", "abs", "controle_estabilidade"],
        "comfort": ["ar_condicionado", "direcao_eletrica", "bancos_couro"],
        "technology": ["central_multimidia", "gps", "android_auto"],
        "extras": ["rodas_liga_leve", "piloto_automatico", "teto_solar"]
    }
    """

    # Media
    images = Column(ARRAY(String))
    main_image = Column(String)
    video_url = Column(String)

    # Documentation
    document_urls = Column(ARRAY(String))
    ownership = Column(String(50))

    # Status
    status = Column(String(20), default=VehicleStatus.ACTIVE, nullable=False)
    sold_at = Column(DateTime)
    sold_price = Column(Numeric(12, 2))

    # AI Analysis (JSONB)
    ai_analysis = Column(JSON)
    """
    {
        "score": 85,
        "selling_points": ["unico_dono", "revisoes_concessionaria"],
        "target_audience": ["familias", "profissionais_liberais"],
        "suggested_improvements": ["mais_fotos_interior"],
        "estimated_ctr": 0.035,
        "estimated_conversion": 0.028,
        "model_version": "v1.2.0"
    }
    """

    # Vector Embeddings (pgvector)
    description_embedding = Column(ARRAY(Float, dimensions=1536), nullable=True)
    """
    Embedding vector for vehicle description and title.
    Used for semantic search and similarity matching.
    Generated using OpenAI text-embedding-3-small (1536 dimensions).
    """

    features_embedding = Column(ARRAY(Float, dimensions=1536), nullable=True)
    """
    Embedding vector for vehicle features and characteristics.
    Used for complementary vehicle recommendations.
    Generated using OpenAI text-embedding-3-small (1536 dimensions).
    """

    # Metadata
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    deleted_at = Column(DateTime)

    # Relationships
    dealership = relationship("Dealership", back_populates="vehicles")
    ads = relationship("Ad", back_populates="vehicle", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Vehicle {self.brand} {self.model} {self.year} ({self.id})>"
