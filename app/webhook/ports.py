"""Ports (interfaces) for webhook domain services."""

from typing import Any, Dict, Optional, Protocol


class ChatApiClient(Protocol):
    """Client for chatbot API."""

    def ask(self, *, message: str, session_id: str) -> str:
        """Return chatbot reply text for a message/session pair."""


class TelegramClient(Protocol):
    """Client for Telegram Bot API."""

    def send_message(self, *, chat_id: int, text: str) -> Dict[str, Any]:
        """Send message to Telegram and return transport details."""


class DedupStore(Protocol):
    """Store used to deduplicate incoming Telegram updates."""

    def mark_if_new(self, *, update_id: int, ttl_seconds: int) -> bool:
        """Return True when update_id was not seen before."""


class TaskQueue(Protocol):
    """Queue used for asynchronous update processing."""

    def enqueue_process_update(self, *, update: Dict[str, Any]) -> Optional[str]:
        """Enqueue update processing and return a job id when available."""
