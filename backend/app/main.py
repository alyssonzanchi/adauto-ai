"""
Main FastAPI application.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import init_db, close_db
from app.core.redis_client import get_redis, close_redis


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Car Ads Platform API",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware (added before app starts)
@app.on_event("startup")
async def setup_rate_limiting():
    """Setup rate limiting middleware if Redis is available."""
    try:
        redis = await get_redis()
        from app.core.rate_limit import RateLimitMiddleware

        app.add_middleware(
            RateLimitMiddleware,
            redis_client=redis,
            requests_per_minute=settings.RATE_LIMIT_PER_MINUTE,
            requests_per_hour=settings.RATE_LIMIT_BURST,
        )
        print("✅ Rate limiting enabled")
    except Exception as e:
        print(f"⚠️  Rate limiting disabled: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    # Initialize database
    await init_db()

    yield

    # Shutdown
    await close_redis()
    await close_db()


app lifespan = lifespan()

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Car Ads Platform API",
        "version": settings.APP_VERSION,
        "status": "online",
        "docs": "/docs",
        "rate_limiting": {
            "per_minute": settings.RATE_LIMIT_PER_MINUTE,
            "burst": settings.RATE_LIMIT_BURST
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
