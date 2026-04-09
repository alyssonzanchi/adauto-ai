"""
SQLAlchemy models.
"""
from app.models.ad import Ad
from app.models.ad_metric import AdMetric
from app.models.ad_optimization import AdOptimization
from app.models.ad_platform_account import AdPlatformAccount
from app.models.dealership import Dealership
from app.models.enums import (
    AdPlatform,
    AdStatus,
    BodyType,
    ConnectionStatus,
    DealershipStatus,
    FuelType,
    OptimizationType,
    PredictionType,
    TransmissionType,
    UserStatus,
    UserRole,
    VehicleStatus,
)
from app.models.ml_prediction import MLPrediction
from app.models.session import Session
from app.models.user import User
from app.models.vehicle import Vehicle

__all__ = [
    # Models
    "Dealership",
    "User",
    "Vehicle",
    "Ad",
    "AdMetric",
    "AdPlatformAccount",
    "AdOptimization",
    "MLPrediction",
    "Session",
    # Enums
    "DealershipStatus",
    "UserRole",
    "UserStatus",
    "FuelType",
    "TransmissionType",
    "BodyType",
    "VehicleStatus",
    "AdPlatform",
    "AdStatus",
    "ConnectionStatus",
    "OptimizationType",
    "PredictionType",
]
