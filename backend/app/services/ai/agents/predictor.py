"""
Predictor Agent - Performance prediction and forecasting
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json

from .base import BaseAgent
from app.services.llm.llm_client import LLMClient
from app.services.llm.prompts.ai_agents import PredictionPrompt

logger = logging.getLogger(__name__)


class PredictorAgent(BaseAgent):
    """
    Agent for predicting ad performance and forecasting.

    Capabilities:
    - Performance prediction (CTR, conversion, ROI)
    - Forecasting (7d, 30d, 90d)
    - Scenario analysis (budget variations)
    - Risk assessment
    """

    def __init__(self, llm_client: LLMClient):
        """
        Initialize PredictorAgent.

        Args:
            llm_client: LLM client for API calls
        """
        # Create a simple prompt template
        prompt_template = PredictionPrompt()

        super().__init__(
            llm_client=llm_client,
            prompt_template=prompt_template,
            name="predictor_agent"
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute prediction task.

        Args:
            context: Contains vehicle_data, forecast_days, target_budget, scenarios

        Returns:
            Prediction results
        """
        vehicle_data = context.get("vehicle_data", {})
        forecast_days = context.get("forecast_days", 30)
        target_budget = context.get("target_budget")
        include_scenarios = context.get("include_scenarios", False)

        # Get ML predictions
        from app.services.ml import PriceModel, CTRModel, ConversionModel

        price_model = PriceModel()
        ctr_model = CTRModel()
        conversion_model = ConversionModel()

        # Run ML predictions
        price_result = await price_model.predict(vehicle_data)
        ctr_result = await ctr_model.predict(vehicle_data)
        conversion_result = await conversion_model.predict(vehicle_data)

        # Build prediction
        prediction = {
            "vehicle_id": vehicle_data.get("id"),
            "predictions": {
                "price": price_result,
                "ctr": ctr_result,
                "conversion": conversion_result
            },
            "forecast": await self._forecast(vehicle_data, forecast_days),
            "risk_assessment": self._assess_risk(vehicle_data, price_result, ctr_result),
            "confidence": self._calculate_confidence(price_result, ctr_result, conversion_result)
        }

        # Add scenarios if requested
        if include_scenarios and target_budget:
            prediction["scenarios"] = await self._analyze_scenarios(
                vehicle_data,
                target_budget,
                ctr_result,
                conversion_result,
                price_result
            )

        return prediction

    async def _forecast(
        self,
        vehicle_data: Dict[str, Any],
        days: int
    ) -> Dict[str, Any]:
        """
        Generate performance forecast.

        Args:
            vehicle_data: Vehicle information
            days: Forecast period (7, 30, or 90)

        Returns:
            Forecast data
        """
        # Simplified forecasting (in production, use time series models)
        base_ctr = 0.045  # 4.5% average
        base_conversion = 0.028  # 2.8% average

        # Adjust for seasonality
        current_date = datetime.now()
        month = current_date.month

        # Summer (Dec-Feb): +15%
        # Winter (Jun-Aug): -10%
        seasonality_factor = 1.0
        if month in [12, 1, 2]:
            seasonality_factor = 1.15
        elif month in [6, 7, 8]:
            seasonality_factor = 0.90

        # Aging decay (listing gets older)
        days_on_market = vehicle_data.get("days_since_listing", 0)
        aging_factor = max(0.5, 1.0 - (days_on_market / 180))  # Decay over 6 months

        # Generate daily forecast
        forecast = {
            "period_days": days,
            "daily_predictions": []
        }

        cumulative_impressions = 0
        cumulative_clicks = 0
        cumulative_conversions = 0

        for day in range(1, days + 1):
            daily_impressions = 100  # Base assumption
            daily_ctr = base_ctr * seasonality_factor * aging_factor
            daily_conversion = base_conversion * seasonality_factor * aging_factor

            daily_clicks = daily_impressions * daily_ctr
            daily_conversions = daily_clicks * daily_conversion

            cumulative_impressions += daily_impressions
            cumulative_clicks += daily_clicks
            cumulative_conversions += daily_conversions

            forecast["daily_predictions"].append({
                "day": day,
                "date": (current_date + timedelta(days=day)).strftime("%Y-%m-%d"),
                "impressions": int(daily_impressions),
                "clicks": round(daily_clicks, 2),
                "conversions": round(daily_conversions, 2),
                "ctr": round(daily_ctr, 4),
                "conversion_rate": round(daily_conversion, 4)
            })

        # Totals
        forecast["totals"] = {
            "impressions": int(cumulative_impressions),
            "clicks": round(cumulative_clicks, 1),
            "conversions": round(cumulative_conversions, 2),
            "avg_ctr": round(base_ctr * seasonality_factor * aging_factor, 4),
            "avg_conversion_rate": round(base_conversion * seasonality_factor * aging_factor, 4)
        }

        return forecast

    def _assess_risk(
        self,
        vehicle_data: Dict[str, Any],
        price_result: Dict[str, Any],
        ctr_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Assess risk of campaign.

        Args:
            vehicle_data: Vehicle info
            price_result: Price prediction
            ctr_result: CTR prediction

        Returns:
            Risk assessment
        """
        risk_score = 0.0  # 0 = low risk, 1 = high risk

        # Price risk
        if price_result["price_position"] == "overpriced":
            risk_score += 0.3
        elif price_result["price_position"] == "expensive":
            risk_score += 0.15

        # CTR risk
        if ctr_result["ctr_bucket"] == "very_low":
            risk_score += 0.25
        elif ctr_result["ctr_bucket"] == "low":
            risk_score += 0.1

        # Age risk
        days_on_market = vehicle_data.get("days_since_listing", 0)
        if days_on_market > 90:
            risk_score += 0.2
        elif days_on_market > 60:
            risk_score += 0.1

        # Competition risk
        # (simplified - in production, use real competitor data)
        risk_score += 0.05  # Base competition risk

        risk_level = "low"
        if risk_score > 0.6:
            risk_level = "high"
        elif risk_score > 0.3:
            risk_level = "medium"

        return {
            "risk_score": round(risk_score, 2),
            "risk_level": risk_level,
            "risk_factors": self._get_risk_factors(vehicle_data, price_result, ctr_result)
        }

    def _get_risk_factors(
        self,
        vehicle_data: Dict[str, Any],
        price_result: Dict[str, Any],
        ctr_result: Dict[str, Any]
    ) -> list:
        """Get list of risk factors"""
        factors = []

        if price_result["price_position"] == "overpriced":
            factors.append("Preço acima do mercado pode dificultar venda")

        if ctr_result["ctr_bucket"] in ["very_low", "low"]:
            factors.append("CTR abaixo da média esperada")

        if vehicle_data.get("days_since_listing", 0) > 60:
            factors.append("Anúncio há muito tempo no mercado")

        if vehicle_data.get("image_count", 0) < 3:
            factors.append("Poucas imagens no anúncio")

        return factors

    def _calculate_confidence(
        self,
        price_result: Dict[str, Any],
        ctr_result: Dict[str, Any],
        conversion_result: Dict[str, Any]
    ) -> float:
        """Calculate overall confidence score"""
        confidences = [
            price_result.get("confidence", 0.5),
            ctr_result.get("confidence", 0.5),
            conversion_result.get("confidence", 0.5)
        ]

        return round(sum(confidences) / len(confidences), 3)

    async def _analyze_scenarios(
        self,
        vehicle_data: Dict[str, Any],
        target_budget: float,
        ctr_result: Dict[str, Any],
        conversion_result: Dict[str, Any],
        price_result: Dict[str, Any]
    ) -> list:
        """
        Analyze different budget scenarios.

        Args:
            vehicle_data: Vehicle info
            target_budget: Target budget
            ctr_result: CTR prediction
            conversion_result: Conversion prediction
            price_result: Price prediction

        Returns:
            List of scenario predictions
        """
        scenarios = []

        # Scenario 1: 50% budget
        scenarios.append({
            "name": "Conservative (50% budget)",
            "budget_multiplier": 0.5,
            "expected_clicks": target_budget * 0.5 * ctr_result["predicted_ctr"],
            "expected_conversions": None,  # Would need more calculation
            "expected_roi": None
        })

        # Scenario 2: 100% budget (target)
        scenarios.append({
            "name": "Target (100% budget)",
            "budget_multiplier": 1.0,
            "expected_clicks": target_budget * ctr_result["predicted_ctr"],
            "expected_conversions": None,
            "expected_roi": None
        })

        # Scenario 3: 150% budget
        scenarios.append({
            "name": "Aggressive (150% budget)",
            "budget_multiplier": 1.5,
            "expected_clicks": target_budget * 1.5 * ctr_result["predicted_ctr"],
            "expected_conversions": None,
            "expected_roi": None
        })

        return scenarios
