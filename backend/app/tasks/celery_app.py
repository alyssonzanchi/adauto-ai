"""
Celery application configuration.
"""
import logging
from celery import Celery

from app.core.config import settings

logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    "car_ads_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.ai_tasks"],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Task routing
celery_app.conf.task_routes = {
    "app.tasks.ai_tasks.generate_vehicle_embeddings": {"queue": "ai_tasks"},
    "app.tasks.ai_tasks.analyze_vehicle_async": {"queue": "ai_tasks"},
    "app.tasks.ai_tasks.warm_vehicle_cache": {"queue": "cache_tasks"},
}

logger.info("Celery app configured")
