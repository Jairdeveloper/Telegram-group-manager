"""Conversation repository interface."""
from abc import ABC, abstractmethod
from typing import List, Optional


class ConversationRepository(ABC):
    """Abstract base class for conversation storage."""

    @abstractmethod
    def save_message(
        self,
        tenant_id: str,
        session_id: str,
        user_message: str,
        bot_response: str,
        metadata: Optional[dict] = None
    ) -> None:
        """Save a message to the conversation history."""
        pass

    @abstractmethod
    def get_history(
        self,
        tenant_id: str,
        session_id: str,
        limit: int = 50
    ) -> List[dict]:
        """Get conversation history for a session."""
        pass

    @abstractmethod
    def get_sessions(self, tenant_id: str) -> List[str]:
        """Get all session IDs for a tenant."""
        pass

    @abstractmethod
    def delete_session(self, tenant_id: str, session_id: str) -> None:
        """Delete a session and its messages."""
        pass
