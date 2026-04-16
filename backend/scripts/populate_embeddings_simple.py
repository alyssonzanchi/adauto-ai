#!/usr/bin/env python3
"""
Populate embeddings for existing vehicles (simplified version).

Uses raw SQL to avoid pgvector type issues.
"""
import asyncio
import sys
from pathlib import Path
from typing import List
from uuid import UUID

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
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


def get_vehicles_without_embeddings(db, limit: int = None):
    """Get vehicles that don't have embeddings using raw SQL."""
    query = text("""
        SELECT id, title, brand, model, year, description,
               mileage, body_type, transmission, fuel_type,
               features, version, color, price
        FROM vehicles
        WHERE deleted_at IS NULL
        AND (description_embedding IS NULL OR features_embedding IS NULL)
        ORDER BY created_at DESC
    """)

    if limit:
        query = text(query.text + f" LIMIT {limit}")

    result = db.execute(query)
    vehicles = result.fetchall()

    return [
        {
            "id": str(row[0]),
            "title": row[1],
            "brand": row[2],
            "model": row[3],
            "year": row[4],
            "description": row[5],
            "mileage": row[6],
            "body_type": row[7],
            "transmission": row[8],
            "fuel_type": row[9],
            "features": row[10],
            "version": row[11],
            "color": row[12],
            "price": float(row[13]) if row[13] else 0.0,
        }
        for row in vehicles
    ]


def update_vehicle_embeddings(db, vehicle_id: str, description_emb: list, features_emb: list):
    """Update vehicle embeddings using raw SQL."""
    query = text("""
        UPDATE vehicles
        SET description_embedding = :desc_emb,
            features_embedding = :feat_emb
        WHERE id = :vehicle_id
    """)

    # Convert lists to PostgreSQL array format
    desc_array = "{" + ",".join(map(str, description_emb)) + "}"
    feat_array = "{" + ",".join(map(str, features_emb)) + "}"

    db.execute(query, {
        "desc_emb": desc_array,
        "feat_emb": feat_array,
        "vehicle_id": vehicle_id,
    })
    db.commit()


async def populate_vehicle_embeddings(
    orchestrator: AgentOrchestrator,
    vehicles: List[dict],
) -> dict:
    """
    Generate embeddings for vehicles.

    Args:
        orchestrator: Agent orchestrator instance
        vehicles: List of vehicle data dictionaries

    Returns:
        Dictionary with results
    """
    results = {
        "success": 0,
        "failed": 0,
        "skipped": 0,
        "total": len(vehicles),
    }

    db = get_sync_db()

    try:
        print_info(f"\nProcessing {len(vehicles)} vehicles...")

        for i, vehicle in enumerate(vehicles, 1):
            vehicle_id = vehicle["id"]

            try:
                print(f"\n[{i}/{len(vehicles)}] Processing: {vehicle['brand']} {vehicle['model']} {vehicle['year']}")

                # Generate embeddings
                embeddings = await orchestrator.embedding_service.generate_vehicle_embeddings(
                    vehicle=vehicle,
                    use_cache=False,  # Don't use cache during population
                )

                # Check if embeddings were generated
                if not embeddings.get("description_embedding") or not embeddings.get("features_embedding"):
                    print_warning(f"  ⚠️  Failed to generate embeddings - OpenAI required")
                    results["failed"] += 1
                    continue

                # Update vehicle in database
                update_vehicle_embeddings(
                    db,
                    vehicle_id,
                    embeddings["description_embedding"],
                    embeddings["features_embedding"],
                )

                print_success(f"  ✅ Embeddings generated and saved")
                results["success"] += 1

            except Exception as e:
                print_warning(f"  ❌ Failed: {e}")
                results["failed"] += 1

    finally:
        db.close()

    return results


async def main():
    """Main entry point."""
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
        return 1

    # Get vehicles to process
    db = get_sync_db()

    try:
        vehicles = get_vehicles_without_embeddings(db)

        if not vehicles:
            print_success("\nAll vehicles already have embeddings!")
            return 0

        print_info(f"Found {len(vehicles)} vehicles without embeddings")

        # Show vehicles to be processed
        print(f"\n{Colors.BOLD}Vehicles to process:{Colors.END}")
        for v in vehicles[:5]:  # Show first 5
            print(f"  - {v['brand']} {v['model']} {v['year']} ({v['title']})")

        if len(vehicles) > 5:
            print(f"  ... and {len(vehicles) - 5} more")

        # Process vehicles
        print(f"\n{Colors.BOLD}Generating embeddings...{Colors.END}")
        print("=" * 60)

        results = await populate_vehicle_embeddings(
            orchestrator=orchestrator,
            vehicles=vehicles,
        )

        # Print summary
        print(f"\n{Colors.BOLD}Summary{Colors.END}")
        print("=" * 60)
        print_success(f"Successfully processed: {results['success']}")
        print_warning(f"Skipped: {results['skipped']}")
        print(f"❌ Failed: {results['failed']}")
        print(f"📊 Total: {results['total']}")

        if results["success"] > 0:
            print_success("\n✨ Embedding population completed!")
        elif results["failed"] > 0:
            print_warning("\nSome vehicles failed to process.")
            print_info("Note: Embeddings require OpenAI API key with available quota")
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
