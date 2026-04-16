#!/usr/bin/env python3
"""
Populate embeddings for existing vehicles.

This script generates embeddings for all vehicles that don't have them yet.
It can be run as a one-time setup or as a periodic maintenance task.

Usage:
    # Dry run (show what would be done)
    python scripts/populate_embeddings.py --dry-run

    # Generate embeddings for all vehicles
    python scripts/populate_embeddings.py

    # Generate embeddings for specific vehicle
    python scripts/populate_embeddings.py --vehicle-id <uuid>

    # Batch size control
    python scripts/populate_embeddings.py --batch-size 50
"""
import argparse
import asyncio
import sys
from pathlib import Path
from typing import List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.vehicle import Vehicle
from app.services.ai.orchestrator import AgentOrchestrator
from app.services.llm.llm_client import LLMClient
from app.services.cache.feature_store import FeatureStore
from app.services.vector.embedding_service import EmbeddingService
from app.services.vector.vector_service import VectorService


# ANSI colors
class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"


def print_success(msg: str):
    print(f"{Colors.GREEN}✅{Colors.END} {msg}")


def print_info(msg: str):
    print(f"{Colors.BLUE}ℹ️  {Colors.END} {msg}")


def print_warning(msg: str):
    print(f"{Colors.YELLOW}⚠️  {Colors.END}{msg}")


def get_sync_db():
    """Get synchronous database session."""
    db_url = settings.DATABASE_URL.replace("+asyncpg", "")
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    return SessionLocal()


def prepare_vehicle_data(vehicle: Vehicle) -> dict:
    """Prepare vehicle data for embedding generation."""
    return {
        "id": str(vehicle.id),
        "brand": vehicle.brand,
        "model": vehicle.model,
        "year": vehicle.year,
        "description": vehicle.description or "",
        "title": vehicle.title,
        "features": vehicle.features or {},
        "body_type": vehicle.body_type,
        "transmission": vehicle.transmission,
        "fuel_type": vehicle.fuel_type,
        "version": vehicle.version,
        "color": vehicle.color,
    }


async def populate_vehicle_embeddings(
    orchestrator: AgentOrchestrator,
    vehicle_ids: List[str],
    batch_size: int = 10,
) -> dict:
    """
    Generate embeddings for a list of vehicles.

    Args:
        orchestrator: Agent orchestrator instance
        vehicle_ids: List of vehicle IDs
        batch_size: Number of vehicles to process concurrently

    Returns:
        Dictionary with results
    """
    results = {
        "success": 0,
        "failed": 0,
        "skipped": 0,
        "total": len(vehicle_ids),
    }

    db = get_sync_db()

    try:
        # Process in batches
        for i in range(0, len(vehicle_ids), batch_size):
            batch_ids = vehicle_ids[i : i + batch_size]
            print_info(f"\nProcessing batch {i // batch_size + 1} ({len(batch_ids)} vehicles)...")

            for vehicle_id in batch_ids:
                try:
                    # Get vehicle
                    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()

                    if not vehicle:
                        print_warning(f"Vehicle {vehicle_id} not found")
                        results["failed"] += 1
                        continue

                    # Check if already has embeddings
                    if vehicle.description_embedding and vehicle.features_embedding:
                        print(f"  ⏭️  Skipping {vehicle.brand} {vehicle.model} (already has embeddings)")
                        results["skipped"] += 1
                        continue

                    # Prepare vehicle data
                    vehicle_data = prepare_vehicle_data(vehicle)

                    # Generate embeddings
                    embeddings = await orchestrator.embedding_service.generate_vehicle_embeddings(
                        vehicle=vehicle_data,
                        use_cache=False,  # Don't use cache during population
                    )

                    # Update vehicle
                    vehicle.description_embedding = embeddings.get("description_embedding")
                    vehicle.features_embedding = embeddings.get("features_embedding")

                    db.commit()

                    print(f"  ✅ {vehicle.brand} {vehicle.model} {vehicle.year}")
                    results["success"] += 1

                except Exception as e:
                    print(f"  ❌ Failed to process {vehicle_id}: {e}")
                    results["failed"] += 1
                    db.rollback()

    finally:
        db.close()

    return results


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Populate embeddings for vehicles",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--vehicle-id",
        type=str,
        help="Generate embeddings for specific vehicle ID",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Number of vehicles to process concurrently (default: 10)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of vehicles to process",
    )

    args = parser.parse_args()

    print(f"\n{Colors.BOLD}Vehicle Embedding Population{Colors.END}")
    print("=" * 60)

    # Check if AI service is enabled
    if not settings.ENABLE_AI_SERVICE:
        print_warning("AI service is disabled via ENABLE_AI_SERVICE flag")
        print_info("Set ENABLE_AI_SERVICE=true in .env to enable")
        return 1

    # Initialize services
    print_info("Initializing AI services...")

    try:
        import redis

        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

        llm_client = LLMClient()
        embedding_service = EmbeddingService()
        vector_service = VectorService(embedding_service=embedding_service)
        feature_store = FeatureStore(redis_client=redis_client)

        orchestrator = AgentOrchestrator(
            llm_client=llm_client,
            embedding_service=embedding_service,
            vector_service=vector_service,
            feature_store=feature_store,
        )

        print_success("AI services initialized")

    except Exception as e:
        print_warning(f"Failed to initialize AI services: {e}")
        print_info("Some features may be limited")

    # Get vehicles to process
    db = get_sync_db()

    try:
        if args.vehicle_id:
            # Process specific vehicle
            from uuid import UUID

            try:
                vehicle_id = UUID(args.vehicle_id)
                vehicles_to_process = [vehicle_id]
            except ValueError:
                print_warning(f"Invalid vehicle ID format: {args.vehicle_id}")
                return 1

        else:
            # Get all vehicles without embeddings
            query = db.query(Vehicle).filter(
                Vehicle.description_embedding.is_(None)
            )

            if args.limit:
                query = query.limit(args.limit)

            vehicles = query.all()
            vehicles_to_process = [v.id for v in vehicles]

        if not vehicles_to_process:
            print_success("\nAll vehicles already have embeddings!")
            return 0

        print_info(f"Found {len(vehicles_to_process)} vehicles to process")

        if args.dry_run:
            print("\n{Colors.BOLD}Dry run - vehicles to be processed:{Colors.END}")
            for vid in vehicles_to_process[:10]:  # Show first 10
                vehicle = db.query(Vehicle).filter(Vehicle.id == vid).first()
                if vehicle:
                    print(f"  - {vehicle.brand} {vehicle.model} {vehicle.year}")

            if len(vehicles_to_process) > 10:
                print(f"  ... and {len(vehicles_to_process) - 10} more")

            print_info(f"\nTotal: {len(vehicles_to_process)} vehicles")
            return 0

        # Process vehicles
        print(f"\n{Colors.BOLD}Generating embeddings...{Colors.END}")
        print("=" * 60)

        results = await populate_vehicle_embeddings(
            orchestrator=orchestrator,
            vehicle_ids=vehicles_to_process,
            batch_size=args.batch_size,
        )

        # Print summary
        print(f"\n{Colors.BOLD}Summary{Colors.END}")
        print("=" * 60)
        print_success(f"Successfully processed: {results['success']}")
        print_warning(f"Skipped (already had embeddings): {results['skipped']}")
        print(f"❌ Failed: {results['failed']}")
        print(f"📊 Total: {results['total']}")

        if results["success"] > 0:
            print_success("\n✨ Embedding population completed!")
        elif results["failed"] > 0:
            print_warning("\nSome vehicles failed to process. Check logs above.")
            return 1

        return 0

    except Exception as e:
        print_warning(f"\nError: {e}")
        import traceback

        traceback.print_exc()
        return 1

    finally:
        db.close()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
