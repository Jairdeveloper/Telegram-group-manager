"""AntiLink menu definitions."""

from typing import Dict, Optional

from app.manager_bot._menus.base import MenuDefinition


def create_antilink_menu(config: Optional[Dict] = None) -> MenuDefinition:
    """Create the anti-link settings menu."""
    menu = MenuDefinition(
        menu_id="mod:antilink",
        title="🔗 Configuración Anti-Enlaces",
        parent_menu="mod",
    )

    enabled = config.get("enabled", False) if config else False
    status = "✅ Activado" if enabled else "❌ Desactivado"

    menu.add_row().add_action(
        f"mod:antilink:toggle:{'on' if enabled else 'off'}",
        f"{status} (Toggle)",
        "🔄"
    )

    menu.add_row().add_action(
        "mod:antilink:whitelist:add",
        "➕ Agregar dominio",
        "➕"
    )

    menu.add_row().add_action("nav:back:mod", "🔙 Volver", "🔙")

    return menu
