"""Main menu definition for /config command."""

from typing import Optional

from app.manager_bot._config.group_config import GroupConfig
from app.manager_bot._menus.base import MenuDefinition, MenuRow, MenuAction


def create_main_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the main configuration menu."""
    menu = MenuDefinition(
        menu_id="main",
        title="⚙️ Configuración del Grupo",
        parent_menu=None,
    )

    antiflood_enabled = config.antiflood_enabled if config else False
    antiflood_status = "✅" if antiflood_enabled else "❌"
    menu.add_row() \
        .add_action(
            "mod:antiflood:show",
            f"{antiflood_status} Anti-Flood",
            "🌊"
        ) \
        .add_action("mod:antichannel:show", "📢 Anti-Canal", "📢")

    menu.add_row() \
        .add_action("antispam:show", "🚫 Antispam", "🚫") \
        .add_action("filtro_seguridad:show", "🔒 Filtros de Seguridad", "🔒")

    menu.add_row() \
        .add_action("filtro_contenido:show", "🔤 Filtros de Contenido", "🔤")

    menu.add_row() \
        .add_action("mod:antilink:show", "🔗 Anti-Enlaces", "🔗") \
        .add_action("multimedia:show", "🖼 Multimedia", "🖼")

    blocked_count = len(config.blocked_words) if config else 0
    menu.add_row() \
        .add_action("mod:words:show", f"🔇 Palabras Bloqueadas ({blocked_count})", "🔇") \
        .add_action("mod:nightmode:show", "🌙 Modo Nocturno", "🌙")

    menu.add_row() \
        .add_action("welcome:show", "👋 Bienvenida", "👋") \
        .add_action("despedida:show", "👋 Despedida", "👋")

    menu.add_row() \
        .add_action("captcha:show", "🔐 Captcha", "🔐") \
        .add_action("reports:show", "📊 Reportes", "📊")

    menu.add_row().add_action("info:show", "ℹ️ Información", "ℹ️")

    return menu


def create_info_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
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
