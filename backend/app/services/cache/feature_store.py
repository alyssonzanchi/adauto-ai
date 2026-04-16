"""
Feature Store for caching vehicle data and AI results.

Uses Redis for high-performance caching with TTL support.
"""
import json
import logging
from decimal import Decimal
from typing import Any, Dict, List, Optional

from redis.asyncio import Redis

from app.core.config import settings

logger = logging.getLogger(__name__)


class FeatureStore:
    """
    Redis-based feature store for caching vehicle data.

    Cache Keys:
    - vehicle:{vehicle_id}:features → Vehicle features JSON (1h TTL)
    - vehicle:{vehicle_id}:analysis → AI analysis JSON (30min TTL)
    - embedding:description:{vehicle_id} → Embedding vector (24h TTL)
    - embedding:features:{vehicle_id} → Embedding vector (24h TTL)
    - ai:analysis:{vehicle_id} → Complete AI analysis (30min TTL)

    Performance Target: < 10ms retrieval
    """

    # Cache TTLs (in seconds)
    VEHICLE_FEATURES_TTL = 3600  # 1 hour
    AI_ANALYSIS_TTL = 1800  # 30 minutes
    EMBEDDING_TTL = 86400  # 24 hours

    def __init__(
        self,
        redis_url: Optional[str] = None,
        redis_client: Optional[Redis] = None,
    ):
        """
        Initialize feature store.

        Args:
            redis_url: Redis connection URL (defaults to settings)
            redis_client: Existing Redis client (optional)
        """
        if redis_client:
            self.client = redis_client
        elif redis_url:
            self.client = Redis.from_url(redis_url, decode_responses=True)
        else:
            self.client = Redis.from_url(settings.REDIS_URL, decode_responses=True)

        # Metrics
        self.metrics = {
            "cache_hits": 0,
            "cache_misses": 0,
            "cache_sets": 0,
            "cache_deletes": 0,
        }

    def _make_key(self, *parts: str) -> str:
        """
        Create cache key from parts.

        Args:
            *parts: Key parts

        Returns:
            Cache key string
        """
        return ":".join(str(part) for part in parts)

    async def get_vehicle_features(
        self,
        vehicle_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached vehicle features.

        Args:
            vehicle_id: Vehicle ID

        Returns:
            Vehicle features dict or None if not cached
        """
        key = self._make_key("vehicle", vehicle_id, "features")

        try:
            cached = await self.client.get(key)
            if cached:
                self.metrics["cache_hits"] += 1
                return json.loads(cached)

            self.metrics["cache_misses"] += 1
            return None

        except Exception as e:
            logger.error(f"Error getting vehicle features from cache: {e}")
            self.metrics["cache_misses"] += 1
            return None

    async def cache_vehicle_features(
        self,
        vehicle_id: str,
        features: Dict[str, Any],
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Cache vehicle features.

        Args:
            vehicle_id: Vehicle ID
            features: Features dictionary
            ttl: Time to live in seconds (defaults to VEHICLE_FEATURES_TTL)

        Returns:
            True if successful
        """
        key = self._make_key("vehicle", vehicle_id, "features")
        ttl = ttl or self.VEHICLE_FEATURES_TTL

        try:
            await self.client.set(key, json.dumps(features), ex=ttl)
            self.metrics["cache_sets"] += 1
            return True

        except Exception as e:
            logger.error(f"Error caching vehicle features: {e}")
            return False

    async def get_vehicle_analysis(
        self,
        vehicle_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached AI analysis.

        Args:
            vehicle_id: Vehicle ID

        Returns:
            AI analysis dict or None if not cached
        """
        key = self._make_key("ai", "analysis", vehicle_id)

        try:
            cached = await self.client.get(key)
            if cached:
                self.metrics["cache_hits"] += 1
                return json.loads(cached)

            self.metrics["cache_misses"] += 1
            return None

        except Exception as e:
            logger.error(f"Error getting AI analysis from cache: {e}")
            self.metrics["cache_misses"] += 1
            return None

    async def cache_vehicle_analysis(
        self,
        vehicle_id: str,
        analysis: Dict[str, Any],
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Cache AI analysis results.

        Args:
            vehicle_id: Vehicle ID
            analysis: Analysis dictionary
            ttl: Time to live in seconds (defaults to AI_ANALYSIS_TTL)

        Returns:
            True if successful
        """
        key = self._make_key("ai", "analysis", vehicle_id)
        ttl = ttl or self.AI_ANALYSIS_TTL

        try:
            # Convert Decimal to float for JSON serialization
            analysis_copy = self._convert_decimals(analysis)

            await self.client.set(key, json.dumps(analysis_copy), ex=ttl)
            self.metrics["cache_sets"] += 1
            return True

        except Exception as e:
            logger.error(f"Error caching AI analysis: {e}")
            return False

    async def get_embedding(
        self,
        vehicle_id: str,
        embedding_type: str,  # "description" or "features"
    ) -> Optional[List[float]]:
        """
        Get cached embedding.

        Args:
            vehicle_id: Vehicle ID
            embedding_type: Type of embedding

        Returns:
            Embedding vector or None if not cached
        """
        key = self._make_key("embedding", embedding_type, vehicle_id)

        try:
            cached = await self.client.get(key)
            if cached:
                self.metrics["cache_hits"] += 1
                return json.loads(cached)

            self.metrics["cache_misses"] += 1
            return None

        except Exception as e:
            logger.error(f"Error getting embedding from cache: {e}")
            self.metrics["cache_misses"] += 1
            return None

    async def cache_embedding(
        self,
        vehicle_id: str,
        embedding_type: str,
        embedding: List[float],
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Cache embedding vector.

        Args:
            vehicle_id: Vehicle ID
            embedding_type: Type of embedding
            embedding: Embedding vector
            ttl: Time to live in seconds (defaults to EMBEDDING_TTL)

        Returns:
            True if successful
        """
        key = self._make_key("embedding", embedding_type, vehicle_id)
        ttl = ttl or self.EMBEDDING_TTL

        try:
            await self.client.set(key, json.dumps(embedding), ex=ttl)
            self.metrics["cache_sets"] += 1
            return True

        except Exception as e:
            logger.error(f"Error caching embedding: {e}")
            return False

    async def invalidate_vehicle(self, vehicle_id: str) -> bool:
        """
        Invalidate all cached data for a vehicle.

        Args:
            vehicle_id: Vehicle ID

        Returns:
            True if successful
        """
        # Pattern match all keys for this vehicle
        patterns = [
            self._make_key("vehicle", vehicle_id, "*"),
            self._make_key("ai", "analysis", vehicle_id),
            self._make_key("embedding", "*", vehicle_id),
        ]

        try:
            for pattern in patterns:
                keys = await self.client.keys(pattern)
                if keys:
                    await self.client.delete(*keys)
                    self.metrics["cache_deletes"] += len(keys)

            logger.info(f"Invalidated cache for vehicle {vehicle_id}")
            return True

        except Exception as e:
            logger.error(f"Error invalidating vehicle cache: {e}")
            return False

    async def warm_cache(
        self,
        vehicle_id: str,
        vehicle_data: Dict[str, Any],
        embeddings: Dict[str, List[float]],
        analysis: Dict[str, Any],
    ) -> bool:
        """
        Warm cache with all vehicle data.

        Args:
            vehicle_id: Vehicle ID
            vehicle_data: Vehicle features
            embeddings: Embedding vectors
            analysis: AI analysis

        Returns:
            True if successful
        """
        try:
            # Cache features
            await self.cache_vehicle_features(vehicle_id, vehicle_data)

            # Cache embeddings
            if embeddings.get("description_embedding"):
                await self.cache_embedding(
                    vehicle_id, "description", embeddings["description_embedding"]
                )

            if embeddings.get("features_embedding"):
                await self.cache_embedding(
                    vehicle_id, "features", embeddings["features_embedding"]
                )

            # Cache analysis
            await self.cache_vehicle_analysis(vehicle_id, analysis)

            logger.info(f"Warmed cache for vehicle {vehicle_id}")
            return True

        except Exception as e:
            logger.error(f"Error warming cache: {e}")
            return False

    async def batch_get_vehicles_features(
        self,
        vehicle_ids: List[str],
    ) -> Dict[str, Optional[Dict[str, Any]]]:
        """
        Batch get vehicle features.

        Args:
            vehicle_ids: List of vehicle IDs

        Returns:
            Dictionary mapping vehicle_id to features
        """
        results = {}

        for vehicle_id in vehicle_ids:
            features = await self.get_vehicle_features(vehicle_id)
            results[vehicle_id] = features

        return results

    async def clear_all_cache(self) -> bool:
        """
        Clear all feature store cache.

        WARNING: Use with caution in production!

        Returns:
            True if successful
        """
        try:
            # Delete all keys starting with our prefixes
            patterns = [
                "vehicle:*",
                "ai:analysis:*",
                "embedding:*",
            ]

            for pattern in patterns:
                keys = await self.client.keys(pattern)
                if keys:
                    await self.client.delete(*keys)

            logger.warning("Cleared all feature store cache")
            return True

        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False

    def _convert_decimals(self, obj: Any) -> Any:
        """
        Convert Decimal objects to float for JSON serialization.

        Args:
            obj: Object to convert

        Returns:
            Converted object
        """
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, dict):
            return {k: self._convert_decimals(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_decimals(item) for item in obj]
        return obj

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get cache metrics.

        Returns:
            Metrics dictionary
        """
        total_requests = self.metrics["cache_hits"] + self.metrics["cache_misses"]
        hit_rate = (
            self.metrics["cache_hits"] / total_requests
            if total_requests > 0
            else 0.0
        )

        return {
            **self.metrics,
            "hit_rate": hit_rate,
            "total_requests": total_requests,
        }

    def reset_metrics(self):
        """Reset metrics."""
        self.metrics = {
            "cache_hits": 0,
            "cache_misses": 0,
            "cache_sets": 0,
            "cache_deletes": 0,
        }

    async def close(self):
        """Close Redis connection."""
        if self.client:
            await self.client.close()
