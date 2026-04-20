"""
Agent Orchestrator - Coordinates AI agents for vehicle analysis.

Replaces the mock AI service with production-ready Claude/OpenAI integration.
Features:
- Agent routing and coordination
- Error handling and fallbacks
- Feature caching (Redis)
- Logging and metrics
- Semantic search integration
"""
import logging
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.vehicle import Vehicle
from app.services.ai.agents.analyzer import AnalyzerAgent
from app.services.ai.agents.generator import GeneratorAgent
from app.services.ai.agents.scorer import ScorerAgent
from app.services.cache.feature_store import FeatureStore
from app.services.llm.llm_client import LLMClient
from app.services.vector.embedding_service import EmbeddingService
from app.services.vector.vector_service import VectorService

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Orchestrator for AI-powered vehicle analysis.

    Coordinates multiple AI agents:
    - AnalyzerAgent: Comprehensive vehicle analysis
    - GeneratorAgent: Ad content generation
    - ScorerAgent: Price scoring and analysis

    Integrates with:
    - LLM Client (Claude + OpenAI fallback)
    - Embedding Service (OpenAI embeddings)
    - Vector Store (pgvector semantic search)
    - Feature Store (Redis caching)
    """

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        embedding_service: Optional[EmbeddingService] = None,
        vector_service: Optional[VectorService] = None,
        feature_store: Optional[FeatureStore] = None,
    ):
        """
        Initialize orchestrator.

        Args:
            llm_client: LLM client (defaults to new instance)
            embedding_service: Embedding service (defaults to new instance)
            vector_service: Vector search service (defaults to new instance)
            feature_store: Feature cache store (defaults to new instance)
        """
        # Initialize services
        self.llm_client = llm_client or LLMClient()
        self.embedding_service = embedding_service or EmbeddingService()
        self.vector_service = vector_service or VectorService(
            embedding_service=self.embedding_service,
        )
        self.feature_store = feature_store or FeatureStore()

        # Initialize agents
        self.analyzer_agent = AnalyzerAgent(self.llm_client)
        self.generator_agent = GeneratorAgent(self.llm_client)
        self.scorer_agent = ScorerAgent(self.llm_client)

        # Metrics
        self.metrics = {
            "analyses_performed": 0,
            "ads_generated": 0,
            "price_scores": 0,
            "cache_hits": 0,
            "errors": 0,
        }

    async def analyze_vehicle(
        self,
        vehicle_data: Dict[str, Any],
        db: AsyncSession,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Perform comprehensive vehicle analysis.

        This is the main entry point, replacing the mock ai_service.analyze_vehicle().

        Args:
            vehicle_data: Vehicle data dictionary
            db: Database session
            use_cache: Whether to use cache

        Returns:
            Analysis results with:
            - price_market: Estimated market price
            - price_score: Competitiveness score (0-100)
            - price_position: Position category
            - selling_points: List of selling points
            - target_audience: List of audience segments
            - suggested_improvements: List of suggestions
            - estimated_ctr: Expected CTR
            - estimated_conversion: Expected conversion rate
            - analysis_version: Version string
            - analyzed_at: Timestamp

        Raises:
            ValueError: If vehicle data invalid
            LLMClientError: If LLM call fails
        """
        try:
            self.metrics["analyses_performed"] += 1

            vehicle_id = vehicle_data.get("id")
            if vehicle_id and use_cache:
                # Try cache first
                cached = await self.feature_store.get_vehicle_analysis(vehicle_id)
                if cached:
                    self.metrics["cache_hits"] += 1
                    logger.info(f"Cache hit for vehicle analysis: {vehicle_id}")
                    return cached

            # Prepare context for analyzer
            context = {"vehicle": vehicle_data}

            # Execute analyzer agent
            analysis = await self.analyzer_agent.execute(context)

            # Cache results if vehicle_id provided
            if vehicle_id and use_cache:
                await self.feature_store.cache_vehicle_analysis(vehicle_id, analysis)

            logger.info(f"Vehicle analysis completed for: {vehicle_data.get('brand')} {vehicle_data.get('model')}")

            return analysis

        except Exception as e:
            self.metrics["errors"] += 1
            logger.error(f"Vehicle analysis failed: {e}")
            raise

    async def generate_ad_content(
        self,
        vehicle_data: Dict[str, Any],
        content_type: str = "full",
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate advertisement content.

        Args:
            vehicle_data: Vehicle data dictionary
            content_type: "headline" or "full"
            use_cache: Whether to use cache

        Returns:
            Generated ad content
        """
        try:
            self.metrics["ads_generated"] += 1

            # Prepare context
            context = {
                "vehicle": vehicle_data,
                "content_type": content_type,
            }

            # Execute generator agent
            ad_content = await self.generator_agent.execute(context)

            logger.info(f"Ad content generated: {content_type}")

            return ad_content

        except Exception as e:
            self.metrics["errors"] += 1
            logger.error(f"Ad generation failed: {e}")
            raise

    async def score_price(
        self,
        vehicle_data: Dict[str, Any],
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Analyze price competitiveness.

        Args:
            vehicle_data: Vehicle data with listed_price
            use_cache: Whether to use cache

        Returns:
            Price scoring results
        """
        try:
            self.metrics["price_scores"] += 1

            # Prepare context
            context = {"vehicle": vehicle_data}

            # Execute scorer agent
            price_score = await self.scorer_agent.execute(context)

            logger.info(f"Price scoring completed: R${vehicle_data.get('listed_price', 0):,.2f}")

            return price_score

        except Exception as e:
            self.metrics["errors"] += 1
            logger.error(f"Price scoring failed: {e}")
            raise

    async def find_similar_vehicles(
        self,
        db: AsyncSession,
        vehicle_id: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Find vehicles similar to a given vehicle.

        Args:
            db: Database session
            vehicle_id: Reference vehicle ID
            limit: Maximum results
            filters: Optional filters

        Returns:
            List of similar vehicles with similarity scores
        """
        try:
            similar = await self.vector_service.find_similar_vehicles(
                db=db,
                vehicle_id=vehicle_id,
                limit=limit,
                filters=filters,
            )

            logger.info(f"Found {len(similar)} similar vehicles to {vehicle_id}")

            return similar

        except Exception as e:
            self.metrics["errors"] += 1
            logger.error(f"Similar vehicles search failed: {e}")
            raise

    async def search_vehicles_semantically(
        self,
        db: AsyncSession,
        query_text: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Semantic search for vehicles.

        Args:
            db: Database session
            query_text: Search query
            limit: Maximum results
            filters: Optional filters

        Returns:
            List of matching vehicles
        """
        try:
            results = await self.vector_service.search_by_text(
                db=db,
                query_text=query_text,
                limit=limit,
                filters=filters,
            )

            logger.info(f"Semantic search '{query_text}' found {len(results)} results")

            return results

        except Exception as e:
            self.metrics["errors"] += 1
            logger.error(f"Semantic search failed: {e}")
            raise

    async def generate_vehicle_embeddings(
        self,
        vehicle_data: Dict[str, Any],
        db: Optional[AsyncSession] = None,
        use_cache: bool = True,
    ) -> Dict[str, Optional[List[float]]]:
        """
        Generate embeddings for a vehicle.

        Args:
            vehicle_data: Vehicle data
            db: Database session (optional, for updating vehicle)
            use_cache: Whether to use cache

        Returns:
            Dictionary with description_embedding and features_embedding
        """
        try:
            embeddings = await self.embedding_service.generate_vehicle_embeddings(
                vehicle=vehicle_data,
                use_cache=use_cache,
            )

            # Update vehicle in database if session provided
            if db and vehicle_data.get("id"):
                vehicle = await db.get(Vehicle, vehicle_data["id"])
                if vehicle:
                    vehicle.description_embedding = embeddings.get("description_embedding")
                    vehicle.features_embedding = embeddings.get("features_embedding")
                    await db.commit()

                    # Cache embeddings
                    if use_cache:
                        await self.feature_store.cache_embedding(
                            vehicle_data["id"],
                            "description",
                            embeddings["description_embedding"],
                        )
                        await self.feature_store.cache_embedding(
                            vehicle_data["id"],
                            "features",
                            embeddings["features_embedding"],
                        )

            logger.info(f"Embeddings generated for vehicle {vehicle_data.get('id')}")

            return embeddings

        except Exception as e:
            self.metrics["errors"] += 1
            logger.error(f"Embedding generation failed: {e}")
            raise

    async def health_check(self) -> Dict[str, Any]:
        """
        Check health of AI services.

        Returns:
            Health status dictionary
        """
        health = {
            "status": "healthy",
            "services": {},
        }

        # Check LLM client
        try:
            if self.llm_client.anthropic_client or self.llm_client.openai_client:
                health["services"]["llm_client"] = "ok"
            else:
                health["services"]["llm_client"] = "misconfigured"
                health["status"] = "degraded"
        except Exception as e:
            health["services"]["llm_client"] = f"error: {e}"
            health["status"] = "unhealthy"

        # Check embedding service
        try:
            if self.embedding_service.client:
                health["services"]["embedding_service"] = "ok"
            else:
                health["services"]["embedding_service"] = "disabled"
        except Exception as e:
            health["services"]["embedding_service"] = f"error: {e}"
            health["status"] = "degraded"

        # Check feature store
        try:
            await self.feature_store.client.ping()
            health["services"]["feature_store"] = "ok"
        except Exception as e:
            health["services"]["feature_store"] = f"error: {e}"
            health["status"] = "degraded"

        return health

    async def predict_performance(
        self,
        vehicle_data: Dict[str, Any],
        forecast_days: int = 30,
        include_scenarios: bool = False,
        target_budget: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Predict complete ad performance using ML + AI.

        Args:
            vehicle_data: Vehicle data dictionary
            forecast_days: Forecast period (7, 30, or 90)
            include_scenarios: Include budget scenario analysis
            target_budget: Target budget for scenarios

        Returns:
            Complete prediction with ML predictions + AI insights
        """
        try:
            from app.services.ai.agents.predictor import PredictorAgent

            # Lazy load predictor agent
            if not hasattr(self, 'predictor_agent'):
                self.predictor_agent = PredictorAgent(self.llm_client)

            self.metrics["analyses_performed"] += 1

            # Prepare context
            context = {
                "vehicle_data": vehicle_data,
                "forecast_days": forecast_days,
                "target_budget": target_budget,
                "include_scenarios": include_scenarios
            }

            # Execute predictor
            prediction = await self.predictor_agent._execute_with_metrics(context)

            logger.info(f"Performance prediction completed for vehicle {vehicle_data.get('id')}")

            return prediction

        except Exception as e:
            self.metrics["errors"] += 1
            logger.error(f"Performance prediction failed: {e}")
            raise

    async def optimize_ad(
        self,
        vehicle_data: Dict[str, Any],
        ad_content: Dict[str, Any],
        current_metrics: Optional[Dict[str, Any]] = None,
        goals: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Optimize ad content and strategy.

        Args:
            vehicle_data: Vehicle information
            ad_content: Current ad content
            current_metrics: Current performance metrics
            goals: Target goals (CTR, conversion, budget)

        Returns:
            Optimization recommendations
        """
        try:
            from app.services.ai.agents.optimizer import OptimizerAgent

            # Lazy load optimizer agent
            if not hasattr(self, 'optimizer_agent'):
                self.optimizer_agent = OptimizerAgent(self.llm_client)

            self.metrics["ads_generated"] += 1

            # Prepare context
            context = {
                "vehicle_data": vehicle_data,
                "ad_content": ad_content,
                "current_metrics": current_metrics or {},
                "goals": goals or {}
            }

            # Execute optimizer
            optimization = await self.optimizer_agent._execute_with_metrics(context)

            logger.info(f"Ad optimization completed for vehicle {vehicle_data.get('id')}")

            return optimization

        except Exception as e:
            self.metrics["errors"] += 1
            logger.error(f"Ad optimization failed: {e}")
            raise

    async def evaluate_content(
        self,
        ad_content: Dict[str, Any],
        vehicle_id: Optional[str] = None,
        include_benchmark: bool = True,
    ) -> Dict[str, Any]:
        """
        Evaluate ad content quality.

        Args:
            ad_content: Ad content to evaluate
            vehicle_id: Associated vehicle ID
            include_benchmark: Include benchmarking comparison

        Returns:
            Quality evaluation with scoring and recommendations
        """
        try:
            from app.services.ai.agents.evaluator import EvaluatorAgent

            # Lazy load evaluator agent
            if not hasattr(self, 'evaluator_agent'):
                self.evaluator_agent = EvaluatorAgent(self.llm_client)

            # Prepare context
            context = {
                "ad_content": ad_content,
                "vehicle_id": vehicle_id,
                "include_benchmark": include_benchmark
            }

            # Execute evaluator
            evaluation = await self.evaluator_agent._execute_with_metrics(context)

            logger.info(f"Content evaluation completed")

            return evaluation

        except Exception as e:
            self.metrics["errors"] += 1
            logger.error(f"Content evaluation failed: {e}")
            raise

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get orchestrator metrics.

        Returns:
            Metrics dictionary with sub-metrics from all services
        """
        base_metrics = super().get_metrics() if hasattr(super(), 'get_metrics') else {}

        return {
            **base_metrics,
            "llm_client": self.llm_client.get_metrics(),
            "embedding_service": self.embedding_service.get_metrics(),
            "vector_service": self.vector_service.get_metrics(),
            "feature_store": self.feature_store.get_metrics(),
            "analyzer_agent": self.analyzer_agent.get_metrics(),
            "generator_agent": self.generator_agent.get_metrics(),
            "scorer_agent": self.scorer_agent.get_metrics(),
            "predictor_agent": self.predictor_agent.get_metrics() if hasattr(self, 'predictor_agent') else {},
            "optimizer_agent": self.optimizer_agent.get_metrics() if hasattr(self, 'optimizer_agent') else {},
            "evaluator_agent": self.evaluator_agent.get_metrics() if hasattr(self, 'evaluator_agent') else {},
        }

    def reset_metrics(self):
        """Reset all metrics."""
        self.metrics = {
            "analyses_performed": 0,
            "ads_generated": 0,
            "price_scores": 0,
            "cache_hits": 0,
            "errors": 0,
        }

        # Reset sub-service metrics
        self.llm_client.reset_metrics()
        self.embedding_service.reset_metrics()
        self.vector_service.reset_metrics()
        self.feature_store.reset_metrics()
        self.analyzer_agent.reset_metrics()
        self.generator_agent.reset_metrics()
        self.scorer_agent.reset_metrics()


# Global orchestrator instance (will be initialized on app startup)
orchestrator: Optional[AgentOrchestrator] = None


def get_orchestrator() -> AgentOrchestrator:
    """
    Get global orchestrator instance.

    Returns:
        Orchestrator instance

    Raises:
        RuntimeError: If orchestrator not initialized
    """
    if orchestrator is None:
        raise RuntimeError("Orchestrator not initialized. Call startup_ai_services() first.")
    return orchestrator
