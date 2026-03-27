from __future__ import annotations

from typing import Iterable, Tuple

from .types import ActionContext


class ActionPermissionError(RuntimeError):
    pass


DEFAULT_ROLE_LEVELS = {
    "owner": 0,
    "admin": 1,
    "moderator": 2,
    "support": 2,
    "whitelist": 2,
    "user": 3,
}


ROLE_ALIASES = {
    "dev": "admin",
    "sudo": "admin",
}


class ActionPermissionPolicy:
    def __init__(self, role_levels=None, role_aliases=None):
        self.role_levels = role_levels or DEFAULT_ROLE_LEVELS
        self.role_aliases = role_aliases or ROLE_ALIASES

    def normalize_roles(self, roles: Iterable[str]) -> list[str]:
        normalized = []
        for role in roles or []:
            key = (role or "").strip().lower()
            if not key:
                continue
            normalized.append(self.role_aliases.get(key, key))
        return normalized

    def check(self, context: ActionContext, required_roles: Iterable[str]) -> Tuple[bool, str]:
        required = self.normalize_roles(required_roles)
        if not required:
            return True, ""
        actor_roles = self.normalize_roles(context.roles)
        if not actor_roles:
            return False, "missing_roles"

        required_levels = [
            self.role_levels.get(role, 999) for role in required
        ]
        if not required_levels:
            return False, "unknown_required_role"
        min_required = min(required_levels)

        for actor in actor_roles:
            level = self.role_levels.get(actor, 999)
            if level <= min_required:
                return True, ""
        return False, "insufficient_role"


def ensure_roles(context: ActionContext, required_roles: Iterable[str]) -> None:
    policy = ActionPermissionPolicy()
    allowed, reason = policy.check(context, required_roles)
    if not allowed:
        raise ActionPermissionError(reason)
