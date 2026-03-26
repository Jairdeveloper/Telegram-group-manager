from __future__ import annotations

from dataclasses import dataclass
from typing import Awaitable, Callable, Dict, Optional, Type

from pydantic import BaseModel

from .types import ActionContext, ActionResult


class ActionError(RuntimeError):
    pass


class ActionNotFound(ActionError):
    pass


class ActionValidationError(ActionError):
    pass


@dataclass(frozen=True)
class ActionDefinition:
    action_id: str
    description: str
    schema: Type[BaseModel]
    permissions: tuple[str, ...]
    execute: Callable[[ActionContext, BaseModel], Awaitable[ActionResult]]


class ActionRegistry:
    def __init__(self):
        self._actions: Dict[str, ActionDefinition] = {}

    def register(self, action: ActionDefinition) -> None:
        if action.action_id in self._actions:
            raise ActionError(f"Action '{action.action_id}' already registered")
        self._actions[action.action_id] = action

    def get(self, action_id: str) -> ActionDefinition:
        action = self._actions.get(action_id)
        if not action:
            raise ActionNotFound(f"Action '{action_id}' not found")
        return action

    def list_actions(self) -> Dict[str, ActionDefinition]:
        return dict(self._actions)


_default_registry: Optional[ActionRegistry] = None


def get_default_registry() -> ActionRegistry:
    global _default_registry
    if _default_registry is None:
        registry = ActionRegistry()
        from .pilot_actions import register_pilot_actions

        register_pilot_actions(registry)
        _default_registry = registry
    return _default_registry
