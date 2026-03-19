# Propuesta de implementacion: Menu Antispan

Objetivo
- Implementar un menu Antispan con descripcion, castigo y eliminacion de mensajes configurables.
- Incluir submenus para Telegram, Reenvio, Citas y General de internet.
- Permitir duraciones de silenciar y ban, y gestion de excepciones (lista blanca).

Contexto actual (Manager Bot)
- Existe menu Antispam basico (antispam_menu.py) con toggles de antispam general.
- No hay estructura de menus avanzados tipo "Telegram/Reenvio/Citas/General" ni castigos por origen.

Propuesta de arquitectura
1) Modelo de configuracion (GroupConfig)
- Nuevos campos sugeridos:
  - antispan_telegram_action: off|warn|kick|mute|ban
  - antispan_telegram_delete_messages: bool
  - antispan_telegram_mute_duration_sec: int|None
  - antispan_telegram_ban_duration_sec: int|None
  - antispan_telegram_usernames_enabled: bool
  - antispan_telegram_bots_enabled: bool
  - antispan_telegram_exceptions: list[str]

  - antispan_forward_channels_action: off|warn|kick|mute|ban
  - antispan_forward_groups_action: off|warn|kick|mute|ban
  - antispan_forward_users_action: off|warn|kick|mute|ban
  - antispan_forward_bots_action: off|warn|kick|mute|ban
  - antispan_forward_delete_messages: bool
  - antispan_forward_mute_duration_sec: int|None
  - antispan_forward_ban_duration_sec: int|None
  - antispan_forward_exceptions: list[str]

  - antispan_quotes_channels_action: off|warn|kick|mute|ban
  - antispan_quotes_groups_action: off|warn|kick|mute|ban
  - antispan_quotes_users_action: off|warn|kick|mute|ban
  - antispan_quotes_bots_action: off|warn|kick|mute|ban
  - antispan_quotes_delete_messages: bool
  - antispan_quotes_mute_duration_sec: int|None
  - antispan_quotes_ban_duration_sec: int|None
  - antispan_quotes_exceptions: list[str]

  - antispan_internet_action: off|warn|kick|mute|ban
  - antispan_internet_delete_messages: bool
  - antispan_internet_mute_duration_sec: int|None
  - antispan_internet_ban_duration_sec: int|None
  - antispan_internet_exceptions: list[str]

2) Menus
- Menu principal Antispan (menu_id: antispan)
  - Descripcion: "En este menu puedes decidir si deseas proteger tus grupos de enlaces, reenvios y citas innecesarias."
  - Botones: Telegram, Reenvio, Citas, General de internet, Volver.

- Menu Telegram (menu_id: antispan:telegram)
  - Mostrar descripcion, castigo actual y eliminacion.
  - Botones: Off, Warn, Kick, Silenciar, Ban, Borrar mensajes.
  - Boton: Escoger duracion de silencio (si mute activo).
  - Boton: Escoger duracion de ban (si ban activo).
  - Boton: Antispan de usernames (toggle).
  - Boton: Antispan de bots (toggle).
  - Boton: Excepciones (lista blanca).

- Menu Excepciones Telegram (menu_id: antispan:telegram:exceptions)
  - Botones: Lista Blanca, Anadir, Eliminar, Lista Blanca Global, Volver.
  - Flujo de texto para agregar/eliminar usernames/enlaces.

- Menu Reenvio (menu_id: antispan:forward)
  - Descripcion + estado por origen (canales, grupos, usuarios, bots).
  - Botones origen: Canales, Grupos, Usuarios, Bots.
  - Boton separador visual "--------" (noop).
  - Botones castigo: Off, Warn, Kick, Silenciar, Ban.
  - Boton borrar mensajes, duracion de silencio/ban, Excepciones, Volver.

- Menu Citas (menu_id: antispan:quotes)
  - Igual a Reenvio pero aplicado a mensajes con citas de chats externos.

- Menu General de internet (menu_id: antispan:internet)
  - Igual a Telegram pero para enlaces externos.

3) Callbacks
- antispan:show -> abrir menu principal.
- antispan:telegram:show / forward:show / quotes:show / internet:show.
- antispan:<scope>:action:<off|warn|kick|mute|ban>.
- antispan:<scope>:delete:toggle:<on|off>.
- antispan:<scope>:mute:duration:show / ban:duration:show.
- antispan:<scope>:duration:clear:<mute|ban>.
- antispan:telegram:usernames:toggle / antispan:telegram:bots:toggle.
- antispan:<scope>:exceptions:show / add / remove.

4) ConversationState
- Estados por duracion:
  - waiting_antispan_<scope>_mute_duration
  - waiting_antispan_<scope>_ban_duration
- Estados para excepciones:
  - waiting_antispan_<scope>_exceptions_add
  - waiting_antispan_<scope>_exceptions_remove

5) UI/UX
- Usar filas de 2 botones y separar secciones como en las capturas.
- Mantener texto explicativo en la cabecera del menu.
- Boton Volver siempre a menu anterior.

Plan de implementacion (alto nivel)
1) Modelo y storage
- Agregar campos a GroupConfig y asegurar serializacion.

2) Menus
- Crear menus antispan en app/manager_bot/_menus/antispan_menu.py
  - create_antispan_menu
  - create_antispan_telegram_menu
  - create_antispan_forward_menu
  - create_antispan_quotes_menu
  - create_antispan_internet_menu
  - create_antispan_*_duration_menu
  - create_antispan_*_exceptions_menu

3) Feature callbacks
- Implementar AntispanFeature con callbacks para acciones, toggles, duraciones y excepciones.

4) ConversationState
- Agregar estados para duraciones y excepciones.

5) Tests
- Unit tests para parseo de duraciones, toggles, y render de menus.

Notas
- Mantener compatibilidad con antispam existente (si aplica).
- Considerar prefijo "antispan" o "antispam" para consistencia con el resto del bot.
