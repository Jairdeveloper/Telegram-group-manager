"""Warnings menu definitions."""

from typing import Optional

from app.manager_bot._menus.base import MenuDefinition
from app.manager_bot._config.group_config import GroupConfig
from app.manager_bot._menus.formatters import yes_no
from app.manager_bot._menus.rendering import build_title, build_section


def create_warnings_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the warnings settings menu."""
    max_warnings = config.max_warnings if config else 3
    auto_ban = config.auto_ban_on_max if config else True

    title = build_title(
        "Configuracion de Advertencias",
        [
            build_section("Maximo", str(max_warnings)),
            build_section("Auto-ban", yes_no(auto_ban)),
        ],
    )

    menu = MenuDefinition(
        menu_id="warnings",
        title=title,
        parent_menu="main",
    )

    menu.add_row().add_action(
        f"warnings:max:{max_warnings}",
        f"Maximo: {max_warnings}",
    )

    menu.add_row().add_action(
        f"warnings:autoban:{'on' if auto_ban else 'off'}",
        "Auto-ban al limite",
    )

    menu.add_row().add_action(
        "warnings:list",
        "Ver advertencias",
    )

    menu.add_row().add_action("nav:back:main", "Volver")

    return menu
