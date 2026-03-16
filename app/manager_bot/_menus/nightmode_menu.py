"""NightMode menu definitions."""

from typing import Optional

from app.manager_bot._menus.base import MenuDefinition
from app.manager_bot._config.group_config import GroupConfig


def create_nightmode_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the night mode settings menu."""
    menu = MenuDefinition(
        menu_id="mod:nightmode",
        title="🌙 Configuración de Modo Nocturno",
        parent_menu="mod",
    )

    enabled = config.nightmode_enabled if config else False
    status = "✅ Activado" if enabled else "❌ Desactivado"

    menu.add_row().add_action(
        f"mod:nightmode:toggle:{'on' if enabled else 'off'}",
        f"{status} (Toggle)",
        "🔄"
    )

    if enabled:
        start = config.nightmode_start if config else "23:00"
        end = config.nightmode_end if config else "07:00"
        menu.add_row().add_action(
            "mod:nightmode:time",
            f"⏰ Horario: {start} - {end}",
            "⏰"
        )

        menu.add_row().add_action(
            "mod:nightmode:action:mute",
            "🔇 Silenciar",
            "🔇"
        )

    menu.add_row().add_action("nav:back:mod", "🔙 Volver", "🔙")

    return menu
