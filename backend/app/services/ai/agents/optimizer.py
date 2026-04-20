"""
Optimizer Agent - Ad optimization and recommendations
"""
import logging
from typing import Dict, Any, List
import json

from .base import BaseAgent
from app.services.llm.llm_client import LLMClient
from app.services.llm.prompts.ai_agents import OptimizationPrompt

logger = logging.getLogger(__name__)


class OptimizerAgent(BaseAgent):
    """
    Agent for optimizing ad content and strategy.

    Capabilities:
    - Content optimization (headline, description, CTA)
    - Bid recommendations
    - Budget optimization
    - A/B testing suggestions
    - Performance improvement tips
    """

    def __init__(self, llm_client: LLMClient):
        """
        Initialize OptimizerAgent.

        Args:
            llm_client: LLM client for API calls
        """
        prompt_template = OptimizationPrompt()

        super().__init__(
            llm_client=llm_client,
            prompt_template=prompt_template,
            name="optimizer_agent"
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute optimization task.

        Args:
            context: Contains vehicle_data, ad_content, current_metrics, goals

        Returns:
            Optimization recommendations
        """
        vehicle_data = context.get("vehicle_data", {})
        ad_content = context.get("ad_content", {})
        current_metrics = context.get("current_metrics", {})
        goals = context.get("goals", {})

        # Analyze current content
        content_analysis = await self._analyze_content(ad_content)

        # Generate optimizations
        optimizations = {
            "content_optimization": await self._optimize_content(
                vehicle_data,
                ad_content,
                current_metrics
            ),
            "bid_recommendations": await self._recommend_bids(
                vehicle_data,
                current_metrics,
                goals
            ),
            "budget_optimization": await self._optimize_budget(
                vehicle_data,
                current_metrics,
                goals
            ),
            "suggested_tests": await self._suggest_ab_tests(
                vehicle_data,
                ad_content
            ),
            "optimization_priority": await self._get_priority_improvements(
                vehicle_data,
                ad_content,
                current_metrics
            )
        }

        return optimizations

    async def _analyze_content(self, ad_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze current ad content.

        Args:
            ad_content: Current ad content

        Returns:
            Content analysis
        """
        headline = ad_content.get("headline", "")
        description = ad_content.get("description", "")
        images = ad_content.get("images", [])
        cta = ad_content.get("cta", "")

        return {
            "headline_length": len(headline),
            "headline_word_count": len(headline.split()),
            "description_length": len(description),
            "description_word_count": len(description.split()),
            "image_count": len(images),
            "has_cta": len(cta) > 0,
            "quality_score": self._calculate_content_quality(ad_content)
        }

    async def _optimize_content(
        self,
        vehicle_data: Dict[str, Any],
        ad_content: Dict[str, Any],
        current_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate content optimizations.

        Args:
            vehicle_data: Vehicle info
            ad_content: Current ad content
            current_metrics: Current performance

        Returns:
            Content optimization recommendations
        """
        optimizations = []

        # Headline optimization
        headline = ad_content.get("headline", "")
        if len(headline) < 30:
            optimizations.append({
                "type": "headline",
                "issue": "Headline muito curto",
                "suggestion": f"Tente '{headline}' → '{vehicle_data.get('brand', '')} {vehicle_data.get('model', '')} {vehicle_data.get('model_year', '')} - Impecável! Único Dono'",
                "expected_improvement": "+15-25% CTR"
            })
        elif len(headline) > 60:
            optimizations.append({
                "type": "headline",
                "issue": "Headline muito longo",
                "suggestion": "Resuma para 30-60 caracteres",
                "expected_improvement": "+10% CTR"
            })

        # Add price to headline if missing
        if "R$" not in headline and "reais" not in headline.lower():
            optimizations.append({
                "type": "headline",
                "issue": "Preço não mencionado",
                "suggestion": f"Adicione preço: '{headline} - R$ {vehicle_data.get('price', 0):,.0f}'",
                "expected_improvement": "+20% CTR"
            })

        # Description optimization
        description = ad_content.get("description", "")
        word_count = len(description.split())
        if word_count < 50:
            optimizations.append({
                "type": "description",
                "issue": "Descrição muito curta",
                "suggestion": "Expanda descrição para 100+ palavras com detalhes do veículo",
                "expected_improvement": "+10% conversão"
            })

        # Image optimization
        images = ad_content.get("images", [])
        if len(images) < 3:
            optimizations.append({
                "type": "images",
                "issue": f"Poucas imagens ({len(images)})",
                "suggestion": "Adicione 5-7 fotos (interior, exterior, detalhes)",
                "expected_improvement": "+30% CTR"
            })
        elif len(images) > 10:
            optimizations.append({
                "type": "images",
                "issue": f"Muitas imagens ({len(images)})",
                "suggestion": "Reduza para 5-7 imagens das melhores qualidades",
                "expected_improvement": "+5% qualidade"
            })

        # CTA optimization
        cta = ad_content.get("cta", "")
        if not cta or len(cta) < 5:
            optimizations.append({
                "type": "cta",
                "issue": "CTA fraco ou ausente",
                "suggestion": "Use CTAs como: 'Entre em contato agora', 'Agende seu test-drive'",
                "expected_improvement": "+15% conversão"
            })

        return {
            "recommendations": optimizations,
            "priority_order": self._prioritize_optimizations(optimizations)
        }

    async def _recommend_bids(
        self,
        vehicle_data: Dict[str, Any],
        current_metrics: Dict[str, Any],
        goals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Recommend bid strategy.

        Args:
            vehicle_data: Vehicle info
            current_metrics: Current performance
            goals: Target goals

        Returns:
            Bid recommendations
        """
        price_position = vehicle_data.get("price_position", "fair_price")

        # Base bid (CPC in BRL)
        base_bid = 2.50

        # Adjust based on price position
        if price_position == "great_deal":
            recommended_bid = base_bid * 1.3  # Bid more for great deals
            reasoning = "Excelente preço, justifica lance mais alto"
        elif price_position == "good_price":
            recommended_bid = base_bid * 1.1
            reasoning = "Bom preço, pode aumentar lance"
        elif price_position == "fair_price":
            recommended_bid = base_bid
            reasoning = "Preço justo, manter lance padrão"
        elif price_position == "expensive":
            recommended_bid = base_bid * 0.8
            reasoning = "Preço acima do mercado, reduzir lance"
        else:  # overpriced
            recommended_bid = base_bid * 0.6
            reasoning = "Preço muito acima, reduzir significativamente"

        # Adjust for competition
        demand_score = vehicle_data.get("demand_score", 0.5)
        if demand_score > 0.7:
            recommended_bid *= 1.2
            reasoning += ", alta competição aumenta bid"

        return {
            "recommended_bid": round(recommended_bid, 2),
            "min_bid": round(recommended_bid * 0.7, 2),
            "max_bid": round(recommended_bid * 1.5, 2),
            "reasoning": reasoning,
            "bid_strategy": self._get_bid_strategy(demand_score)
        }

    def _get_bid_strategy(self, demand_score: float) -> str:
        """Get bidding strategy name"""
        if demand_score > 0.7:
            return "aggressive"
        elif demand_score > 0.4:
            return "moderate"
        else:
            return "conservative"

    async def _optimize_budget(
        self,
        vehicle_data: Dict[str, Any],
        current_metrics: Dict[str, Any],
        goals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Optimize budget allocation.

        Args:
            vehicle_data: Vehicle info
            current_metrics: Current performance
            goals: Target goals

        Returns:
            Budget optimization recommendations
        """
        target_ctr = goals.get("target_ctr", 0.05)
        target_conversion = goals.get("target_conversion", 0.03)

        current_ctr = current_metrics.get("ctr", 0.03)
        current_conversion = current_metrics.get("conversion_rate", 0.02)

        recommendations = []

        # Budget increase/decrease recommendations
        if current_ctr < target_ctr * 0.8:
            recommendations.append({
                "action": "increase_budget",
                "reason": f"CTR atual ({current_ctr:.1%}) abaixo da meta ({target_ctr:.1%})",
                "suggestion": "Aumentar budget em 20-30% para aumentar impressions",
                "expected_impact": "+20-30% cliques"
            })
        elif current_ctr > target_ctr * 1.2:
            recommendations.append({
                "action": "maintain_or_decrease",
                "reason": f"CTR atual ({current_ctr:.1%}) acima da meta ({target_ctr:.1%})",
                "suggestion": "Manter budget atual ou redistribuir para outros anúncios",
                "expected_impact": "Mesmos resultados com menor custo"
            })

        # Dayparting recommendations
        recommendations.append({
            "action": "optimize_schedule",
            "reason": "Otimizar horários de exibição",
            "suggestion": "Concentrar budget entre 8h-12h e 18h-22h (horários de pico)",
            "expected_impact": "+15-25% eficiência"
        })

        return {
            "recommendations": recommendations,
            "optimal_daily_budget": self._calculate_optimal_daily_budget(
                goals.get("target_budget", 1000)
            )
        }

    def _calculate_optimal_daily_budget(self, total_budget: float) -> float:
        """Calculate optimal daily budget"""
        return round(total_budget / 30, 2)  # Monthly to daily

    async def _suggest_ab_tests(
        self,
        vehicle_data: Dict[str, Any],
        ad_content: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Suggest A/B tests.

        Args:
            vehicle_data: Vehicle info
            ad_content: Current ad content

        Returns:
            List of A/B test suggestions
        """
        tests = []

        # Headline tests
        headline = ad_content.get("headline", "")
        tests.append({
            "test_type": "headline",
            "test_name": "Variação de headline com preço",
            "variants": [
                headline,
                f"{headline} - R$ {vehicle_data.get('price', 0):,.0f}",
                f"{vehicle_data.get('brand', '')} {vehicle_data.get('model', '')} - Oferta!"
            ],
            "success_metric": "ctr",
            "expected_winner": "Com preço no título"
        })

        # Image order tests
        tests.append({
            "test_type": "images",
            "test_name": "Ordem das imagens",
            "variants": [
                "Imagem principal: foto frontal",
                "Imagem principal: foto lateral",
                "Imagem principal: foto interior"
            ],
            "success_metric": "ctr",
            "duration_days": 7
        })

        # CTA tests
        tests.append({
            "test_type": "cta",
            "test_name": "Variação de CTA",
            "variants": [
                "Entre em contato",
                "Agende test-drive",
                "Chame no WhatsApp"
            ],
            "success_metric": "conversion_rate",
            "expected_winner": "Chame no WhatsApp"
        })

        return tests

    async def _get_priority_improvements(
        self,
        vehicle_data: Dict[str, Any],
        ad_content: Dict[str, Any],
        current_metrics: Dict[str, Any]
    ) -> List[str]:
        """
        Get prioritized list of improvements.

        Args:
            vehicle_data: Vehicle info
            ad_content: Current ad content
            current_metrics: Current performance

        Returns:
            Prioritized improvements list
        """
        improvements = []

        # High priority (immediate impact)
        images = ad_content.get("images", [])
        if len(images) < 3:
            improvements.append("🔥 ADICIONAR MAIS FOTOS - Prioridade máxima")

        if vehicle_data.get("price_position") == "overpriced":
            improvements.append("🔥 REAJUSTAR PREÇO - Acima do mercado")

        # Medium priority (significant impact)
        headline = ad_content.get("headline", "")
        if "R$" not in headline:
            improvements.append("⚡ ADICIONAR PREÇO NO TÍTULO")

        description = ad_content.get("description", "")
        if len(description.split()) < 50:
            improvements.append("⚡ EXPANDIR DESCRIÇÃO - Adicionar mais detalhes")

        # Low priority (nice to have)
        cta = ad_content.get("cta", "")
        if not cta:
            improvements.append("💡 ADICIONAR CALL-TO-ACTION")

        days_listed = vehicle_data.get("days_since_listing", 0)
        if days_listed > 30:
            improvements.append("💡 ATUALIZAR ANÚNCIO - Repostar para renovar")

        return improvements

    def _calculate_content_quality(self, ad_content: Dict[str, Any]) -> float:
        """Calculate content quality score (0-1)"""
        score = 0.0

        # Headline quality (30%)
        headline = ad_content.get("headline", "")
        if 30 <= len(headline) <= 60:
            score += 0.3
        elif len(headline) > 0:
            score += 0.1

        # Images (40%)
        images = ad_content.get("images", [])
        if 5 <= len(images) <= 7:
            score += 0.4
        elif len(images) >= 3:
            score += 0.2
        elif len(images) >= 1:
            score += 0.1

        # Description (20%)
        description = ad_content.get("description", "")
        if len(description.split()) >= 100:
            score += 0.2
        elif len(description.split()) >= 50:
            score += 0.1

        # CTA (10%)
        cta = ad_content.get("cta", "")
        if len(cta) > 5:
            score += 0.1

        return min(score, 1.0)

    def _prioritize_optimizations(self, optimizations: List[Dict[str, Any]]) -> List[str]:
        """Return prioritized list of optimization types"""
        priority_map = {
            "images": 1,
            "headline": 2,
            "price": 3,
            "description": 4,
            "cta": 5
        }

        sorted_opts = sorted(
            optimizations,
            key=lambda x: priority_map.get(x.get("type", ""), 10)
        )

        return [opt["type"] for opt in sorted_opts]
