"""Analysis tasks for heavy processing."""

from typing import Dict, Any, List
from celery import Task

from app.celery_app import get_celery_app


class AnalysisTask(Task):
    """Base class for analysis tasks with error handling."""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure."""
        return super().on_failure(exc, task_id, args, kwargs, einfo)


def analyze_message(message_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze a message for complex patterns."""
    try:
        text = message_data.get("text", "")
        chat_id = message_data.get("chat_id")
        
        analysis = {
            "word_count": len(text.split()),
            "char_count": len(text),
            "has_links": "http" in text.lower() or "www" in text.lower(),
            "has_mentions": "@" in text,
            "has_hashtags": "#" in text,
            "is_spam_likely": False,
        }
        
        if analysis["word_count"] > 500:
            analysis["is_spam_likely"] = True
            analysis["spam_reason"] = "excessive_length"
        
        if analysis["has_links"] and analysis["word_count"] < 10:
            analysis["is_spam_likely"] = True
            analysis["spam_reason"] = "link_spam"
        
        return analysis
    except Exception as e:
        return {"status": "error", "error": str(e)}


def analyze_batch(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Analyze batch of messages."""
    results = []
    for msg in messages:
        result = analyze_message(msg)
        results.append(result)
    return results


celery_app = get_celery_app()


@celery_app.task(
    bind=True,
    base=AnalysisTask,
    name="app.tasks.analysis_tasks.analyze_message",
    queue="heavy",
    default_retry_delay=30,
    max_retries=3,
)
def analyze_message_async(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
    """Async wrapper for message analysis."""
    return analyze_message(message_data)


@celery_app.task(
    bind=True,
    base=AnalysisTask,
    name="app.tasks.analysis_tasks.analyze_batch",
    queue="heavy",
)
def analyze_batch_async(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Async wrapper for batch analysis."""
    return analyze_batch(messages)
