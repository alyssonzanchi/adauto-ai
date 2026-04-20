"""
Basic smoke tests for Ads endpoints.

These tests validate that the ads endpoints are properly registered and accessible.

Run with: pytest tests/api/test_ads.py -v
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_ads_endpoints_exist(client):
    """Test that ads endpoints are registered."""
    # Test listing ads without auth (should return 401)
    response = await client.get("/api/v1/ads")
    assert response.status_code in [401, 403]  # Either unauthorized or forbidden


@pytest.mark.asyncio
async def test_ads_preview_endpoint_exists(client):
    """Test that ads preview endpoint is registered."""
    # Test preview without auth (might be public or require auth)
    response = await client.post(
        "/api/v1/ads/preview",
        json={
            "title": "Test",
            "platform": "facebook"
        }
    )
    # Should either work (200) or require auth (401, 403) or have validation error (422)
    assert response.status_code in [200, 401, 403, 422]  # 422 = validation error


@pytest.mark.asyncio
async def test_api_includes_ads_router(client):
    """Verify ads router is included in API."""
    # The OpenAPI spec should include the ads endpoints
    response = await client.get("/openapi.json")
    assert response.status_code == 200

    openapi_spec = response.json()
    assert "/api/v1/ads" in openapi_spec["paths"]
    assert "/api/v1/ads/{ad_id}" in openapi_spec["paths"]


@pytest.mark.asyncio
async def test_ads_endpoint_in_openapi(client):
    """Test that ads endpoints are documented in OpenAPI."""
    response = await client.get("/openapi.json")
    assert response.status_code == 200

    openapi_spec = response.json()

    # Check that ads endpoints are defined
    paths = openapi_spec["paths"]

    # Main ads endpoint
    assert "/api/v1/ads" in paths
    ads_path = paths["/api/v1/ads"]
    assert "get" in ads_path
    assert "post" in ads_path

    # Ad by ID endpoint
    assert "/api/v1/ads/{ad_id}" in paths
    ad_by_id_path = paths["/api/v1/ads/{ad_id}"]
    assert "get" in ad_by_id_path
    assert "put" in ad_by_id_path
    assert "delete" in ad_by_id_path

    # Status update endpoint
    assert "/api/v1/ads/{ad_id}/status" in paths
    assert "patch" in paths["/api/v1/ads/{ad_id}/status"]

    # Preview endpoint
    assert "/api/v1/ads/preview" in paths
    assert "post" in paths["/api/v1/ads/preview"]


@pytest.mark.asyncio
async def test_ads_openapi_schema(client):
    """Test that ads endpoints have proper OpenAPI schema."""
    response = await client.get("/openapi.json")
    assert response.status_code == 200

    openapi_spec = response.json()
    ad_schema = openapi_spec["components"]["schemas"].get("AdResponse")

    # Verify AdResponse schema exists and has required fields
    assert ad_schema is not None
    assert "properties" in ad_schema

    required_fields = ["id", "vehicle_id", "platform", "status", "title"]
    for field in required_fields:
        assert field in ad_schema["properties"], f"Field {field} not in AdResponse schema"
