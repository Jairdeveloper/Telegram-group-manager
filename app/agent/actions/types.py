from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class ActionContext:
    chat_id: int
    tenant_id: str = "default"
    user_id: Optional[int] = None
    roles: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ActionResult:
    status: str
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
