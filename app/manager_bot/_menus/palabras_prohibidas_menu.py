"""Palabras Prohibidas menu definitions."""

from typing import Optional

from app.manager_bot._menus.base import MenuDefinition
from app.manager_bot._config.group_config import GroupConfig


PALABRAS_ACCIONES = ["kick", "ban", "silenciar", "warn", "aviso", "off"]

PALABRAS_ACCION_LABELS = {
    "kick": "Kick",
    "ban": "Ban",
    "silenciar": "Silenciar",
    "warn": "Warn",
    "aviso": "Aviso",
    "off": "Apagado",
}


def _get_action_label(action: str) -> str:
    """Get label for action."""
    return PALABRAS_ACCION_LABELS.get(action, action)


def create_palabras_prohibidas_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the main Palabras Prohibidas menu."""
    enabled = config.blocked_words_enabled if config else True
    action = config.blocked_words_action if config else "off"
    delete = config.blocked_words_delete if config else False
    words_count = len(config.blocked_words) if config else 0

    status = "✅ Activo" if enabled else "❌ Apagado"
    action_label = _get_action_label(action)
    delete_status = "Si" if delete else "No"

    title = (
        f"🔤 Palabras Prohibidas\n\n"
        f"Estado: {status}\n"
        f"Castigo: {action_label}\n"
        f"Eliminacion: {delete_status}\n"
        f"Palabras: {words_count}"
    )

    menu = MenuDefinition(
        menu_id="palabras_prohibidas",
        title=title,
        parent_menu="main",
    )

    menu.add_row() \
        .add_action(f"palabras_prohibidas:action:show", "Accion") \
        .add_action("palabras_prohibidas:list", f"Ver Palabras ({words_count})")

    menu.add_row() \
        .add_action("palabras_prohibidas:delete:show", "Eliminacion") \
        .add_action("palabras_prohibidas:add", "Agregar Palabra")

    menu.add_row() \
        .add_action("palabras_prohibidas:clear", "Eliminar Todas")

    menu.add_row() \
        .add_action("palabras_prohibidas:toggle", "Activar/Desactivar")

    menu.add_row().add_action("nav:back:main", "Volver")

    return menu


def create_palabras_prohibidas_action_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the action selection menu."""
    current_action = config.blocked_words_action if config else "off"

    title = (
        f"Accion de Castigo\n\n"
        f"Castigo actual: {_get_action_label(current_action)}\n\n"
        f"Selecciona la accion que se tomara cuando un usuario\n"
        f"utilice una palabra prohibida."
    )

    menu = MenuDefinition(
        menu_id="palabras_prohibidas:action",
        title=title,
        parent_menu="palabras_prohibidas",
    )

    for action in PALABRAS_ACCIONES:
        action_label = _get_action_label(action)
        is_current = action == current_action
        menu.add_row().add_action(
            f"palabras_prohibidas:action:{action}",
            f"[{action_label}]" if is_current else action_label,
        )

    menu.add_row().add_action("palabras_prohibidas:show", "Volver")

    return menu


def create_palabras_prohibidas_delete_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the delete toggle menu."""
    current_delete = config.blocked_words_delete if config else False

    title = (
        f"Eliminacion de Mensajes\n\n"
        f"Estado actual: {'Si' if current_delete else 'No'}\n\n"
        f"Si esta activo, se eliminaran automaticamente los mensajes\n"
        f"que contengan palabras prohibidas."
    )

    menu = MenuDefinition(
        menu_id="palabras_prohibidas:delete",
        title=title,
        parent_menu="palabras_prohibidas",
    )

    next_delete = not current_delete
    menu.add_row() \
        .add_action(f"palabras_prohibidas:delete:{'on' if next_delete else 'off'}",
                    "Activar Eliminacion" if next_delete else "Desactivar Eliminacion")

    menu.add_row().add_action("palabras_prohibidas:show", "Volver")

    return menu


def create_palabras_prohibidas_add_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the add word menu."""
    title = (
        "Agregar Palabra Prohibida\n\n"
        "Envia la palabra o frase que deseas prohibir.\n"
        "El mensaje sera eliminado automaticamente."
    )

    menu = MenuDefinition(
        menu_id="palabras_prohibidas:add",
        title=title,
        parent_menu="palabras_prohibidas",
    )

    menu.add_row().add_action("palabras_prohibidas:show", "Volver")

    return menu


def create_palabras_prohibidas_list_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the words list menu."""
    words = config.blocked_words if config else []
    words_count = len(words)

    title = (
        f"Lista de Palabras Prohibidas\n\n"
        f"Total: {words_count}\n\n"
        f"Toca una palabra para eliminarla."
    )

    menu = MenuDefinition(
        menu_id="palabras_prohibidas:list",
        title=title,
        parent_menu="palabras_prohibidas",
    )

    if words:
        for word in words[:10]:
            menu.add_row().add_action(
                f"palabras_prohibidas:del:{word}",
                f"Eliminar: {word[:30]}",
            )
        if len(words) > 10:
            menu.add_row().add_action(
                "palabras_prohibidas:list:page:1",
                f"Mas ({len(words) - 10})"
            )
    else:
        menu.add_row().add_action("palabras_prohibidas:add", "Agregar primera palabra")

    menu.add_row().add_action("palabras_prohibidas:show", "Volver")

    return menu
