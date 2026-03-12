"""Welcome and goodbye menu definitions."""

from typing import Optional

from app.manager_bot.menus.base import MenuDefinition
from app.manager_bot.config.group_config import GroupConfig


def create_welcome_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the welcome settings menu."""
    menu = MenuDefinition(
        menu_id="welcome",
        title="👋 Configuración de Bienvenida",
        parent_menu="main",
    )

    welcome_enabled = config.welcome_enabled if config else False
    welcome_status = "✅ Activada" if welcome_enabled else "❌ Desactivada"

    menu.add_row().add_action(
        f"welcome:toggle",
        f"{welcome_status} Bienvenida",
        "👋"
    )

    if welcome_enabled:
        has_text = bool(config.welcome_text) if config else False
        menu.add_row().add_action(
            "welcome:edit:text",
            f"📝 {'Texto configurado' if has_text else 'Agregar texto'}",
            "📝"
        )

        has_media = bool(config.welcome_media) if config else False
        menu.add_row().add_action(
            "welcome:edit:media",
            f"🖼️ {'Media configurado' if has_media else 'Agregar media'}",
            "🖼️"
        )

    menu.add_row().add_action("nav:back:main", "🔙 Volver", "🔙")

    return menu


def create_goodbye_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the goodbye settings menu."""
    menu = MenuDefinition(
        menu_id="goodbye",
        title="👋 Configuración de Despedida",
        parent_menu="main",
    )

    goodbye_enabled = config.goodbye_enabled if config else False
    goodbye_status = "✅ Activada" if goodbye_enabled else "❌ Desactivada"

    menu.add_row().add_action(
        f"goodbye:toggle",
        f"{goodbye_status} Despedida",
        "👋"
    )

    if goodbye_enabled:
        has_text = bool(config.goodbye_text) if config else False
        menu.add_row().add_action(
            "goodbye:edit:text",
            f"📝 {'Texto configurado' if has_text else 'Agregar texto'}",
            "📝"
        )

    menu.add_row().add_action("nav:back:main", "🔙 Volver", "🔙")

    return menu
