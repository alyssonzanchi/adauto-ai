"""
Rate Limiting Examples for FastAPI Endpoints.

This file demonstrates how to use the rate limiting functionality
in your FastAPI application.
"""
from fastapi import APIRouter, Depends, Request, HTTPException, status

from app.core.rate_limit import check_rate_limit

router = APIRouter(prefix="/examples", tags=["rate-limiting-examples"])


# Example 1: Basic usage with custom per-minute limit
@router.get("/expensive-computation")
async def expensive_computation(
    request: Request,
    _: None = Depends(check_rate_limit(requests_per_minute=10))
):
    """
    Endpoint with custom rate limit of 10 requests per minute.

    This is useful for expensive operations that should not be called too frequently.
    """
    return {
        "message": "This endpoint is limited to 10 requests per minute",
        "data": "expensive computation result"
    }


# Example 2: Both per-minute and per-hour limits
@router.post("/generate-report")
async def generate_report(
    request: Request,
    _: None = Depends(check_rate_limit(
        requests_per_minute=5,
        requests_per_hour=50
    ))
):
    """
    Endpoint with both per-minute (5) and per-hour (50) limits.

    This prevents both rapid bursts and excessive usage over time.
    """
    return {
        "message": "Report generation started",
        "limits": {
            "per_minute": 5,
            "per_hour": 50
        }
    }


# Example 3: Using default limits from settings
@router.get("/search")
async def search(
    request: Request,
    _: None = Depends(check_rate_limit())
):
    """
    Endpoint using default rate limits from settings.

    Defaults: RATE_LIMIT_PER_MINUTE (100) and RATE_LIMIT_BURST (200)
    """
    return {
        "message": "Search results",
        "results": []
    }


# Example 4: Very strict rate limiting for sensitive operations
@router.post("/reset-password")
async def reset_password(
    request: Request,
    _: None = Depends(check_rate_limit(requests_per_minute=3))
):
    """
    Very strict rate limiting for sensitive operations.

    Password reset should be limited to prevent abuse.
    """
    return {
        "message": "Password reset email sent"
    }


# Example 5: API endpoint with rate limiting
@router.get("/api/v1/vehicles")
async def list_vehicles(
    request: Request,
    _: None = Depends(check_rate_limit(requests_per_minute=60))
):
    """
    API endpoint with moderate rate limiting.

    60 requests per minute = 1 request per second on average.
    """
    return {
        "vehicles": [],
        "total": 0
    }


# Example 6: Admin endpoint with stricter limits
@router.get("/admin/analytics")
async def admin_analytics(
    request: Request,
    _: None = Depends(check_rate_limit(
        requests_per_minute=20,
        requests_per_hour=200
    ))
):
    """
    Admin endpoint with custom rate limits.

    Even though admins are trusted, we still want to prevent abuse.
    """
    return {
        "analytics": {
            "users": 1000,
            "vehicles": 5000
        }
    }


# Example 7: Integration with authentication
@router.get("/user/profile")
async def get_profile(
    request: Request,
    # Rate limiting + authentication dependency
    _: None = Depends(check_rate_limit(requests_per_minute=30))
):
    """
    Endpoint that uses rate limiting.

    The rate limiter will automatically use the user ID from the JWT token
    if available, otherwise it falls back to IP address.
    """
    return {
        "user": {
            "id": "123",
            "name": "John Doe"
        }
    }


# Example 8: File upload with rate limiting
@router.post("/upload-image")
async def upload_image(
    request: Request,
    _: None = Depends(check_rate_limit(requests_per_minute=15))
):
    """
    File upload endpoint with rate limiting.

    Prevents spam uploads and protects server resources.
    """
    return {
        "message": "Image uploaded successfully",
        "url": "https://example.com/image.jpg"
    }


# Example response when rate limit is exceeded:
# {
#     "detail": "Rate limit exceeded (per minute)"
# }
#
# HTTP Status: 429 Too Many Requests
#
# Response Headers:
# X-RateLimit-Limit: 10
# X-RateLimit-Remaining: 0
# X-RateLimit-Reset: 1713456789
# Retry-After: 45
