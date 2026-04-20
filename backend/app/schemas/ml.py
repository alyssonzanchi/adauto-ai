"""
ML Schemas - Pydantic schemas for ML predictions
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# Price Prediction Schemas
class VehicleDataBase(BaseModel):
    """Base vehicle data schema"""
    brand: str
    model: str
    model_year: int
    year: int
    mileage: float
    color: str
    transmission: str
    fuel_type: str
    body_type: str
    doors: int
    engine_capacity: float
    horsepower: int
    price: float
    status: str


class PricePredictionRequest(BaseModel):
    """Request for price prediction"""
    vehicle_data: VehicleDataBase


class PricePredictionResponse(BaseModel):
    """Response from price prediction"""
    predicted_price: float = Field(..., description="Predicted fair market price")
    price_range: List[float] = Field(..., description="Estimated price range [min, max]")
    price_score: int = Field(..., ge=0, le=100, description="Competitiveness score (0-100)")
    price_position: str = Field(..., description="Category (great_deal, good_price, fair_price, expensive, overpriced)")
    confidence: float = Field(..., ge=0, le=1, description="Prediction confidence")


# CTR Prediction Schemas
class AdContentData(BaseModel):
    """Ad content data"""
    headline: str
    description: str
    images: List[Dict[str, str]] = Field(default_factory=list)
    cta: str = ""


class InteractionDataBase(BaseModel):
    """Interaction data base"""
    view_count: int = 0
    unique_views: int = 0
    repeat_views: int = 0
    days_since_listing: int = 0
    image_views: int = 0
    gallery_views: int = 0
    phone_clicks: int = 0
    avg_session_duration: float = 0
    total_session_duration: float = 0
    bounce_rate: float = 0
    avg_click_depth: float = 0
    avg_time_on_page: float = 0
    avg_scroll_depth: float = 0
    form_submissions: int = 0
    test_drive_requests: int = 0
    financing_inquiries: int = 0
    lead_source: str = "unknown"
    lead_type: str = "unknown"
    device_type: str = "desktop"
    os: str = "unknown"
    browser: str = ""


class CTRPredictionRequest(BaseModel):
    """Request for CTR prediction"""
    vehicle_data: VehicleDataBase
    ad_content: Optional[AdContentData] = None
    interaction_data: Optional[InteractionDataBase] = None


class CTRPredictionResponse(BaseModel):
    """Response from CTR prediction"""
    predicted_ctr: float = Field(..., ge=0, le=1, description="Predicted CTR (0-1)")
    ctr_bucket: str = Field(..., description="Category (very_low, low, medium, high, very_high)")
    confidence: float = Field(..., ge=0, le=1, description="Prediction confidence")
    optimization_suggestions: List[str] = Field(default_factory=list, description="List of optimization suggestions")


# Conversion Prediction Schemas
class LeadDataBase(BaseModel):
    """Lead data"""
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    type: str = "unknown"
    source: str = "unknown"
    response_time: float = 0
    engagement_score: float = 0.5


class ConversionPredictionRequest(BaseModel):
    """Request for conversion prediction"""
    vehicle_data: VehicleDataBase
    lead_data: Optional[LeadDataBase] = None
    interaction_data: Optional[InteractionDataBase] = None


class ConversionPredictionResponse(BaseModel):
    """Response from conversion prediction"""
    predicted_conversion_rate: float = Field(..., ge=0, le=1, description="Predicted conversion rate (0-1)")
    conversion_probability: str = Field(..., description="Category (low, medium, high)")
    lead_quality_score: int = Field(..., ge=0, le=100, description="Lead quality score (0-100)")
    confidence: float = Field(..., ge=0, le=1, description="Prediction confidence")
