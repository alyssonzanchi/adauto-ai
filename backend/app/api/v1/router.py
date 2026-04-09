"""
API router.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, dealerships, profile

api_router = APIRouter()

# Include routers
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
)

api_router.include_router(
    dealerships.router,
    prefix="/dealerships",
    tags=["Dealerships"]
)

api_router.include_router(
    profile.router,
    tags=["Profile"]
)
