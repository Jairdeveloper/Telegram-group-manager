"""Data models for Telegram ingress dispatch."""

from dataclasses import dataclass, field
from typing import Any, Dict, Literal, Optional, Tuple


DispatchKind = Literal["ops_command", "enterprise_command", "chat_message", "unsupported"]


@dataclass(frozen=True)
class DispatchResult:
    """Classification result for a Telegram update."""

    kind: DispatchKind
    update_id: Optional[int]
    chat_id: Optional[int]
    user_id: Optional[int] = None
    text: str = ""
    command: Optional[str] = None
    args: Tuple[str, ...] = field(default_factory=tuple)
    reason: Optional[str] = None
    raw_update: Dict[str, Any] = field(default_factory=dict)
