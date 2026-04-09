"""
Database enumerations.
"""
import enum


class DealershipStatus(str, enum.Enum):
    """Dealership status."""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING = "pending"


class UserRole(str, enum.Enum):
    """User role."""
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"


class UserStatus(str, enum.Enum):
    """User status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"


class FuelType(str, enum.Enum):
    """Fuel type."""
    GASOLINE = "gasoline"
    ETHANOL = "ethanol"
    DIESEL = "diesel"
    FLEX = "flex"
    ELECTRIC = "electric"
    HYBRID = "hybrid"


class TransmissionType(str, enum.Enum):
    """Transmission type."""
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    CVT = "cvt"
    DCT = "dct"


class BodyType(str, enum.Enum):
    """Vehicle body type."""
    SEDAN = "sedan"
    HATCH = "hatch"
    SUV = "suv"
    PICKUP = "pickup"
    COUPE = "coupe"
    CONVERTIBLE = "convertible"
    VAN = "van"
    WAGON = "wagon"


class VehicleStatus(str, enum.Enum):
    """Vehicle status."""
    ACTIVE = "active"
    SOLD = "sold"
    PENDING = "pending"
    INACTIVE = "inactive"


class AdPlatform(str, enum.Enum):
    """Ad platform."""
    FACEBOOK = "facebook"
    GOOGLE = "google"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    LINKEDIN = "linkedin"


class AdStatus(str, enum.Enum):
    """Ad status."""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ConnectionStatus(str, enum.Enum):
    """Connection status."""
    ACTIVE = "active"
    EXPIRED = "expired"
    ERROR = "error"
    PENDING = "pending"


class OptimizationType(str, enum.Enum):
    """Optimization type."""
    BUDGET = "budget"
    CREATIVE = "creative"
    TARGETING = "targeting"
    BID = "bid"


class PredictionType(str, enum.Enum):
    """Prediction type."""
    CTR = "ctr"
    CONVERSION = "conversion"
    CLICKS = "clicks"
    IMPRESSIONS = "impressions"
    ROI = "roi"
    COST_PER_LEAD = "cost_per_lead"
