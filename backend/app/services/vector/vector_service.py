"""
Vector service for semantic search and recommendations.

Uses pgvector for fast similarity search with HNSW indexes.
"""
import logging
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import select, text, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from app.models.vehicle import Vehicle
from app.services.vector.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class VectorService:
    """
    Service for semantic search using vector embeddings.

    Features:
    - Similar vehicles search
    - Semantic text search
    - Recommendation engine
    - Hybrid search (vector + filters)
    - Performance optimized with HNSW indexes

    Performance Target: < 100ms per search
    """

    DEFAULT_SIMILARITY_THRESHOLD = 0.7
    DEFAULT_LIMIT = 10
    MAX_LIMIT = 50

    def __init__(
        self,
        embedding_service: EmbeddingService,
        similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
    ):
        """
        Initialize vector service.

        Args:
            embedding_service: Service for generating embeddings
            similarity_threshold: Minimum similarity score (0-1)
        """
        self.embedding_service = embedding_service
        self.similarity_threshold = similarity_threshold

        # Metrics
        self.metrics = {
            "searches_performed": 0,
            "total_results": 0,
            "avg_search_time_ms": 0.0,
            "cache_hits": 0,
        }

    async def find_similar_vehicles(
        self,
        db: AsyncSession,
        vehicle_id: str,
        limit: int = DEFAULT_LIMIT,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Find vehicles similar to a given vehicle.

        Args:
            db: Database session
            vehicle_id: ID of reference vehicle
            limit: Maximum number of results
            filters: Optional filters (price range, brand, etc.)

        Returns:
            List of similar vehicles with similarity scores
        """
        import time

        start_time = time.time()

        # Get reference vehicle
        vehicle = await db.get(Vehicle, vehicle_id)
        if not vehicle or not vehicle.description_embedding:
            logger.warning(f"Vehicle {vehicle_id} not found or has no embeddings")
            return []

        # Build query
        query = self._build_similarity_query(
            embedding_column="description_embedding",
            embedding_vector=vehicle.description_embedding,
            filters=filters,
        )

        # Exclude the reference vehicle
        query = query.where(Vehicle.id != vehicle_id)

        # Apply limit
        limit = min(limit, self.MAX_LIMIT)
        query = query.limit(limit)

        # Execute query
        result = await db.execute(query)
        vehicles = result.all()

        # Format results
        similar_vehicles = []
        for v, similarity in vehicles:
            similar_vehicles.append(
                {
                    "id": str(v.id),
                    "title": v.title,
                    "brand": v.brand,
                    "model": v.model,
                    "year": v.year,
                    "price": float(v.price),
                    "mileage": v.mileage,
                    "similarity": float(similarity),
                    "main_image": v.main_image,
                }
            )

        # Update metrics
        elapsed_ms = (time.time() - start_time) * 1000
        self.metrics["searches_performed"] += 1
        self.metrics["total_results"] += len(similar_vehicles)
        self.metrics["avg_search_time_ms"] = (
            (self.metrics["avg_search_time_ms"] * (self.metrics["searches_performed"] - 1) + elapsed_ms)
            / self.metrics["searches_performed"]
        )

        logger.info(
            f"Found {len(similar_vehicles)} similar vehicles to {vehicle_id} "
            f"in {elapsed_ms:.2f}ms"
        )

        return similar_vehicles

    async def search_by_text(
        self,
        db: AsyncSession,
        query_text: str,
        limit: int = DEFAULT_LIMIT,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Semantic search by text query.

        Args:
            db: Database session
            query_text: Search query text
            limit: Maximum number of results
            filters: Optional filters

        Returns:
            List of matching vehicles with similarity scores
        """
        import time

        start_time = time.time()

        # Generate embedding for query text
        query_embedding = await self.embedding_service.generate_embedding(query_text)
        if not query_embedding:
            logger.warning(f"Failed to generate embedding for query: {query_text}")
            return []

        # Build query
        query = self._build_similarity_query(
            embedding_column="description_embedding",
            embedding_vector=query_embedding,
            filters=filters,
        )

        # Apply limit
        limit = min(limit, self.MAX_LIMIT)
        query = query.limit(limit)

        # Execute query
        result = await db.execute(query)
        vehicles = result.all()

        # Format results
        matching_vehicles = []
        for v, similarity in vehicles:
            # Filter by similarity threshold
            if similarity >= self.similarity_threshold:
                matching_vehicles.append(
                    {
                        "id": str(v.id),
                        "title": v.title,
                        "brand": v.brand,
                        "model": v.model,
                        "year": v.year,
                        "price": float(v.price),
                        "mileage": v.mileage,
                        "similarity": float(similarity),
                        "main_image": v.main_image,
                        "description": v.description,
                    }
                )

        # Update metrics
        elapsed_ms = (time.time() - start_time) * 1000
        self.metrics["searches_performed"] += 1
        self.metrics["total_results"] += len(matching_vehicles)
        self.metrics["avg_search_time_ms"] = (
            (self.metrics["avg_search_time_ms"] * (self.metrics["searches_performed"] - 1) + elapsed_ms)
            / self.metrics["searches_performed"]
        )

        logger.info(
            f"Text search '{query_text}' found {len(matching_vehicles)} results "
            f"in {elapsed_ms:.2f}ms"
        )

        return matching_vehicles

    async def recommend_similar(
        self,
        db: AsyncSession,
        vehicle_data: Dict[str, Any],
        limit: int = DEFAULT_LIMIT,
    ) -> List[Dict[str, Any]]:
        """
        Recommend vehicles similar to provided data.

        Useful for "vehicles like this" feature.

        Args:
            db: Database session
            vehicle_data: Vehicle data (doesn't need to exist in DB)
            limit: Maximum number of results

        Returns:
            List of recommended vehicles
        """
        # Generate embeddings for the vehicle data
        embeddings = await self.embedding_service.generate_vehicle_embeddings(vehicle_data)
        if not embeddings.get("description_embedding"):
            logger.warning("Failed to generate embeddings for recommendation")
            return []

        # Build query
        query = self._build_similarity_query(
            embedding_column="description_embedding",
            embedding_vector=embeddings["description_embedding"],
            filters=None,
        )

        # Apply limit
        limit = min(limit, self.MAX_LIMIT)
        query = query.limit(limit)

        # Execute query
        result = await db.execute(query)
        vehicles = result.all()

        # Format results
        recommendations = []
        for v, similarity in vehicles:
            if similarity >= self.similarity_threshold:
                recommendations.append(
                    {
                        "id": str(v.id),
                        "title": v.title,
                        "brand": v.brand,
                        "model": v.model,
                        "year": v.year,
                        "price": float(v.price),
                        "mileage": v.mileage,
                        "similarity": float(similarity),
                        "main_image": v.main_image,
                    }
                )

        return recommendations

    async def find_complementary_vehicles(
        self,
        db: AsyncSession,
        vehicle_id: str,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Find complementary vehicles (different but related).

        Useful for cross-selling (e.g., suggest SUV when viewing sedan).

        Args:
            db: Database session
            vehicle_id: ID of reference vehicle
            limit: Maximum number of results

        Returns:
            List of complementary vehicles
        """
        # Get reference vehicle
        vehicle = await db.get(Vehicle, vehicle_id)
        if not vehicle:
            return []

        # Build query with features embedding (focus on features, not description)
        if not vehicle.features_embedding:
            return []

        query = self._build_similarity_query(
            embedding_column="features_embedding",
            embedding_vector=vehicle.features_embedding,
            filters={
                "exclude_body_type": vehicle.body_type,  # Suggest different body types
                "similar_price_range": float(vehicle.price),  # Similar price point
            },
        )

        query = query.where(Vehicle.id != vehicle_id)
        query = query.limit(limit)

        # Execute query
        result = await db.execute(query)
        vehicles = result.all()

        # Format results
        complementary = []
        for v, similarity in vehicles:
            complementary.append(
                {
                    "id": str(v.id),
                    "title": v.title,
                    "brand": v.brand,
                    "model": v.model,
                    "year": v.year,
                    "price": float(v.price),
                    "body_type": v.body_type,
                    "similarity": float(similarity),
                    "main_image": v.main_image,
                }
            )

        return complementary

    def _build_similarity_query(
        self,
        embedding_column: str,
        embedding_vector: List[float],
        filters: Optional[Dict[str, Any]] = None,
    ) -> Select:
        """
        Build SQL query for similarity search.

        Uses cosine similarity: 1 - (embedding <=> query_vector)

        Args:
            embedding_column: Column to search (description_embedding or features_embedding)
            embedding_vector: Query embedding vector
            filters: Optional filters

        Returns:
            SQLAlchemy Select query
        """
        # Build query with cosine similarity
        # Note: <=> is pgvector's cosine distance operator
        # Cosine similarity = 1 - cosine_distance
        similarity_expr = text(
            f"1 - ({embedding_column} <=> :embedding_vector)"
        ).bindparams(embedding_vector=embedding_vector)

        query = select(
            Vehicle,
            similarity_expr.label("similarity"),
        ).where(
            Vehicle.deleted_at.is_(None),
            Vehicle.status == "active",
        )

        # Apply optional filters
        if filters:
            if filters.get("brand"):
                query = query.where(Vehicle.brand.ilike(f"%{filters['brand']}%"))

            if filters.get("price_min"):
                query = query.where(Vehicle.price >= filters["price_min"])

            if filters.get("price_max"):
                query = query.where(Vehicle.price <= filters["price_max"])

            if filters.get("year_min"):
                query = query.where(Vehicle.year >= filters["year_min"])

            if filters.get("year_max"):
                query = query.where(Vehicle.year <= filters["year_max"])

            if filters.get("exclude_body_type"):
                query = query.where(Vehicle.body_type != filters["exclude_body_type"])

            if filters.get("similar_price_range"):
                price = filters["similar_price_range"]
                query = query.where(
                    Vehicle.price.between(price * 0.8, price * 1.2)
                )

        # Order by similarity (highest first)
        query = query.order_by(similarity_expr.desc())

        return query

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get service metrics.

        Returns:
            Metrics dictionary
        """
        return {
            **self.metrics,
            "avg_results_per_search": (
                self.metrics["total_results"] / self.metrics["searches_performed"]
                if self.metrics["searches_performed"] > 0
                else 0.0
            ),
        }

    def reset_metrics(self):
        """Reset metrics."""
        self.metrics = {
            "searches_performed": 0,
            "total_results": 0,
            "avg_search_time_ms": 0.0,
            "cache_hits": 0,
        }
