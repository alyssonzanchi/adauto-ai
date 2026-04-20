"""
Pydantic schemas for request/response validation.
"""
from app.schemas.ad import (
    AdCreate,
    AdFilter,
    AdPreviewRequest,
    AdPreviewResponse,
    AdResponse,
    AdStatusUpdate,
    AdUpdate,
)
from app.schemas.auth import (
    Token,
    TokenPayload,
    UserLogin,
    UserRegister,
)
from app.schemas.dealership import (
    DealershipCreate,
    DealershipResponse,
    DealershipUpdate,
)
from app.schemas.user import (
    UserChangePassword,
    UserResponse,
    UserUpdate,
)

__all__ = [
    # Auth
    "UserRegister",
    "UserLogin",
    "Token",
    "TokenPayload",
    # User
    "UserResponse",
    "UserUpdate",
    "UserChangePassword",
    # Dealership
    "DealershipCreate",
    "DealershipResponse",
    "DealershipUpdate",
    # Ad
    "AdCreate",
    "AdUpdate",
    "AdResponse",
    "AdStatusUpdate",
    "AdFilter",
    "AdPreviewRequest",
    "AdPreviewResponse",
]
