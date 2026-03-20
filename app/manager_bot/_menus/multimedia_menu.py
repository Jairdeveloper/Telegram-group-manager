"""Multimedia moderation menu definitions."""

from typing import Optional, Dict

from app.manager_bot._config.group_config import GroupConfig
from app.manager_bot._menus.base import MenuDefinition
from app.manager_bot._menus.formatters import duration_label
from app.manager_bot._menus.rendering import build_title

MULTIMEDIA_TYPES_PAGE1 = [
    ("story", "📲 Historia", "multimedia_story_action"),
    ("photo", "📸 Foto", "multimedia_photo_action"),
    ("video", "🎞 Video", "multimedia_video_action"),
    ("album", "🖼 Album", "multimedia_album_action"),
    ("gif", "🎥 Gif", "multimedia_gif_action"),
    ("voice", "🎤 Voz", "multimedia_voice_action"),
    ("audio", "🎧 Audio", "multimedia_audio_action"),
    ("sticker", "🃏 Sticker", "multimedia_sticker_action"),
    ("animated_sticker", "🎭 Sticker anim", "multimedia_animated_sticker_action"),
    ("game_sticker", "🎲 Sticker juego", "multimedia_game_sticker_action"),
    ("animated_emoji", "😀 Emoji anim", "multimedia_animated_emoji_action"),
    ("custom_emoji", "👾 Emoji custom", "multimedia_custom_emoji_action"),
    ("file", "💾 Archivo", "multimedia_file_action"),
]

MULTIMEDIA_TYPES_PAGE2 = [
    ("game", "🎮 Juegos", "multimedia_game_action"),
    ("contact", "☎️ Contactos", "multimedia_contact_action"),
    ("poll", "📊 Encuestas", "multimedia_poll_action"),
    ("checklist", "📋 Checklist", "multimedia_checklist_action"),
    ("location", "📍 Ubicacion", "multimedia_location_action"),
    ("caps", "🆎 Mayusculas", "multimedia_caps_action"),
    ("payment", "💶 Pagos", "multimedia_payment_action"),
    ("inline_bot", "🤖 Bot Inline", "multimedia_inline_bot_action"),
    ("spoiler", "🗯 Spoiler", "multimedia_spoiler_action"),
    ("spoiler_media", "🌌 Spoiler media", "multimedia_spoiler_media_action"),
    ("video_note", "👁‍🗨 Video note", "multimedia_video_note_action"),
    ("giveaway", "🎁 Sorteo", "multimedia_giveaway_action"),
]

ACTION_ICONS = {
    "warn": "❕",
    "mute": "🔇",
    "delete": "🗑",
    "kick": "❗️",
    "ban": "🚷",
    "off": "☑️",
}

ACTIONS = ["warn", "mute", "delete", "kick", "ban", "off"]


def _get_action_icon(action: str) -> str:
    return ACTION_ICONS.get(action, "☑️")


def _build_multimedia_title(config: Optional[GroupConfig], types: list) -> str:
    """Build the dynamic title with current states."""
    static_header = "❕=Warn | ❗️=Kick | 🔇=Silenciar | 🚷=Ban | 🗑=Eliminacion | ☑️=Off"
    
    states = []
    for tipo, emoji_with_label, field in types:
        action = getattr(config, field, "off") if config else "off"
        icon = ACTION_ICONS.get(action, "☑️")
        states.append(f"{emoji_with_label} = {icon} {action.capitalize()}")
    
    return (
        f"Multimedia\n"
        f"{static_header}\n"
        f"______________________________\n\n"
        + "\n".join(states)
    )


def _build_action_buttons(
    config: Optional[GroupConfig],
    type_key: str,
    field_name: str,
    menu: MenuDefinition,
) -> None:
    current_action = getattr(config, field_name, "off") if config else "off"
    for action in ACTIONS:
        is_current = current_action == action
        icon = _get_action_icon(action)
        label = f"[{icon}]" if is_current else icon
        menu.add_row().add_action(
            f"multimedia:{type_key}:action:{action}",
            label,
        )


def _build_matrix_row(
    emoji: str,
    type_key: str,
    config: Optional[GroupConfig],
    field_name: str,
    menu: MenuDefinition,
) -> None:
    current_action = getattr(config, field_name, "off") if config else "off"
    row = menu.add_row()
    row.add_action(f"multimedia:{type_key}:select", emoji)
    for action in ACTIONS:
        is_current = current_action == action
        icon = _get_action_icon(action)
        label_text = f"[{icon}]" if is_current else icon
        row.add_action(f"multimedia:{type_key}:action:{action}", label_text)


def create_multimedia_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the main Multimedia menu (Page 1)."""
    title = _build_multimedia_title(config, MULTIMEDIA_TYPES_PAGE1)

    menu = MenuDefinition(
        menu_id="multimedia",
        title=title,
        parent_menu="main",
    )

    for type_key, emoji, field_name in MULTIMEDIA_TYPES_PAGE1:
        _build_matrix_row(emoji, type_key, config, field_name, menu)

    menu.add_row() \
        .add_action("nav:back:main", "Volver") \
        .add_action("multimedia:duration:show", "⏱ Duracion") \
        .add_action("multimedia:page2:show", "Mas")

    return menu


def create_multimedia_page2_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the Multimedia menu (Page 2)."""
    title = _build_multimedia_title(config, MULTIMEDIA_TYPES_PAGE2)

    menu = MenuDefinition(
        menu_id="multimedia:page2",
        title=title,
        parent_menu="main",
    )

    for type_key, emoji, field_name in MULTIMEDIA_TYPES_PAGE2:
        _build_matrix_row(emoji, type_key, config, field_name, menu)

    menu.add_row() \
        .add_action("nav:back:main", "Volver") \
        .add_action("multimedia:duration:show", "⏱ Duracion") \
        .add_action("multimedia:page1:show", "Atras")

    return menu


def create_multimedia_duration_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the Multimedia duration settings menu."""
    mute_duration = duration_label(
        config.multimedia_mute_duration_sec if config else None
    )
    ban_duration = duration_label(
        config.multimedia_ban_duration_sec if config else None
    )

    text = build_title(
        "Duracion de Multimedia\n"
        "Configura la duracion de los castigos para contenido multimedia.\n\n"
        "Minimo: 30 segundos\n"
        "Maximo: 365 dias\n\n"
        "Formato ejemplo: 3 months 2 days 12 hours",
        [
            f"Duracion Mute: {mute_duration}",
            f"Duracion Ban: {ban_duration}",
        ],
    )

    menu = MenuDefinition(
        menu_id="multimedia:duration",
        title=text,
        parent_menu="multimedia",
    )

    menu.add_row() \
        .add_action("multimedia:duration:mute:show", f"Duracion Mute ({mute_duration})")
    menu.add_row() \
        .add_action("multimedia:duration:ban:show", f"Duracion Ban ({ban_duration})")

    menu.add_row() \
        .add_action("multimedia:duration:clear", "Limpiar duraciones")

    menu.add_row() \
        .add_action("multimedia:show", "Volver")

    return menu


def create_multimedia_mute_duration_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the mute duration input menu."""
    current = duration_label(config.multimedia_mute_duration_sec if config else None)
    text = build_title(
        "Duracion de Silenciar\n"
        "Envia ahora la duracion del castigo (Silenciar).\n\n"
        "Minimo: 30 segundos\n"
        "Maximo: 365 dias\n\n"
        "Formato ejemplo: 3 months 2 days 12 hours 4 minutes 34 seconds\n\n"
        f"Duracion actual: {current}",
        [],
    )

    menu = MenuDefinition(
        menu_id="multimedia:mute:duration",
        title=text,
        parent_menu="multimedia:duration",
    )

    menu.add_row().add_action("multimedia:duration:clear:mute", "Eliminar duracion")
    menu.add_row().add_action("multimedia:duration:show", "Cancelar")

    return menu


def create_multimedia_ban_duration_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the ban duration input menu."""
    current = duration_label(config.multimedia_ban_duration_sec if config else None)
    text = build_title(
        "Duracion de Ban\n"
        "Envia ahora la duracion del castigo (Ban).\n\n"
        "Minimo: 30 segundos\n"
        "Maximo: 365 dias\n\n"
        "Formato ejemplo: 3 months 2 days 12 hours 4 minutes 34 seconds\n\n"
        f"Duracion actual: {current}",
        [],
    )

    menu = MenuDefinition(
        menu_id="multimedia:ban:duration",
        title=text,
        parent_menu="multimedia:duration",
    )

    menu.add_row().add_action("multimedia:duration:clear:ban", "Eliminar duracion")
    menu.add_row().add_action("multimedia:duration:show", "Cancelar")

    return menu
