"""Queue monitoring and status endpoints."""

import time
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

from app.config.redis import get_redis_connection


logger = logging.getLogger(__name__)


@dataclass
class QueueStatus:
    """Status of a queue."""
    name: str
    pending: int = 0
    active: int = 0
    completed: int = 0
    failed: int = 0
    consumers: int = 0


@dataclass
class QueueCongestionAlert:
    """Alert for queue congestion."""
    queue_name: str
    severity: str  # "low", "medium", "high", "critical"
    message: str
    pending_tasks: int
    timestamp: str


class QueueMonitor:
    """Monitor for queue status and congestion."""
    
    def __init__(self):
        self.redis = get_redis_connection()
        self.congestion_thresholds = {
            "high": {"pending": 100, "active": 50},
            "normal": {"pending": 50, "active": 25},
            "low": {"pending": 10, "active": 5},
        }
    
    def get_queue_status(self, queue_name: str) -> QueueStatus:
        """Get status of a specific queue."""
        try:
            from app.celery_app import get_celery_app
            
            celery_app = get_celery_app()
            inspect = celery_app.control.inspect()
            
            stats = inspect.stats()
            
            pending = 0
            active = 0
            
            if stats:
                for worker, worker_stats in stats.items():
                    queue_stats = worker_stats.get("celery", {}).get(queue_name, {})
                    pending += queue_stats.get("pending", 0)
                    active += queue_stats.get("active", 0)
            
            return QueueStatus(
                name=queue_name,
                pending=pending,
                active=active,
            )
        except Exception as e:
            logger.error(f"Failed to get queue status: {e}")
            return QueueStatus(name=queue_name)
    
    def get_all_queue_status(self) -> List[QueueStatus]:
        """Get status of all queues."""
        queues = ["high", "default", "low", "nlp", "heavy", "maintenance"]
        return [self.get_queue_status(q) for q in queues]
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get rate limit status from Redis."""
        try:
            pattern = "rate_limit:*"
            cursor = 0
            rate_limit_keys = []
            
            while True:
                cursor, keys = self.redis.scan(cursor=cursor, match=pattern, count=100)
                rate_limit_keys.extend(keys)
                if cursor == 0:
                    break
            
            return {
                "total_limits": len(rate_limit_keys),
                "active_limits": len(rate_limit_keys),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to get rate limit status: {e}")
            return {"error": str(e)}
    
    def check_congestion(self, queue_status: QueueStatus) -> Optional[QueueCongestionAlert]:
        """Check if queue is congested."""
        pending = queue_status.pending
        active = queue_status.active
        
        if pending > self.congestion_thresholds["high"]["pending"]:
            return QueueCongestionAlert(
                queue_name=queue_status.name,
                severity="critical",
                message=f"Queue {queue_status.name} is critically congested",
                pending_tasks=pending,
                timestamp=datetime.now().isoformat(),
            )
        
        if pending > self.congestion_thresholds["normal"]["pending"]:
            return QueueCongestionAlert(
                queue_name=queue_status.name,
                severity="high",
                message=f"Queue {queue_status.name} is heavily congested",
                pending_tasks=pending,
                timestamp=datetime.now().isoformat(),
            )
        
        if pending > self.congestion_thresholds["low"]["pending"]:
            return QueueCongestionAlert(
                queue_name=queue_status.name,
                severity="medium",
                message=f"Queue {queue_status.name} is moderately congested",
                pending_tasks=pending,
                timestamp=datetime.now().isoformat(),
            )
        
        return None
    
    def get_congestion_alerts(self) -> List[QueueCongestionAlert]:
        """Get all congestion alerts."""
        alerts = []
        for queue_status in self.get_all_queue_status():
            alert = self.check_congestion(queue_status)
            if alert:
                alerts.append(alert)
        return alerts
    
    def get_full_status(self) -> Dict[str, Any]:
        """Get full queue system status."""
        return {
            "queues": [
                {
                    "name": qs.name,
                    "pending": qs.pending,
                    "active": qs.active,
                }
                for qs in self.get_all_queue_status()
            ],
            "rate_limits": self.get_rate_limit_status(),
            "congestion_alerts": [
                {
                    "queue_name": alert.queue_name,
                    "severity": alert.severity,
                    "message": alert.message,
                    "pending_tasks": alert.pending_tasks,
                }
                for alert in self.get_congestion_alerts()
            ],
            "timestamp": datetime.now().isoformat(),
        }


_queue_monitor = None


def get_queue_monitor() -> QueueMonitor:
    """Get or create queue monitor singleton."""
    global _queue_monitor
    if _queue_monitor is None:
        _queue_monitor = QueueMonitor()
    return _queue_monitor
