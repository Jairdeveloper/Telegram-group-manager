"""Minimal conversation storage implementation."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone


class SimpleConversationStorage:
    """Simple JSON-backed conversation storage.

    Used by the modular API runtime as a lightweight default.
    """

    def __init__(self, filename: str = "conversations.json"):
        self.filename = filename
        self.data = self._load()

    def _load(self) -> dict:
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save(self, session_id: str, message: str, response: str):
        if session_id not in self.data:
            self.data[session_id] = []

        self.data[session_id].append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message": message,
                "response": response,
            }
        )
        self._persist()

    def _persist(self):
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, default=str)

    def get_history(self, session_id: str) -> list:
        return self.data.get(session_id, [])
