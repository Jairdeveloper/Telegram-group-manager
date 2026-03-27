from __future__ import annotations

from typing import Any, Dict, Optional

from app.audit import AuditEventType, get_audit_service

from .types import ActionContext, ActionResult


def log_action(
    *,
    context: ActionContext,
    action_id: str,
    payload: Dict[str, Any],
    previous_state: Optional[Dict[str, Any]],
    result: ActionResult,
) -> None:
    audit = get_audit_service()
    audit.log(
        event_type=AuditEventType.CONFIG_CHANGE,
        tenant_id=context.tenant_id,
        actor_id=str(context.user_id) if context.user_id is not None else None,
        actor_type="user" if context.user_id is not None else "system",
        resource_type="action",
        resource_id=str(context.chat_id),
        action=action_id,
        result=result.status,
        metadata={
            "payload": payload,
            "previous_state": previous_state,
            "result": result.data,
        },
    )
