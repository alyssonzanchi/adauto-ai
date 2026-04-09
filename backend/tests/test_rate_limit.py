"""
Rate limiting tests.
"""
import time
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import Request, HTTPException, status

from app.core.rate_limit import RateLimiter, check_rate_limit, _get_identifier_from_request


@pytest.fixture
async def mock_redis():
    """Create mock Redis client."""
    redis = AsyncMock()
    redis.zremrangebyscore = AsyncMock(return_value=0)
    redis.zcard = AsyncMock(return_value=0)
    redis.zadd = AsyncMock(return_value=1)
    redis.zrange = AsyncMock(return_value=[])
    redis.expire = AsyncMock(return_value=True)
    return redis


@pytest.fixture
def rate_limiter(mock_redis):
    """Create RateLimiter instance."""
    return RateLimiter(mock_redis)


class TestRateLimiter:
    """Tests for RateLimiter class."""

    @pytest.mark.asyncio
    async def test_is_allowed_under_limit(self, rate_limiter, mock_redis):
        """Test request is allowed when under limit."""
        # Mock Redis to return 5 requests (under limit of 10)
        mock_redis.zcard = AsyncMock(return_value=5)

        allowed, info = await rate_limiter.is_allowed(
            "test_key",
            limit=10,
            window=60
        )

        assert allowed is True
        assert info["limit"] == 10
        assert info["remaining"] == 5
        assert "reset" in info

    @pytest.mark.asyncio
    async def test_is_allowed_over_limit(self, rate_limiter, mock_redis):
        """Test request is denied when over limit."""
        current_time = time.time()

        # Mock Redis to return 10 requests (at limit)
        mock_redis.zcard = AsyncMock(return_value=10)

        # Mock oldest request time for retry-after calculation
        mock_redis.zrange = AsyncMock(
            return_value=[("request_id", current_time - 30)]
        )

        allowed, info = await rate_limiter.is_allowed(
            "test_key",
            limit=10,
            window=60
        )

        assert allowed is False
        assert info["limit"] == 10
        assert info["remaining"] == 0
        assert "reset" in info

    @pytest.mark.asyncio
    async def test_is_allowed_adds_request(self, rate_limiter, mock_redis):
        """Test that request is added to Redis."""
        mock_redis.zcard = AsyncMock(return_value=0)

        await rate_limiter.is_allowed("test_key", limit=10, window=60)

        # Verify request was added
        mock_redis.zadd.assert_called_once()
        mock_redis.expire.assert_called_once_with("ratelimit:test_key", 60)

    @pytest.mark.asyncio
    async def test_is_allowed_removes_old_requests(self, rate_limiter, mock_redis):
        """Test that old requests outside window are removed."""
        mock_redis.zcard = AsyncMock(return_value=0)

        await rate_limiter.is_allowed("test_key", limit=10, window=60)

        # Verify old entries were removed
        mock_redis.zremrangebyscore.assert_called_once()


class TestCheckRateLimit:
    """Tests for check_rate_limit dependency."""

    @pytest.mark.asyncio
    async def test_check_rate_limit_under_threshold(self, mock_redis):
        """Test dependency passes when under limit."""
        from app.core.redis_client import get_redis
        original_get_redis = get_redis

        # Mock get_redis to return our mock
        async def mock_get_redis():
            return mock_redis

        # Patch get_redis
        import app.core.rate_limit
        app.core.rate_limit.get_redis = mock_get_redis
        mock_redis.zcard = AsyncMock(return_value=5)

        # Create mock request
        request = MagicMock(spec=Request)
        request.headers = {}
        request.client = MagicMock(host="127.0.0.1")

        # Should not raise exception
        await check_rate_limit(requests_per_minute=10)(request)

        # Restore original
        app.core.rate_limit.get_redis = original_get_redis

    @pytest.mark.asyncio
    async def test_check_rate_limit_over_threshold_raises(self, mock_redis):
        """Test dependency raises HTTPException when over limit."""
        from app.core.redis_client import get_redis

        # Mock get_redis to return our mock
        async def mock_get_redis():
            return mock_redis

        # Patch get_redis
        import app.core.rate_limit
        app.core.rate_limit.get_redis = mock_get_redis

        current_time = time.time()
        mock_redis.zcard = AsyncMock(return_value=10)
        mock_redis.zrange = AsyncMock(
            return_value=[("request_id", current_time - 30)]
        )

        # Create mock request
        request = MagicMock(spec=Request)
        request.headers = {}
        request.client = MagicMock(host="127.0.0.1")

        # Should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await check_rate_limit(requests_per_minute=10)(request)

        assert exc_info.value.status_code == status.HTTP_429_TOO_MANY_REQUESTS

    @pytest.mark.asyncio
    async def test_check_rate_limit_redis_unavailable(self):
        """Test dependency fails open when Redis is unavailable."""
        from app.core.redis_client import get_redis, ConnectionError

        # Mock get_redis to raise ConnectionError
        async def mock_get_redis():
            raise ConnectionError("Redis unavailable")

        # Patch get_redis
        import app.core.rate_limit
        app.core.rate_limit.get_redis = mock_get_redis

        # Create mock request
        request = MagicMock(spec=Request)
        request.headers = {}
        request.client = MagicMock(host="127.0.0.1")

        # Should not raise exception (fail open)
        await check_rate_limit(requests_per_minute=10)(request)


class TestIdentifierExtraction:
    """Tests for identifier extraction from requests."""

    @pytest.mark.asyncio
    async def test_identifier_from_ip_address(self):
        """Test identifier is extracted from IP address."""
        request = MagicMock(spec=Request)
        request.headers = {}
        request.client = MagicMock(host="192.168.1.1")

        identifier = await _get_identifier_from_request(request)

        assert identifier == "ip:192.168.1.1"

    @pytest.mark.asyncio
    async def test_identifier_from_x_forwarded_for(self):
        """Test identifier is extracted from X-Forwarded-For header."""
        request = MagicMock(spec=Request)
        request.headers = {"X-Forwarded-For": "203.0.113.1, 70.41.3.18"}
        request.client = MagicMock(host="192.168.1.1")

        identifier = await _get_identifier_from_request(request)

        assert identifier == "ip:203.0.113.1"

    @pytest.mark.asyncio
    async def test_identifier_from_jwt_token(self):
        """Test identifier is extracted from JWT token."""
        request = MagicMock(spec=Request)
        request.headers = {"Authorization": "Bearer valid_token"}

        # Mock decode_token to return user_id
        async def mock_decode_token(token):
            return {"sub": "user123"}

        # Patch decode_token
        import app.core.rate_limit
        app.core.rate_limit.decode_token = mock_decode_token

        identifier = await _get_identifier_from_request(request)

        assert identifier == "user:user123"

    @pytest.mark.asyncio
    async def test_identifier_fallback_to_ip_on_invalid_token(self):
        """Test identifier falls back to IP when token is invalid."""
        request = MagicMock(spec=Request)
        request.headers = {"Authorization": "Bearer invalid_token"}
        request.client = MagicMock(host="192.168.1.1")

        # Mock decode_token to raise exception
        async def mock_decode_token(token):
            raise Exception("Invalid token")

        # Patch decode_token
        import app.core.rate_limit
        app.core.rate_limit.decode_token = mock_decode_token

        identifier = await _get_identifier_from_request(request)

        assert identifier == "ip:192.168.1.1"


@pytest.mark.integration
class TestRateLimitIntegration:
    """Integration tests for rate limiting."""

    @pytest.mark.asyncio
    async def test_rate_limit_middleware_flow(self):
        """Test complete rate limiting flow through middleware."""
        # This would require actual Redis connection
        pytest.skip("Requires actual Redis - mark as integration test")

    @pytest.mark.asyncio
    async def test_multiple_requests_rate_limiting(self):
        """Test multiple requests are properly rate limited."""
        # This would require actual Redis connection
        pytest.skip("Requires actual Redis - mark as integration test")
