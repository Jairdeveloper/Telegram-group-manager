Fecha: 2026-03-19
version: v1.0
referencia: antispan.md

Resumen de la implementacion
- Definir modelo de configuracion antispan con acciones, eliminacion, duraciones y excepciones.
- Crear menus para Antispan (principal, Telegram, Reenvio, Citas, General de internet).
- Implementar callbacks y estados de conversacion para duraciones y lista blanca.

Arquitectura final:
- Menu principal Antispan (antispan)
  - Botones: Telegram, Reenvio, Citas, General de internet, Volver.
- Menu Telegram (antispan:telegram)
  - Castigo, eliminacion, toggles de usernames/bots, duraciones y excepciones.
- Menu Reenvio (antispan:forward)
  - Estado por origen (canales, grupos, usuarios, bots) + castigo, eliminacion, duraciones, excepciones.
- Menu Citas (antispan:quotes)
  - Igual a reenvio, aplicado a citas.
- Menu General de internet (antispan:internet)
  - Castigo, eliminacion, duraciones, excepciones.

Tabla de tareas:
| Fase | Objetivo fase | Implementacion fase |
| --- | --- | --- |
| 1 | Modelo y storage | Agregar campos antispan en GroupConfig y validar serializacion. |
| 2 | Menus y callbacks | Crear menus antispan y callbacks para acciones, toggles, duraciones y excepciones. |
| 3 | Conversacion y tests | Agregar estados de conversacion y pruebas unitarias. |

Fase: 1
OBjetivo fase: Modelo y storage.
Implementacion fase:
- Actualizar app/manager_bot/_config/group_config.py con campos antispan (acciones, eliminacion, duraciones, excepciones).
- Validar to_dict/from_dict para nuevos campos.

Fase: 2
OBjetivo fase: Menus y callbacks.
Implementacion fase:
- Crear app/manager_bot/_menus/antispan_menu.py con menus principales y submenus.
- Registrar menus en app/manager_bot/_menus/__init__.py.
- Crear AntispanFeature con callbacks para:
  - acciones (off/warn/kick/mute/ban)
  - delete toggle
  - duraciones mute/ban
  - toggles de usernames/bots
  - excepciones (add/remove)

Fase: 3
OBjetivo fase: Conversacion y tests.
Implementacion fase:
- Agregar estados ConversationState para duraciones y excepciones.
- Tests unitarios de parseo y render de menus.
