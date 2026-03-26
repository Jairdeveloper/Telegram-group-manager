from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any

from app.agent.memory import MemorySystem


@dataclass
class ContextWindow:
    messages: List[Dict[str, Any]]
    summary: str = ""

    def render(self) -> str:
        lines: List[str] = []
        if self.summary:
            lines.append(f"Resumen: {self.summary}")
        for item in self.messages:
            user_text = item.get("user", "")
            bot_text = item.get("bot", "")
            if user_text:
                lines.append(f"Usuario: {user_text}")
            if bot_text:
                lines.append(f"Asistente: {bot_text}")
        return "\n".join(lines)


class ContextBuilder:
    def __init__(self, memory: MemorySystem, max_messages: int = 10):
        self.memory = memory
        self.max_messages = max_messages

    def build(self, tenant_id: str, session_id: str) -> ContextWindow:
        history = self.memory.get_history(
            tenant_id=tenant_id,
            session_id=session_id,
            limit=self.max_messages,
        )
        summary = self.memory.summarize_old_messages(tenant_id, session_id) or ""
        return ContextWindow(messages=history, summary=summary)
