"""
Generator Agent - Ad content generation.

Generates:
- Compelling headlines
- Detailed descriptions
- Call-to-action phrases
- SEO keywords
"""
import logging
from typing import Any, Dict

from app.services.ai.agents.base import BaseAgent
from app.services.llm.llm_client import LLMClient
from app.services.llm.prompts.ad_generation import AdGenerationPrompt

logger = logging.getLogger(__name__)


class GeneratorAgent(BaseAgent):
    """
    Agent for generating advertisement content.

    Input: Vehicle data
    Output: Ad headline, description, CTA, keywords
    """

    REQUIRED_KEYS_HEADLINE = ["headline", "subheadline"]
    REQUIRED_KEYS_DESCRIPTION = [
        "headline",
        "subheadline",
        "description",
        "cta",
        "keywords",
    ]

    def __init__(self, llm_client: LLMClient):
        """
        Initialize generator agent.

        Args:
            llm_client: LLM client
        """
        prompt_template = AdGenerationPrompt()
        super().__init__(
            llm_client=llm_client,
            prompt_template=prompt_template,
            name="GeneratorAgent",
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute ad content generation.

        Args:
            context: Must contain 'vehicle' and 'content_type' keys

        Returns:
            Generated ad content

        Raises:
            ValueError: If context invalid
            LLMClientError: If LLM call fails
        """
        vehicle = context.get("vehicle")
        content_type = context.get("content_type", "full")

        if not vehicle:
            raise ValueError("Missing 'vehicle' in context")

        # Generate based on content type
        if content_type == "headline":
            return await self._generate_headline(vehicle)
        else:
            return await self._generate_full_ad(vehicle)

    async def _generate_headline(self, vehicle: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate headline and subheadline.

        Args:
            vehicle: Vehicle data

        Returns:
            Headline content
        """
        prompt = self.prompt_template.render_headline_prompt(vehicle)

        response_text = await self._call_llm(
            prompt=prompt,
            response_format="json",
            temperature=0.9,  # Higher creativity for headlines
        )

        response = self.prompt_template.format_response(response_text)
        self.validate_response(response, self.REQUIRED_KEYS_HEADLINE)

        response["generated_at"] = self._get_timestamp()

        return self.sanitize_response(response)

    async def _generate_full_ad(self, vehicle: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate full ad content.

        Args:
            vehicle: Vehicle data

        Returns:
            Full ad content
        """
        prompt = self.prompt_template.render_description_prompt(vehicle)

        response_text = await self._call_llm(
            prompt=prompt,
            response_format="json",
            temperature=0.8,  # High creativity for ad copy
        )

        response = self.prompt_template.format_response(response_text)
        self.validate_response(response, self.REQUIRED_KEYS_DESCRIPTION)

        response["generated_at"] = self._get_timestamp()

        return self.sanitize_response(response)

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime

        return datetime.utcnow().isoformat()
