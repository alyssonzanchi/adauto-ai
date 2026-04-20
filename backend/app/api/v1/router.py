"""
API router.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import ads, auth, users, dealerships, profile, vehicles, ml
# from app.api.v1.endpoints import ai_agents  # Temporarily disabled due to missing schemas

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
    vehicles.router,
    prefix="/vehicles",
    tags=["Vehicles"]
)

api_router.include_router(
    ads.router,
    prefix="/ads",
    tags=["Ads"]
)

api_router.include_router(
    profile.router,
    tags=["Profile"]
)

api_router.include_router(
    ml.router,
    prefix="/ml",
    tags=["Machine Learning"]
)

# Temporarily disabled due to missing schemas
# api_router.include_router(
#     ai_agents.router,
#     prefix="/ai",
#     tags=["AI Agents"]
# )
