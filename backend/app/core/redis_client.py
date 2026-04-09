"""
Redis client configuration.
"""
import redis.asyncio as redis
from typing import Optional

from app.core.config import settings


# Global Redis client
redis_client: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    """
    Get Redis client instance.

    Returns:
        Redis client

    Raises:
        ConnectionError: If Redis is not available
    """
    global redis_client

    if redis_client is None:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=50,
        )

        # Test connection
        try:
            await redis_client.ping()
        except Exception as e:
            redis_client = None
            raise ConnectionError(f"Failed to connect to Redis: {e}")

    return redis_client


async def close_redis():
    """Close Redis connection."""
    global redis_client

    if redis_client:
        await redis_client.close()
        redis_client = None
