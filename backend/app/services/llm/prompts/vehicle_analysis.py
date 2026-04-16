"""
Vehicle analysis prompt template.
"""
from typing import Any, Dict

from app.services.llm.prompts.base import BasePromptTemplate


class VehicleAnalysisPrompt(BasePromptTemplate):
    """
    Prompt template for comprehensive vehicle analysis.

    Analyzes:
    - Market price positioning
    - Selling points
    - Target audience
    - Suggested improvements
    - Performance metrics (CTR, conversion)
    """

    def get_system_prompt(self) -> str:
        """Get system prompt for vehicle analysis."""
        return """You are an expert automotive market analyst with 20 years of experience in the Brazilian car market.

You have deep knowledge of:
- Vehicle pricing dynamics across all segments
- Consumer behavior and preferences in Brazil
- Features that drive sales and engagement
- Market trends and seasonal variations
- Price elasticity and competitive positioning

Your analysis is:
- Data-driven and objective
- Tailored to the Brazilian market context
- Actionable and specific
- Based on real-world market conditions

Always provide responses in valid JSON format as requested."""

    def get_template_name(self) -> str:
        """Get template filename."""
        return "vehicle_analysis.jinja2"

    def render_vehicle_context(self, vehicle: Dict[str, Any]) -> str:
        """
        Render vehicle analysis prompt with context.

        Args:
            vehicle: Vehicle data dictionary

        Returns:
            Rendered prompt
        """
        context = {
            "vehicle": vehicle,
            "current_year": 2025,  # Could be dynamic
        }
        return self.render(context)


class VehicleAnalysisFewShots:
    """Few-shot examples for vehicle analysis."""

    EXAMPLES = [
        {
            "input": {
                "brand": "Toyota",
                "model": "Corolla XEI",
                "year": 2021,
                "mileage": 35000,
                "price": 125000,
                "body_type": "sedan",
                "features": {
                    "security": ["airbags", "abs", "controle_estabilidade"],
                    "comfort": ["ar_condicionado", "direcao_eletrica", "bancos_couro"],
                    "technology": ["central_multimidia", "gps", "android_auto"],
                }
            },
            "output": {
                "price_market": 118000.0,
                "price_score": 75,
                "price_position": "above_market",
                "selling_points": [
                    "manutencao_economica",
                    "conforto_destaque",
                    "tecnologia_moderna",
                    "seguranca_avancada",
                    "marca_consolidada"
                ],
                "target_audience": [
                    "familias",
                    "profissionais_liberais",
                    "motoristas_exigentes"
                ],
                "suggested_improvements": [
                    "destacar_historico_manutencao",
                    "fotos_profissionais_interior"
                ],
                "estimated_ctr": 0.042,
                "estimated_conversion": 0.025,
                "reasoning": {
                    "market_analysis": "Corolla holds value well in Brazilian market. 2021 models with 35k km are priced around R$118k. Listed 6% above market.",
                    "selling_points_rationale": "Strong features package including leather seats and advanced safety. Toyota brand reliability is a key selling point.",
                    "audience_rationale": "Sedan format appeals to professionals and families. Premium pricing targets middle-upper class buyers."
                }
            }
        },
        {
            "input": {
                "brand": " Hyundai",
                "model": "HB20S Platinum",
                "year": 2023,
                "mileage": 12000,
                "price": 75000,
                "body_type": "hatch",
                "features": {
                    "security": ["airbags", "abs"],
                    "comfort": ["ar_condicionado", "direcao_eletrica"],
                    "technology": ["central_multimidia", "android_auto"],
                }
            },
            "output": {
                "price_market": 72000.0,
                "price_score": 80,
                "price_position": "fair_price",
                "selling_points": [
                    "seminovo_zero_km",
                    "baixa_quilometragem",
                    "economia_combustivel",
                    "garantia_fabrica",
                    "tecnologia_moderna"
                ],
                "target_audience": [
                    "jovens",
                    "primeira_compra",
                    "motoristas_urbanos",
                    "classe_media"
                ],
                "suggested_improvements": [
                    "video_passeio_veiculo",
                    "destacar_garantia_restante"
                ],
                "estimated_ctr": 0.058,
                "estimated_conversion": 0.035,
                "reasoning": {
                    "market_analysis": "HB20S is popular in Brazil. 2023 Platinum with 12k km is well-positioned at R$75k. Competitive pricing.",
                    "selling_points_rationale": "Nearly new with factory warranty remaining. HB20S has strong fuel economy reputation.",
                    "audience_rationale": "Hatchback format and price point target younger buyers and first-time car buyers."
                }
            }
        },
    ]
