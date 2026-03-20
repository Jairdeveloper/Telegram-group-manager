# Propuesta de implementacion: Menu Multimedia

Objetivo
- Implementar un menu Multimedia con una unica matriz que muestre todos los tipos de contenido y sus acciones configurables.
- Incluir navegacion por paginas si hay muchos elementos (12-13 por pagina).
- Incluir configuracion de duracion para las acciones (Ban/Silenciar/Warn).

Contexto actual (Manager Bot)
- Existe un menu de moderation basico en media_menu.py.
- No existe configuracion granular por tipo de contenido multimedia.
- Se necesita una estructura similar a la del menu Antispan para gestionar acciones configurables.

Propuesta de arquitectura
1) Modelo de configuracion (GroupConfig)
- Nuevos campos sugeridos (siguiendo el patron antispan):
  - multimedia_story_action: off|warn|mute|kick|ban|delete
  - multimedia_photo_action: off|warn|mute|kick|ban|delete
  - multimedia_video_action: off|warn|mute|kick|ban|delete
  - multimedia_album_action: off|warn|mute|kick|ban|delete
  - multimedia_gif_action: off|warn|mute|kick|ban|delete
  - multimedia_voice_action: off|warn|mute|kick|ban|delete
  - multimedia_audio_action: off|warn|mute|kick|ban|delete
  - multimedia_sticker_action: off|warn|mute|kick|ban|delete
  - multimedia_animated_sticker_action: off|warn|mute|kick|ban|delete
  - multimedia_game_sticker_action: off|warn|mute|kick|ban|delete
  - multimedia_animated_emoji_action: off|warn|mute|kick|ban|delete
  - multimedia_custom_emoji_action: off|warn|mute|kick|ban|delete
  - multimedia_file_action: off|warn|mute|kick|ban|delete
  - multimedia_game_action: off|warn|mute|kick|ban|delete
  - multimedia_contact_action: off|warn|mute|kick|ban|delete
  - multimedia_poll_action: off|warn|mute|kick|ban|delete
  - multimedia_checklist_action: off|warn|mute|kick|ban|delete
  - multimedia_location_action: off|warn|mute|kick|ban|delete
  - multimedia_caps_action: off|warn|mute|kick|ban|delete
  - multimedia_payment_action: off|warn|mute|kick|ban|delete
  - multimedia_inline_bot_action: off|warn|mute|kick|ban|delete
  - multimedia_spoiler_action: off|warn|mute|kick|ban|delete
  - multimedia_spoiler_media_action: off|warn|mute|kick|ban|delete
  - multimedia_video_note_action: off|warn|mute|kick|ban|delete
  - multimedia_giveaway_action: off|warn|mute|kick|ban|delete

2) Menus
- Menu principal Multimedia Pagina 1 (menu_id: multimedia)
  - Titulo: "Configuracion Multimedia\n❕=Warn | ❗️=Kick | 🔇=Silenciar | 🚷=Ban | 🗑=Eliminacion | ☑️=Off"
  - Matriz con primeras 12-13 opciones:
    - 📲 Historia | ❕|🔇|🗑|❗️|🚷|☑️
    - 📸 Foto | ❕|🔇|🗑|❗️|🚷|☑️
    - 🎞 Video | ❕|🔇|🗑|❗️|🚷|☑️
    - 🖼 Album | ❕|🔇|🗑|❗️|🚷|☑️
    - 🎥 Gif | ❕|🔇|🗑|❗️|🚷|☑️
    - 🎤 Voz | ❕|🔇|🗑|❗️|🚷|☑️
    - 🎧 Audio | ❕|🔇|🗑|❗️|🚷|☑️
    - 🃏 Sticker | ❕|🔇|🗑|❗️|🚷|☑️
    - 🎭 Sticker anim | ❕|🔇|🗑|❗️|🚷|☑️
    - 🎲 Sticker juego | ❕|🔇|🗑|❗️|🚷|☑️
    - 😀 Emoji anim | ❕|🔇|🗑|❗️|🚷|☑️
    - 👾 Emoji custom | ❕|🔇|🗑|❗️|🚷|☑️
    - 💾 Archivo | ❕|🔇|🗑|❗️|🚷|☑️
  - Botones finales: Volver | ⏱ Duracion | Mas

- Menu principal Multimedia Pagina 2 (menu_id: multimedia:page2)
  - Matriz con segundas 12-13 opciones:
    - 🎮 Juegos | ❕|🔇|🗑|❗️|🚷|☑️
    - ☎️ Contactos | ❕|🔇|🗑|❗️|🚷|☑️
    - 📊 Encuestas | ❕|🔇|🗑|❗️|🚷|☑️
    - 📋 Checklist | ❕|🔇|🗑|❗️|🚷|☑️
    - 📍 Ubicacion | ❕|🔇|🗑|❗️|🚷|☑️
    - 🆎 Mayusculas | ❕|🔇|🗑|❗️|🚷|☑️
    - 💶 Pagos | ❕|🔇|🗑|❗️|🚷|☑️
    - 🤖 Bot Inline | ❕|🔇|🗑|❗️|🚷|☑️
    - 🗯 Spoiler | ❕|🔇|🗑|❗️|🚷|☑️
    - 🌌 Spoiler media | ❕|🔇|🗑|❗️|🚷|☑️
    - 👁‍🗨 Video note | ❕|🔇|🗑|❗️|🚷|☑️
    - 🎁 Sorteo | ❕|🔇|🗑|❗️|🚷|☑️
  - Botones finales: Volver | ⏱ Duracion | Atras

- Menu Duracion (menu_id: multimedia:duration)
  - Titulo: "Duracion de Ban/Silenciar/Warn"
  - Descripcion: "Envía ahora la duración del castigo establecido.\nMinimo: 30 segundos\nMaximo: 365 dias\nFormato ejemplo: 3 months 2 days 12 hours"
  - Botones:
    - Duracion Mute: [valor actual]
    - Duracion Ban: [valor actual]
    - Duracion Warn: [valor actual] (opcional)
    - Volver | Limpiar duracion

3) Callbacks
- multimedia:show -> abrir menu principal (pagina 1).
- multimedia:page2:show -> mostrar pagina 2.
- multimedia:page1:show -> volver a pagina 1.
- multimedia:duration:show -> mostrar menu de duracion.
- multimedia:<type>:action:<off|warn|mute|kick|ban|delete> -> cambiar accion.
- multimedia:duration:mute -> estado waiting_multimedia_duration_mute.
- multimedia:duration:ban -> estado waiting_multimedia_duration_ban.
- multimedia:duration:warn -> estado waiting_multimedia_duration_warn.
- multimedia:duration:clear -> limpiar duraciones.

4) ConversationState
- Estados de conversacion para duracion:
  - waiting_multimedia_duration_mute
  - waiting_multimedia_duration_ban
  - waiting_multimedia_duration_warn

5) UI/UX
- Estructura de matriz unica con navegacion por paginas:
  - Primera fila: encabezado con iconos de acciones.
  - Filas intermedias: icono tipo contenido + 6 botones de accion.
  - Ultima fila: navegacion (Volver | Duracion | Siguiente/Atras).
- Resaltar la opcion seleccionada con un indicador visual.
- Usar iconos: ❕ Warn, ❗️ Kick, 🔇 Silenciar, 🚷 Ban, 🗑 Eliminacion, ☑️ Off.
- Navegacion clara entre paginas con "Mas" y "Atras".

Plan de implementacion (alto nivel)
1) Modelo y storage
- Agregar campos a GroupConfig para cada tipo de contenido multimedia.
- Agregar campos de duracion: multimedia_mute_duration_sec, multimedia_ban_duration_sec, multimedia_warn_duration_sec.
- Asegurar serializacion en ConfigStorage.

2) Menus
- Crear menus multimedia en app/manager_bot/_menus/multimedia_menu.py
  - create_multimedia_menu (pagina 1)
  - create_multimedia_page2_menu (pagina 2)
  - create_multimedia_duration_menu

3) Feature callbacks
- Implementar MultimediaFeature con callbacks para acciones y navegacion.
- Cada callback actualizara el campo correspondiente en GroupConfig.

4) ConversationState
- Agregar estados para entrada de duracion en handlers.py.

5) Logica de procesamiento
- En el handler de mensajes, detectar el tipo de contenido.
- Consultar la configuracion para ese tipo.
- Aplicar la accion correspondiente y la duracion si aplica.

6) Tests
- Unit tests para verificacion de acciones, render de menus, navegacion.

Notas
- Usar prefijo "multimedia" para consistencia.
- Valores por defecto: Off para la mayoria, Warn para Foto/Video/Historia.
- La eliminacion de mensajes es complementaria a otras acciones.
- Navegacion por paginas con callback data: multimedia:page2 y multimedia:page1.
