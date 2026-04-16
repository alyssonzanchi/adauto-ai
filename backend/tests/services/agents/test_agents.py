"""
Unit tests for AI Agents.

Tests agent functionality:
- AnalyzerAgent
- GeneratorAgent
- ScorerAgent
- BaseAgent functionality

Run with: pytest tests/services/agents/test_agents.py -v
"""
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.ai.agents.base import BaseAgent
from app.services.ai.agents.analyzer import AnalyzerAgent
from app.services.ai.agents.generator import GeneratorAgent
from app.services.ai.agents.scorer import ScorerAgent
from app.services.llm.llm_client import LLMClientError
from app.services.llm.prompts.vehicle_analysis import VehicleAnalysisPrompt
from app.services.llm.prompts.ad_generation import AdGenerationPrompt
from app.services.llm.prompts.price_scoring import PriceScoringPrompt


@pytest.fixture
def mock_llm_client():
    """Create mock LLM client."""
    client = MagicMock()
    client.generate = AsyncMock()
    return client


@pytest.fixture
def sample_vehicle_data():
    """Create sample vehicle data for testing."""
    return {
        "id": "test-uuid-123",
        "brand": "Honda",
        "model": "Civic",
        "year": 2021,
        "mileage": 25000,
        "price": 115000.0,
        "body_type": "sedan",
        "transmission": "automatic",
        "fuel_type": "flex",
        "features": {
            "security": ["airbags", "abs"],
            "comfort": ["ar_condicionado"],
            "technology": ["central_multimidia"],
        },
        "description": "Carro impecável",
        "title": "Honda Civic Touring 2021",
    }


class TestBaseAgent:
    """Test BaseAgent functionality."""

    def test_base_agent_initialization(self, mock_llm_client):
        """Test base agent initialization."""
        prompt_template = VehicleAnalysisPrompt()
        agent = BaseAgent(
            llm_client=mock_llm_client,
            prompt_template=prompt_template,
            name="test_agent",
        )

        assert agent.llm_client == mock_llm_client
        assert agent.prompt_template == prompt_template
        assert agent.name == "test_agent"
        assert agent.metrics["executions"] == 0

    def test_validate_response_success(self, mock_llm_client):
        """Test successful response validation."""
        prompt_template = VehicleAnalysisPrompt()
        agent = BaseAgent(
            llm_client=mock_llm_client,
            prompt_template=prompt_template,
            name="test_agent",
        )

        response = {
            "price_market": 100000.0,
            "price_score": 75,
            "selling_points": ["test"],
        }

        # Should not raise
        agent.validate_response(response, ["price_market", "price_score"])

    def test_validate_response_missing_keys(self, mock_llm_client):
        """Test response validation with missing keys."""
        prompt_template = VehicleAnalysisPrompt()
        agent = BaseAgent(
            llm_client=mock_llm_client,
            prompt_template=prompt_template,
            name="test_agent",
        )

        response = {
            "price_market": 100000.0,
        }

        # Should raise ValueError
        with pytest.raises(ValueError, match="missing required keys"):
            agent.validate_response(response, ["price_market", "price_score"])

    def test_sanitize_response(self, mock_llm_client):
        """Test response sanitization."""
        prompt_template = VehicleAnalysisPrompt()
        agent = BaseAgent(
            llm_client=mock_llm_client,
            prompt_template=prompt_template,
            name="test_agent",
        )

        response = {
            "price_market": 100000.0,
            "price_score": 75,
            "null_value": None,
            "empty_string": "",
        }

        sanitized = agent.sanitize_response(response)

        assert "price_market" in sanitized
        assert "price_score" in sanitized
        assert "null_value" not in sanitized  # None values removed

    def test_get_metrics(self, mock_llm_client):
        """Test getting agent metrics."""
        prompt_template = VehicleAnalysisPrompt()
        agent = BaseAgent(
            llm_client=mock_llm_client,
            prompt_template=prompt_template,
            name="test_agent",
        )

        # Simulate some executions
        agent.metrics["executions"] = 10
        agent.metrics["successes"] = 8
        agent.metrics["failures"] = 2

        metrics = agent.get_metrics()

        assert metrics["executions"] == 10
        assert metrics["successes"] == 8
        assert metrics["failures"] == 2
        assert metrics["success_rate"] == 0.8


class TestAnalyzerAgent:
    """Test AnalyzerAgent functionality."""

    def test_analyzer_agent_initialization(self, mock_llm_client):
        """Test analyzer agent initialization."""
        agent = AnalyzerAgent(llm_client=mock_llm_client)

        assert agent.name == "AnalyzerAgent"
        assert isinstance(agent.prompt_template, VehicleAnalysisPrompt)

    @pytest.mark.asyncio
    async def test_analyzer_execute_success(
        self, mock_llm_client, sample_vehicle_data
    ):
        """Test successful vehicle analysis."""
        # Mock LLM response
        mock_llm_client.generate.return_value = """{
            "price_market": 110000.0,
            "price_score": 80,
            "price_position": "good_price",
            "selling_points": ["unico_dono", "baixa_quilometragem"],
            "target_audience": ["familias", "profissionais"],
            "suggested_improvements": ["mais_fotos"],
            "estimated_ctr": 0.045,
            "estimated_conversion": 0.028,
            "reasoning": {
                "market_analysis": "Test analysis",
                "selling_points_rationale": "Test rationale",
                "audience_rationale": "Test audience rationale"
            }
        }"""

        agent = AnalyzerAgent(llm_client=mock_llm_client)

        result = await agent.execute({"vehicle": sample_vehicle_data})

        assert result["price_market"] == 110000.0
        assert result["price_score"] == 80
        assert result["price_position"] == "good_price"
        assert isinstance(result["selling_points"], list)
        assert "analysis_version" in result
        assert "analyzed_at" in result

    @pytest.mark.asyncio
    async def test_analyzer_execute_missing_vehicle(self, mock_llm_client):
        """Test analyzer with missing vehicle data."""
        agent = AnalyzerAgent(llm_client=mock_llm_client)

        with pytest.raises(ValueError, match="Missing 'vehicle'"):
            await agent.execute({})

    @pytest.mark.asyncio
    async def test_analyzer_invalid_json_response(
        self, mock_llm_client, sample_vehicle_data
    ):
        """Test analyzer with invalid JSON response."""
        # Mock invalid JSON response
        mock_llm_client.generate.return_value = "This is not JSON"

        agent = AnalyzerAgent(llm_client=mock_llm_client)

        with pytest.raises(ValueError, match="Invalid LLM response format"):
            await agent.execute({"vehicle": sample_vehicle_data})


class TestGeneratorAgent:
    """Test GeneratorAgent functionality."""

    def test_generator_agent_initialization(self, mock_llm_client):
        """Test generator agent initialization."""
        agent = GeneratorAgent(llm_client=mock_llm_client)

        assert agent.name == "GeneratorAgent"
        assert isinstance(agent.prompt_template, AdGenerationPrompt)

    @pytest.mark.asyncio
    async def test_generator_headline_success(
        self, mock_llm_client, sample_vehicle_data
    ):
        """Test headline generation."""
        # Mock LLM response
        mock_llm_client.generate.return_value = """{
            "headline": "Honda Civic Touring 2021 - Impecável",
            "subheadline": "Único dono, baixa quilometragem"
        }"""

        agent = GeneratorAgent(llm_client=mock_llm_client)

        result = await agent.execute({
            "vehicle": sample_vehicle_data,
            "content_type": "headline",
        })

        assert result["headline"] == "Honda Civic Touring 2021 - Impecável"
        assert result["subheadline"] == "Único dono, baixa quilometragem"
        assert "generated_at" in result

    @pytest.mark.asyncio
    async def test_generator_full_ad_success(
        self, mock_llm_client, sample_vehicle_data
    ):
        """Test full ad generation."""
        # Mock LLM response
        mock_llm_client.generate.return_value = """{
            "headline": "Honda Civic Touring 2021",
            "subheadline": "Sedã premium completo",
            "description": "Carro impecável com todos os opcionais...",
            "cta": "Agende seu test-drive",
            "keywords": ["honda civic", "sedan usado", "carros em sp"]
        }"""

        agent = GeneratorAgent(llm_client=mock_llm_client)

        result = await agent.execute({
            "vehicle": sample_vehicle_data,
            "content_type": "full",
        })

        assert "headline" in result
        assert "description" in result
        assert "cta" in result
        assert "keywords" in result
        assert isinstance(result["keywords"], list)

    @pytest.mark.asyncio
    async def test_generator_missing_vehicle(self, mock_llm_client):
        """Test generator with missing vehicle data."""
        agent = GeneratorAgent(llm_client=mock_llm_client)

        with pytest.raises(ValueError, match="Missing 'vehicle'"):
            await agent.execute({"content_type": "full"})


class TestScorerAgent:
    """Test ScorerAgent functionality."""

    def test_scorer_agent_initialization(self, mock_llm_client):
        """Test scorer agent initialization."""
        agent = ScorerAgent(llm_client=mock_llm_client)

        assert agent.name == "ScorerAgent"
        assert isinstance(agent.prompt_template, PriceScoringPrompt)

    @pytest.mark.asyncio
    async def test_scorer_execute_success(
        self, mock_llm_client, sample_vehicle_data
    ):
        """Test successful price scoring."""
        # Add listed_price to vehicle data
        vehicle_with_price = {
            **sample_vehicle_data,
            "listed_price": 115000.0,
        }

        # Mock LLM response
        mock_llm_client.generate.return_value = """{
            "fair_market_price": 110000.0,
            "price_range": {
                "excellent_condition": 115000,
                "good_condition": 110000,
                "fair_condition": 105000
            },
            "competitiveness_score": 85,
            "positioning": "good_price",
            "listed_vs_market": {
                "difference": -5000,
                "difference_percent": -4.3,
                "assessment": "Priced 4.3% below fair market value"
            },
            "market_insights": {
                "demand_level": "moderate",
                "supply_level": "moderate",
                "trend": "stable",
                "reasoning": "Test reasoning"
            },
            "recommendations": [
                "Price is competitive",
                "Highlight low mileage"
            ],
            "estimated_days_to_sell": {
                "at_current_price": 25,
                "at_recommended_price": 25
            }
        }"""

        agent = ScorerAgent(llm_client=mock_llm_client)

        result = await agent.execute({"vehicle": vehicle_with_price})

        assert result["fair_market_price"] == 110000.0
        assert result["competitiveness_score"] == 85
        assert result["positioning"] == "good_price"
        assert "price_range" in result
        assert "market_insights" in result
        assert "scored_at" in result

    @pytest.mark.asyncio
    async def test_scorer_missing_listed_price(
        self, mock_llm_client, sample_vehicle_data
    ):
        """Test scorer with missing listed_price."""
        agent = ScorerAgent(llm_client=mock_llm_client)

        with pytest.raises(ValueError, match="Missing 'listed_price'"):
            await agent.execute({"vehicle": sample_vehicle_data})


@pytest.mark.asyncio
async def test_agent_metrics_tracking(mock_llm_client, sample_vehicle_data):
    """Test that agents properly track metrics."""
    # Setup mock
    mock_llm_client.generate.return_value = """{
        "price_market": 100000.0,
        "price_score": 75,
        "price_position": "fair_price",
        "selling_points": ["test"],
        "target_audience": ["test"],
        "suggested_improvements": ["test"],
        "estimated_ctr": 0.03,
        "estimated_conversion": 0.02,
        "reasoning": {}
    }"""

    agent = AnalyzerAgent(llm_client=mock_llm_client)

    # Execute multiple times
    await agent.execute({"vehicle": sample_vehicle_data})
    await agent.execute({"vehicle": sample_vehicle_data})

    metrics = agent.get_metrics()

    assert metrics["executions"] == 2
    assert metrics["successes"] == 2
    assert metrics["failures"] == 0
    assert metrics["success_rate"] == 1.0


@pytest.mark.asyncio
async def test_agent_error_handling(mock_llm_client, sample_vehicle_data):
    """Test agent error handling."""
    # Mock LLM error
    mock_llm_client.generate.side_effect = LLMClientError("API error")

    agent = AnalyzerAgent(llm_client=mock_llm_client)

    # Should raise the error
    with pytest.raises(LLMClientError):
        await agent.execute({"vehicle": sample_vehicle_data})

    # Metrics should track the failure
    metrics = agent.get_metrics()
    assert metrics["executions"] == 1
    assert metrics["failures"] == 1
    assert metrics["success_rate"] == 0.0
