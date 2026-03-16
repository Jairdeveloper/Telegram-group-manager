"""Warnings menu definitions."""

from typing import Optional

from app.manager_bot._menus.base import MenuDefinition
from app.manager_bot._config.group_config import GroupConfig


def create_warnings_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the warnings settings menu."""
    menu = MenuDefinition(
        menu_id="warnings",
        title="⚠️ Configuración de Advertencias",
        parent_menu="main",
    )

    max_warnings = config.max_warnings if config else 3
    menu.add_row().add_action(
        f"warnings:max:{max_warnings}",
        f"⚠️ Máximo: {max_warnings} advertencias",
        "⚠️"
    )

    auto_ban = config.auto_ban_on_max if config else True
    auto_ban_status = "✅" if auto_ban else "❌"
    menu.add_row().add_action(
        f"warnings:autoban:{'on' if auto_ban else 'off'}",
        f"{auto_ban_status} Auto-ban al límite",
        "🚫"
    )

    menu.add_row().add_action(
        "warnings:list",
        "📋 Ver advertencias",
        "📋"
    )

    menu.add_row().add_action("nav:back:main", "🔙 Volver", "🔙")

    return menu
