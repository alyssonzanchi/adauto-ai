"""
Vehicle schemas.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl, field_validator

from app.models.enums import FuelType, TransmissionType, BodyType, VehicleStatus


class VehicleBase(BaseModel):
    """Base vehicle schema."""

    model_config = {"protected_namespaces": ()}

    title: str = Field(..., min_length=5, max_length=500)
    description: Optional[str] = Field(None, max_length=5000)
    brand: str = Field(..., min_length=2, max_length=100)
    model: str = Field(..., min_length=2, max_length=100)
    year: int = Field(..., ge=1900, le=2030)
    model_year: Optional[int] = Field(None, ge=1900, le=2030)
    version: Optional[str] = Field(None, max_length=100)
    color: Optional[str] = Field(None, max_length=50)
    mileage: Optional[int] = Field(None, ge=0)
    plate: Optional[str] = Field(None, max_length=20)
    chassis: Optional[str] = Field(None, max_length=50)
    doors: Optional[int] = Field(None, ge=2, le=5)
    seats: Optional[int] = Field(None, ge=2, le=9)
    fuel_type: Optional[FuelType] = None
    transmission: Optional[TransmissionType] = None
    body_type: Optional[BodyType] = None
    price: Decimal = Field(..., gt=0)
    video_url: Optional[HttpUrl] = None
    features: Optional[Dict] = Field(default_factory=dict)

    @field_validator('model_year')
    @classmethod
    def validate_model_year(cls, v, info):
        """Validate model_year is >= year and <= year + 1."""
        if v is not None:
            year = info.data.get('year')
            if year is not None:
                if v < year or v > year + 1:
                    raise ValueError(
                        'model_year must be >= year and <= year + 1'
                    )
        return v


class VehicleCreate(VehicleBase):
    """Schema for vehicle creation."""

    status: VehicleStatus = VehicleStatus.PENDING


class VehicleUpdate(BaseModel):
    """Schema for vehicle update."""

    title: Optional[str] = Field(None, min_length=5, max_length=500)
    description: Optional[str] = Field(None, max_length=5000)
    brand: Optional[str] = Field(None, min_length=2, max_length=100)
    model: Optional[str] = Field(None, min_length=2, max_length=100)
    year: Optional[int] = Field(None, ge=1900, le=2030)
    model_year: Optional[int] = Field(None, ge=1900, le=2030)
    version: Optional[str] = Field(None, max_length=100)
    color: Optional[str] = Field(None, max_length=50)
    mileage: Optional[int] = Field(None, ge=0)
    plate: Optional[str] = Field(None, max_length=20)
    chassis: Optional[str] = Field(None, max_length=50)
    doors: Optional[int] = Field(None, ge=2, le=5)
    seats: Optional[int] = Field(None, ge=2, le=9)
    fuel_type: Optional[FuelType] = None
    transmission: Optional[TransmissionType] = None
    body_type: Optional[BodyType] = None
    price: Optional[Decimal] = Field(None, gt=0)
    video_url: Optional[HttpUrl] = None
    features: Optional[Dict] = None
    status: Optional[VehicleStatus] = None

    @field_validator('model_year')
    @classmethod
    def validate_model_year(cls, v, info):
        """Validate model_year is >= year and <= year + 1."""
        if v is not None:
            year = info.data.get('year')
            if year is not None:
                if v < year or v > year + 1:
                    raise ValueError(
                        'model_year must be >= year and <= year + 1'
                    )
        return v


class VehicleResponse(VehicleBase):
    """Schema for vehicle response."""

    id: UUID
    dealership_id: UUID
    status: VehicleStatus
    price_market: Optional[Decimal]
    price_score: Optional[int]
    price_position: Optional[str]
    images: Optional[List[str]] = Field(default_factory=list)
    main_image: Optional[str]
    ai_analysis: Optional[Dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class VehicleAnalyzeResponse(BaseModel):
    """Schema for vehicle analysis response."""

    price_market: Decimal
    price_score: int
    price_position: str
    selling_points: List[str]
    target_audience: List[str]
    suggested_improvements: List[str]
    estimated_ctr: float
    estimated_conversion: float
    ai_analysis: Dict
    analysis_version: str
    analyzed_at: datetime


class SimilarVehicleResponse(BaseModel):
    """Schema for similar vehicle response."""

    id: UUID
    title: str
    brand: str
    model: str
    year: int
    price: Decimal
    mileage: Optional[int]
    similarity: float
    main_image: Optional[str]


class SemanticSearchResponse(BaseModel):
    """Schema for semantic search response."""

    id: UUID
    title: str
    brand: str
    model: str
    year: int
    price: Decimal
    mileage: Optional[int]
    similarity: float
    main_image: Optional[str]
    description: Optional[str]


class ImageUploadResponse(BaseModel):
    """Schema for image upload response."""

    images: List[str]
    main_image: Optional[str]
