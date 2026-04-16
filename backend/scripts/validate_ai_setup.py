#!/usr/bin/env python3
"""
AI Service Validation Script

Validates that all AI service components are properly configured and working.

Usage:
    python scripts/validate_ai_setup.py

Checks:
1. Environment variables
2. API keys validity
3. PostgreSQL pgvector extension
4. Redis connection
5. Database migrations
6. AI service health
7. Embedding service
8. Vector store
9. Feature store
"""
import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ANSI color codes
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"


def print_success(msg: str):
    """Print success message in green."""
    print(f"{Colors.GREEN}✅{Colors.END} {msg}")


def print_error(msg: str):
    """Print error message in red."""
    print(f"{Colors.RED}❌{Colors.END} {msg}")


def print_warning(msg: str):
    """Print warning message in yellow."""
    print(f"{Colors.YELLOW}⚠️  {Colors.END}{msg}")


def print_info(msg: str):
    """Print info message in blue."""
    print(f"{Colors.BLUE}ℹ️  {Colors.END} {msg}")


def print_header(msg: str):
    """Print section header."""
    print(f"\n{Colors.BOLD}{msg}{Colors.END}")
    print("=" * 60)


async def validate_environment() -> bool:
    """Validate environment variables."""
    print_header("1. Environment Variables")

    required_vars = {
        "DATABASE_URL": "PostgreSQL connection string",
        "REDIS_URL": "Redis connection string",
        "ANTHROPIC_API_KEY": "Anthropic API key for Claude",
        "OPENAI_API_KEY": "OpenAI API key for embeddings/fallback",
    }

    optional_vars = {
        "ENABLE_AI_SERVICE": "Enable AI features",
        "ENABLE_CLAUDE_AI": "Enable Claude (primary LLM)",
        "ENABLE_OPENAI_FALLBACK": "Enable OpenAI fallback",
        "ENABLE_VECTOR_SEARCH": "Enable semantic search",
    }

    all_valid = True

    # Check required variables
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Mask API keys in output
            if "API_KEY" in var or "SECRET" in var:
                display = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "****"
            else:
                display = value

            print_success(f"{var}: {display}")
        else:
            print_error(f"{var}: Missing ({description})")
            all_valid = False

    # Check optional variables
    print()
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            print_success(f"{var}: {value}")
        else:
            print_warning(f"{var}: Not set (using default: {description})")

    return all_valid


async def validate_pgvector() -> bool:
    """Validate pgvector extension in PostgreSQL."""
    print_header("2. PostgreSQL pgvector Extension")

    try:
        from sqlalchemy import create_engine, text
        from app.core.config import settings

        # Create sync engine
        db_url = settings.DATABASE_URL.replace("+asyncpg", "")
        engine = create_engine(db_url)

        with engine.connect() as conn:
            # Check if pgvector extension exists
            result = conn.execute(
                text("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
            )
            exists = result.fetchone() is not None

            if exists:
                print_success("pgvector extension is installed")

                # Check pgvector version
                result = conn.execute(
                    text("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
                )
                version = result.fetchone()[0]
                print_info(f"pgvector version: {version}")

                # Check for vector columns
                result = conn.execute(
                    text("""
                        SELECT column_name, data_type
                        FROM information_schema.columns
                        WHERE table_name = 'vehicles'
                        AND column_name LIKE '%embedding%'
                    """)
                )
                columns = result.fetchall()

                if columns:
                    print_success(f"Vector columns found: {len(columns)}")
                    for col_name, col_type in columns:
                        print_info(f"  - {col_name}: {col_type}")
                else:
                    print_warning("No vector columns found - run migrations!")

                return True
            else:
                print_error("pgvector extension NOT installed")
                print_info("Run: CREATE EXTENSION IF NOT EXISTS vector;")
                return False

    except Exception as e:
        print_error(f"Failed to check pgvector: {e}")
        return False


async def validate_redis() -> bool:
    """Validate Redis connection."""
    print_header("3. Redis Connection")

    try:
        import redis
        from app.core.config import settings

        # Try sync connection
        client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        client.ping()

        print_success("Redis connection successful")

        # Get Redis info
        info = client.info("server")
        print_info(f"Redis version: {info.get('redis_version', 'unknown')}")

        # Check memory
        memory_info = client.info("memory")
        used_memory = memory_info.get("used_memory_human", "unknown")
        print_info(f"Memory used: {used_memory}")

        return True

    except Exception as e:
        print_error(f"Redis connection failed: {e}")
        return False


async def validate_api_keys() -> bool:
    """Validate API keys."""
    print_header("4. API Keys Validation")

    all_valid = True

    # Test Anthropic API
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key:
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=anthropic_key)

            # Simple API call
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}]
            )

            print_success("Anthropic API key is valid")

        except Exception as e:
            print_error(f"Anthropic API key validation failed: {e}")
            all_valid = False
    else:
        print_warning("ANTHROPIC_API_KEY not set")

    # Test OpenAI API
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            import openai

            client = openai.OpenAI(api_key=openai_key)

            # Simple API call
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=10
            )

            print_success("OpenAI API key is valid")

        except Exception as e:
            print_error(f"OpenAI API key validation failed: {e}")
            all_valid = False
    else:
        print_warning("OPENAI_API_KEY not set")

    return all_valid


async def validate_database_migrations() -> bool:
    """Validate database migrations."""
    print_header("5. Database Migrations")

    try:
        import alembic.config
        from alembic.script import ScriptDirectory
        from alembic.runtime.migration import MigrationContext
        from sqlalchemy import create_engine

        from app.core.config import settings

        # Create engine
        db_url = settings.DATABASE_URL.replace("+asyncpg", "")
        engine = create_engine(db_url)

        # Get current revision
        with engine.connect() as conn:
            context = MigrationContext.configure(conn)
            current_rev = context.get_current_revision()

        # Get latest revision
        config = alembic.config.Config("alembic.ini")
        script = ScriptDirectory.from_config(config)
        latest_rev = script.get_current_head()

        if current_rev:
            print_success(f"Database migrated to: {current_rev[:10]}...")

            if current_rev == latest_rev:
                print_success("Database is up to date")
                return True
            else:
                print_warning(f"Latest revision: {latest_rev[:10]}...")
                print_info("Run: alembic upgrade head")
                return True  # Not critical
        else:
            print_warning("No migrations applied yet")
            print_info("Run: alembic upgrade head")
            return False

    except Exception as e:
        print_error(f"Failed to check migrations: {e}")
        return False


async def validate_ai_services() -> bool:
    """Validate AI services initialization."""
    print_header("6. AI Services Health")

    try:
        from app.services.ai.orchestrator import AgentOrchestrator
        from app.services.cache.feature_store import FeatureStore
        from app.services.llm.llm_client import LLMClient
        from app.services.vector.embedding_service import EmbeddingService
        from app.services.vector.vector_service import VectorService

        # Initialize services
        print_info("Initializing AI services...")

        llm_client = LLMClient()
        print_success("LLM Client initialized")

        embedding_service = EmbeddingService()
        if embedding_service.client:
            print_success("Embedding Service initialized")
        else:
            print_warning("Embedding Service disabled (no OpenAI key)")

        vector_service = VectorService(embedding_service=embedding_service)
        print_success("Vector Service initialized")

        # Test Redis for feature store
        import redis
        from app.core.config import settings

        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        feature_store = FeatureStore(redis_client=redis_client)
        print_success("Feature Store initialized")

        # Initialize orchestrator
        orchestrator = AgentOrchestrator(
            llm_client=llm_client,
            embedding_service=embedding_service,
            vector_service=vector_service,
            feature_store=feature_store,
        )
        print_success("Agent Orchestrator initialized")

        # Health check
        print_info("Running health check...")
        health = await orchestrator.health_check()

        print()
        for service, status in health.get("services", {}).items():
            if status == "ok":
                print_success(f"{service}: {status}")
            else:
                print_warning(f"{service}: {status}")

        overall_status = health.get("status", "unknown")
        if overall_status == "healthy":
            print_success(f"\nOverall AI Service Status: {overall_status}")
            return True
        else:
            print_warning(f"\nOverall AI Service Status: {overall_status}")
            return True  # Degraded is still OK

    except Exception as e:
        print_error(f"Failed to initialize AI services: {e}")
        import traceback
        traceback.print_exc()
        return False


async def validate_embeddings_exist() -> bool:
    """Check if any vehicles have embeddings."""
    print_header("7. Vehicle Embeddings")

    try:
        from sqlalchemy import create_engine, select, func
        from app.core.config import settings
        from app.models.vehicle import Vehicle

        db_url = settings.DATABASE_URL.replace("+asyncpg", "")
        engine = create_engine(db_url)

        with engine.connect() as conn:
            # Count vehicles
            total_vehicles = conn.execute(
                select(func.count()).select_from(Vehicle)
            ).scalar()

            # Count vehicles with description_embedding
            with_embeddings = conn.execute(
                select(func.count()).select_from(Vehicle).where(
                    Vehicle.description_embedding.isnot(None)
                )
            ).scalar()

            print_info(f"Total vehicles: {total_vehicles}")
            print_info(f"Vehicles with embeddings: {with_embeddings}")

            if total_vehicles > 0:
                percentage = (with_embeddings / total_vehicles) * 100
                print_info(f"Embedding coverage: {percentage:.1f}%")

                if with_embeddings == 0:
                    print_warning("No embeddings found - run population script!")
                    return False
                elif percentage < 50:
                    print_warning("Less than 50% of vehicles have embeddings")
                    return True
                else:
                    print_success("Good embedding coverage")
                    return True
            else:
                print_warning("No vehicles in database")
                return True  # Not critical for validation

    except Exception as e:
        print_error(f"Failed to check embeddings: {e}")
        return False


async def main():
    """Run all validation checks."""
    print(f"\n{Colors.BOLD}AI Service Validation{Colors.END}")
    print("=" * 60)

    results = {}

    # Run all validations
    results["environment"] = await validate_environment()
    results["pgvector"] = await validate_pgvector()
    results["redis"] = await validate_redis()
    results["api_keys"] = await validate_api_keys()
    results["migrations"] = await validate_database_migrations()
    results["ai_services"] = await validate_ai_services()
    results["embeddings"] = await validate_embeddings_exist()

    # Summary
    print_header("Summary")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for check, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        color = Colors.GREEN if result else Colors.RED
        print(f"{color}{status}{Colors.END} {check}")

    print()
    if passed == total:
        print_success(f"All {total} validation checks passed! 🎉")
        print_info("\nAI Service is ready to use!")
        return 0
    else:
        print_warning(f"{passed}/{total} checks passed")
        print_info("\nPlease fix the failed checks above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
