"""Adapter to make ConversationRepository compatible with legacy storage interface."""
from typing import Any, List


class StorageAdapter:
    """Adapter that wraps ConversationRepository to provide legacy storage interface.
    
    This allows the new repository pattern to work with existing code that expects
    SimpleConversationStorage methods.
    """
    
    def __init__(self, repository):
        self._repo = repository
        self._data: dict = {}
    
    @property
    def data(self) -> dict:
        """Legacy property for stats endpoint.
        
        Note: This is a best-effort compatibility property. 
        For large datasets, use repository.get_sessions() instead.
        """
        if hasattr(self._repo, "_data"):
            return self._repo._data
        return self._data
    
    def save(self, session_id: str, message: str, response: str) -> None:
        """Save a message to the conversation history.
        
        Uses 'default' tenant_id for backward compatibility.
        """
        self._repo.save_message(
            tenant_id="default",
            session_id=session_id,
            user_message=message,
            bot_response=response
        )
    
    def get_history(self, session_id: str) -> List[tuple]:
        """Get conversation history for a session.
        
        Returns list of (user_message, bot_response) tuples for backward compatibility.
        """
        history = self._repo.get_history(
            tenant_id="default",
            session_id=session_id,
            limit=50
        )
        return [(h["user"], h["bot"]) for h in history]
    
    def get_history_dict(self, session_id: str) -> List[dict]:
        """Get conversation history as list of dicts."""
        return self._repo.get_history(
            tenant_id="default",
            session_id=session_id,
            limit=50
        )
    
    def get_sessions(self) -> List[str]:
        """Get all session IDs."""
        return self._repo.get_sessions(tenant_id="default")
    
    def delete_session(self, session_id: str) -> None:
        """Delete a session and its messages."""
        self._repo.delete_session(tenant_id="default", session_id=session_id)
