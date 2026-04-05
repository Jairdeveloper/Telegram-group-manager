"""Database tasks for heavy database operations."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from celery import Task

from app.celery_app import get_celery_app


logger = logging.getLogger(__name__)


class DatabaseTask(Task):
    """Base class for database tasks with error handling."""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure."""
        logger.error(f"Database task failed: {exc}")
        return super().on_failure(exc, task_id, args, kwargs, einfo)


def fetch_conversations(chat_id: int, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
    """Fetch conversations for a chat with pagination."""
    try:
        from app.enterprise.infrastructure.repositories import ConversationRepository
        
        repo = ConversationRepository()
        conversations = repo.get_by_chat_id(chat_id, limit=limit, offset=offset)
        
        return {
            "status": "ok",
            "chat_id": chat_id,
            "conversations": [
                {
                    "id": c.id,
                    "user_id": c.user_id,
                    "text": c.text[:100],  # Truncate for result
                    "timestamp": c.timestamp.isoformat() if c.timestamp else None,
                }
                for c in conversations
            ],
            "count": len(conversations),
            "limit": limit,
            "offset": offset,
        }
    except Exception as e:
        logger.error(f"Failed to fetch conversations: {e}")
        return {"status": "error", "error": str(e)}


def fetch_user_history(user_id: int, days: int = 30) -> Dict[str, Any]:
    """Fetch user message history for analysis."""
    try:
        from app.enterprise.infrastructure.repositories import MessageRepository
        
        repo = MessageRepository()
        cutoff = datetime.now() - timedelta(days=days)
        
        messages = repo.get_by_user_id(user_id, since=cutoff)
        
        return {
            "status": "ok",
            "user_id": user_id,
            "message_count": len(messages),
            "days": days,
            "cutoff": cutoff.isoformat(),
        }
    except Exception as e:
        logger.error(f"Failed to fetch user history: {e}")
        return {"status": "error", "error": str(e)}


def bulk_update_conversations(conversation_ids: List[int], updates: Dict[str, Any]) -> Dict[str, Any]:
    """Bulk update conversations."""
    try:
        from app.enterprise.infrastructure.repositories import ConversationRepository
        
        repo = ConversationRepository()
        updated = 0
        
        for conv_id in conversation_ids:
            try:
                repo.update(conv_id, updates)
                updated += 1
            except Exception as e:
                logger.warning(f"Failed to update conversation {conv_id}: {e}")
        
        return {
            "status": "ok",
            "requested": len(conversation_ids),
            "updated": updated,
            "failed": len(conversation_ids) - updated,
        }
    except Exception as e:
        logger.error(f"Failed to bulk update: {e}")
        return {"status": "error", "error": str(e)}


def aggregate_statistics(chat_id: int, days: int = 7) -> Dict[str, Any]:
    """Aggregate statistics for a chat."""
    try:
        from app.enterprise.infrastructure.repositories import MessageRepository, ConversationRepository
        
        msg_repo = MessageRepository()
        conv_repo = ConversationRepository()
        
        cutoff = datetime.now() - timedelta(days=days)
        
        messages = msg_repo.get_by_chat_id(chat_id, since=cutoff)
        conversations = conv_repo.get_by_chat_id(chat_id, since=cutoff)
        
        user_stats = {}
        for msg in messages:
            uid = msg.user_id
            if uid not in user_stats:
                user_stats[uid] = {"message_count": 0, "word_count": 0}
            user_stats[uid]["message_count"] += 1
            if msg.text:
                user_stats[uid]["word_count"] += len(msg.text.split())
        
        return {
            "status": "ok",
            "chat_id": chat_id,
            "period_days": days,
            "total_messages": len(messages),
            "total_conversations": len(conversations),
            "unique_users": len(user_stats),
            "user_stats": user_stats,
            "generated_at": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Failed to aggregate statistics: {e}")
        return {"status": "error", "error": str(e)}


celery_app = get_celery_app()


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="app.tasks.db_tasks.fetch_conversations",
    queue="heavy",
    default_retry_delay=30,
    max_retries=3,
    time_limit=60,
    soft_time_limit=45,
)
def fetch_conversations_async(self, chat_id: int, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
    """Async wrapper for fetching conversations."""
    return fetch_conversations(chat_id, limit, offset)


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="app.tasks.db_tasks.fetch_user_history",
    queue="heavy",
    default_retry_delay=30,
    max_retries=3,
    time_limit=60,
    soft_time_limit=45,
)
def fetch_user_history_async(self, user_id: int, days: int = 30) -> Dict[str, Any]:
    """Async wrapper for fetching user history."""
    return fetch_user_history(user_id, days)


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="app.tasks.db_tasks.bulk_update_conversations",
    queue="heavy",
    default_retry_delay=60,
    max_retries=2,
    time_limit=120,
    soft_time_limit=90,
)
def bulk_update_conversations_async(self, conversation_ids: List[int], updates: Dict[str, Any]) -> Dict[str, Any]:
    """Async wrapper for bulk updates."""
    return bulk_update_conversations(conversation_ids, updates)


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="app.tasks.db_tasks.aggregate_statistics",
    queue="heavy",
    default_retry_delay=30,
    max_retries=3,
    time_limit=90,
    soft_time_limit=60,
)
def aggregate_statistics_async(self, chat_id: int, days: int = 7) -> Dict[str, Any]:
    """Async wrapper for statistics aggregation."""
    return aggregate_statistics(chat_id, days)
