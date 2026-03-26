"""Antispam menu definitions (includes antispan advanced menus)."""

from typing import Optional

from app.manager_bot._menus.base import MenuDefinition
from app.manager_bot._config.group_config import GroupConfig
from app.manager_bot._menus.formatters import yes_no, on_off, action_label, duration_label
from app.manager_bot._menus.rendering import build_title, build_section


def create_antispam_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the antispam settings menu."""
    antispam_enabled = config.antispam_enabled if config else False
    spamwatch_enabled = config.spamwatch_enabled if config else False
    sibyl_enabled = config.sibyl_enabled if config else False

    title = build_title(
        "Configuracion Antispam",
        [
            build_section("Estado", on_off(antispam_enabled)),
            build_section("SpamWatch", yes_no(spamwatch_enabled)) if antispam_enabled else "",
            build_section("Sibyl", yes_no(sibyl_enabled)) if antispam_enabled else "",
        ],
    )

    menu = MenuDefinition(
        menu_id="antispam",
        title=title,
        parent_menu="main",
    )

    antispam_status = "Activado" if antispam_enabled else "Desactivado"

    menu.add_row().add_action(
        f"antispam:toggle:{'on' if antispam_enabled else 'off'}",
        f"{antispam_status} Antispam General",
    )

    if antispam_enabled:
        spamwatch_status = "ON" if spamwatch_enabled else "OFF"
        menu.add_row().add_action(
            f"antispam:spamwatch:toggle:{'on' if spamwatch_enabled else 'off'}",
            f"{spamwatch_status} SpamWatch",
        )

        sibyl_status = "ON" if sibyl_enabled else "OFF"
        menu.add_row().add_action(
            f"antispam:sibyl:toggle:{'on' if sibyl_enabled else 'off'}",
            f"{sibyl_status} Sibyl",
        )

        menu.add_row().add_action("antispam:sensitivity:show", "Sensibilidad")

    menu.add_row().add_action("antispan:telegram:show", "Telegram")
    menu.add_row() \
        .add_action("antispan:forward:show", "Reenvio") \
        .add_action("antispan:quotes:show", "Citas")
    menu.add_row().add_action("antispan:internet:show", "General de internet")
    menu.add_row().add_action("nav:back:main", "Volver")

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


def _format_duration(seconds: Optional[int]) -> str:
    return duration_label(seconds)


def _format_action(action: str, mute_sec: Optional[int], ban_sec: Optional[int]) -> str:
    return action_label(action, mute_sec, ban_sec)


def create_antispan_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Backward-compatible alias to the Antispam menu."""
    return create_antispam_menu(config)


def create_antispan_telegram_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    action_text = _format_action(
        config.antispan_telegram_action if config else "off",
        config.antispan_telegram_mute_duration_sec if config else None,
        config.antispan_telegram_ban_duration_sec if config else None,
    )
    delete_text = "Si" if config and config.antispan_telegram_delete_messages else "No"
    usernames = "Si" if config and config.antispan_telegram_usernames_enabled else "No"
    bots = "Si" if config and config.antispan_telegram_bots_enabled else "No"

    menu = MenuDefinition(
        menu_id="antispan:telegram",
        title=(
            "Telegram\n"
            "Desde este menu puedes establecer un castigo para los usuarios que envien mensajes que contengan enlaces de Telegram.\n\n"
            f"Castigo: {action_text}\n"
            f"Eliminacion: {delete_text}\n"
            f"Antispan de usernames: {usernames}\n"
            f"Antispan de bots: {bots}"
        ),
        parent_menu="antispam",
    )

    menu.add_row() \
        .add_action("antispan:telegram:action:off", "Off") \
        .add_action("antispan:telegram:action:warn", "Warn") \
        .add_action("antispan:telegram:action:kick", "Kick")

    menu.add_row() \
        .add_action("antispan:telegram:action:mute", "Silenciar") \
        .add_action("antispan:telegram:action:ban", "Ban")

    delete_toggle = "off" if config and config.antispan_telegram_delete_messages else "on"
    menu.add_row().add_action(
        f"antispan:telegram:delete:toggle:{delete_toggle}",
        "Borrar los Mensajes",
    )

    if config and config.antispan_telegram_action == "mute":
        menu.add_row().add_action("antispan:telegram:mute:duration:show", "Escoger duracion de silencio")
    if config and config.antispan_telegram_action == "ban":
        menu.add_row().add_action("antispan:telegram:ban:duration:show", "Escoger duracion de ban")

    usernames_toggle = "off" if config and config.antispan_telegram_usernames_enabled else "on"
    menu.add_row().add_action(
        f"antispan:telegram:usernames:toggle:{usernames_toggle}",
        "Antispan de usernames",
    )

    bots_toggle = "off" if config and config.antispan_telegram_bots_enabled else "on"
    menu.add_row().add_action(
        f"antispan:telegram:bots:toggle:{bots_toggle}",
        "Antispan de bots",
    )

    menu.add_row() \
        .add_action("nav:back:antispam", "Volver") \
        .add_action("antispan:telegram:exceptions:show", "Excepciones")

    return menu


def create_antispan_telegram_exceptions_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    menu = MenuDefinition(
        menu_id="antispan:telegram:exceptions",
        title=(
            "Excepciones Antispan\n"
            "Edita aqui los enlaces/@username de canales/grupos de telegram que no seran considerados como spam.\n\n"
            "El enlace de invitacion de este grupo esta automaticamente en las excepciones."
        ),
        parent_menu="antispan:telegram",
    )

    menu.add_row().add_action("antispan:telegram:exceptions:list", "Lista Blanca")
    menu.add_row() \
        .add_action("antispan:telegram:exceptions:add", "Anadir") \
        .add_action("antispan:telegram:exceptions:remove", "Eliminar")
    menu.add_row().add_action("antispan:telegram:exceptions:global", "Lista Blanca Global")
    menu.add_row().add_action("antispan:telegram:show", "Volver")
    return menu


def create_antispan_telegram_exception_input_menu(mode: str) -> MenuDefinition:
    title = (
        "OK, ahora envia uno o mas enlaces o @username de canales/grupos para "
        f"{'agregarlos' if mode == 'add' else 'eliminarlos'} de la Lista Blanca.\n\n"
        "Envia un enlace/username en cada linea."
    )
    menu = MenuDefinition(
        menu_id=f"antispan:telegram:exceptions:{mode}",
        title=title,
        parent_menu="antispan:telegram:exceptions",
    )
    menu.add_row().add_action("antispan:telegram:exceptions:show", "Cancelar")
    return menu


def create_antispan_forward_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    menu = MenuDefinition(
        menu_id="antispan:forward",
        title=(
            "Reenvio\n"
            "Desde este menu puedes seleccionar un castigo para cualquier usuario que reenvie mensajes al grupo."
        ),
        parent_menu="antispam",
    )

    channels = config.antispan_forward_channels_action if config else "off"
    groups = config.antispan_forward_groups_action if config else "off"
    users = config.antispan_forward_users_action if config else "off"
    bots = config.antispan_forward_bots_action if config else "off"

    menu.add_row().add_action("antispan:forward:channels:show", f"Canales ({channels})")
    menu.add_row() \
        .add_action("antispan:forward:groups:show", f"Grupos ({groups})") \
        .add_action("antispan:forward:users:show", f"Usuarios ({users})")
    menu.add_row().add_action("antispan:forward:bots:show", f"Bots ({bots})")
    menu.add_row() \
        .add_action("nav:back:antispam", "Volver") \
        .add_action("antispan:forward:exceptions:show", "Excepciones")

    return menu


def create_antispan_forward_target_menu(target: str, config: Optional[GroupConfig] = None) -> MenuDefinition:
    action = "off"
    if config:
        if target == "channels":
            action = config.antispan_forward_channels_action
        elif target == "groups":
            action = config.antispan_forward_groups_action
        elif target == "users":
            action = config.antispan_forward_users_action
        elif target == "bots":
            action = config.antispan_forward_bots_action

    menu = MenuDefinition(
        menu_id=f"antispan:forward:{target}",
        title=f"Reenvio ({target})\nCastigo: {action}",
        parent_menu="antispan:forward",
    )

    menu.add_row() \
        .add_action(f"antispan:forward:{target}:action:off", "Off") \
        .add_action(f"antispan:forward:{target}:action:warn", "Warn") \
        .add_action(f"antispan:forward:{target}:action:kick", "Kick")
    menu.add_row() \
        .add_action(f"antispan:forward:{target}:action:mute", "Silenciar") \
        .add_action(f"antispan:forward:{target}:action:ban", "Ban")

    delete_toggle = "off" if config and config.antispan_forward_delete_messages else "on"
    menu.add_row().add_action(
        f"antispan:forward:delete:toggle:{delete_toggle}",
        "Borrar los Mensajes",
    )

    menu.add_row().add_action("antispan:forward:mute:duration:show", "Escoger duracion de silencio")
    menu.add_row().add_action("antispan:forward:ban:duration:show", "Escoger duracion de ban")
    menu.add_row() \
        .add_action("antispan:forward:show", "Volver") \
        .add_action("antispan:forward:exceptions:show", "Excepciones")
    return menu


def create_antispan_forward_exceptions_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    menu = MenuDefinition(
        menu_id="antispan:forward:exceptions",
        title="Excepciones Reenvio",
        parent_menu="antispan:forward",
    )
    menu.add_row().add_action("antispan:forward:exceptions:list", "Lista Blanca")
    menu.add_row() \
        .add_action("antispan:forward:exceptions:add", "Anadir") \
        .add_action("antispan:forward:exceptions:remove", "Eliminar")
    menu.add_row().add_action("antispan:forward:exceptions:global", "Lista Blanca Global")
    menu.add_row().add_action("antispan:forward:show", "Volver")
    return menu


def create_antispan_forward_exception_input_menu(mode: str) -> MenuDefinition:
    menu = MenuDefinition(
        menu_id=f"antispan:forward:exceptions:{mode}",
        title=f"Envia los enlaces/usernames a {('agregar' if mode == 'add' else 'eliminar')} de la lista blanca.",
        parent_menu="antispan:forward:exceptions",
    )
    menu.add_row().add_action("antispan:forward:exceptions:show", "Cancelar")
    return menu


def create_antispan_quotes_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    menu = MenuDefinition(
        menu_id="antispan:quotes",
        title=(
            "Citas\n"
            "Desde este menu puedes seleccionar un castigo para mensajes que contengan citas de chats externos."
        ),
        parent_menu="antispam",
    )

    channels = config.antispan_quotes_channels_action if config else "off"
    groups = config.antispan_quotes_groups_action if config else "off"
    users = config.antispan_quotes_users_action if config else "off"
    bots = config.antispan_quotes_bots_action if config else "off"

    menu.add_row().add_action("antispan:quotes:channels:show", f"Canales ({channels})")
    menu.add_row() \
        .add_action("antispan:quotes:groups:show", f"Grupos ({groups})") \
        .add_action("antispan:quotes:users:show", f"Usuarios ({users})")
    menu.add_row().add_action("antispan:quotes:bots:show", f"Bots ({bots})")
    menu.add_row() \
        .add_action("nav:back:antispam", "Volver") \
        .add_action("antispan:quotes:exceptions:show", "Excepciones")
    return menu


def create_antispan_quotes_target_menu(target: str, config: Optional[GroupConfig] = None) -> MenuDefinition:
    action = "off"
    if config:
        if target == "channels":
            action = config.antispan_quotes_channels_action
        elif target == "groups":
            action = config.antispan_quotes_groups_action
        elif target == "users":
            action = config.antispan_quotes_users_action
        elif target == "bots":
            action = config.antispan_quotes_bots_action

    menu = MenuDefinition(
        menu_id=f"antispan:quotes:{target}",
        title=f"Citas ({target})\nCastigo: {action}",
        parent_menu="antispan:quotes",
    )

    menu.add_row() \
        .add_action(f"antispan:quotes:{target}:action:off", "Off") \
        .add_action(f"antispan:quotes:{target}:action:warn", "Warn") \
        .add_action(f"antispan:quotes:{target}:action:kick", "Kick")
    menu.add_row() \
        .add_action(f"antispan:quotes:{target}:action:mute", "Silenciar") \
        .add_action(f"antispan:quotes:{target}:action:ban", "Ban")

    delete_toggle = "off" if config and config.antispan_quotes_delete_messages else "on"
    menu.add_row().add_action(
        f"antispan:quotes:delete:toggle:{delete_toggle}",
        "Borrar los Mensajes",
    )

    menu.add_row().add_action("antispan:quotes:mute:duration:show", "Escoger duracion de silencio")
    menu.add_row().add_action("antispan:quotes:ban:duration:show", "Escoger duracion de ban")
    menu.add_row() \
        .add_action("antispan:quotes:show", "Volver") \
        .add_action("antispan:quotes:exceptions:show", "Excepciones")
    return menu


def create_antispan_quotes_exceptions_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    menu = MenuDefinition(
        menu_id="antispan:quotes:exceptions",
        title="Excepciones Citas",
        parent_menu="antispan:quotes",
    )
    menu.add_row().add_action("antispan:quotes:exceptions:list", "Lista Blanca")
    menu.add_row() \
        .add_action("antispan:quotes:exceptions:add", "Anadir") \
        .add_action("antispan:quotes:exceptions:remove", "Eliminar")
    menu.add_row().add_action("antispan:quotes:exceptions:global", "Lista Blanca Global")
    menu.add_row().add_action("antispan:quotes:show", "Volver")
    return menu


def create_antispan_quotes_exception_input_menu(mode: str) -> MenuDefinition:
    menu = MenuDefinition(
        menu_id=f"antispan:quotes:exceptions:{mode}",
        title=f"Envia los enlaces/usernames a {('agregar' if mode == 'add' else 'eliminar')} de la lista blanca.",
        parent_menu="antispan:quotes:exceptions",
    )
    menu.add_row().add_action("antispan:quotes:exceptions:show", "Cancelar")
    return menu


def create_antispan_internet_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    action_text = _format_action(
        config.antispan_internet_action if config else "off",
        config.antispan_internet_mute_duration_sec if config else None,
        config.antispan_internet_ban_duration_sec if config else None,
    )
    delete_text = "Si" if config and config.antispan_internet_delete_messages else "No"

    menu = MenuDefinition(
        menu_id="antispan:internet",
        title=(
            "General de internet\n"
            "Desde este menu puedes establecer un castigo para los usuarios que envien cualquier clase de enlace.\n\n"
            f"Castigo: {action_text}\n"
            f"Eliminacion: {delete_text}"
        ),
        parent_menu="antispam",
    )

    menu.add_row() \
        .add_action("antispan:internet:action:off", "Off") \
        .add_action("antispan:internet:action:warn", "Warn") \
        .add_action("antispan:internet:action:kick", "Kick")
    menu.add_row() \
        .add_action("antispan:internet:action:mute", "Silenciar") \
        .add_action("antispan:internet:action:ban", "Ban")

    delete_toggle = "off" if config and config.antispan_internet_delete_messages else "on"
    menu.add_row().add_action(
        f"antispan:internet:delete:toggle:{delete_toggle}",
        "Borrar los Mensajes",
    )

    if config and config.antispan_internet_action == "mute":
        menu.add_row().add_action("antispan:internet:mute:duration:show", "Escoger duracion de silencio")
    if config and config.antispan_internet_action == "ban":
        menu.add_row().add_action("antispan:internet:ban:duration:show", "Escoger duracion de ban")

    menu.add_row() \
        .add_action("nav:back:antispam", "Volver") \
        .add_action("antispan:internet:exceptions:show", "Excepciones")

    return menu


def create_antispan_internet_exceptions_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    menu = MenuDefinition(
        menu_id="antispan:internet:exceptions",
        title="Excepciones General de internet",
        parent_menu="antispan:internet",
    )
    menu.add_row().add_action("antispan:internet:exceptions:list", "Lista Blanca")
    menu.add_row() \
        .add_action("antispan:internet:exceptions:add", "Anadir") \
        .add_action("antispan:internet:exceptions:remove", "Eliminar")
    menu.add_row().add_action("antispan:internet:exceptions:global", "Lista Blanca Global")
    menu.add_row().add_action("antispan:internet:show", "Volver")
    return menu


def create_antispan_internet_exception_input_menu(mode: str) -> MenuDefinition:
    menu = MenuDefinition(
        menu_id=f"antispan:internet:exceptions:{mode}",
        title=f"Envia los enlaces/usernames a {('agregar' if mode == 'add' else 'eliminar')} de la lista blanca.",
        parent_menu="antispan:internet:exceptions",
    )
    menu.add_row().add_action("antispan:internet:exceptions:show", "Cancelar")
    return menu


def create_antispan_duration_menu(scope: str, kind: str, config: Optional[GroupConfig] = None) -> MenuDefinition:
    current = "sin duracion"
    if config:
        if scope == "telegram":
            current = _format_duration(
                config.antispan_telegram_mute_duration_sec if kind == "mute" else config.antispan_telegram_ban_duration_sec
            )
        elif scope == "forward":
            current = _format_duration(
                config.antispan_forward_mute_duration_sec if kind == "mute" else config.antispan_forward_ban_duration_sec
            )
        elif scope == "quotes":
            current = _format_duration(
                config.antispan_quotes_mute_duration_sec if kind == "mute" else config.antispan_quotes_ban_duration_sec
            )
        elif scope == "internet":
            current = _format_duration(
                config.antispan_internet_mute_duration_sec if kind == "mute" else config.antispan_internet_ban_duration_sec
            )

    menu = MenuDefinition(
        menu_id=f"antispan:{scope}:{kind}:duration",
        title=(
            f"Duracion de {('Silenciar' if kind == 'mute' else 'Ban')}\n"
            "Envia ahora la duracion del castigo.\n\n"
            "Minimo: 30 segundos\n"
            "Maximo: 365 dias\n\n"
            "Formato ejemplo: 3 months 2 days 12 hours 4 minutes 34 seconds\n\n"
            f"Duracion actual: {current}"
        ),
        parent_menu=f"antispan:{scope}",
    )
    menu.add_row().add_action(f"antispan:{scope}:duration:clear:{kind}", "Eliminar la duracion")
    menu.add_row().add_action(f"antispan:{scope}:show", "Cancelar")
    return menu
