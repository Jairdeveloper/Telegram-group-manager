"""Celery tasks for async processing."""

from .nlp_tasks import (
    process_nlp_message,
    process_batch_nlp,
    process_nlp_async,
    process_batch_nlp_async,
)
from .analysis_tasks import (
    analyze_message,
    analyze_batch,
    analyze_message_async,
    analyze_batch_async,
)
from .maintenance_tasks import (
    cleanup_old_data,
    health_check,
    cleanup_old_data_async,
    health_check_async,
)
from .db_tasks import (
    fetch_conversations,
    fetch_user_history,
    bulk_update_conversations,
    aggregate_statistics,
    fetch_conversations_async,
    fetch_user_history_async,
    bulk_update_conversations_async,
    aggregate_statistics_async,
)
from .task_signatures import (
    nlp_pipeline_signature,
    analysis_pipeline_signature,
    db_pipeline_signature,
)

__all__ = [
    # NLP tasks
    "process_nlp_message",
    "process_batch_nlp",
    "process_nlp_async",
    "process_batch_nlp_async",
    # Analysis tasks
    "analyze_message",
    "analyze_batch",
    "analyze_message_async",
    "analyze_batch_async",
    # Maintenance tasks
    "cleanup_old_data",
    "health_check",
    "cleanup_old_data_async",
    "health_check_async",
    # Database tasks
    "fetch_conversations",
    "fetch_user_history",
    "bulk_update_conversations",
    "aggregate_statistics",
    "fetch_conversations_async",
    "fetch_user_history_async",
    "bulk_update_conversations_async",
    "aggregate_statistics_async",
    # Task signatures
    "nlp_pipeline_signature",
    "analysis_pipeline_signature",
    "db_pipeline_signature",
]
