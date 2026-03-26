from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from app.database.repositories.factory import create_conversation_repository


@dataclass
class MemoryEntry:
    user: str
    bot: str
    metadata: Dict[str, Any]


class MemorySystem:
    def __init__(
        self,
        repository=None,
        max_messages: int = 20,
    ):
        self.repository = repository or create_conversation_repository()
        self.max_messages = max_messages
        self._buffers: Dict[str, List[MemoryEntry]] = {}

    def add_exchange(
        self,
        tenant_id: str,
        session_id: str,
        user_message: str,
        bot_response: str,
        metadata: Optional[dict] = None,
    ) -> None:
        metadata = metadata or {}
        self.repository.save_message(
            tenant_id=tenant_id,
            session_id=session_id,
            user_message=user_message,
            bot_response=bot_response,
            metadata=metadata,
        )

        key = self._key(tenant_id, session_id)
        buffer = self._buffers.setdefault(key, [])
        buffer.append(MemoryEntry(user=user_message, bot=bot_response, metadata=metadata))
        if len(buffer) > self.max_messages:
            self._buffers[key] = buffer[-self.max_messages :]

    def get_history(
        self,
        tenant_id: str,
        session_id: str,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        key = self._key(tenant_id, session_id)
        if key in self._buffers and len(self._buffers[key]) >= limit:
            return [
                {"user": entry.user, "bot": entry.bot, "metadata": entry.metadata}
                for entry in self._buffers[key][-limit:]
            ]

        history = self.repository.get_history(
            tenant_id=tenant_id,
            session_id=session_id,
            limit=limit,
        )
        return history

    def summarize_old_messages(self, tenant_id: str, session_id: str) -> Optional[str]:
        return None

    def _key(self, tenant_id: str, session_id: str) -> str:
        return f"{tenant_id}:{session_id}"
