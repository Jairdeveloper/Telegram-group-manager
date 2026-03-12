"""Enterprise roles and permission helpers."""

from enum import Enum


class EnterpriseRole(str, Enum):
    OWNER = "owner"
    DEV = "dev"
    SUDO = "sudo"
    SUPPORT = "support"
    WHITELIST = "whitelist"
    USER = "user"
    SARDEGNA = "sardegna"


ROLE_ORDER = {
    EnterpriseRole.OWNER: 0,
    EnterpriseRole.DEV: 1,
    EnterpriseRole.SUDO: 2,
    EnterpriseRole.SUPPORT: 3,
    EnterpriseRole.WHITELIST: 4,
    EnterpriseRole.USER: 5,
}


def parse_role(raw: str) -> EnterpriseRole:
    """Parse role name into EnterpriseRole."""
    normalized = (raw or "").strip().lower()
    for role in EnterpriseRole:
        if role.value == normalized:
            return role
    raise ValueError(f"Unknown role: {raw}")


def has_role_at_least(actor_role: EnterpriseRole, required_role: EnterpriseRole) -> bool:
    """Return True if actor_role is equal or above required_role."""
    if actor_role == EnterpriseRole.SARDEGNA:
        # Sardegna users are treated as immune for moderation actions.
        return True
    return ROLE_ORDER.get(actor_role, 999) <= ROLE_ORDER.get(required_role, 999)
