"""Shared UI formatters for menu descriptions."""

from typing import Optional


def yes_no(value: Optional[bool]) -> str:
    """Return Si/No for boolean-like values."""
    return "Si" if value else "No"


def on_off(value: Optional[bool]) -> str:
    """Return Activado/Desactivado for boolean-like values."""
    return "Activado" if value else "Desactivado"


def duration_label(seconds: Optional[int]) -> str:
    """Return a short human-friendly duration label."""
    if not seconds:
        return "sin duracion"
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        return f"{seconds // 60}m"
    if seconds < 86400:
        return f"{seconds // 3600}h"
    return f"{seconds // 86400}d"


def action_label(
    action: Optional[str],
    mute_sec: Optional[int] = None,
    ban_sec: Optional[int] = None,
) -> str:
    """Return label for action with optional duration."""
    normalized = (action or "off").lower()
    mapping = {
        "off": "Off",
        "warn": "Warn",
        "kick": "Kick",
        "mute": "Silenciar",
        "ban": "Ban",
    }
    label = mapping.get(normalized, normalized)
    if normalized == "mute":
        return f"{label} {duration_label(mute_sec)}"
    if normalized == "ban":
        return f"{label} {duration_label(ban_sec)}"
    return label

