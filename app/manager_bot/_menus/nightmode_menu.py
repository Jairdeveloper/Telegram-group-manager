"""NightMode menu definitions."""

from typing import Optional

from app.manager_bot._menus.base import MenuDefinition
from app.manager_bot._config.group_config import GroupConfig
from app.manager_bot._menus.formatters import on_off
from app.manager_bot._menus.rendering import build_title, build_section


def create_nightmode_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the night mode settings menu."""
    enabled = config.nightmode_enabled if config else False
    start = config.nightmode_start if config else "23:00"
    end = config.nightmode_end if config else "07:00"

    base = "Modo Nocturno"
    title = build_title(
        base,
        [
            build_section("Estado", on_off(enabled)),
            build_section("Horario", f"{start} - {end}") if enabled else "",
        ],
    )

    menu = MenuDefinition(
        menu_id="mod:nightmode",
        title=title,
        parent_menu="main",
    )

    toggle_label = "Desactivar" if enabled else "Activar"
    menu.add_row().add_action(
        f"mod:nightmode:toggle:{'off' if enabled else 'on'}",
        toggle_label,
    )

    if enabled:
        menu.add_row().add_action(
            "mod:nightmode:time",
            "Configurar horario",
        )
        menu.add_row().add_action(
            "mod:nightmode:action:mute",
            "Silenciar",
        )

    menu.add_row().add_action("nav:back:main", "Volver")

    return menu
