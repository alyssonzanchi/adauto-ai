"""
Evaluator Agent - Content quality evaluation and benchmarking
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from .base import BaseAgent
from app.services.llm.llm_client import LLMClient
from app.services.llm.prompts.ai_agents import EvaluationPrompt

logger = logging.getLogger(__name__)


class EvaluatorAgent(BaseAgent):
    """
    Agent for evaluating ad content quality and benchmarking.

    Capabilities:
    - Quality scoring (0-100)
    - Content analysis (headline, description, images, CTA)
    - Benchmarking vs top performers
    - Gap analysis
    - Improvement roadmap
    """

    def __init__(self, llm_client: LLMClient):
        """
        Initialize EvaluatorAgent.

        Args:
            llm_client: LLM client for API calls
        """
        prompt_template = EvaluationPrompt()

        super().__init__(
            llm_client=llm_client,
            prompt_template=prompt_template,
            name="evaluator_agent"
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute evaluation task.

        Args:
            context: Contains ad_content, vehicle_id, include_benchmark

        Returns:
            Evaluation results
        """
        ad_content = context.get("ad_content", {})
        vehicle_id = context.get("vehicle_id")
        include_benchmark = context.get("include_benchmark", True)

        # Evaluate content
        quality_score = await self._calculate_quality_score(ad_content)
        content_analysis = await self._analyze_content(ad_content)

        # Benchmark if requested
        benchmark = None
        if include_benchmark and vehicle_id:
            benchmark = await self._benchmark_comparison(vehicle_id, quality_score["overall"])

        # Generate recommendations
        recommendations = await self._generate_recommendations(
            ad_content,
            quality_score,
            content_analysis,
            benchmark
        )

        return {
            "quality_score": quality_score["overall"],
            "quality_grade": self._get_grade(quality_score["overall"]),
            "content_analysis": content_analysis,
            "gaps": quality_score.get("gaps", []),
            "benchmark_comparison": benchmark,
            "recommendations": recommendations
        }

    async def _calculate_quality_score(self, ad_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate comprehensive quality score.

        Args:
            ad_content: Ad content

        Returns:
            Quality scores
        """
        scores = {}

        # Headline quality (0-10)
        headline = ad_content.get("headline", "")
        scores["headline"] = self._score_headline(headline)

        # Description quality (0-10)
        description = ad_content.get("description", "")
        scores["description"] = self._score_description(description)

        # Image quality (0-10)
        images = ad_content.get("images", [])
        scores["images"] = self._score_images(images)

        # CTA quality (0-10)
        cta = ad_content.get("cta", "")
        scores["cta"] = self._score_cta(cta)

        # Overall score (0-100)
        weights = {"headline": 0.25, "description": 0.30, "images": 0.30, "cta": 0.15}
        overall = (
            scores["headline"]["score"] * weights["headline"] * 10 +
            scores["description"]["score"] * weights["description"] * 10 +
            scores["images"]["score"] * weights["images"] * 10 +
            scores["cta"]["score"] * weights["cta"] * 10
        )

        scores["overall"] = round(overall, 0)

        # Identify gaps
        gaps = []
        if scores["headline"]["score"] < 7:
            gaps.append("Headline precisa melhorar (length, clareza)")
        if scores["description"]["score"] < 7:
            gaps.append("Descrição muito curta ou pobre")
        if scores["images"]["score"] < 7:
            gaps.append(f"Poucas imagens ({len(images)}) - ideal: 5-7")
        if scores["cta"]["score"] < 7:
            gaps.append("CTA fraco ou ausente")

        scores["gaps"] = gaps

        return scores

    def _score_headline(self, headline: str) -> Dict[str, Any]:
        """Score headline quality"""
        score = 0.0
        feedback = []

        # Length
        length = len(headline)
        if 30 <= length <= 60:
            score += 3.0
            feedback.append("Tamanho adequado")
        elif 20 <= length < 30 or 60 < length <= 70:
            score += 2.0
            feedback.append("Tamanho aceitável")
        elif length > 0:
            score += 1.0
            feedback.append("Tamanho inadequado")

        # Has price
        if "R$" in headline or "reais" in headline.lower():
            score += 2.0
            feedback.append("Contém preço")

        # Has numbers
        if any(c.isdigit() for c in headline):
            score += 1.5
            feedback.append("Contém números (ano, kms)")

        # Has emoji
        if any(c in headline for c in "😀😃😄😁🚗🚙"):
            score += 0.5
            feedback.append("Contém emoji")

        # Is compelling
        compelling_words = ["impecável", "único dono", "seminova", "garantia", "oferta"]
        if any(word in headline.lower() for word in compelling_words):
            score += 2.0
            feedback.append("Palavras compelativas")

        # Capitalization
        if headline[0].isupper():
            score += 0.5
            feedback.append("Primeira letra maiúscula")

        return {"score": min(score, 10), "feedback": feedback}

    def _score_description(self, description: str) -> Dict[str, Any]:
        """Score description quality"""
        score = 0.0
        feedback = []

        # Length
        word_count = len(description.split())
        if word_count >= 100:
            score += 3.0
            feedback.append("Tamanho adequado")
        elif word_count >= 50:
            score += 2.0
            feedback.append("Tamanho aceitável")
        elif word_count > 0:
            score += 0.5
            feedback.append("Muito curta")

        # Contains key info
        key_info = ["airbag", "abs", "ar condicionado", "direção elétrica", "garantia", "blindagem"]
        found_info = [word for word in key_info if word.lower() in description.lower()]
        score += min(len(found_info) * 0.5, 3.0)
        if found_info:
            feedback.append(f"Contém {len(found_info)} infos-chave")

        # Structure (has paragraphs)
        if len(description.split('\n')) > 1:
            score += 1.0
            feedback.append("Bem estruturado")

        # No grammatical issues (simplified check)
        if description.count('!') > 3:
            feedback.append("Muitas exclamações")

        return {"score": min(score, 10), "feedback": feedback}

    def _score_images(self, images: List) -> Dict[str, Any]:
        """Score image quality"""
        score = 0.0
        feedback = []

        count = len(images)

        if 5 <= count <= 7:
            score += 4.0
            feedback.append("Quantidade ideal (5-7)")
        elif 3 <= count < 5:
            score += 2.5
            feedback.append("Quantidade aceitável")
        elif count > 0:
            score += 1.0
            feedback.append("Poucas imagens")
        else:
            feedback.append("Sem imagens")

        # Image variety (would need analysis in production)
        # For now, assume variety if count >= 3
        if count >= 3:
            score += 2.0
            feedback.append("Diversos ângulos")

        # Max score cap
        return {"score": min(score, 10), "feedback": feedback}

    def _score_cta(self, cta: str) -> Dict[str, Any]:
        """Score CTA quality"""
        score = 0.0
        feedback = []

        if not cta:
            return {"score": 0, "feedback": ["Sem CTA"]}

        # Length
        if 5 <= len(cta) <= 30:
            score += 3.0
            feedback.append("Tamanho adequado")
        elif len(cta) > 0:
            score += 1.0
            feedback.append("Tamanho inadequado")

        # Action-oriented
        action_words = ["entre", "agende", "chame", "contato", "whatsapp"]
        if any(word in cta.lower() for word in action_words):
            score += 3.0
            feedback.append("Orientado para ação")

        # Urgency
        urgency_words = ["agora", "hoje", "últimas", "oportunidade"]
        if any(word in cta.lower() for word in urgency_words):
            score += 2.0
            feedback.append("Cria urgência")

        return {"score": min(score, 10), "feedback": feedback}

    async def _analyze_content(self, ad_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze content in detail.

        Args:
            ad_content: Ad content

        Returns:
            Content analysis
        """
        headline = ad_content.get("headline", "")
        description = ad_content.get("description", "")
        images = ad_content.get("images", [])
        cta = ad_content.get("cta", "")

        return {
            "headline_quality": round(self._score_headline(headline)["score"], 1),
            "description_quality": round(self._score_description(description)["score"], 1),
            "image_quality": round(self._score_images(images)["score"], 1),
            "cta_quality": round(self._score_cta(cta)["score"], 1),
            "word_count": len(description.split()),
            "character_count": len(description)
        }

    async def _benchmark_comparison(
        self,
        vehicle_id: str,
        quality_score: float
    ) -> Optional[Dict[str, Any]]:
        """
        Compare with benchmarks.

        Args:
            vehicle_id: Vehicle ID
            quality_score: Current quality score

        Returns:
            Benchmark comparison
        """
        # In production, would query database for top performers
        # For now, return simulated data

        industry_avg = 65.0
        top_10_pct = 80.0

        return {
            "vs_industry": {
                "score_diff": round(quality_score - industry_avg, 1),
                "percentage_diff": round(((quality_score - industry_avg) / industry_avg) * 100, 1)
            },
            "vs_top_10": {
                "score_diff": round(quality_score - top_10_pct, 1),
                "percentage_diff": round(((quality_score - top_10_pct) / top_10_pct) * 100, 1)
            },
            "industry_average": industry_avg,
            "top_10_percent": top_10_pct,
            "percentile": self._calculate_percentile(quality_score)
        }

    def _calculate_percentile(self, score: float) -> float:
        """Calculate percentile rank"""
        # Simplified percentile calculation
        if score >= 80:
            return min(90, ((score - 80) / 20) * 10 + 90)
        elif score >= 65:
            return ((score - 65) / 15) * 50 + 40
        else:
            return (score / 65) * 40

    def _get_grade(self, score: float) -> str:
        """Get letter grade"""
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        else:
            return "D"

    async def _generate_recommendations(
        self,
        ad_content: Dict[str, Any],
        quality_score: Dict[str, Any],
        content_analysis: Dict[str, Any],
        benchmark: Optional[Dict[str, Any]]
    ) -> List[str]:
        """
        Generate improvement recommendations.

        Args:
            ad_content: Current ad content
            quality_score: Quality scores
            content_analysis: Content analysis
            benchmark: Benchmark comparison

        Returns:
            List of recommendations
        """
        recommendations = []

        overall_score = quality_score.get("overall", 0)
        gaps = quality_score.get("gaps", [])

        # High priority recommendations
        if overall_score < 60:
            recommendations.append("🔥 Prioridade alta: Revisar completamente o anúncio")

        # Specific recommendations based on gaps
        for gap in gaps:
            if "headline" in gap.lower():
                recommendations.append("📝 Melhore o título (30-60 caracteres, inclua preço)")
            if "descrição" in gap.lower():
                recommendations.append("📝 Expanda a descrição (100+ palavras com detalhes)")
            if "imagens" in gap.lower():
                recommendations.append("📸 Adicione mais fotos (5-7, boa qualidade)")
            if "CTA" in gap.upper() or "cta" in gap.lower():
                recommendations.append("🎯 Adicione call-to-action claro")

        # Benchmark-based recommendations
        if benchmark:
            vs_industry = benchmark["vs_industry"]["score_diff"]
            if vs_industry < -10:
                recommendations.append("📊 Abaixo da média da indústria - revisar conteúdo")

        # Quick wins
        recommendations.append("💡 Quick win: Adicione preço no título")
        recommendations.append("💡 Quick win: Use CTAs orientados à ação")

        return recommendations[:10]  # Top 10 recommendations
