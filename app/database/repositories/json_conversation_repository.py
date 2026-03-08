"""JSON file implementation of conversation repository (fallback)."""
import json
import logging
from pathlib import Path
from typing import List, Optional

from app.database.repositories.conversation_repository import ConversationRepository

logger = logging.getLogger(__name__)


class JsonConversationRepository(ConversationRepository):
    """JSON file fallback implementation."""

    def __init__(self, filepath: str = "conversations.json"):
        self.filepath = Path(filepath)
        self._data: dict = {}
        self._load()

    def _load(self) -> None:
        if self.filepath.exists():
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except json.JSONDecodeError:
                logger.warning("Could not parse conversations.json, starting fresh")
                self._data = {}
        else:
            self._data = {}

    def _save(self) -> None:
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False, default=str)

    def save_message(
        self,
        tenant_id: str,
        session_id: str,
        user_message: str,
        bot_response: str,
        metadata: Optional[dict] = None
    ) -> None:
        key = f"{tenant_id}:{session_id}"
        if key not in self._data:
            self._data[key] = []
        self._data[key].append({
            "user": user_message,
            "bot": bot_response,
            "ts": None,
            "metadata": metadata or {}
        })
        self._save()

    def get_history(
        self,
        tenant_id: str,
        session_id: str,
        limit: int = 50
    ) -> List[dict]:
        key = f"{tenant_id}:{session_id}"
        messages = self._data.get(key, [])
        return messages[-limit:]

    def get_sessions(self, tenant_id: str) -> List[str]:
        prefix = f"{tenant_id}:"
        return [
            key.replace(prefix, "")
            for key in self._data.keys()
            if key.startswith(prefix)
        ]

    def delete_session(self, tenant_id: str, session_id: str) -> None:
        key = f"{tenant_id}:{session_id}"
        if key in self._data:
            del self._data[key]
            self._save()
