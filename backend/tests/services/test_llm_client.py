"""
Unit tests for LLM Client.

Tests LLM client functionality:
- Claude API calls
- OpenAI fallback
- Retry logic
- Circuit breaker
- Error handling

Run with: pytest tests/services/test_llm_client.py -v
"""
from decimal import Decimal

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.llm.llm_client import LLMClient, LLMClientError, CircuitBreaker


@pytest.fixture
def mock_anthropic_client():
    """Create mock Anthropic client."""
    client = MagicMock()
    client.messages = MagicMock()
    client.messages.create = AsyncMock()
    return client


@pytest.fixture
def mock_openai_client():
    """Create mock OpenAI client."""
    client = MagicMock()
    client.chat = MagicMock()
    client.chat.completions = MagicMock()
    client.chat.completions.create = AsyncMock()
    return client


@pytest.fixture
def llm_client():
    """Create LLM client instance for testing."""
    # Use empty strings for API keys in tests
    # We'll mock the actual clients
    client = LLMClient(
        anthropic_api_key="test-anthropic-key",
        openai_api_key="test-openai-key",
    )
    return client


class TestCircuitBreaker:
    """Test circuit breaker functionality."""

    def test_circuit_breaker_initially_closed(self):
        """Test that circuit breaker starts closed."""
        cb = CircuitBreaker()
        assert cb.state == "closed"
        assert cb.can_attempt() is True

    def test_circuit_breaker_opens_after_threshold(self):
        """Test that circuit breaker opens after failure threshold."""
        cb = CircuitBreaker(failure_threshold=3)

        # Record failures up to threshold
        cb.record_failure()
        cb.record_failure()
        cb.record_failure()

        assert cb.state == "open"
        assert cb.can_attempt() is False

    def test_circuit_breaker_closes_after_success(self):
        """Test that circuit breaker closes after success."""
        cb = CircuitBreaker(failure_threshold=3)

        # Add some failures
        cb.record_failure()
        cb.record_failure()

        # Record success
        cb.record_success()

        assert cb.state == "closed"
        assert cb.failures == 0

    def test_circuit_breaker_half_open_after_timeout(self):
        """Test that circuit breaker enters half-open state after timeout."""
        cb = CircuitBreaker(failure_threshold=2, timeout=0)

        # Open the circuit
        cb.record_failure()
        cb.record_failure()

        assert cb.state == "open"

        # After timeout, should allow attempt (half-open)
        assert cb.can_attempt() is True
        assert cb.state == "half_open"


class TestLLMClient:
    """Test LLM client functionality."""

    def test_llm_client_initialization(self):
        """Test LLM client initialization."""
        client = LLMClient(
            anthropic_api_key="test-key",
            openai_api_key="test-key",
        )

        assert client.model_primary == "claude-3-5-sonnet-20241022"
        assert client.model_fallback == "gpt-4-turbo-preview"
        assert client.max_retries == 3
        assert client.timeout == 30
        assert client.metrics["claude_calls"] == 0
        assert client.metrics["openai_calls"] == 0

    def test_metrics_initialization(self):
        """Test that metrics are initialized correctly."""
        client = LLMClient()

        expected_metrics = {
            "claude_calls": 0,
            "claude_errors": 0,
            "claude_fallbacks": 0,
            "openai_calls": 0,
            "openai_errors": 0,
            "total_tokens": 0,
            "total_cost": Decimal("0.0"),
        }

        assert client.metrics == expected_metrics

    def test_get_metrics(self):
        """Test getting metrics."""
        client = LLMClient()
        client.metrics["claude_calls"] = 10
        client.metrics["claude_errors"] = 1

        metrics = client.get_metrics()

        assert metrics["claude_calls"] == 10
        assert metrics["claude_errors"] == 1
        assert "claude_success_rate" in metrics
        assert "openai_success_rate" in metrics
        assert "fallback_rate" in metrics

    def test_reset_metrics(self):
        """Test resetting metrics."""
        client = LLMClient()
        client.metrics["claude_calls"] = 100
        client.metrics["total_cost"] = Decimal("10.0")

        client.reset_metrics()

        assert client.metrics["claude_calls"] == 0
        assert client.metrics["total_cost"] == Decimal("0.0")

    @pytest.mark.asyncio
    async def test_generate_claude_success(self, llm_client, mock_anthropic_client):
        """Test successful generation with Claude."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Test response")]
        mock_response.usage = MagicMock(
            input_tokens=100,
            output_tokens=50,
        )
        mock_anthropic_client.messages.create.return_value = mock_response

        # Patch the client
        llm_client.anthropic_client = mock_anthropic_client

        # Generate
        result = await llm_client.generate(
            prompt="Test prompt",
            system_prompt="Test system prompt",
            response_format="json",
        )

        assert result == "Test response"
        assert llm_client.metrics["claude_calls"] == 1
        assert llm_client.metrics["total_tokens"] == 150

    @pytest.mark.asyncio
    async def test_generate_with_openai_fallback(
        self, llm_client, mock_anthropic_client, mock_openai_client
    ):
        """Test fallback to OpenAI when Claude fails."""
        # Mock Claude failure
        mock_anthropic_client.messages.create.side_effect = Exception("Claude error")

        # Mock OpenAI success
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Fallback response"))]
        mock_response.usage = MagicMock(
            prompt_tokens=100,
            completion_tokens=50,
        )
        mock_openai_client.chat.completions.create.return_value = mock_response

        # Patch the clients
        llm_client.anthropic_client = mock_anthropic_client
        llm_client.openai_client = mock_openai_client

        # Generate with fallback
        result = await llm_client.generate(
            prompt="Test prompt",
            use_fallback=True,
        )

        assert result == "Fallback response"
        assert llm_client.metrics["claude_errors"] == 1
        assert llm_client.metrics["claude_fallbacks"] == 1
        assert llm_client.metrics["openai_calls"] == 1

    @pytest.mark.asyncio
    async def test_generate_without_fallback(
        self, llm_client, mock_anthropic_client
    ):
        """Test generation without fallback raises error."""
        # Mock Claude failure
        mock_anthropic_client.messages.create.side_effect = Exception("Claude error")

        # Patch the client
        llm_client.anthropic_client = mock_anthropic_client

        # Generate without fallback - should raise
        with pytest.raises(LLMClientError):
            await llm_client.generate(
                prompt="Test prompt",
                use_fallback=False,
            )

        assert llm_client.metrics["claude_errors"] == 1

    @pytest.mark.asyncio
    async def test_circuit_breaker_opens(self, llm_client, mock_anthropic_client):
        """Test that circuit breaker opens after failures."""
        # Mock repeated failures
        mock_anthropic_client.messages.create.side_effect = Exception("API error")

        # Patch the client
        llm_client.anthropic_client = mock_anthropic_client

        # Attempt multiple generations
        for _ in range(10):
            try:
                await llm_client.generate(
                    prompt="Test prompt",
                    use_fallback=False,
                )
            except LLMClientError:
                pass

        # Circuit breaker should be open
        assert llm_client.claude_circuit_breaker.state == "open"

    @pytest.mark.asyncio
    async def test_retry_logic(self, llm_client, mock_anthropic_client):
        """Test retry logic with exponential backoff."""
        call_count = 0

        async def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary error")
            # Success on third try
            mock_response = MagicMock()
            mock_response.content = [MagicMock(text="Success after retries")]
            mock_response.usage = MagicMock(input_tokens=100, output_tokens=50)
            return mock_response

        mock_anthropic_client.messages.create.side_effect = side_effect
        llm_client.anthropic_client = mock_anthropic_client

        # Should succeed after retries
        result = await llm_client.generate(
            prompt="Test prompt",
            use_fallback=False,
        )

        assert result == "Success after retries"
        assert call_count == 3  # Initial + 2 retries

    @pytest.mark.asyncio
    async def test_cost_tracking(self, llm_client, mock_anthropic_client):
        """Test that costs are tracked correctly."""
        # Mock response
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Response")]
        mock_response.usage = MagicMock(
            input_tokens=1000,
            output_tokens=500,
        )
        mock_anthropic_client.messages.create.return_value = mock_response

        llm_client.anthropic_client = mock_anthropic_client

        # Generate
        await llm_client.generate(
            prompt="Test",
            model="claude-3-5-sonnet-20241022",
        )

        # Check cost calculation
        # Claude pricing: $3/1M input, $15/1M output
        expected_cost = (1000 / 1_000_000) * 3 + (500 / 1_000_000) * 15
        assert llm_client.metrics["total_cost"] == Decimal(str(expected_cost))


@pytest.mark.asyncio
async def test_temperature_parameter(llm_client, mock_anthropic_client):
    """Test that temperature parameter is passed correctly."""
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Response")]
    mock_response.usage = MagicMock(input_tokens=100, output_tokens=50)
    mock_anthropic_client.messages.create.return_value = mock_response

    llm_client.anthropic_client = mock_anthropic_client

    # Generate with custom temperature
    await llm_client.generate(
        prompt="Test",
        temperature=0.5,
    )

    # Verify temperature was passed
    call_args = mock_anthropic_client.messages.create.call_args
    assert call_args.kwargs["temperature"] == 0.5


@pytest.mark.asyncio
async def test_max_tokens_parameter(llm_client, mock_anthropic_client):
    """Test that max_tokens parameter is passed correctly."""
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Response")]
    mock_response.usage = MagicMock(input_tokens=100, output_tokens=50)
    mock_anthropic_client.messages.create.return_value = mock_response

    llm_client.anthropic_client = mock_anthropic_client

    # Generate with custom max_tokens
    await llm_client.generate(
        prompt="Test",
        max_tokens=1000,
    )

    # Verify max_tokens was passed
    call_args = mock_anthropic_client.messages.create.call_args
    assert call_args.kwargs["max_tokens"] == 1000
