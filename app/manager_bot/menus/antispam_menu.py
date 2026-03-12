"""Antispam menu definitions."""

from typing import Optional

from app.manager_bot.menus.base import MenuDefinition
from app.manager_bot.config.group_config import GroupConfig


def create_antispam_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the antispam settings menu."""
    menu = MenuDefinition(
        menu_id="antispam",
        title="🚫 Configuración Antispam",
        parent_menu="main",
    )

    antispam_enabled = config.antispam_enabled if config else False
    antispam_status = "✅ Activado" if antispam_enabled else "❌ Desactivado"

    menu.add_row().add_action(
        f"antispam:toggle",
        f"{antispam_status} Antispam General",
        "🚫"
    )

    if antispam_enabled:
        spamwatch_enabled = config.spamwatch_enabled if config else False
        spamwatch_status = "✅" if spamwatch_enabled else "❌"
        menu.add_row().add_action(
            f"antispam:spamwatch:toggle",
            f"{spamwatch_status} SpamWatch",
            "🔍"
        )

        sibyl_enabled = config.sibyl_enabled if config else False
        sibyl_status = "✅" if sibyl_enabled else "❌"
        menu.add_row().add_action(
            f"antispam:sibyl:toggle",
            f"{sibyl_status} Sibyl",
            "🛡️"
        )

        menu.add_row().add_action("antispam:sensitivity:show", "📊 Sensibilidad", "📊")

    menu.add_row().add_action("nav:back:main", "🔙 Volver", "🔙")

    return menu


def create_sensitivity_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the sensitivity settings menu."""
    menu = MenuDefinition(
        menu_id="antispam:sensitivity",
        title="📊 Configuración de Sensibilidad",
        parent_menu="antispam",
    )

    current = "medium"
    if config:
        pass

    menu.add_row().add_action(
        "antispam:sensitivity:low" if current != "low" else "antispam:sensitivity:noop",
        "🔵 Baja" if current != "low" else "✅ Baja (actual)",
        "🔵"
    )

    menu.add_row().add_action(
        "antispam:sensitivity:medium" if current != "medium" else "antispam:sensitivity:noop",
        "🟡 Media" if current != "medium" else "✅ Media (actual)",
        "🟡"
    )

    menu.add_row().add_action(
        "antispam:sensitivity:high" if current != "high" else "antispam:sensitivity:noop",
        "🔴 Alta" if current != "high" else "✅ Alta (actual)",
        "🔴"
    )

    menu.add_row().add_action("nav:back:antispam", "🔙 Volver", "🔙")

    return menu
