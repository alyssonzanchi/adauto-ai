"""
Prompt templates for AI Agents (Predictor, Optimizer, Evaluator).
"""
from typing import Any, Dict

from app.services.llm.prompts.base import BasePromptTemplate


class PredictionPrompt(BasePromptTemplate):
    """Prompt template for performance prediction."""

    def get_system_prompt(self) -> str:
        """Get system prompt for prediction."""
        return """You are an expert in predicting ad performance for automotive listings.
You analyze vehicle data, market conditions, and historical patterns to provide accurate predictions.

Your predictions cover:
- Click-through rate (CTR)
- Conversion rate
- Pricing performance
- Risk assessment
- Future forecasting

Always provide responses in valid JSON format with numeric estimates."""

    def get_template_name(self) -> str:
        """Get template filename."""
        return "prediction.jinja2"

    def render_prediction_prompt(
        self,
        vehicle_data: Dict[str, Any],
        forecast_days: int = 30,
        target_budget: float = None
    ) -> str:
        """
        Render prediction prompt.

        Args:
            vehicle_data: Vehicle information
            forecast_days: Number of days to forecast
            target_budget: Target budget for scenarios

        Returns:
            Rendered prompt
        """
        # Simple text-based prompt (no template file needed)
        prompt = f"""Predict the performance for this vehicle listing:

Vehicle: {vehicle_data.get('brand', '')} {vehicle_data.get('model', '')} {vehicle_data.get('model_year', '')}
Price: R$ {vehicle_data.get('price', 0):,.2f}
Mileage: {vehicle_data.get('mileage', 0):,} km
Days on market: {vehicle_data.get('days_since_listing', 0)}

Provide a JSON response with:
- predicted_ctr: Expected CTR (0-1)
- predicted_conversion_rate: Expected conversion rate (0-1)
- predicted_price: Expected sale price
- price_position: "great_deal", "good_price", "fair_price", "expensive", "overpriced"
- confidence: Overall confidence score (0-1)
- risk_factors: List of potential risks
"""

        if forecast_days:
            prompt += f"\nForecast period: {forecast_days} days"

        if target_budget:
            prompt += f"\nTarget budget: R$ {target_budget:,.2f}"

        return prompt


class OptimizationPrompt(BasePromptTemplate):
    """Prompt template for ad optimization."""

    def get_system_prompt(self) -> str:
        """Get system prompt for optimization."""
        return """You are an expert in optimizing digital advertisements for automotive listings.
You provide actionable, specific recommendations to improve ad performance.

Your optimization covers:
- Content improvement (headline, description, CTA)
- Bid recommendations
- Budget allocation
- A/B testing suggestions
- Performance improvement strategies

Always provide responses in valid JSON format with specific recommendations."""

    def get_template_name(self) -> str:
        """Get template filename."""
        return "optimization.jinja2"

    def render_optimization_prompt(
        self,
        vehicle_data: Dict[str, Any],
        ad_content: Dict[str, Any],
        current_metrics: Dict[str, Any] = None,
        goals: Dict[str, Any] = None
    ) -> str:
        """
        Render optimization prompt.

        Args:
            vehicle_data: Vehicle information
            ad_content: Current ad content
            current_metrics: Current performance metrics
            goals: Target goals

        Returns:
            Rendered prompt
        """
        prompt = f"""Optimize this ad for better performance:

Vehicle: {vehicle_data.get('brand', '')} {vehicle_data.get('model', '')} {vehicle_data.get('model_year', '')}
Price: R$ {vehicle_data.get('price', 0):,.2f}

Current Ad Content:
- Headline: {ad_content.get('headline', '')}
- Description: {ad_content.get('description', '')}
- Images: {len(ad_content.get('images', []))} photos
- CTA: {ad_content.get('cta', 'None')}
"""

        if current_metrics:
            prompt += f"""
Current Performance:
- CTR: {current_metrics.get('ctr', 0):.2%}
- Conversion: {current_metrics.get('conversion_rate', 0):.2%}
- Impressions: {current_metrics.get('impressions', 0):,}
"""

        if goals:
            prompt += f"""
Goals:
- Target CTR: {goals.get('target_ctr', 0):.2%}
- Target Conversion: {goals.get('target_conversion', 0):.2%}
- Target Budget: R$ {goals.get('target_budget', 0):,.2f}
"""

        prompt += """
Provide a JSON response with specific optimization recommendations.
"""

        return prompt


class EvaluationPrompt(BasePromptTemplate):
    """Prompt template for content evaluation."""

    def get_system_prompt(self) -> str:
        """Get system prompt for evaluation."""
        return """You are an expert in evaluating digital advertisement quality for automotive listings.
You provide honest, constructive feedback and actionable recommendations.

Your evaluation covers:
- Quality scoring (0-100)
- Content analysis (headline, description, images, CTA)
- Benchmarking vs top performers
- Gap analysis
- Improvement roadmap

Always provide responses in valid JSON format with detailed analysis."""

    def get_template_name(self) -> str:
        """Get template filename."""
        return "evaluation.jinja2"

    def render_evaluation_prompt(
        self,
        ad_content: Dict[str, Any],
        vehicle_id: str = None,
        include_benchmark: bool = True
    ) -> str:
        """
        Render evaluation prompt.

        Args:
            ad_content: Ad content to evaluate
            vehicle_id: Vehicle ID for benchmarking
            include_benchmark: Whether to include benchmark comparison

        Returns:
            Rendered prompt
        """
        prompt = f"""Evaluate this ad content:

Ad Content:
- Headline: {ad_content.get('headline', '')}
- Description: {ad_content.get('description', '')}
- Images: {len(ad_content.get('images', []))} photos
- CTA: {ad_content.get('cta', 'None')}
"""

        if include_benchmark:
            prompt += "\nInclude benchmark comparison with industry standards."

        prompt += """
Provide a JSON response with:
- quality_score: Overall score (0-100)
- headline_quality: Score for headline (0-10)
- description_quality: Score for description (0-10)
- image_quality: Score for images (0-10)
- cta_quality: Score for CTA (0-10)
- gaps: List of identified gaps
- recommendations: List of specific improvements
"""

        return prompt
