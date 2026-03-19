# Propuesta de implementacion: Menu Anti-Flood

Objetivo
- Implementar un menu de Anti-Flood con estado, descripcion y castigo configurable.
- Permitir configurar cantidad de mensajes y ventana de tiempo.
- Permitir seleccionar castigo (off, warn, kick, silenciar, ban) y opciones adicionales (borrar mensajes, duracion warn/ban).
- Mantener navegacion coherente con el menu principal.

Contexto actual (Manager Bot)
- Ya existe antiflood_enabled, antiflood_limit, antiflood_interval en GroupConfig.
- Existen callbacks basicos en AntiFloodFeature (toggle/limit/interval) con prefijo mod:antiflood:*.
- No hay menus dedicados de antiflood ni campos de castigo/duracion en el modelo.

Propuesta de arquitectura
1) Modelo de configuracion (GroupConfig)
- Agregar campos nuevos:
  - antiflood_action: str = "off" | "warn" | "kick" | "mute" | "ban"
  - antiflood_delete_messages: bool = False
  - antiflood_warn_duration_sec: int | None
  - antiflood_ban_duration_sec: int | None
  - antiflood_mute_duration_sec: int | None
- Mantener los actuales:
  - antiflood_enabled, antiflood_limit, antiflood_interval.

2) Menus
- Menu principal Anti-Flood (menu_id: antiflood o mod:antiflood)
  - Texto con descripcion + estado actual (limit/interval) + castigo actual.
  - Botones:
    - Mensajes -> abre submenu de cantidad.
    - Tiempo -> abre submenu de intervalo.
    - Off -> set antiflood_action=off y antiflood_enabled=False.
    - Warn -> set antiflood_action=warn y antiflood_enabled=True.
    - Kick -> set antiflood_action=kick.
    - Silenciar -> set antiflood_action=mute.
    - Ban -> set antiflood_action=ban.
    - Borrar mensajes -> toggle antiflood_delete_messages.
    - Duracion advertencia (solo si warn activo) -> submenu input.
    - Duracion ban (solo si ban activo) -> submenu input.
    - Volver -> nav:back:main.

- Submenu Cantidad de Mensajes (menu_id: antiflood:limit)
  - Muestra valor actual.
  - Botones numericos: 2,3,4,5,6,7,8,9,10,12,15,20.
  - Callback: mod:antiflood:limit:set:<n>.
  - Volver a antiflood.

- Submenu Intervalo de Tiempo (menu_id: antiflood:interval)
  - Muestra valor actual.
  - Botones numericos: 2,3,4,5,6,7,8,9,10,12,15,20 (segundos).
  - Callback: mod:antiflood:interval:set:<n>.
  - Volver a antiflood.

- Submenu Duracion Warn (menu_id: antiflood:warn:duration)
  - Texto con formato permitido.
  - Entrada por texto (ConversationState) para parsear duracion.
  - Boton Eliminar duracion (set None).
  - Boton Cancelar.

- Submenu Duracion Ban (menu_id: antiflood:ban:duration)
  - Igual que warn, con minimo y maximo.

3) Callbacks
- mod:antiflood:show -> render menu principal antiflood.
- mod:antiflood:limit:set:<n> -> actualizar antiflood_limit.
- mod:antiflood:interval:set:<n> -> actualizar antiflood_interval.
- mod:antiflood:action:off|warn|kick|mute|ban -> set antiflood_action y antiflood_enabled.
- mod:antiflood:delete:toggle:on|off -> toggle antiflood_delete_messages.
- mod:antiflood:warn:duration:show -> entrar a flujo de input.
- mod:antiflood:ban:duration:show -> entrar a flujo de input.
- mod:antiflood:duration:clear:<warn|ban|mute> -> set a None.

4) ConversationState
- Nuevos estados:
  - waiting_antiflood_warn_duration
  - waiting_antiflood_ban_duration
  - waiting_antiflood_mute_duration
- Parseador de duracion (ej: "3 months 2 days 12 hours 4 minutes 34 seconds").

5) Render del texto del menu
- Texto recomendado:
  - "Desde este menu puedes establecer un castigo para quienes envien muchos mensajes en poco tiempo."
  - "Actualmente se activa si se envian: {limit} mensajes en {interval} segundos."
  - "Castigo: {accion} (+Eliminar mensajes si aplica)."

Plan de implementacion (alto nivel)
1) Modelo y almacenamiento
- Agregar campos a GroupConfig y asegurar serializacion (to_dict/from_dict).

2) Menus
- Crear app/manager_bot/_menus/antiflood_menu.py con:
  - create_antiflood_menu(config)
  - create_antiflood_limit_menu(config)
  - create_antiflood_interval_menu(config)
  - create_antiflood_warn_duration_menu(config)
  - create_antiflood_ban_duration_menu(config)

3) Feature callbacks
- Expandir AntiFloodFeature para:
  - nuevos callbacks de accion, delete toggle, y navegacion a submenus.
  - render de los submenus usando las funciones anteriores.

4) Menu registry
- Registrar los nuevos menus en app/manager_bot/_menus/__init__.py.

5) UI/UX
- Usar filas de 2 botones y una fila especial para "Borrar mensajes" y "Duracion".
- Respetar el orden visual de las capturas.

6) Tests
- Unit tests para:
  - actualizacion de antiflood_action, antiflood_delete_messages.
  - parseo de duraciones.
  - menu keyboard contiene botones esperados.

Notas importantes
- Mantener callbacks existentes mod:antiflood:toggle, mod:antiflood:limit, mod:antiflood:interval por compatibilidad.
- Migrar gradualmente al nuevo esquema mod:antiflood:action:*.
- El boton "Off" puede simplemente setear antiflood_enabled=False y antiflood_action="off".
