"""
Rate limiting middleware using Redis.
"""
import time
from typing import Callable, Optional
from uuid import uuid4

from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings


class RateLimiter:
    """Rate limiter using Redis."""

    def __init__(self, redis_client):
        """
        Initialize rate limiter.

        Args:
            redis_client: Redis client instance
        """
        self.redis = redis_client

    async def is_allowed(
        self,
        key: str,
        limit: int,
        window: int
    ) -> tuple[bool, dict]:
        """
        Check if request is allowed using sliding window algorithm.

        Args:
            key: Unique identifier for rate limit (user_id, IP, etc.)
            limit: Number of requests allowed
            window: Time window in seconds

        Returns:
            Tuple of (allowed, info_dict)
        """
        current_time = time.time()
        window_start = current_time - window

        # Remove old entries outside the window
        await self.redis.zremrangebyscore(
            f"ratelimit:{key}",
            0,
            window_start
        )

        # Count requests in current window
        current_requests = await self.redis.zcard(
            f"ratelimit:{key}"
        )

        if current_requests >= limit:
            # Get oldest request to calculate retry-after
            oldest_request = await self.redis.zrange(
                f"ratelimit:{key}",
                0,
                0,
                withscores=True
            )
            if oldest_request:
                retry_after = int(oldest_request[0][1] + window - current_time)
                return False, {
                    "limit": limit,
                    "remaining": 0,
                    "reset": int(oldest_request[0][1] + window)
                }

        # Add current request
        await self.redis.zadd(
            f"ratelimit:{key}",
            {str(uuid4()): current_time}
        )

        # Set expiration
        await self.redis.expire(f"ratelimit:{key}", window)

        # Get updated count
        total_requests = await self.redis.zcard(f"ratelimit:{key}")

        return True, {
            "limit": limit,
            "remaining": max(0, limit - total_requests),
            "reset": int(current_time + window)
        }


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware for FastAPI."""

    def __init__(
        self,
        app,
        redis_client,
        requests_per_minute: int = None,
        requests_per_hour: int = None,
    ):
        """
        Initialize rate limiting middleware.

        Args:
            app: FastAPI application
            redis_client: Redis client instance
            requests_per_minute: Requests per minute limit
            requests_per_hour: Requests per hour limit
        """
        super().__init__(app)
        self.redis = redis_client
        self.limiter = RateLimiter(redis_client)
        self.requests_per_minute = requests_per_minute or settings.RATE_LIMIT_PER_MINUTE
        self.requests_per_hour = requests_per_hour or settings.RATE_LIMIT_BURST

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with rate limiting.

        Args:
            request: Incoming request
            call_next: Next middleware/route

        Returns:
            Response

        Raises:
            HTTPException: If rate limit exceeded
        """
        # Skip rate limiting for health check and docs
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        # Get identifier for rate limiting
        identifier = await self._get_identifier(request)

        # Check per-minute limit
        allowed, info = await self.limiter.is_allowed(
            f"{identifier}:minute",
            self.requests_per_minute,
            60
        )

        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests",
                headers={
                    "X-RateLimit-Limit": str(info["limit"]),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(info["reset"]),
                    "Retry-After": str(info.get("retry_after", 60))
                }
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(info["reset"])

        return response

    async def _get_identifier(self, request: Request) -> str:
        """
        Get identifier for rate limiting.

        Priority:
        1. User ID (from JWT token)
        2. API Key (if implemented)
        3. IP Address

        Args:
            request: Incoming request

        Returns:
            Identifier string
        """
        # Try to get user ID from JWT token
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                from app.core.security import decode_token
                token = auth_header.split(" ")[1]
                payload = decode_token(token)
                if payload:
                    user_id = payload.get("sub")
                    if user_id:
                        return f"user:{user_id}"
            except Exception:
                pass

        # Fallback to IP address
        # Get real IP behind proxy
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            ip = forwarded_for.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"

        return f"ip:{ip}"


async def _check_rate_limit_dependency(
    request: Request,
    requests_per_minute: int = None,
    requests_per_hour: int = None
):
    """
    FastAPI dependency for custom rate limiting per endpoint.

    This function checks rate limits and raises HTTPException if exceeded.
    It should be used with Depends() in endpoint parameters.

    Args:
        request: Incoming FastAPI request
        requests_per_minute: Custom requests per minute limit
        requests_per_hour: Custom requests per hour limit

    Raises:
        HTTPException: If rate limit is exceeded

    Usage:
        @app.get("/expensive-endpoint")
        async def expensive_endpoint(
            _: None = Depends(check_rate_limit(requests_per_minute=10))
        ):
            ...
    """
    from app.core.redis_client import get_redis
    from app.core.config import settings

    try:
        redis = await get_redis()
        limiter = RateLimiter(redis)

        # Get identifier for rate limiting
        identifier = await _get_identifier_from_request(request)

        # Use custom limits or defaults
        limit_per_minute = requests_per_minute or settings.RATE_LIMIT_PER_MINUTE
        limit_per_hour = requests_per_hour or settings.RATE_LIMIT_BURST

        # Check per-minute limit
        allowed, info = await limiter.is_allowed(
            f"{identifier}:minute:custom",
            limit_per_minute,
            60
        )

        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded (per minute)",
                headers={
                    "X-RateLimit-Limit": str(info["limit"]),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(info["reset"]),
                    "Retry-After": str(info.get("retry_after", 60))
                }
            )

        # Check per-hour limit if specified
        if requests_per_hour:
            allowed, info = await limiter.is_allowed(
                f"{identifier}:hour:custom",
                limit_per_hour,
                3600
            )

            if not allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded (per hour)",
                    headers={
                        "X-RateLimit-Limit": str(info["limit"]),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(info["reset"]),
                        "Retry-After": str(info.get("retry_after", 3600))
                    }
                )

    except ConnectionError:
        # If Redis is unavailable, allow the request (fail open)
        pass
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log error but allow request (fail open)
        import logging
        logging.warning(f"Rate limiting error: {e}")


def check_rate_limit(
    requests_per_minute: int = None,
    requests_per_hour: int = None
):
    """
    Factory function that creates a rate limiting dependency for FastAPI.

    Use this with Depends() in your endpoint parameters to apply custom
    rate limiting to specific endpoints.

    Args:
        requests_per_minute: Custom requests per minute limit
        requests_per_hour: Custom requests per hour limit (3600 seconds)

    Returns:
        Dependency function for use with FastAPI's Depends()

    Usage Examples:
        # Basic usage - custom per-minute limit
        @app.get("/expensive-endpoint")
        async def expensive_endpoint(
            _: None = Depends(check_rate_limit(requests_per_minute=10))
        ):
            return {"data": "expensive computation"}

        # Both per-minute and per-hour limits
        @app.post("/api/generate-report")
        async def generate_report(
            _: None = Depends(check_rate_limit(
                requests_per_minute=5,
                requests_per_hour=50
            ))
        ):
            return {"report_id": "123"}

        # Use default limits from settings
        @app.get("/api/search")
        async def search(
            _: None = Depends(check_rate_limit())
        ):
            return {"results": []}
    """
    # Return a partial function with the rate limit parameters
    from functools import partial

    async def dependency(request: Request):
        await _check_rate_limit_dependency(
            request=request,
            requests_per_minute=requests_per_minute,
            requests_per_hour=requests_per_hour
        )

    return dependency


async def _get_identifier_from_request(request: Request) -> str:
    """
    Get identifier for rate limiting from request.

    Priority:
    1. User ID (from JWT token)
    2. API Key (if implemented)
    3. IP Address

    Args:
        request: Incoming request

    Returns:
        Identifier string
    """
    # Try to get user ID from JWT token
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        try:
            from app.core.security import decode_token
            token = auth_header.split(" ")[1]
            payload = decode_token(token)
            if payload:
                user_id = payload.get("sub")
                if user_id:
                    return f"user:{user_id}"
        except Exception:
            pass

    # Fallback to IP address
    # Get real IP behind proxy
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        ip = forwarded_for.split(",")[0].strip()
    else:
        ip = request.client.host if request.client else "unknown"

    return f"ip:{ip}"
