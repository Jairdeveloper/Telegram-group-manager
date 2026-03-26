from __future__ import annotations

from typing import Any, Dict

from pydantic import ValidationError

from .permissions import ActionPermissionPolicy
from .audit import log_action
from .templates import ActionTemplateEngine, TemplateContext, get_default_template_engine
from .registry import ActionDefinition, ActionError, ActionNotFound, ActionValidationError
from .types import ActionContext, ActionResult


class ActionExecutor:
    def __init__(
        self,
        registry,
        permission_policy: ActionPermissionPolicy | None = None,
        template_engine: ActionTemplateEngine | None = None,
    ):
        self.registry = registry
        self.permission_policy = permission_policy or ActionPermissionPolicy()
        self.template_engine = template_engine or get_default_template_engine()

    async def execute(
        self,
        action_id: str,
        context: ActionContext,
        payload: Dict[str, Any] | None = None,
        *,
        dry_run: bool = False,
        confirm: bool = False,
    ) -> ActionResult:
        action = self._get_action(action_id)
        payload = payload or {}
        params, error = self._parse_payload(action, payload)
        if error:
            return ActionResult(
                status="error",
                message=self.template_engine.render(
                    TemplateContext(action_id=action.action_id, status="error", data={"error": error})
                ),
                data={"error": error},
            )

        allowed, reason = self.permission_policy.check(context, action.permissions)
        if not allowed:
            return ActionResult(
                status="denied",
                message=self.template_engine.render(
                    TemplateContext(
                        action_id=action.action_id,
                        status="denied",
                        data={
                            "reason": reason,
                            "required_roles": list(action.permissions),
                            "actor_roles": list(context.roles or []),
                        },
                    )
                ),
                data={
                    "reason": reason,
                    "required_roles": list(action.permissions),
                    "actor_roles": list(context.roles or []),
                },
            )
        if dry_run:
            if action.dry_run is None:
                return ActionResult(
                    status="error",
                    message=self.template_engine.render(
                        TemplateContext(
                            action_id=action.action_id,
                            status="dry_run_unsupported",
                            data={"action_id": action.action_id},
                        )
                    ),
                    data={"action_id": action.action_id},
                )
            return await action.dry_run(context, params)

        if action.requires_confirmation and not confirm:
            preview = None
            if action.dry_run is not None:
                preview = await action.dry_run(context, params)
            return ActionResult(
                status="confirm",
                message=self.template_engine.render(
                    TemplateContext(
                        action_id=action.action_id,
                        status="confirm",
                        data={"preview": preview.data if preview else {}},
                    )
                ),
                data={
                    "action_id": action.action_id,
                    "preview": preview.data if preview else {},
                },
            )
        previous_state = None
        if action.snapshot is not None:
            previous_state = await action.snapshot(context, params)

        result = await action.execute(context, params)

        if previous_state is not None:
            log_action(
                context=context,
                action_id=action.action_id,
                payload=payload,
                previous_state=previous_state,
                result=result,
            )
            result.data = dict(result.data)
            result.data["previous_state"] = previous_state

        return result

    async def rollback(
        self,
        action_id: str,
        context: ActionContext,
        payload: Dict[str, Any] | None,
        previous_state: Dict[str, Any],
    ) -> ActionResult:
        action = self._get_action(action_id)
        if action.undo is None:
            return ActionResult(
                status="error",
                message=self.template_engine.render(
                    TemplateContext(
                        action_id=action_id,
                        status="rollback_unsupported",
                        data={"action_id": action_id},
                    )
                ),
                data={"action_id": action_id},
            )
        params, error = self._parse_payload(action, payload or {})
        if error:
            return ActionResult(
                status="error",
                message=self.template_engine.render(
                    TemplateContext(action_id=action_id, status="error", data={"error": error})
                ),
                data={"error": error},
            )
        return await action.undo(context, params, previous_state)

    def _get_action(self, action_id: str) -> ActionDefinition:
        return self.registry.get(action_id)

    def _parse_payload(self, action: ActionDefinition, payload: Dict[str, Any]):
        try:
            return action.schema.model_validate(payload), ""
        except ValidationError as exc:
            return None, str(exc)
