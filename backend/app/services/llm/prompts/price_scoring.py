"""
Price scoring prompt template.
"""
from typing import Any, Dict

from app.services.llm.prompts.base import BasePromptTemplate


class PriceScoringPrompt(BasePromptTemplate):
    """
    Prompt template for price scoring and analysis.

    Analyzes:
    - Fair market price
    - Price competitiveness score
    - Price positioning (great deal, good, fair, expensive, overpriced)
    - Recommended price range
    - Price adjustment suggestions
    """

    def get_system_prompt(self) -> str:
        """Get system prompt for price scoring."""
        return """You are an expert automotive pricing analyst with deep knowledge of the Brazilian used car market.

Your expertise includes:
- Real-time market pricing across all Brazilian regions
- Seasonal pricing trends and fluctuations
- Brand-specific depreciation curves
- Feature-based value adjustments
- Geographic price variations
- Supply and demand dynamics

Your analysis is:
- Based on current market data
- Regionally contextualized
- Transparent in methodology
- Actionable for sellers

You consider:
- Vehicle age and mileage
- Brand reputation and reliability
- Feature completeness and rarity
- Market demand trends
- Economic factors
- Seasonal patterns

Always provide responses in valid JSON format."""

    def get_template_name(self) -> str:
        """Get template filename."""
        return "price_scoring.jinja2"

    def render_price_context(self, vehicle: Dict[str, Any]) -> str:
        """Render price scoring prompt with context."""
        return self.render({"vehicle": vehicle})


class PriceScoringFewShots:
    """Few-shot examples for price scoring."""

    EXAMPLES = [
        {
            "input": {
                "brand": "Volkswagen",
                "model": "Golf Highline",
                "year": 2019,
                "mileage": 52000,
                "listed_price": 95000,
                "body_type": "hatch",
                "features": {
                    "security": ["airbags", "abs", "controle_estabilidade"],
                    "comfort": ["ar_condicionado", "direcao_eletrica", "teto_solar"],
                    "technology": ["central_multimidia", "android_auto"],
                }
            },
            "output": {
                "fair_market_price": 88000.0,
                "price_range": {
                    "excellent_condition": 92000,
                    "good_condition": 88000,
                    "fair_condition": 84000,
                },
                "competitiveness_score": 72,
                "positioning": "above_market",
                "listed_vs_market": {
                    "difference": 7000,
                    "difference_percent": 8.0,
                    "assessment": "Priced 8% above fair market value"
                },
                "market_insights": {
                    "demand_level": "moderate",
                    "supply_level": "moderate",
                    "trend": "stable",
                    "reasoning": "Golf holds value well but demand has softened compared to SUVs. Premium features help justify price."
                },
                "recommendations": [
                    "Consider reducing to R$88-90k for faster sale",
                    "Highlight premium features (sunroof, advanced safety)",
                    "Emphasize VW reliability and maintenance records",
                    "Target buyers seeking performance hatchbacks"
                ],
                "estimated_days_to_sell": {
                    "at_current_price": 60,
                    "at_recommended_price": 35,
                }
            }
        },
        {
            "input": {
                "brand": "Fiat",
                "model": "Toro Volcano",
                "year": 2021,
                "mileage": 40000,
                "listed_price": 160000,
                "body_type": "pickup",
                "features": {
                    "security": ["airbags", "abs", "controle_estabilidade", "tracao"],
                    "comfort": ["ar_condicionado", "direcao_eletrica", "bancos_couro"],
                    "technology": ["central_multimidia", "gps"],
                }
            },
            "output": {
                "fair_market_price": 165000.0,
                "price_range": {
                    "excellent_condition": 172000,
                    "good_condition": 165000,
                    "fair_condition": 158000,
                },
                "competitiveness_score": 88,
                "positioning": "good_price",
                "listed_vs_market": {
                    "difference": -5000,
                    "difference_percent": -3.0,
                    "assessment": "Priced 3% below fair market value - attractive pricing"
                },
                "market_insights": {
                    "demand_level": "high",
                    "supply_level": "low",
                    "trend": "appreciating",
                    "reasoning": "Pickup market is strong in Brazil. Toro Volcano is in high demand with limited supply."
                },
                "recommendations": [
                    "Current price is competitive - no changes needed",
                    "Emphasize 4x4 capability and versatility",
                    "Target both work and lifestyle buyers",
                    "Quick sale expected at current pricing"
                ],
                "estimated_days_to_sell": {
                    "at_current_price": 21,
                    "at_recommended_price": 21,
                }
            }
        },
    ]
