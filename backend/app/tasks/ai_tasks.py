"""
Celery tasks for AI operations.

These tasks run asynchronously in the background:
- Generate embeddings for vehicles
- Perform AI analysis
- Warm cache for better performance
"""
import logging
from uuid import UUID

from celery import shared_task
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.database import get_db
from app.models.vehicle import Vehicle
from app.services.ai.orchestrator import AgentOrchestrator

logger = logging.getLogger(__name__)


def get_sync_db():
    """
    Get synchronous database session for Celery tasks.

    Celery doesn't support async natively, so we use sync sessions.
    """
    engine = create_engine(settings.DATABASE_URL.replace("+asyncpg", ""))
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    return SessionLocal()


@shared_task(bind=True, max_retries=3)
def generate_vehicle_embeddings(self, vehicle_id: str):
    """
    Generate embeddings for a vehicle.

    This task:
    1. Retrieves vehicle from database
    2. Generates description and features embeddings
    3. Updates vehicle with embeddings
    4. Caches embeddings in Redis

    Args:
        vehicle_id: Vehicle UUID as string

    Returns:
        True if successful
    """
    try:
        from app.services.ai.orchestrator import get_orchestrator

        db = get_sync_db()

        try:
            # Get vehicle
            vehicle = db.query(Vehicle).filter(Vehicle.id == UUID(vehicle_id)).first()

            if not vehicle:
                logger.warning(f"Vehicle {vehicle_id} not found for embedding generation")
                return False

            # Prepare vehicle data
            vehicle_data = {
                "id": str(vehicle.id),
                "brand": vehicle.brand,
                "model": vehicle.model,
                "year": vehicle.year,
                "description": vehicle.description,
                "title": vehicle.title,
                "features": vehicle.features or {},
                "body_type": vehicle.body_type,
                "transmission": vehicle.transmission,
                "fuel_type": vehicle.fuel_type,
            }

            # Get orchestrator and generate embeddings
            orchestrator = get_orchestrator()
            embeddings = await orchestrator.embedding_service.generate_vehicle_embeddings(
                vehicle=vehicle_data,
                use_cache=True,
            )

            # Update vehicle
            vehicle.description_embedding = embeddings.get("description_embedding")
            vehicle.features_embedding = embeddings.get("features_embedding")

            db.commit()

            logger.info(f"Embeddings generated for vehicle {vehicle_id}")

            return True

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Failed to generate embeddings for vehicle {vehicle_id}: {e}")

        # Retry with exponential backoff
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=2 ** self.request.retries * 60)

        return False


@shared_task(bind=True, max_retries=3)
def analyze_vehicle_async(self, vehicle_id: str):
    """
    Perform AI analysis on a vehicle asynchronously.

    This task:
    1. Retrieves vehicle from database
    2. Performs comprehensive AI analysis
    3. Updates vehicle with analysis results
    4. Caches analysis in Redis

    Args:
        vehicle_id: Vehicle UUID as string

    Returns:
        True if successful
    """
    try:
        from app.services.ai.orchestrator import get_orchestrator

        db = get_sync_db()

        try:
            # Get vehicle
            vehicle = db.query(Vehicle).filter(Vehicle.id == UUID(vehicle_id)).first()

            if not vehicle:
                logger.warning(f"Vehicle {vehicle_id} not found for AI analysis")
                return False

            # Prepare vehicle data
            vehicle_data = {
                "id": str(vehicle.id),
                "price": float(vehicle.price),
                "year": vehicle.year,
                "mileage": vehicle.mileage or 0,
                "brand": vehicle.brand,
                "model": vehicle.model,
                "body_type": vehicle.body_type,
                "fuel_type": vehicle.fuel_type,
                "features": vehicle.features or {},
                "ownership": vehicle.ownership,
                "description": vehicle.description,
                "title": vehicle.title,
            }

            # Get orchestrator and analyze
            orchestrator = get_orchestrator()
            analysis = await orchestrator.analyze_vehicle(
                vehicle_data=vehicle_data,
                db=db,  # Note: passing sync session, orchestrator should handle
                use_cache=True,
            )

            # Update vehicle
            vehicle.price_market = analysis.get("price_market")
            vehicle.price_score = analysis.get("price_score")
            vehicle.price_position = analysis.get("price_position")
            vehicle.ai_analysis = analysis

            db.commit()

            logger.info(f"AI analysis completed for vehicle {vehicle_id}")

            return True

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Failed to analyze vehicle {vehicle_id}: {e}")

        # Retry with exponential backoff
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=2 ** self.request.retries * 60)

        return False


@shared_task(bind=True, max_retries=2)
def warm_vehicle_cache(self, vehicle_id: str):
    """
    Warm cache for a vehicle.

    This task:
    1. Retrieves vehicle from database
    2. Generates embeddings (if not present)
    3. Performs AI analysis (if not present)
    4. Caches all data in Redis

    Args:
        vehicle_id: Vehicle UUID as string

    Returns:
        True if successful
    """
    try:
        from app.services.ai.orchestrator import get_orchestrator

        db = get_sync_db()

        try:
            # Get vehicle
            vehicle = db.query(Vehicle).filter(Vehicle.id == UUID(vehicle_id)).first()

            if not vehicle:
                logger.warning(f"Vehicle {vehicle_id} not found for cache warming")
                return False

            # Prepare vehicle data
            vehicle_data = {
                "id": str(vehicle.id),
                "price": float(vehicle.price),
                "year": vehicle.year,
                "mileage": vehicle.mileage or 0,
                "brand": vehicle.brand,
                "model": vehicle.model,
                "body_type": vehicle.body_type,
                "fuel_type": vehicle.fuel_type,
                "features": vehicle.features or {},
                "ownership": vehicle.ownership,
                "description": vehicle.description,
                "title": vehicle.title,
                "version": vehicle.version,
                "color": vehicle.color,
            }

            # Get orchestrator
            orchestrator = get_orchestrator()

            # Generate embeddings if needed
            if not vehicle.description_embedding or not vehicle.features_embedding:
                embeddings = await orchestrator.generate_vehicle_embeddings(
                    vehicle_data=vehicle_data,
                    db=db,
                    use_cache=True,
                )

                # Update vehicle
                vehicle.description_embedding = embeddings.get("description_embedding")
                vehicle.features_embedding = embeddings.get("features_embedding")
                db.commit()

            # Perform analysis if needed
            if not vehicle.ai_analysis:
                analysis = await orchestrator.analyze_vehicle(
                    vehicle_data=vehicle_data,
                    db=db,
                    use_cache=True,
                )

                # Update vehicle
                vehicle.price_market = analysis.get("price_market")
                vehicle.price_score = analysis.get("price_score")
                vehicle.price_position = analysis.get("price_position")
                vehicle.ai_analysis = analysis
                db.commit()

            # Warm cache with all data
            await orchestrator.feature_store.warm_cache(
                vehicle_id=str(vehicle.id),
                vehicle_data=vehicle_data,
                embeddings={
                    "description_embedding": vehicle.description_embedding,
                    "features_embedding": vehicle.features_embedding,
                },
                analysis=vehicle.ai_analysis or {},
            )

            logger.info(f"Cache warmed for vehicle {vehicle_id}")

            return True

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Failed to warm cache for vehicle {vehicle_id}: {e}")

        # Retry with exponential backoff
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=2 ** self.request.retries * 60)

        return False


@shared_task
def batch_generate_embeddings(vehicle_ids: list[str]):
    """
    Generate embeddings for multiple vehicles in batch.

    Args:
        vehicle_ids: List of vehicle UUIDs as strings

    Returns:
        Dictionary with results
    """
    results = {
        "success": 0,
        "failed": 0,
        "total": len(vehicle_ids),
    }

    for vehicle_id in vehicle_ids:
        try:
            success = generate_vehicle_embeddings(vehicle_id)
            if success:
                results["success"] += 1
            else:
                results["failed"] += 1
        except Exception as e:
            logger.error(f"Failed to generate embeddings for {vehicle_id}: {e}")
            results["failed"] += 1

    logger.info(f"Batch embedding generation completed: {results}")

    return results


@shared_task
def batch_analyze_vehicles(vehicle_ids: list[str]):
    """
    Analyze multiple vehicles in batch.

    Args:
        vehicle_ids: List of vehicle UUIDs as strings

    Returns:
        Dictionary with results
    """
    results = {
        "success": 0,
        "failed": 0,
        "total": len(vehicle_ids),
    }

    for vehicle_id in vehicle_ids:
        try:
            success = analyze_vehicle_async(vehicle_id)
            if success:
                results["success"] += 1
            else:
                results["failed"] += 1
        except Exception as e:
            logger.error(f"Failed to analyze vehicle {vehicle_id}: {e}")
            results["failed"] += 1

    logger.info(f"Batch vehicle analysis completed: {results}")

    return results
