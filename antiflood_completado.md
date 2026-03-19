Fecha: 2026-03-18
version: v1.0
referencia: implementacion_antiflood.md

Fase: 1
Objetivo fase: Modelo y storage.
Implementacion fase:
- app/manager_bot/_config/group_config.py
  - Se agregaron los campos de configuracion antiflood:
    - antiflood_action (default: off)
    - antiflood_delete_messages (default: False)
    - antiflood_warn_duration_sec (default: None)
    - antiflood_ban_duration_sec (default: None)
    - antiflood_mute_duration_sec (default: None)
  - Se mantiene compatibilidad con serializacion existente (to_dict/from_dict) al usar dataclass + defaults.

Fase: 2
Objetivo fase: Menus y callbacks.
Implementacion fase:
- app/manager_bot/_menus/antiflood_menu.py
  - Se creo el menu principal Anti-Flood con descripcion, estado actual y castigo.
  - Se agregaron submenus de Mensajes, Tiempo y Duraciones (warn/ban/mute).
  - Botones de accion: Off/Warn/Kick/Silenciar/Ban, Borrar mensajes y Volver.
- app/manager_bot/_menus/__init__.py
  - Se registraron los nuevos menus de antiflood.
- app/manager_bot/_menus/main_menu.py
  - El boton Anti-Flood ahora abre el menu antiflood (mod:antiflood:show).
- app/manager_bot/_features/antiflood/__init__.py
  - Se agregaron callbacks para mostrar menus, acciones, toggle de borrado y limpiar duraciones.
  - Se mantiene compatibilidad con callbacks existentes mod:antiflood:limit/interval.

Fase: 3
Objetivo fase: Conversacion y tests.
Implementacion fase:
- app/manager_bot/_menu_service.py
  - Se agregaron estados de conversacion para duraciones de antiflood.
- app/manager_bot/_utils/duration_parser.py
  - Se implemento parser de duraciones en segundos con unidades en ingles y español.
- app/manager_bot/_features/antiflood/__init__.py
  - Se actualizo para setear/limpiar estados de conversacion al abrir/cerrar duraciones.
- app/webhook/handlers.py
  - Se agrego manejo de mensajes para guardar duraciones warn/ban/mute.
  - Se valida minimo 30 segundos y maximo 365 dias.
- tests/manager_bot/test_antiflood_duration.py
  - Tests de parser y flujo de actualizacion de duracion.

Notas:
- No se ejecutaron tests en esta fase.
