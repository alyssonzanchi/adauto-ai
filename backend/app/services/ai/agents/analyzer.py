"""
Analyzer Agent - Comprehensive vehicle analysis.

Analyzes vehicles for:
- Market price positioning
- Selling points
- Target audience
- Suggested improvements
- Performance metrics (CTR, conversion)
"""
import logging
from typing import Any, Dict

from app.services.ai.agents.base import BaseAgent
from app.services.llm.llm_client import LLMClient
from app.services.llm.prompts.vehicle_analysis import VehicleAnalysisPrompt

logger = logging.getLogger(__name__)


class AnalyzerAgent(BaseAgent):
    """
    Agent for comprehensive vehicle analysis.

    Input: Vehicle data
    Output: Analysis with price, selling points, audience, suggestions, metrics
    """

    REQUIRED_KEYS = [
        "price_market",
        "price_score",
        "price_position",
        "selling_points",
        "target_audience",
        "suggested_improvements",
        "estimated_ctr",
        "estimated_conversion",
    ]

    def __init__(self, llm_client: LLMClient):
        """
        Initialize analyzer agent.

        Args:
            llm_client: LLM client
        """
        prompt_template = VehicleAnalysisPrompt()
        super().__init__(
            llm_client=llm_client,
            prompt_template=prompt_template,
            name="AnalyzerAgent",
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute vehicle analysis.

        Args:
            context: Must contain 'vehicle' key with vehicle data

        Returns:
            Analysis results dictionary

        Raises:
            ValueError: If context invalid
            LLMClientError: If LLM call fails
        """
        vehicle = context.get("vehicle")
        if not vehicle:
            raise ValueError("Missing 'vehicle' in context")

        # Render prompt
        prompt = self.prompt_template.render_vehicle_context(vehicle)

        # Call LLM
        response_text = await self._call_llm(
            prompt=prompt,
            response_format="json",
            temperature=0.7,  # Balance creativity and accuracy
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
        response["analysis_version"] = "v2.0.0"
        response["analyzed_at"] = self._get_timestamp()

        # Sanitize and return
        return self.sanitize_response(response)

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime

        return datetime.utcnow().isoformat()
