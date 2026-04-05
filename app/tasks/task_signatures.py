"""Task signatures and pipelines for Celery workflows."""

from typing import Dict, Any, List
from celery import group, chain, chord

from app.celery_app import get_celery_app


celery_app = get_celery_app()


def nlp_pipeline_signature(text: str, chat_id: int, update_id: int) -> Dict[str, Any]:
    """Create signature for NLP pipeline processing.
    
    Returns a task signature that can be sent to the queue.
    """
    from app.tasks.nlp_tasks import process_nlp_async
    
    return process_nlp_async.s(
        text=text,
        chat_id=chat_id,
        update_id=update_id
    )


def analysis_pipeline_signature(message_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create signature for message analysis pipeline.
    
    Returns a task signature for analyzing a message.
    """
    from app.tasks.analysis_tasks import analyze_message_async
    
    return analyze_message_async.s(message_data=message_data)


def db_pipeline_signature(chat_id: int, days: int = 7) -> Dict[str, Any]:
    """Create signature for database statistics aggregation.
    
    Returns a task signature for fetching chat statistics.
    """
    from app.tasks.db_tasks import aggregate_statistics_async
    
    return aggregate_statistics_async.s(chat_id=chat_id, days=days)


def batch_nlp_signature(messages: List[Dict[str, Any]]) -> chain:
    """Create signature for batch NLP processing.
    
    Returns a chain of tasks for processing multiple messages.
    """
    from app.tasks.nlp_tasks import process_nlp_async
    
    return chain(
        process_nlp_async.s(
            text=msg.get("text", ""),
            chat_id=msg.get("chat_id", 0),
            update_id=msg.get("update_id", 0)
        )
        for msg in messages
    )


def batch_analysis_signature(messages: List[Dict[str, Any]]) -> group:
    """Create signature for parallel batch analysis.
    
    Returns a group of tasks for parallel message analysis.
    """
    from app.tasks.analysis_tasks import analyze_message_async
    
    return group(
        analyze_message_async.s(message_data=msg)
        for msg in messages
    )


def full_analysis_pipeline(text: str, chat_id: int, update_id: int) -> chain:
    """Create full analysis pipeline: NLP + message analysis.
    
    Returns a chain that runs NLP first, then analysis.
    """
    from app.tasks.nlp_tasks import process_nlp_async
    from app.tasks.analysis_tasks import analyze_message_async
    
    return chain(
        process_nlp_async.s(text=text, chat_id=chat_id, update_id=update_id),
        analyze_message_async.s(message_data={"text": text, "chat_id": chat_id})
    )


def nlp_with_db_signature(text: str, chat_id: int, update_id: int) -> chain:
    """Create pipeline that includes NLP and DB aggregation.
    
    Returns a chain that runs NLP, then aggregates stats.
    """
    from app.tasks.nlp_tasks import process_nlp_async
    from app.tasks.db_tasks import aggregate_statistics_async
    
    return chain(
        process_nlp_async.s(text=text, chat_id=chat_id, update_id=update_id),
        aggregate_statistics_async.s(chat_id=chat_id, days=1)
    )


class TaskCallbacks:
    """Callbacks for task results."""
    
    @staticmethod
    def on_nlp_success(result: Any) -> None:
        """Callback when NLP task succeeds."""
        pass
    
    @staticmethod
    def on_nlp_failure(request, exc: Exception, traceback: str) -> None:
        """Callback when NLP task fails."""
        pass
    
    @staticmethod
    def on_analysis_success(result: Any) -> None:
        """Callback when analysis task succeeds."""
        pass
    
    @staticmethod
    def on_analysis_failure(request, exc: Exception, traceback: str) -> None:
        """Callback when analysis task fails."""
        pass
    
    @staticmethod
    def on_db_success(result: Any) -> None:
        """Callback when DB task succeeds."""
        pass
    
    @staticmethod
    def on_db_failure(request, exc: Exception, traceback: str) -> None:
        """Callback when DB task fails."""
        pass


task_callbacks = TaskCallbacks()
