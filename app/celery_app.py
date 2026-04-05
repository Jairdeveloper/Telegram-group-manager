"""Celery application configuration."""

import os

try:
    from celery import Celery
    from celery.schedules import crontab
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    Celery = object
    crontab = None


def create_celery_app():
    """Create and configure Celery application."""
    if not CELERY_AVAILABLE:
        raise RuntimeError("Celery is not installed. Install with: pip install celery[redis]")

    from app.config.redis import get_redis_config

    redis_config = get_redis_config()

    app = Celery(
        "robot",
        broker=redis_config.url,
        backend=redis_config.url,
        include=[
            "app.tasks.nlp_tasks",
            "app.tasks.analysis_tasks",
            "app.tasks.maintenance_tasks",
            "app.tasks.db_tasks",
            "app.tasks.task_signatures",
        ],
    )

    app.conf.update(
        broker_connection_retry_on_reconnect=True,
        broker_connection_retry=True,
        broker_connection_max_retries=10,

        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,

        task_track_started=True,
        task_time_limit=300,
        task_soft_time_limit=240,

        worker_prefetch_multiplier=4,
        worker_max_tasks_per_child=1000,

        result_expires=3600,

        task_routes={
            "app.tasks.nlp_tasks.process_nlp_message": {"queue": "nlp"},
            "app.tasks.nlp_tasks.process_batch_nlp": {"queue": "nlp"},
            "app.tasks.nlp_tasks.process_nlp_async": {"queue": "nlp"},
            "app.tasks.nlp_tasks.process_batch_nlp_async": {"queue": "nlp"},
            "app.tasks.analysis_tasks.analyze_message": {"queue": "heavy"},
            "app.tasks.analysis_tasks.analyze_batch": {"queue": "heavy"},
            "app.tasks.analysis_tasks.analyze_message_async": {"queue": "heavy"},
            "app.tasks.analysis_tasks.analyze_batch_async": {"queue": "heavy"},
            "app.tasks.db_tasks.fetch_conversations_async": {"queue": "heavy"},
            "app.tasks.db_tasks.fetch_user_history_async": {"queue": "heavy"},
            "app.tasks.db_tasks.bulk_update_conversations_async": {"queue": "heavy"},
            "app.tasks.db_tasks.aggregate_statistics_async": {"queue": "heavy"},
            "app.tasks.maintenance_tasks.cleanup_old_data": {"queue": "maintenance"},
            "app.tasks.maintenance_tasks.generate_report": {"queue": "maintenance"},
            "app.tasks.maintenance_tasks.cleanup_old_data_async": {"queue": "maintenance"},
            "app.tasks.maintenance_tasks.health_check_async": {"queue": "maintenance"},
        },

        task_default_queue="default",
        task_default_exchange="default",
        task_default_routing_key="default",

        task_annotations={
            "app.tasks.nlp_tasks.process_nlp_async": {"rate_limit": "10/m"},
            "app.tasks.analysis_tasks.analyze_message_async": {"rate_limit": "5/m"},
        },

        worker_consumer_prefetch_multiplier={
            "high": 1,
            "default": 4,
            "low": 8,
        },

        beat_schedule={
            "cleanup-old-data": {
                "task": "app.tasks.maintenance_tasks.cleanup_old_data",
                "schedule": crontab(hour=3, minute=0),
            },
            "health-check": {
                "task": "app.tasks.maintenance_tasks.health_check",
                "schedule": 60.0,
            },
        },

        worker_log_format="%(asctime)s: %(levelname)s [%(process)d] [%(name)s] %(message)s",
        worker_task_log_format="%(asctime)s: %(levelname)s [%(process)d] [%(name)s] [%(task_name)s(%(task_id)s)] %(message)s",

        task_acks_late=True,
        task_reject_on_worker_lost=True,
    )

    return app


_celery_app = None


def get_celery_app():
    """Get or create Celery app singleton."""
    if not CELERY_AVAILABLE:
        raise RuntimeError("Celery is not installed. Install with: pip install celery[redis]")

    global _celery_app
    if _celery_app is None:
        _celery_app = create_celery_app()
    return _celery_app
