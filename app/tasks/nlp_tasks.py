"""NLP tasks for Celery workers."""

from typing import Dict, Any, Optional
from celery import Task

from app.celery_app import get_celery_app


class NLPTask(Task):
    """Base class for NLP tasks with error handling."""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure."""
        return super().on_failure(exc, task_id, args, kwargs, einfo)


def process_nlp_message(text: str, chat_id: int, update_id: int) -> Dict[str, Any]:
    """Process message through NLP pipeline."""
    try:
        from app.nlp.integration import get_nlp_integration
        
        nlp_integration = get_nlp_integration()
        
        if not text or not nlp_integration.should_use_nlp(text):
            return {"status": "skipped", "reason": "not_nlp_candidate"}
        
        result = nlp_integration.process_message(text)
        
        return {
            "status": "ok",
            "intent": getattr(result, "intent", None),
            "action_result": getattr(result, "action_result", None),
            "confidence": getattr(result, "action_result", {}).get("confidence", 0) if hasattr(result, "action_result") else 0,
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def process_batch_nlp(messages: list) -> list:
    """Process batch of messages through NLP."""
    results = []
    for msg in messages:
        result = process_nlp_message(
            text=msg.get("text", ""),
            chat_id=msg.get("chat_id"),
            update_id=msg.get("update_id"),
        )
        results.append(result)
    return results


celery_app = get_celery_app()


@celery_app.task(
    bind=True,
    base=NLPTask,
    name="app.tasks.nlp_tasks.process_nlp_message",
    queue="nlp",
    default_retry_delay=30,
    max_retries=3,
)
def process_nlp_async(self, text: str, chat_id: int, update_id: int) -> Dict[str, Any]:
    """Async wrapper for NLP processing."""
    try:
        return process_nlp_message(text, chat_id, update_id)
    except Exception as e:
        self.retry(exc=e)


@celery_app.task(
    bind=True,
    base=NLPTask,
    name="app.tasks.nlp_tasks.process_batch_nlp",
    queue="nlp",
)
def process_batch_nlp_async(self, messages: list) -> list:
    """Async wrapper for batch NLP processing."""
    return process_batch_nlp(messages)
