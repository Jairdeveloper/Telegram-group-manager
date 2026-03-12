"""Main menu definition for /config command."""

from app.manager_bot.menus.base import MenuDefinition, MenuRow, MenuAction


def create_main_menu() -> MenuDefinition:
    """Create the main configuration menu."""
    menu = MenuDefinition(
        menu_id="main",
        title="⚙️ Configuración del Grupo",
        parent_menu=None,
    )

    menu.add_row().add_action("mod:show", "🛡️ Moderación", "🛡️")

    menu.add_row() \
        .add_action("antispam:show", "🚫 Antispam", "🚫") \
        .add_action("filters:show", "🔤 Filtros", "🔤")

    menu.add_row() \
        .add_action("welcome:show", "👋 Bienvenida", "👋") \
        .add_action("goodbye:show", "👋 Despedida", "👋")

    menu.add_row() \
        .add_action("captcha:show", "🔐 Captcha", "🔐") \
        .add_action("reports:show", "📊 Reportes", "📊")

    menu.add_row().add_action("info:show", "ℹ️ Información", "ℹ️")

    return menu


def create_info_menu() -> MenuDefinition:
    """Create the information menu."""
    menu = MenuDefinition(
        menu_id="info",
        title="ℹ️ Información del Grupo",
        parent_menu="main",
    )

    menu.add_row().add_action("info:stats", "📊 Estadísticas", "📊")
    menu.add_row().add_action("info:settings", "⚙️ Ajustes Actuales", "⚙️")

    menu.add_row().add_action("nav:back:main", "🔙 Volver", "🔙")

    return menu
