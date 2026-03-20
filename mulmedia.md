Objetivo
- Implementar un menu multimedia con las siguientes opciones configurables:

UI:

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