"""External Celery configuration module.

This file can be imported by Celery workers directly or used as a configuration
source for the Celery application. It provides a centralized way to configure
Celery settings that can be overridden via environment variables.

Usage:
    celery -A celeryconfig worker --loglevel=info
    celery -A celeryconfig beat --loglevel=info
"""

import os
from celery.schedules import crontab


broker_url = os.getenv("CELERY_BROKER_URL", os.getenv("REDIS_URL", "redis://localhost:6379/0"))
result_backend = os.getenv("CELERY_RESULT_BACKEND", os.getenv("REDIS_URL", "redis://localhost:6379/0"))

task_serializer = "json"
accept_content = ["json"]
result_serializer = "json"
timezone = "UTC"
enable_utc = True

task_track_started = True
task_time_limit = int(os.getenv("CELERY_TASK_TIME_LIMIT", "300"))
task_soft_time_limit = int(os.getenv("CELERY_TASK_SOFT_TIME_LIMIT", "240"))

worker_prefetch_multiplier = int(os.getenv("CELERY_WORKER_PREFETCH_MULTIPLIER", "4"))
worker_max_tasks_per_child = int(os.getenv("CELERY_WORKER_MAX_TASKS_PER_CHILD", "1000"))
worker_concurrency = int(os.getenv("CELERY_WORKER_CONCURRENCY", "4"))

result_expires = int(os.getenv("CELERY_RESULT_EXPIRES", "3600"))

broker_connection_retry_on_reconnect = True
broker_connection_retry = True
broker_connection_max_retries = int(os.getenv("CELERY_BROKER_MAX_RETRIES", "10"))

task_routes = {
    "app.tasks.nlp_tasks.process_nlp_message": {"queue": "nlp"},
    "app.tasks.nlp_tasks.process_batch_nlp": {"queue": "nlp"},
    "app.tasks.analysis_tasks.analyze_message": {"queue": "heavy"},
    "app.tasks.analysis_tasks.analyze_batch": {"queue": "heavy"},
    "app.tasks.maintenance_tasks.cleanup_old_data": {"queue": "maintenance"},
    "app.tasks.maintenance_tasks.generate_report": {"queue": "maintenance"},
}

task_default_queue = os.getenv("CELERY_DEFAULT_QUEUE", "default")
task_default_exchange = os.getenv("CELERY_DEFAULT_EXCHANGE", "default")
task_default_routing_key = os.getenv("CELERY_DEFAULT_ROUTING_KEY", "default")

beat_schedule = {
    "cleanup-old-data": {
        "task": "app.tasks.maintenance_tasks.cleanup_old_data",
        "schedule": crontab(hour=3, minute=0),
    },
    "health-check": {
        "task": "app.tasks.maintenance_tasks.health_check",
        "schedule": 60.0,
    },
}

imports = (
    "app.tasks.nlp_tasks",
    "app.tasks.analysis_tasks",
    "app.tasks.maintenance_tasks",
)

task_acks_late = os.getenv("CELERY_TASK_ACKS_LATE", "true").lower() == "true"
task_reject_on_worker_lost = os.getenv("CELERY_TASK_REJECT_ON_WORKER_LOST", "true").lower() == "true"

worker_log_level = os.getenv("CELERY_WORKER_LOG_LEVEL", "INFO")
worker_log_format = "%(asctime)s: %(levelname)s [%(process)d] [%(name)s] %(message)s"
worker_task_log_format = "%(asctime)s: %(levelname)s [%(process)d] [%(name)s] [%(task_name)s(%(task_id)s)] %(message)s"

broker_transport_options = {
    "visibility_timeout": 43200,
}

result_extended = True
result_backend_transport_options = {
    "master_name": os.getenv("REDIS_CLUSTER_MASTER", "mymaster"),
}
