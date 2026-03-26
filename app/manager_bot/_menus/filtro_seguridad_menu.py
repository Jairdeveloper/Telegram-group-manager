"""Filtro de Seguridad menu definitions."""

from typing import Optional

from app.manager_bot._menus.base import MenuDefinition
from app.manager_bot._config.group_config import GroupConfig


FILTRO_OBLIGATIONS = ["username", "photo", "channel", "add_users"]

FILTRO_OBLIGATION_LABELS = {
    "username": "Username",
    "photo": "Foto de Perfil",
    "channel": "Union Canal",
    "add_users": "Aniadir Usuarios",
}

FILTRO_BLOCKS = ["arabic", "chinese", "russian", "spam"]

FILTRO_BLOCK_LABELS = {
    "arabic": "Nombre Arabe",
    "chinese": "Nombre Chino",
    "russian": "Nombre Ruso",
    "spam": "Nombre Spam",
}

FILTRO_ACTIONS = ["kick", "ban", "silenciar", "off", "warn", "aviso"]

FILTRO_ACTION_LABELS = {
    "kick": "Kick",
    "ban": "Ban",
    "silenciar": "Silenciar",
    "off": "Apagado",
    "warn": "Warn",
    "aviso": "Aviso",
}


def _get_obligation_field(obligation_type: str) -> str:
    """Get the config field name for an obligation type."""
    field_map = {
        "username": "filtro_obligation_username_action",
        "photo": "filtro_obligation_photo_action",
        "channel": "filtro_obligation_channel_action",
        "add_users": "filtro_obligation_add_users_action",
    }
    return field_map.get(obligation_type, "")


def _get_action_for_obligation(config: Optional[GroupConfig], obligation_type: str) -> str:
    """Get current action for an obligation type."""
    field = _get_obligation_field(obligation_type)
    if config and field:
        return getattr(config, field, "off")
    return "off"


def _get_block_field(block_type: str) -> str:
    """Get the config field name for a block type."""
    field_map = {
        "arabic": "filtro_block_arabic_action",
        "chinese": "filtro_block_chinese_action",
        "russian": "filtro_block_russian_action",
        "spam": "filtro_block_spam_action",
    }
    return field_map.get(block_type, "")


def _get_action_for_block(config: Optional[GroupConfig], block_type: str) -> str:
    """Get current action for a block type."""
    field = _get_block_field(block_type)
    if config and field:
        return getattr(config, field, "off")
    return "off"


def _build_filtro_title(config: Optional[GroupConfig]) -> str:
    """Build the dynamic title for filtro menu."""
    on_entry = config.filtro_on_entry if config else True
    delete_msgs = config.filtro_delete_messages if config else False

    on_entry_icon = "✅" if on_entry else "❌"
    delete_icon = "✅" if delete_msgs else "❌"

    title = (
        "🔦 Filtros de Seguridad\n\n"
        "El bot aplica controles automaticos a todos los usuarios, ya sea cuando ingresan "
        "o mientras estan activos en el chat.\n\n"
        "‼️ Obligaciones:\n"
        f"  • Username: {_get_action_for_obligation(config, 'username').capitalize()}\n"
        f"  • Foto de Perfil: {_get_action_for_obligation(config, 'photo').capitalize()}\n"
        f"  • Union Canal: {_get_action_for_obligation(config, 'channel').capitalize()}\n"
        f"  • Aniadir Usuarios: {_get_action_for_obligation(config, 'add_users').capitalize()}\n\n"
        "🚫 Bloquear:\n"
        f"  • Nombre Arabe: {_get_action_for_block(config, 'arabic').capitalize()}\n"
        f"  • Nombre Chino: {_get_action_for_block(config, 'chinese').capitalize()}\n"
        f"  • Nombre Ruso: {_get_action_for_block(config, 'russian').capitalize()}\n"
        f"  • Nombre Spam: {_get_action_for_block(config, 'spam').capitalize()}\n\n"
        f"🚪 Filtrar al ingreso: {on_entry_icon}\n"
        f"🗑 Borrar los Mensajes: {delete_icon}"
    )

    return title


def create_filtro_seguridad_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the main Filtro menu."""
    title = _build_filtro_title(config)

    menu = MenuDefinition(
        menu_id="filtro_seguridad",
        title=title,
        parent_menu="main",
    )

    menu.add_row().add_action("filtro_seguridad:obligation:show", "Obligaciones")
    menu.add_row().add_action("filtro_seguridad:block:show", "Bloquear")
    menu.add_row().add_action("filtro_seguridad:config:show", "Configuracion")

    menu.add_row().add_action("nav:back:main", "Volver")

    return menu


def create_obligation_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the Obligations submenu."""
    title = (
        "Obligaciones\n\n"
        "Configura que accion tomar cuando un usuario no cumpla con las obligaciones."
    )

    menu = MenuDefinition(
        menu_id="filtro_seguridad:obligation",
        title=title,
        parent_menu="filtro_seguridad",
    )

    for obligation_type in FILTRO_OBLIGATIONS:
        label = FILTRO_OBLIGATION_LABELS.get(obligation_type, obligation_type)
        current_action = _get_action_for_obligation(config, obligation_type)
        current_label = FILTRO_ACTION_LABELS.get(current_action, current_action)

        menu.add_row().add_action(
            f"filtro_seguridad:obligation:{obligation_type}:show",
            f"{label}: {current_label}",
        )

    menu.add_row().add_action("filtro_seguridad:show", "Volver")

    return menu


def create_obligation_action_menu(
    obligation_type: str, config: Optional[GroupConfig] = None
) -> MenuDefinition:
    """Create the action selection menu for a specific obligation."""
    label = FILTRO_OBLIGATION_LABELS.get(obligation_type, obligation_type)
    current_action = _get_action_for_obligation(config, obligation_type)
    current_label = FILTRO_ACTION_LABELS.get(current_action, current_action)

    title = (
        f"Accion: {label}\n\n"
        f"Accion actual: {current_label}"
    )

    menu = MenuDefinition(
        menu_id=f"filtro_seguridad:obligation:{obligation_type}",
        title=title,
        parent_menu="filtro_seguridad:obligation",
    )

    for action in FILTRO_ACTIONS:
        action_label = FILTRO_ACTION_LABELS.get(action, action)
        is_current = action == current_action
        menu.add_row().add_action(
            f"filtro_seguridad:obligation:{action}:{obligation_type}",
            f"[{action_label}]" if is_current else action_label,
        )

    menu.add_row().add_action(f"filtro_seguridad:obligation:show", "Volver")

    return menu


def create_block_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the Blocks submenu."""
    title = (
        "Bloquear Nombres\n\n"
        "Configura que accion tomar cuando un usuario tenga un nombre en el idioma seleccionado."
    )

    menu = MenuDefinition(
        menu_id="filtro_seguridad:block",
        title=title,
        parent_menu="filtro_seguridad",
    )

    for block_type in FILTRO_BLOCKS:
        label = FILTRO_BLOCK_LABELS.get(block_type, block_type)
        current_action = _get_action_for_block(config, block_type)
        current_label = FILTRO_ACTION_LABELS.get(current_action, current_action)

        menu.add_row().add_action(
            f"filtro_seguridad:block:{block_type}:show",
            f"{label}: {current_label}",
        )

    menu.add_row().add_action("filtro_seguridad:show", "Volver")

    return menu


def create_block_action_menu(
    block_type: str, config: Optional[GroupConfig] = None
) -> MenuDefinition:
    """Create the action selection menu for a specific block type."""
    label = FILTRO_BLOCK_LABELS.get(block_type, block_type)
    current_action = _get_action_for_block(config, block_type)
    current_label = FILTRO_ACTION_LABELS.get(current_action, current_action)

    title = (
        f"Bloquear: {label}\n\n"
        f"Accion actual: {current_label}"
    )

    menu = MenuDefinition(
        menu_id=f"filtro_seguridad:block:{block_type}",
        title=title,
        parent_menu="filtro_seguridad:block",
    )

    for action in FILTRO_ACTIONS:
        action_label = FILTRO_ACTION_LABELS.get(action, action)
        is_current = action == current_action
        menu.add_row().add_action(
            f"filtro_seguridad:block:{action}:{block_type}",
            f"[{action_label}]" if is_current else action_label,
        )

    menu.add_row().add_action(f"filtro_seguridad:block:show", "Volver")

    return menu


def create_config_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the general Configuration submenu."""
    on_entry = config.filtro_on_entry if config else True
    delete_msgs = config.filtro_delete_messages if config else False

    on_entry_status = "Activo" if on_entry else "Apagado"
    delete_status = "Activo" if delete_msgs else "Apagado"

    title = (
        "Configuracion General\n\n"
        f"🚪 Filtrar al ingreso: {on_entry_status}\n"
        f"   Si esta activo, el bot verificara Obligaciones/Bloqueos cuando el usuario se una al grupo.\n"
        f"   En cambio si no, solo lohara cuando el usuario envie un mensaje.\n\n"
        f"🗑 Borrar los Mensajes: {delete_status}\n"
        f"   Si esta activo, el bot eliminara todos los mensajes enviados por usuarios\n"
        f"   que no cumplan con las Obligaciones/Bloqueos."
    )

    menu = MenuDefinition(
        menu_id="filtro_seguridad:config",
        title=title,
        parent_menu="filtro_seguridad",
    )

    on_entry_next = "off" if on_entry else "on"
    menu.add_row().add_action(
        f"filtro_seguridad:config:on_entry:{on_entry_next}",
        f"Filtrar al ingreso: {'Desactivar' if on_entry else 'Activar'}",
    )

    delete_next = "off" if delete_msgs else "on"
    menu.add_row().add_action(
        f"filtro_seguridad:config:delete:{delete_next}",
        f"Borrar mensajes: {'Desactivar' if delete_msgs else 'Activar'}",
    )

    menu.add_row().add_action("filtro_seguridad:show", "Volver")

    return menu
