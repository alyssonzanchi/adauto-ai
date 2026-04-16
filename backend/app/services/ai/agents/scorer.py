"""
Scorer Agent - Price scoring and analysis.

Analyzes:
- Fair market price
- Price competitiveness score
- Price positioning
- Recommended price range
- Price adjustment suggestions
- Estimated days to sell
"""
import logging
from typing import Any, Dict

from app.services.ai.agents.base import BaseAgent
from app.services.llm.llm_client import LLMClient
from app.services.llm.prompts.price_scoring import PriceScoringPrompt

logger = logging.getLogger(__name__)


class ScorerAgent(BaseAgent):
    """
    Agent for price scoring and analysis.

    Input: Vehicle data with listed_price
    Output: Price analysis with fair price, score, positioning, recommendations
    """

    REQUIRED_KEYS = [
        "fair_market_price",
        "price_range",
        "competitiveness_score",
        "positioning",
        "listed_vs_market",
        "market_insights",
        "recommendations",
        "estimated_days_to_sell",
    ]

    def __init__(self, llm_client: LLMClient):
        """
        Initialize scorer agent.

        Args:
            llm_client: LLM client
        """
        prompt_template = PriceScoringPrompt()
        super().__init__(
            llm_client=llm_client,
            prompt_template=prompt_template,
            name="ScorerAgent",
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute price scoring.

        Args:
            context: Must contain 'vehicle' key with vehicle data (including listed_price)

        Returns:
            Price scoring results

        Raises:
            ValueError: If context invalid
            LLMClientError: If LLM call fails
        """
        vehicle = context.get("vehicle")
        if not vehicle:
            raise ValueError("Missing 'vehicle' in context")

        if "listed_price" not in vehicle:
            raise ValueError("Missing 'listed_price' in vehicle data")

        # Render prompt
        prompt = self.prompt_template.render_price_context(vehicle)

        # Call LLM
        response_text = await self._call_llm(
            prompt=prompt,
            response_format="json",
            temperature=0.5,  # Lower temperature for analytical tasks
        )

        # Parse response
        try:
            response = self.prompt_template.format_response(response_text)
        except ValueError as e:
            logger.error(f"Failed to parse LLM response: {e}")
            raise ValueError(f"Invalid LLM response format: {e}")

        # Validate response
        self.validate_response(response, self.REQUIRED_KEYS)

        # Add metadata
        response["scored_at"] = self._get_timestamp()

        # Sanitize and return
        return self.sanitize_response(response)

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime

        return datetime.utcnow().isoformat()
