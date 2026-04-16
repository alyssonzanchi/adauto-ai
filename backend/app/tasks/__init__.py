"""
Celery tasks for async AI operations.
"""
from app.tasks.celery_app import celery_app
from app.tasks.ai_tasks import (
    generate_vehicle_embeddings,
    analyze_vehicle_async,
    warm_vehicle_cache,
)

__all__ = [
    "celery_app",
    "generate_vehicle_embeddings",
    "analyze_vehicle_async",
    "warm_vehicle_cache",
]
