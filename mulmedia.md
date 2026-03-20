Objetivo
- Implementar un  Definir modelo de configuracion con las siguientes opciones configurables:

 ❕ = Warn | ❗️ = Kick
🔇 = Silenciar | 🚷 = Ban
🗑 = Eliminación
☑️ = Off
______________________________

- Opciones que cambien de acuerdo a la seleccion del menu.

📲 Historia = ❕ Warn
📸 Foto = ❕ Warn
🎞 Video = ❕ Warn
🖼 Álbum = ☑️ Off
🎥 Gif = ☑️ Off
🎤 Mensaje de voz = ☑️ Off
🎧 Audio = ☑️ Off
🃏 Sticker = ☑️ Off
🎭 Sticker animado = ☑️ Off
🎲 Sticker de juego = ☑️ Off
😀 Emoji animado = ☑️ Off
👾 Emoji custom = ☑️ Off
💾 Archivo = ☑️ Off
🎮 Juegos = ☑️ Off
☎️ Contactos = 🚷 Ban
📊 Encuestas = 🔇 Silenciar
📋 Checklist = ☑️ Off
📍 Ubicación = ❕ Warn
🆎 Mayusculas = 🚷 Ban
💶 Pagos = ☑️ Off
🤖 Bot Inline = ❗️ Kick
🗯 Spoiler = ❕ Warn
🌌🌌 Spoiler multimedia = ❗️ Kick
👁‍🗨 Video redondo = ☑️ Off
🎁 Sorteo = ☑️ Off + 🗑

-Menus:
Para setear estas opciones debe haber un menu selecionable con el siguiente formato: La opcion que este seleccionada debe ser resaltada de alguna manera.

📲|❕|🔇|🗑|❗️|🚷|☑️|
📸|❕|🔇|🗑|❗️|🚷|☑️|
🎞|❕|🔇|🗑|❗️|🚷|☑️|
🖼|❕|🔇|🗑|❗️|🚷|☑️|
🎥|❕|🔇|🗑|❗️|🚷|☑️|
🎤|❕|🔇|🗑|❗️|🚷|☑️|
🎧|❕|🔇|🗑|❗️|🚷|☑️|
🃏|❕|🔇|🗑|❗️|🚷|☑️|
🎭|❕|🔇|🗑|❗️|🚷|☑️|
🎲|❕|🔇|🗑|❗️|🚷|☑️|
😀|❕|🔇|🗑|❗️|🚷|☑️|
👾|❕|🔇|🗑|❗️|🚷|☑️|
💾|❕|🔇|🗑|❗️|🚷|☑️|
📲|❕|🔇|🗑|❗️|🚷|☑️|
🎮|❕|🔇|🗑|❗️|🚷|☑️|
☎️|❕|🔇|🗑|❗️|🚷|☑️|
📊|❕|🔇|🗑|❗️|🚷|☑️|
📋|❕|🔇|🗑|❗️|🚷|☑️|
📍|❕|🔇|🗑|❗️|🚷|☑️|
🆎|❕|🔇|🗑|❗️|🚷|☑️|
💶|❕|🔇|🗑|❗️|🚷|☑️|
🤖|❕|🔇|🗑|❗️|🚷|☑️|
🗯|❕|🔇|🗑|❗️|🚷|☑️|
🌌|❕|🔇|🗑|❗️|🚷|☑️|
👁‍🗨|❕|🔇|🗑|❗️|🚷|☑️|
🎁|❕|🔇|🗑|❗️|🚷|☑️|

volver|tiempo|Mas

Propuesta de arquitectura

- multimedia_telegram_action: off|warn|silenciar|kick|ban| Eliminación
- multimedia_forward_channels_action: off|warn|silenciar|kick|ban| Eliminación

formato de tiempo:

⏱️ Duración de Ban/Silenciar/Warn

Envía ahora la duración del castigo establecido (Ban/Silenciar/Warn)

Mínimo: 30 seconds
Máximo: 365 days

Ejemplo de formato de elección: 3 months 2 days 12 hours 4 minutes 34 seconds

Duración actual: Apagado

la funcion de la ui debe tener un formato parecido al siguiente pero de acuerdo a la descripcion anterior:


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