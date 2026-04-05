"""Maintenance tasks for Celery workers."""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any
from celery import Task

from app.celery_app import get_celery_app


logger = logging.getLogger(__name__)


class MaintenanceTask(Task):
    """Base class for maintenance tasks."""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure."""
        logger.error(f"Maintenance task failed: {exc}")
        return super().on_failure(exc, task_id, args, kwargs, einfo)


def cleanup_old_data(days: int = 7) -> Dict[str, Any]:
    """Clean up old data from Redis/DB."""
    try:
        from app.config.redis import get_redis_connection
        
        redis_conn = get_redis_connection()
        
        keys_deleted = 0
        cutoff = datetime.now() - timedelta(days=days)
        
        cursor = 0
        while True:
            cursor, keys = redis_conn.scan(cursor=cursor, match="*:temp:*", count=100)
            for key in keys:
                ttl = redis_conn.ttl(key)
                if ttl == -1:
                    redis_conn.delete(key)
                    keys_deleted += 1
            
            if cursor == 0:
                break
        
        return {
            "status": "ok",
            "keys_deleted": keys_deleted,
            "cutoff_date": cutoff.isoformat(),
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def health_check() -> Dict[str, Any]:
    """Perform health check on system components."""
    try:
        from app.config.redis import get_redis_connection
        
        redis_conn = get_redis_connection()
        redis_ok = redis_conn.ping()
        
        return {
            "status": "ok" if redis_ok else "degraded",
            "components": {
                "redis": "ok" if redis_ok else "error",
            },
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


celery_app = get_celery_app()


@celery_app.task(
    bind=True,
    base=MaintenanceTask,
    name="app.tasks.maintenance_tasks.cleanup_old_data",
    queue="maintenance",
    schedule=3600.0,
)
def cleanup_old_data_async(self, days: int = 7) -> Dict[str, Any]:
    """Async wrapper for cleanup task."""
    return cleanup_old_data(days)


@celery_app.task(
    bind=True,
    base=MaintenanceTask,
    name="app.tasks.maintenance_tasks.health_check",
    queue="maintenance",
    schedule=60.0,
)
def health_check_async(self) -> Dict[str, Any]:
    """Async wrapper for health check."""
    return health_check()
