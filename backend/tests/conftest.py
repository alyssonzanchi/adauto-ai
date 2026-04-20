"""
Test configuration and fixtures.
"""
import asyncio
from typing import AsyncGenerator, Generator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.core.config import settings


# Override settings for testing
settings.TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/car_ads_test"
settings.REDIS_URL = "redis://localhost:6379/15"  # Use DB 15 for tests


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def app() -> FastAPI:
    """Create test FastAPI application."""
    from app.main import app
    return app


@pytest.fixture
async def client(app: FastAPI) -> AsyncGenerator:
    """Create test HTTP client."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
