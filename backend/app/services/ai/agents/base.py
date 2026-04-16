"""
Base AI Agent class.
"""
import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from app.services.llm.llm_client import LLMClient
from app.services.llm.prompts.base import BasePromptTemplate

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Base class for all AI agents.

    Provides:
    - LLM integration
    - Prompt template rendering
    - Response validation
    - Error handling
    - Logging
    """

    def __init__(
        self,
        llm_client: LLMClient,
        prompt_template: BasePromptTemplate,
        name: str = "base_agent",
    ):
        """
        Initialize agent.

        Args:
            llm_client: LLM client for API calls
            prompt_template: Prompt template for rendering
            name: Agent name for logging
        """
        self.llm_client = llm_client
        self.prompt_template = prompt_template
        self.name = name

        # Metrics
        self.metrics = {
            "executions": 0,
            "successes": 0,
            "failures": 0,
            "avg_execution_time_ms": 0.0,
        }

    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent task.

        Args:
            context: Input context for the task

        Returns:
            Task results as dictionary

        Raises:
            LLMClientError: If LLM call fails
        """
        pass

    async def _call_llm(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_format: str = "json",
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        """
        Call LLM with prompt.

        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            response_format: Response format ("json" or "text")
            temperature: Temperature (0-1)
            max_tokens: Maximum tokens

        Returns:
            LLM response string

        Raises:
            LLMClientError: If LLM call fails
        """
        try:
            system = system_prompt or self.prompt_template.get_system_prompt()

            response = await self.llm_client.generate(
                prompt=prompt,
                system_prompt=system,
                response_format=response_format,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            return response

        except Exception as e:
            logger.error(f"{self.name}: LLM call failed: {e}")
            raise

    async def _execute_with_metrics(
        self,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute agent with metrics tracking.

        Args:
            context: Input context

        Returns:
            Task results
        """
        import time

        self.metrics["executions"] += 1
        start_time = time.time()

        try:
            # Call subclass execute method
            result = await self.execute(context)

            # Update metrics
            elapsed_ms = (time.time() - start_time) * 1000
            self.metrics["avg_execution_time_ms"] = (
                (self.metrics["avg_execution_time_ms"] * (self.metrics["executions"] - 1) + elapsed_ms)
                / self.metrics["executions"]
            )
            self.metrics["successes"] += 1

            logger.info(
                f"{self.name}: Executed successfully in {elapsed_ms:.2f}ms"
            )

            return result

        except Exception as e:
            # Update metrics
            elapsed_ms = (time.time() - start_time) * 1000
            self.metrics["avg_execution_time_ms"] = (
                (self.metrics["avg_execution_time_ms"] * (self.metrics["executions"] - 1) + elapsed_ms)
                / self.metrics["executions"]
            )
            self.metrics["failures"] += 1

            logger.error(f"{self.name}: Execution failed after {elapsed_ms:.2f}ms: {e}")
            raise

    def validate_response(
        self,
        response: Dict[str, Any],
        required_keys: list[str],
    ) -> bool:
        """
        Validate response has required keys.

        Args:
            response: Response dict to validate
            required_keys: List of required keys

        Returns:
            True if valid

        Raises:
            ValueError: If validation fails
        """
        missing_keys = [key for key in required_keys if key not in response]

        if missing_keys:
            raise ValueError(
                f"{self.name}: Response missing required keys: {missing_keys}"
            )

        return True

    def sanitize_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize response for storage/return.

        Args:
            response: Raw response dict

        Returns:
            Sanitized response
        """
        # Remove null values
        return {k: v for k, v in response.items() if v is not None}

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get agent metrics.

        Returns:
            Metrics dictionary
        """
        success_rate = (
            self.metrics["successes"] / self.metrics["executions"]
            if self.metrics["executions"] > 0
            else 0.0
        )

        return {
            **self.metrics,
            "success_rate": success_rate,
        }

    def reset_metrics(self):
        """Reset metrics."""
        self.metrics = {
            "executions": 0,
            "successes": 0,
            "failures": 0,
            "avg_execution_time_ms": 0.0,
        }
