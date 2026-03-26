from __future__ import annotations

from typing import Any, Dict

from pydantic import ValidationError

from .permissions import ActionPermissionPolicy
from .registry import ActionDefinition, ActionError, ActionNotFound, ActionValidationError
from .types import ActionContext, ActionResult


class ActionExecutor:
    def __init__(self, registry, permission_policy: ActionPermissionPolicy | None = None):
        self.registry = registry
        self.permission_policy = permission_policy or ActionPermissionPolicy()

    async def execute(
        self,
        action_id: str,
        context: ActionContext,
        payload: Dict[str, Any] | None = None,
    ) -> ActionResult:
        action = self._get_action(action_id)
        params, error = self._parse_payload(action, payload or {})
        if error:
            return ActionResult(
                status="error",
                message="Parametros invalidos",
                data={"error": error},
            )

        allowed, reason = self.permission_policy.check(context, action.permissions)
        if not allowed:
            return ActionResult(
                status="denied",
                message="No autorizado",
                data={
                    "reason": reason,
                    "required_roles": list(action.permissions),
                    "actor_roles": list(context.roles or []),
                },
            )
        return await action.execute(context, params)

    def _get_action(self, action_id: str) -> ActionDefinition:
        return self.registry.get(action_id)

    def _parse_payload(self, action: ActionDefinition, payload: Dict[str, Any]):
        try:
            return action.schema.model_validate(payload), ""
        except ValidationError as exc:
            return None, str(exc)
