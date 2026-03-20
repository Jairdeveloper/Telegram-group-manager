"""AntiLink menu definitions."""

from typing import Optional

from app.manager_bot._menus.base import MenuDefinition
from app.manager_bot._config.group_config import GroupConfig
from app.manager_bot._menus.formatters import on_off
from app.manager_bot._menus.rendering import build_title, build_section


def create_antilink_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the anti-link settings menu."""
    enabled = config.antilink_enabled if config else False
    title = build_title(
        "Anti-Enlaces",
        [build_section("Estado", on_off(enabled))],
    )

    menu = MenuDefinition(
        menu_id="mod:antilink",
        title=title,
        parent_menu="main",
    )

    toggle_label = "Desactivar" if enabled else "Activar"
    menu.add_row().add_action(
        f"mod:antilink:toggle:{'off' if enabled else 'on'}",
        toggle_label,
    )

    menu.add_row().add_action(
        "mod:antilink:whitelist:add",
        "Agregar dominio",
    )

    menu.add_row().add_action("nav:back:main", "Volver")

    return menu
