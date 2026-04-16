"""
LLM Client with Claude (primary) and OpenAI (fallback) support.

Provides async API calls with retry logic, circuit breaker, and cost tracking.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Literal, Optional, Union

import anthropic
import openai
from anthropic import Anthropic
from openai import OpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMClientError(Exception):
    """Base exception for LLM client errors."""
    pass


class CircuitBreakerOpenError(LLMClientError):
    """Raised when circuit breaker is open."""
    pass


class CircuitBreaker:
    """
    Circuit breaker for preventing cascading failures.

    Opens after failure_threshold failures and remains open for timeout period.
    """

    def __init__(self, failure_threshold: int = 5, timeout: int = 300):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening
            timeout: Seconds to wait before attempting recovery
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time: Optional[datetime] = None
        self.state: Literal["closed", "open", "half_open"] = "closed"

    def record_success(self):
        """Record successful call."""
        self.failures = 0
        self.state = "closed"

    def record_failure(self):
        """Record failed call."""
        self.failures += 1
        self.last_failure_time = datetime.utcnow()

        if self.failures >= self.failure_threshold:
            self.state = "open"
            logger.warning(
                f"Circuit breaker opened after {self.failures} failures"
            )

    def can_attempt(self) -> bool:
        """
        Check if request can proceed.

        Returns:
            True if circuit is closed or half-open
        """
        if self.state == "closed":
            return True

        if self.state == "open":
            if self.last_failure_time and \
               datetime.utcnow() - self.last_failure_time > timedelta(seconds=self.timeout):
                self.state = "half_open"
                logger.info("Circuit breaker entering half-open state")
                return True
            return False

        return True  # half_open


class LLMClient:
    """
    LLM client with Claude (primary) and OpenAI (fallback).

    Features:
    - Async API calls to Claude and OpenAI
    - Automatic fallback from Claude to OpenAI
    - Retry with exponential backoff
    - Circuit breaker for preventing cascading failures
    - Token counting and cost tracking
    - Timeout handling
    """

    # Pricing per 1M tokens (as of 2025)
    PRICING = {
        "claude-3-5-sonnet-20241022": {"input": 3.0, "output": 15.0},
        "gpt-4-turbo-preview": {"input": 10.0, "output": 30.0},
        "text-embedding-3-small": {"input": 0.02, "output": 0.0},
    }

    def __init__(
        self,
        anthropic_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        model_primary: str = "claude-3-5-sonnet-20241022",
        model_fallback: str = "gpt-4-turbo-preview",
        max_retries: int = 3,
        timeout: int = 30,
    ):
        """
        Initialize LLM client.

        Args:
            anthropic_api_key: Anthropic API key (defaults to settings)
            openai_api_key: OpenAI API key (defaults to settings)
            model_primary: Primary model (Claude)
            model_fallback: Fallback model (OpenAI)
            max_retries: Maximum number of retries
            timeout: Request timeout in seconds
        """
        self.anthropic_api_key = anthropic_api_key or settings.ANTHROPIC_API_KEY
        self.openai_api_key = openai_api_key or settings.OPENAI_API_KEY
        self.model_primary = model_primary
        self.model_fallback = model_fallback
        self.max_retries = max_retries
        self.timeout = timeout

        # Initialize clients
        self.anthropic_client: Optional[Anthropic] = None
        self.openai_client: Optional[OpenAI] = None

        if self.anthropic_api_key:
            self.anthropic_client = Anthropic(api_key=self.anthropic_api_key)

        if self.openai_api_key:
            self.openai_client = OpenAI(api_key=self.openai_api_key)

        # Circuit breakers
        self.claude_circuit_breaker = CircuitBreaker()
        self.openai_circuit_breaker = CircuitBreaker()

        # Metrics
        self.metrics = {
            "claude_calls": 0,
            "claude_errors": 0,
            "claude_fallbacks": 0,
            "openai_calls": 0,
            "openai_errors": 0,
            "total_tokens": 0,
            "total_cost": Decimal("0.0"),
        }

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_format: Literal["text", "json"] = "json",
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        use_fallback: bool = True,
    ) -> str:
        """
        Generate response from LLM.

        Args:
            prompt: User prompt
            system_prompt: System prompt (for Claude)
            response_format: Response format ("text" or "json")
            model: Specific model to use (defaults to primary)
            temperature: Temperature (0-1)
            max_tokens: Maximum tokens to generate
            use_fallback: Whether to use fallback on error

        Returns:
            Generated response text

        Raises:
            LLMClientError: If all attempts fail
        """
        model_to_use = model or self.model_primary

        # Try Claude first
        if "claude" in model_to_use.lower():
            try:
                response = await self._generate_claude(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    response_format=response_format,
                    model=model_to_use,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return response
            except LLMClientError as e:
                if use_fallback and self.openai_client:
                    logger.warning(f"Claude failed, trying OpenAI: {e}")
                    self.metrics["claude_fallbacks"] += 1
                    return await self._generate_openai(
                        prompt=prompt,
                        system_prompt=system_prompt,
                        response_format=response_format,
                        model=self.model_fallback,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                raise

        # Try OpenAI
        return await self._generate_openai(
            prompt=prompt,
            system_prompt=system_prompt,
            response_format=response_format,
            model=model_to_use,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    async def _generate_claude(
        self,
        prompt: str,
        system_prompt: Optional[str],
        response_format: Literal["text", "json"],
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        """
        Generate response using Claude.

        Args:
            prompt: User prompt
            system_prompt: System prompt
            response_format: Response format
            model: Model name
            temperature: Temperature
            max_tokens: Maximum tokens

        Returns:
            Generated response

        Raises:
            LLMClientError: If generation fails
        """
        if not self.anthropic_client:
            raise LLMClientError("Anthropic client not initialized")

        if not self.claude_circuit_breaker.can_attempt():
            raise CircuitBreakerOpenError("Claude circuit breaker is open")

        retry_count = 0
        last_error = None

        while retry_count < self.max_retries:
            try:
                self.metrics["claude_calls"] += 1

                # Prepare messages
                messages = [{"role": "user", "content": prompt}]

                # Add JSON format instruction
                if response_format == "json":
                    messages[0]["content"] = f"{prompt}\n\nRespond with JSON only."

                # Call API (sync, wrapped in asyncio)
                response = await asyncio.to_thread(
                    self.anthropic_client.messages.create,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system_prompt or "You are a helpful assistant.",
                    messages=messages,
                )

                # Extract response
                content = response.content[0].text

                # Update metrics
                usage = response.usage
                self.metrics["total_tokens"] += usage.input_tokens + usage.output_tokens
                cost = (
                    (usage.input_tokens / 1_000_000) * self.PRICING[model]["input"]
                    + (usage.output_tokens / 1_000_000) * self.PRICING[model]["output"]
                )
                self.metrics["total_cost"] += Decimal(str(cost))

                # Record success
                self.claude_circuit_breaker.record_success()

                return content

            except asyncio.TimeoutError:
                last_error = f"Request timed out after {self.timeout}s"
                logger.warning(f"Claude timeout: {last_error}")
            except anthropic.APITimeoutError as e:
                last_error = f"API timeout: {e}"
                logger.warning(f"Claude API timeout: {last_error}")
            except anthropic.APIError as e:
                last_error = f"API error: {e}"
                logger.warning(f"Claude API error: {last_error}")
            except Exception as e:
                last_error = f"Unexpected error: {e}"
                logger.error(f"Claude unexpected error: {last_error}")

            retry_count += 1
            if retry_count < self.max_retries:
                # Exponential backoff
                wait_time = 2 ** retry_count
                logger.info(f"Retrying Claude in {wait_time}s...")
                await asyncio.sleep(wait_time)

        # All retries failed
        self.metrics["claude_errors"] += 1
        self.claude_circuit_breaker.record_failure()

        raise LLMClientError(f"Claude generation failed after {self.max_retries} retries: {last_error}")

    async def _generate_openai(
        self,
        prompt: str,
        system_prompt: Optional[str],
        response_format: Literal["text", "json"],
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        """
        Generate response using OpenAI.

        Args:
            prompt: User prompt
            system_prompt: System prompt
            response_format: Response format
            model: Model name
            temperature: Temperature
            max_tokens: Maximum tokens

        Returns:
            Generated response

        Raises:
            LLMClientError: If generation fails
        """
        if not self.openai_client:
            raise LLMClientError("OpenAI client not initialized")

        if not self.openai_circuit_breaker.can_attempt():
            raise CircuitBreakerOpenError("OpenAI circuit breaker is open")

        retry_count = 0
        last_error = None

        while retry_count < self.max_retries:
            try:
                self.metrics["openai_calls"] += 1

                # Prepare messages
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})

                # Call API (sync, wrapped in asyncio)
                response = await asyncio.to_thread(
                    self.openai_client.chat.completions.create,
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    response_format={"type": response_format} if response_format == "json" else None,
                )

                # Extract response
                content = response.choices[0].message.content or ""

                # Update metrics
                usage = response.usage
                self.metrics["total_tokens"] += usage.prompt_tokens + usage.completion_tokens
                cost = (
                    (usage.prompt_tokens / 1_000_000) * self.PRICING[model]["input"]
                    + (usage.completion_tokens / 1_000_000) * self.PRICING[model]["output"]
                )
                self.metrics["total_cost"] += Decimal(str(cost))

                # Record success
                self.openai_circuit_breaker.record_success()

                return content

            except asyncio.TimeoutError:
                last_error = f"Request timed out after {self.timeout}s"
                logger.warning(f"OpenAI timeout: {last_error}")
            except openai.APITimeoutError as e:
                last_error = f"API timeout: {e}"
                logger.warning(f"OpenAI API timeout: {last_error}")
            except openai.APIError as e:
                last_error = f"API error: {e}"
                logger.warning(f"OpenAI API error: {last_error}")
            except Exception as e:
                last_error = f"Unexpected error: {e}"
                logger.error(f"OpenAI unexpected error: {last_error}")

            retry_count += 1
            if retry_count < self.max_retries:
                # Exponential backoff
                wait_time = 2 ** retry_count
                logger.info(f"Retrying OpenAI in {wait_time}s...")
                await asyncio.sleep(wait_time)

        # All retries failed
        self.metrics["openai_errors"] += 1
        self.openai_circuit_breaker.record_failure()

        raise LLMClientError(f"OpenAI generation failed after {self.max_retries} retries: {last_error}")

    def get_metrics(self) -> Dict:
        """
        Get client metrics.

        Returns:
            Dictionary with metrics
        """
        return {
            **self.metrics,
            "total_cost": float(self.metrics["total_cost"]),
            "claude_success_rate": (
                (self.metrics["claude_calls"] - self.metrics["claude_errors"]) / self.metrics["claude_calls"]
                if self.metrics["claude_calls"] > 0
                else 0.0
            ),
            "openai_success_rate": (
                (self.metrics["openai_calls"] - self.metrics["openai_errors"]) / self.metrics["openai_calls"]
                if self.metrics["openai_calls"] > 0
                else 0.0
            ),
            "fallback_rate": (
                self.metrics["claude_fallbacks"] / self.metrics["claude_calls"]
                if self.metrics["claude_calls"] > 0
                else 0.0
            ),
        }

    def reset_metrics(self):
        """Reset metrics."""
        self.metrics = {
            "claude_calls": 0,
            "claude_errors": 0,
            "claude_fallbacks": 0,
            "openai_calls": 0,
            "openai_errors": 0,
            "total_tokens": 0,
            "total_cost": Decimal("0.0"),
        }
