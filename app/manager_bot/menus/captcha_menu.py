"""Captcha menu definitions."""

from typing import Optional

from app.manager_bot.menus.base import MenuDefinition
from app.manager_bot.config.group_config import GroupConfig


def create_captcha_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the captcha settings menu."""
    menu = MenuDefinition(
        menu_id="captcha",
        title="🔐 Configuración de Captcha",
        parent_menu="main",
    )

    captcha_enabled = config.captcha_enabled if config else False
    status = "✅ Activado" if captcha_enabled else "❌ Desactivado"

    menu.add_row().add_action(
        f"captcha:toggle",
        f"{status} Captcha",
        "🔐"
    )

    if captcha_enabled:
        current_type = config.captcha_type if config else "button"
        menu.add_row().add_action(
            f"captcha:type:{current_type}",
            f"📝 Tipo: {current_type}",
            "📝"
        )

        current_timeout = config.captcha_timeout if config else 300
        menu.add_row().add_action(
            "captcha:timeout:show",
            f"⏱️ Timeout: {current_timeout}s",
            "⏱️"
        )

    menu.add_row().add_action("nav:back:main", "🔙 Volver", "🔙")

    return menu
