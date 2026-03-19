"""Moderation menu definitions."""

from typing import Optional

from app.manager_bot._menus.base import MenuDefinition
from app.manager_bot._config.group_config import GroupConfig


def create_moderation_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the moderation settings menu."""
    menu = MenuDefinition(
        menu_id="mod",
        title="🛡️ Configuración de Moderación",
        parent_menu="main",
    )

    antiflood_status = "✅" if config and config.antiflood_enabled else "❌"
    menu.add_row().add_action(
        f"mod:antiflood:toggle:{'on' if config and config.antiflood_enabled else 'off'}",
        f"{antiflood_status} Anti-Flood",
        "🌊"
    )

    antichannel_status = "✅" if config and config.antichannel_enabled else "❌"
    antilink_status = "✅" if config and config.antilink_enabled else "❌"

    menu.add_row() \
        .add_action("mod:antichannel:show", f"{antichannel_status} Anti-Canal", "📢") \
        .add_action("mod:antilink:show", f"{antilink_status} Anti-Enlaces", "🔗")

    menu.add_row().add_action("mod:media:show", "📸 Moderación Media", "📸")

    blocked_count = len(config.blocked_words) if config else 0
    menu.add_row().add_action(
        "mod:words:show",
        f"🔇 Palabras Bloqueadas ({blocked_count})",
        "🔇"
    )

    nightmode_status = "🌙" if config and config.nightmode_enabled else "☀️"
    menu.add_row().add_action(
        "mod:nightmode:show",
        f"{nightmode_status} Modo Nocturno",
        "🌙"
    )

    menu.add_row().add_action("nav:back:main", "🔙 Volver", "🔙")

    return menu


def create_antichannel_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the anti-channel settings menu."""
    menu = MenuDefinition(
        menu_id="mod:antichannel",
        title="📢 Configuración Anti-Canal",
        parent_menu="main",
    )

    enabled = config.antichannel_enabled if config else False
    status = "✅ Activado" if enabled else "❌ Desactivado"

    menu.add_row().add_action(f"mod:antichannel:toggle:{'on' if enabled else 'off'}", f"{status} (Toggle)", "🔄")
    menu.add_row().add_action("nav:back:main", "🔙 Volver", "🔙")

    return menu


def create_antilink_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the anti-link settings menu."""
    menu = MenuDefinition(
        menu_id="mod:antilink",
        title="🔗 Configuración Anti-Enlaces",
        parent_menu="main",
    )

    enabled = config.antilink_enabled if config else False
    status = "✅ Activado" if enabled else "❌ Desactivado"

    menu.add_row().add_action(f"mod:antilink:toggle:{'on' if enabled else 'off'}", f"{status} (Toggle)", "🔄")
    menu.add_row().add_action("nav:back:main", "🔙 Volver", "🔙")

    return menu


def create_media_moderation_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the media moderation settings menu."""
    menu = MenuDefinition(
        menu_id="mod:media",
        title="📸 Moderación de Multimedia",
        parent_menu="main",
    )

    restrictions = config.media_restrictions if config else {}
    
    menu.add_row().add_action(f"mod:media:photo:toggle:{'on' if restrictions.get('photo') else 'off'}", "📷 Fotos", "📷")
    menu.add_row().add_action(f"mod:media:video:toggle:{'on' if restrictions.get('video') else 'off'}", "🎬 Videos", "🎬")
    menu.add_row().add_action(f"mod:media:document:toggle:{'on' if restrictions.get('document') else 'off'}", "📄 Documentos", "📄")
    menu.add_row().add_action(f"mod:media:sticker:toggle:{'on' if restrictions.get('sticker') else 'off'}", "😀 Stickers", "😀")
    menu.add_row().add_action("nav:back:main", "🔙 Volver", "🔙")

    return menu


def create_blocked_words_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the blocked words menu."""
    menu = MenuDefinition(
        menu_id="mod:words",
        title="🔇 Palabras Bloqueadas",
        parent_menu="main",
    )

    words = config.blocked_words if config else []
    if words:
        for word in words[:10]:
            menu.add_row().add_action(f"mod:words:del:{word}", f"❌ {word}", "❌")
        
        if len(words) > 10:
            menu.add_row().add_action("mod:words:page:1", f"📄 Más ({len(words) - 10})", "📄")
    else:
        menu.add_row().add_action("mod:words:add", "➕ Agregar palabra", "➕")

    menu.add_row().add_action("nav:back:main", "🔙 Volver", "🔙")

    return menu


def create_nightmode_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the night mode settings menu."""
    menu = MenuDefinition(
        menu_id="mod:nightmode",
        title="🌙 Modo Nocturno",
        parent_menu="main",
    )

    enabled = config.nightmode_enabled if config else False
    status = "✅ Activado" if enabled else "❌ Desactivado"

    menu.add_row().add_action(f"mod:nightmode:toggle:{'on' if enabled else 'off'}", f"{status} (Toggle)", "🔄")

    if enabled:
        menu.add_row().add_action(
            "mod:nightmode:time",
            f"⏰ {config.nightmode_start} - {config.nightmode_end}" if config else "⏰ Horario",
            "⏰"
        )

    menu.add_row().add_action("nav:back:main", "🔙 Volver", "🔙")

    return menu
