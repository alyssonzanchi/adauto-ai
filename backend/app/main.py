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
from app.services.ai.orchestrator import orchestrator, AgentOrchestrator
from app.services.cache.feature_store import FeatureStore
from app.services.llm.llm_client import LLMClient
from app.services.vector.embedding_service import EmbeddingService
from app.services.vector.vector_service import VectorService


async def startup_ai_services():
    """Initialize AI services on application startup."""
    if not settings.ENABLE_AI_SERVICE:
        print("⚠️  AI service disabled via feature flag")
        return

    try:
        # Initialize services
        redis_client = await get_redis()

        llm_client = LLMClient()
        embedding_service = EmbeddingService(cache_client=redis_client)
        vector_service = VectorService(embedding_service=embedding_service)
        feature_store = FeatureStore(redis_client=redis_client)

        # Initialize global orchestrator
        from app.services.ai import orchestrator as orch_module
        orch_module.orchestrator = AgentOrchestrator(
            llm_client=llm_client,
            embedding_service=embedding_service,
            vector_service=vector_service,
            feature_store=feature_store,
        )

        print("✅ AI services initialized successfully")

    except Exception as e:
        print(f"⚠️  Failed to initialize AI services: {e}")
        print("⚠️  AI features will be disabled")


async def shutdown_ai_services():
    """Shutdown AI services gracefully."""
    try:
        from app.services.ai import orchestrator as orch_module

        if orch_module.orchestrator:
            # Close feature store Redis connection
            if orch_module.orchestrator.feature_store:
                await orch_module.orchestrator.feature_store.close()

            # Reset global orchestrator
            orch_module.orchestrator = None

            print("✅ AI services shut down successfully")

    except Exception as e:
        print(f"⚠️  Error shutting down AI services: {e}")



@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    # Initialize database
    await init_db()

    # Initialize AI services
    await startup_ai_services()

    yield

    # Shutdown
    await shutdown_ai_services()
    await close_redis()
    await close_db()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Car Ads Platform API",
    lifespan=lifespan,
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


@app.get("/health/ai")
async def ai_health_check():
    """AI service health check endpoint."""
    try:
        from app.services.ai.orchestrator import get_orchestrator

        orchestrator = get_orchestrator()
        health = await orchestrator.health_check()

        return health

    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
        }

