"""
Embedding service for generating and managing text embeddings.

Uses OpenAI text-embedding-3-small model (1536 dimensions).
Cost: $0.00002/1K tokens - highly economical.
"""
import asyncio
import logging
from typing import Any, Dict, List, Optional

import openai
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service for generating and managing text embeddings.

    Features:
    - OpenAI text-embedding-3-small model
    - Batch embedding support
    - Redis caching for performance
    - Async operations
    - Cost optimization

    Model Details:
    - Dimensions: 1536
    - Cost: $0.00002/1K tokens
    - Performance: Excellent for semantic search
    """

    EMBEDDING_MODEL = "text-embedding-3-small"
    EMBEDDING_DIMENSIONS = 1536
    MAX_BATCH_SIZE = 100

    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        cache_client: Optional[Any] = None,
    ):
        """
        Initialize embedding service.

        Args:
            openai_api_key: OpenAI API key (defaults to settings)
            cache_client: Redis client for caching (optional)
        """
        self.api_key = openai_api_key or settings.OPENAI_API_KEY
        self.cache_client = cache_client

        if not self.api_key:
            logger.warning("OpenAI API key not configured - embedding service disabled")
            self.client = None
        else:
            self.client = AsyncOpenAI(api_key=self.api_key)

        # Metrics
        self.metrics = {
            "embeddings_generated": 0,
            "tokens_used": 0,
            "total_cost": 0.0,
            "cache_hits": 0,
            "cache_misses": 0,
        }

    async def generate_embedding(
        self,
        text: str,
        use_cache: bool = True,
    ) -> Optional[List[float]]:
        """
        Generate embedding for a single text.

        Args:
            text: Input text
            use_cache: Whether to use cache

        Returns:
            Embedding vector (1536 dimensions) or None if failed
        """
        if not self.client:
            logger.error("OpenAI client not initialized")
            return None

        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return None

        # Check cache
        if use_cache and self.cache_client:
            cache_key = f"embedding:text:{hash(text)}"
            cached = await self._get_from_cache(cache_key)
            if cached:
                self.metrics["cache_hits"] += 1
                return cached
            self.metrics["cache_misses"] += 1

        try:
            # Generate embedding
            response = await self.client.embeddings.create(
                model=self.EMBEDDING_MODEL,
                input=text,
            )

            embedding = response.data[0].embedding

            # Update metrics
            self.metrics["embeddings_generated"] += 1
            self.metrics["tokens_used"] += response.usage.total_tokens
            cost = (response.usage.total_tokens / 1000) * 0.00002
            self.metrics["total_cost"] += cost

            # Cache result
            if use_cache and self.cache_client:
                await self._save_to_cache(cache_key, embedding)

            return embedding

        except openai.APIError as e:
            logger.error(f"OpenAI API error generating embedding: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error generating embedding: {e}")
            return None

    async def generate_vehicle_embeddings(
        self,
        vehicle: Dict[str, Any],
        use_cache: bool = True,
    ) -> Dict[str, Optional[List[float]]]:
        """
        Generate embeddings for a vehicle.

        Args:
            vehicle: Vehicle data dictionary
            use_cache: Whether to use cache

        Returns:
            Dictionary with description_embedding and features_embedding
        """
        # Generate description text
        description_text = self._create_description_text(vehicle)

        # Generate features text
        features_text = self._create_features_text(vehicle)

        # Generate embeddings in parallel
        description_embedding, features_embedding = await asyncio.gather(
            self.generate_embedding(description_text, use_cache),
            self.generate_embedding(features_text, use_cache),
        )

        return {
            "description_embedding": description_embedding,
            "features_embedding": features_embedding,
        }

    async def batch_generate_embeddings(
        self,
        texts: List[str],
        use_cache: bool = True,
    ) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts in batches.

        Args:
            texts: List of input texts
            use_cache: Whether to use cache

        Returns:
            List of embedding vectors
        """
        if not self.client:
            logger.error("OpenAI client not initialized")
            return [None] * len(texts)

        # Filter out empty texts
        valid_indices = [i for i, text in enumerate(texts) if text and text.strip()]
        valid_texts = [texts[i] for i in valid_indices]

        if not valid_texts:
            return [None] * len(texts)

        results = [None] * len(texts)

        # Process in batches
        for i in range(0, len(valid_texts), self.MAX_BATCH_SIZE):
            batch_texts = valid_texts[i : i + self.MAX_BATCH_SIZE]
            batch_indices = valid_indices[i : i + self.MAX_BATCH_SIZE]

            # Check cache first
            uncached_texts = []
            uncached_indices = []

            for j, text in enumerate(batch_texts):
                original_index = batch_indices[j]

                if use_cache and self.cache_client:
                    cache_key = f"embedding:text:{hash(text)}"
                    cached = await self._get_from_cache(cache_key)
                    if cached:
                        results[original_index] = cached
                        self.metrics["cache_hits"] += 1
                        continue

                uncached_texts.append(text)
                uncached_indices.append(original_index)
                self.metrics["cache_misses"] += 1

            # Generate embeddings for uncached texts
            if uncached_texts:
                try:
                    response = await self.client.embeddings.create(
                        model=self.EMBEDDING_MODEL,
                        input=uncached_texts,
                    )

                    for j, embedding_data in enumerate(response.data):
                        original_index = uncached_indices[j]
                        embedding = embedding_data.embedding
                        results[original_index] = embedding

                        # Cache result
                        if use_cache and self.cache_client:
                            cache_key = f"embedding:text:{hash(uncached_texts[j])}"
                            await self._save_to_cache(cache_key, embedding)

                    # Update metrics
                    self.metrics["embeddings_generated"] += len(uncached_texts)
                    self.metrics["tokens_used"] += response.usage.total_tokens
                    cost = (response.usage.total_tokens / 1000) * 0.00002
                    self.metrics["total_cost"] += cost

                except openai.APIError as e:
                    logger.error(f"OpenAI API error in batch embedding: {e}")
                    for idx in uncached_indices:
                        results[idx] = None
                except Exception as e:
                    logger.error(f"Unexpected error in batch embedding: {e}")
                    for idx in uncached_indices:
                        results[idx] = None

        return results

    async def batch_generate_vehicle_embeddings(
        self,
        vehicles: List[Dict[str, Any]],
        db: Optional[AsyncSession] = None,
        use_cache: bool = True,
    ) -> Dict[str, Dict[str, Optional[List[float]]]]:
        """
        Generate embeddings for multiple vehicles.

        Args:
            vehicles: List of vehicle data dictionaries
            db: Database session (optional, for updating vehicles)
            use_cache: Whether to use cache

        Returns:
            Dictionary mapping vehicle_id to embeddings
        """
        results = {}

        for vehicle in vehicles:
            vehicle_id = vehicle.get("id")
            if not vehicle_id:
                continue

            embeddings = await self.generate_vehicle_embeddings(vehicle, use_cache)
            results[vehicle_id] = embeddings

        return results

    def _create_description_text(self, vehicle: Dict[str, Any]) -> str:
        """
        Create text for description embedding.

        Args:
            vehicle: Vehicle data

        Returns:
            Formatted text
        """
        parts = [
            f"{vehicle.get('brand', '')} {vehicle.get('model', '')}",
            f"Ano {vehicle.get('year', '')}",
        ]

        if vehicle.get("version"):
            parts.append(vehicle["version"])

        if vehicle.get("description"):
            parts.append(vehicle["description"])

        return " ".join(parts)

    def _create_features_text(self, vehicle: Dict[str, Any]) -> str:
        """
        Create text for features embedding.

        Args:
            vehicle: Vehicle data

        Returns:
            Formatted text
        """
        parts = []

        features = vehicle.get("features", {})
        if features:
            for category, items in features.items():
                if isinstance(items, list):
                    parts.extend(items)

        # Add other attributes
        if vehicle.get("body_type"):
            parts.append(vehicle["body_type"])

        if vehicle.get("transmission"):
            parts.append(vehicle["transmission"])

        if vehicle.get("fuel_type"):
            parts.append(vehicle["fuel_type"])

        return " ".join(parts)

    async def _get_from_cache(self, key: str) -> Optional[List[float]]:
        """Get embedding from Redis cache."""
        if not self.cache_client:
            return None

        try:
            import json

            cached = await self.cache_client.get(key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Error reading from cache: {e}")

        return None

    async def _save_to_cache(self, key: str, embedding: List[float], ttl: int = 86400):
        """
        Save embedding to Redis cache.

        Args:
            key: Cache key
            embedding: Embedding vector
            ttl: Time to live in seconds (default 24h)
        """
        if not self.cache_client:
            return

        try:
            import json

            await self.cache_client.set(key, json.dumps(embedding), ex=ttl)
        except Exception as e:
            logger.warning(f"Error writing to cache: {e}")

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get service metrics.

        Returns:
            Metrics dictionary
        """
        cache_hit_rate = (
            self.metrics["cache_hits"]
            / (self.metrics["cache_hits"] + self.metrics["cache_misses"])
            if (self.metrics["cache_hits"] + self.metrics["cache_misses"]) > 0
            else 0.0
        )

        return {
            **self.metrics,
            "cache_hit_rate": cache_hit_rate,
            "avg_cost_per_embedding": (
                self.metrics["total_cost"] / self.metrics["embeddings_generated"]
                if self.metrics["embeddings_generated"] > 0
                else 0.0
            ),
        }

    def reset_metrics(self):
        """Reset metrics."""
        self.metrics = {
            "embeddings_generated": 0,
            "tokens_used": 0,
            "total_cost": 0.0,
            "cache_hits": 0,
            "cache_misses": 0,
        }
