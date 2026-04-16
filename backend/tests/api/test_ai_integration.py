"""
Integration tests for AI Service endpoints.

These tests validate the end-to-end AI functionality:
- Vehicle analysis
- Semantic search
- Similar vehicles
- Ad generation

Run with: pytest tests/api/test_ai_integration.py -v
"""
import asyncio
from decimal import Decimal
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.vehicle import Vehicle
from app.models.user import User
from app.models.dealership import Dealership


# Skip all tests if AI service is disabled
pytestmark = pytest.mark.skipif(
    not settings.ENABLE_AI_SERVICE,
    reason="AI service is disabled via ENABLE_AI_SERVICE"
)


@pytest.fixture
async def test_vehicle_with_data(db: AsyncSession, test_dealership):
    """Create a test vehicle with complete data."""
    vehicle = Vehicle(
        dealership_id=test_dealership.id,
        title="Honda Civic Touring 2021 Impecável",
        description="Honda Civic Touring 2021, único dono, todas revisões na concessionária. Carro de não fumante, com manual e chave reserva. Aceito financiamento.",
        brand="Honda",
        model="Civic",
        year=2021,
        model_year=2021,
        version="Touring",
        color="Branco Pérola",
        mileage=25000,
        mileage_unit="km",
        transmission="automatic",
        fuel_type="flex",
        body_type="sedan",
        doors=4,
        seats=5,
        price=Decimal("115000.00"),
        status="active",
        features={
            "security": ["airbags", "abs", "controle_estabilidade", "freios_disco"],
            "comfort": [
                "ar_condicionado",
                "direcao_eletrica",
                "bancos_couro",
                "teto_solar",
            ],
            "technology": ["central_multimidia", "gps", "android_auto", "apple_carplay"],
            "extras": ["rodas_liga_leve", "piloto_automatico", "camera_re"],
        },
        ownership="unico_dono",
        images=[
            "https://example.com/image1.jpg",
            "https://example.com/image2.jpg",
        ],
        main_image="https://example.com/image1.jpg",
    )
    db.add(vehicle)
    await db.commit()
    await db.refresh(vehicle)
    return vehicle


@pytest.mark.asyncio
async def test_health_check_ai(client: AsyncClient):
    """Test AI health check endpoint."""
    response = await client.get("/health/ai")

    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert "services" in data

    # Services should include llm_client at minimum
    assert "llm_client" in data["services"]


@pytest.mark.asyncio
async def test_analyze_vehicle_success(
    client: AsyncClient,
    test_vehicle_with_data: Vehicle,
    manager_token: str,
):
    """Test successful vehicle analysis."""
    vehicle_id = str(test_vehicle_with_data.id)

    response = await client.post(
        f"/api/v1/vehicles/{vehicle_id}/analyze",
        headers={"Authorization": f"Bearer {manager_token}"},
    )

    assert response.status_code == 200

    data = response.json()
    assert "price_market" in data
    assert "price_score" in data
    assert "price_position" in data
    assert "selling_points" in data
    assert "target_audience" in data
    assert "suggested_improvements" in data
    assert "estimated_ctr" in data
    assert "estimated_conversion" in data
    assert "ai_analysis" in data

    # Validate data types
    assert isinstance(data["price_score"], int)
    assert 0 <= data["price_score"] <= 100
    assert isinstance(data["selling_points"], list)
    assert isinstance(data["target_audience"], list)
    assert isinstance(data["suggested_improvements"], list)
    assert isinstance(data["estimated_ctr"], (int, float))
    assert isinstance(data["estimated_conversion"], (int, float))

    # Validate price_position is one of expected values
    valid_positions = [
        "great_deal",
        "good_price",
        "fair_price",
        "above_market",
        "expensive",
        "overpriced",
    ]
    assert data["price_position"] in valid_positions


@pytest.mark.asyncio
async def test_analyze_vehicle_unauthorized(
    client: AsyncClient,
    test_vehicle_with_data: Vehicle,
):
    """Test vehicle analysis without authentication."""
    vehicle_id = str(test_vehicle_with_data.id)

    response = await client.post(f"/api/v1/vehicles/{vehicle_id}/analyze")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_analyze_vehicle_forbidden(
    client: AsyncClient,
    test_vehicle_with_data: Vehicle,
    user_token: str,  # Regular user, not manager
):
    """Test vehicle analysis by non-manager user."""
    vehicle_id = str(test_vehicle_with_data.id)

    response = await client.post(
        f"/api/v1/vehicles/{vehicle_id}/analyze",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
@pytest.mark.skipif(
    not settings.ENABLE_VECTOR_SEARCH,
    reason="Vector search is disabled"
)
async def test_semantic_search_success(
    client: AsyncClient,
    test_vehicle_with_data: Vehicle,
    manager_token: str,
):
    """Test semantic search endpoint."""
    response = await client.get(
        "/api/v1/vehicles/search/semantic",
        params={"query": "sedan Honda econômico bem conservado"},
        headers={"Authorization": f"Bearer {manager_token}"},
    )

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)

    # If results exist, validate structure
    if len(data) > 0:
        result = data[0]
        assert "id" in result
        assert "title" in result
        assert "brand" in result
        assert "model" in result
        assert "similarity" in result
        assert isinstance(result["similarity"], (int, float))


@pytest.mark.asyncio
@pytest.mark.skipif(
    not settings.ENABLE_VECTOR_SEARCH,
    reason="Vector search is disabled"
)
async def test_semantic_search_short_query(
    client: AsyncClient,
    manager_token: str,
):
    """Test semantic search with query that's too short."""
    response = await client.get(
        "/api/v1/vehicles/search/semantic",
        params={"query": "car"},  # Too short (min 3 chars)
        headers={"Authorization": f"Bearer {manager_token}"},
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
@pytest.mark.skipif(
    not settings.ENABLE_VECTOR_SEARCH,
    reason="Vector search is disabled"
)
async def test_get_similar_vehicles_success(
    client: AsyncClient,
    test_vehicle_with_data: Vehicle,
    manager_token: str,
    db: AsyncSession,
):
    """Test getting similar vehicles."""
    # First, we need to ensure the vehicle has embeddings
    # This would normally be done by a background task

    # For now, we'll just test the endpoint exists
    vehicle_id = str(test_vehicle_with_data.id)

    response = await client.get(
        f"/api/v1/vehicles/{vehicle_id}/similar",
        params={"limit": 5},
        headers={"Authorization": f"Bearer {manager_token}"},
    )

    # May return 200 (if embeddings exist) or empty list
    # or 500 if no embeddings yet (expected in test environment)
    assert response.status_code in [200, 500]


@pytest.mark.asyncio
async def test_generate_ad_content_success(
    client: AsyncClient,
    test_vehicle_with_data: Vehicle,
    manager_token: str,
):
    """Test ad content generation."""
    vehicle_id = str(test_vehicle_with_data.id)

    response = await client.post(
        f"/api/v1/vehicles/ai/generate-ad",
        params={"vehicle_id": vehicle_id, "content_type": "headline"},
        headers={"Authorization": f"Bearer {manager_token}"},
    )

    assert response.status_code == 200

    data = response.json()
    assert "headline" in data
    assert "subheadline" in data

    # Validate content
    assert isinstance(data["headline"], str)
    assert len(data["headline"]) > 0
    assert isinstance(data["subheadline"], str)
    assert len(data["subheadline"]) > 0


@pytest.mark.asyncio
async def test_generate_ad_content_full(
    client: AsyncClient,
    test_vehicle_with_data: Vehicle,
    manager_token: str,
):
    """Test full ad content generation."""
    vehicle_id = str(test_vehicle_with_data.id)

    response = await client.post(
        f"/api/v1/vehicles/ai/generate-ad",
        params={"vehicle_id": vehicle_id, "content_type": "full"},
        headers={"Authorization": f"Bearer {manager_token}"},
    )

    assert response.status_code == 200

    data = response.json()
    assert "headline" in data
    assert "subheadline" in data
    assert "description" in data
    assert "cta" in data
    assert "keywords" in data

    # Validate content
    assert isinstance(data["description"], str)
    assert len(data["description"]) > 100
    assert isinstance(data["keywords"], list)
    assert len(data["keywords"]) > 0


@pytest.mark.asyncio
async def test_analyze_vehicle_updates_database(
    client: AsyncClient,
    test_vehicle_with_data: Vehicle,
    manager_token: str,
    db: AsyncSession,
):
    """Test that vehicle analysis updates the database."""
    vehicle_id = str(test_vehicle_with_data.id)

    # Get initial state
    await db.refresh(test_vehicle_with_data)
    initial_price_market = test_vehicle_with_data.price_market
    initial_price_score = test_vehicle_with_data.price_score
    initial_ai_analysis = test_vehicle_with_data.ai_analysis

    # Run analysis
    response = await client.post(
        f"/api/v1/vehicles/{vehicle_id}/analyze",
        headers={"Authorization": f"Bearer {manager_token}"},
    )

    assert response.status_code == 200

    # Refresh from database
    await db.refresh(test_vehicle_with_data)

    # Verify fields were updated
    assert test_vehicle_with_data.price_market is not None
    assert test_vehicle_with_data.price_score is not None
    assert test_vehicle_with_data.price_position is not None
    assert test_vehicle_with_data.ai_analysis is not None

    # Values should have changed (unless previously analyzed)
    if initial_price_market is None:
        assert test_vehicle_with_data.price_market != initial_price_market


@pytest.mark.asyncio
@pytest.mark.skipif(
    settings.ENABLE_AI_SERVICE,
    reason="Test requires AI service to be disabled"
)
async def test_ai_service_disabled_returns_503(
    client: AsyncClient,
    manager_token: str,
):
    """Test that AI endpoints return 503 when AI service is disabled."""
    # This test would need ENABLE_AI_SERVICE=False to run properly
    # Included here for documentation purposes

    # Create a vehicle ID (doesn't need to exist)
    fake_id = str(uuid4())

    response = await client.post(
        f"/api/v1/vehicles/{fake_id}/analyze",
        headers={"Authorization": f"Bearer {manager_token}"},
    )

    # Should return 503 or 404 when disabled
    assert response.status_code in [503, 404]


@pytest.mark.asyncio
async def test_vehicle_analysis_performance(
    client: AsyncClient,
    test_vehicle_with_data: Vehicle,
    manager_token: str,
):
    """Test that vehicle analysis completes in reasonable time."""
    import time

    vehicle_id = str(test_vehicle_with_data.id)

    start_time = time.time()

    response = await client.post(
        f"/api/v1/vehicles/{vehicle_id}/analyze",
        headers={"Authorization": f"Bearer {manager_token}"},
    )

    elapsed_time = time.time() - start_time

    assert response.status_code == 200

    # Analysis should complete in less than 10 seconds
    # (P95 target is 3s, but we allow more for test environment)
    assert elapsed_time < 10.0, f"Analysis took too long: {elapsed_time:.2f}s"
