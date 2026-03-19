Fecha: 2026-03-18
version: v1.0
referencia: antiflood.md

Resumen de la migracion:
- Crear menus dedicados para Anti-Flood con configuracion de mensajes, tiempo y castigo.
- Extender GroupConfig con accion, borrado de mensajes y duraciones.
- Agregar callbacks y estados de conversacion para duraciones.

Arquitectura final:
- Menu principal Anti-Flood (mod:antiflood:show)
  - Descripcion, estado actual (limit/interval) y castigo.
  - Botones: Mensajes, Tiempo, Off, Warn, Kick, Silenciar, Ban, Borrar mensajes, Duracion warn, Duracion ban, Volver.
- Submenu Mensajes (antiflood:limit)
  - Botones numericos para limite.
- Submenu Tiempo (antiflood:interval)
  - Botones numericos para intervalo.
- Submenu Duracion Warn / Ban
  - Input por texto con validacion y boton para limpiar duracion.

Tabla de tareas:
| Fase | Objetivo fase | Implementacion fase |
| --- | --- | --- |
| 1 | Modelo y storage | Agregar campos antiflood_action/delete/duraciones en GroupConfig y asegurar serializacion. |
| 2 | Menus y callbacks | Crear menus antiflood y extender AntiFloodFeature con nuevas acciones y submenus. |
| 3 | Conversacion y tests | Agregar estados ConversationState y pruebas para callbacks y duraciones. |

Fase: 1
OBjetivo fase: Modelo y storage.
Implementacion fase:
- Actualizar app/manager_bot/_config/group_config.py con nuevos campos.
- Validar to_dict/from_dict para los nuevos campos.

Fase: 2
OBjetivo fase: Menus y callbacks.
Implementacion fase:
- Crear app/manager_bot/_menus/antiflood_menu.py con menu principal y submenus.
- Registrar menus en app/manager_bot/_menus/__init__.py.
- Extender app/manager_bot/_features/antiflood/__init__.py:
  - Callbacks para action, delete, limit:set, interval:set, warn/ban duration.
  - Render de menus con config actual.

Fase: 3
OBjetivo fase: Conversacion y tests.
Implementacion fase:
- Agregar estados a ConversationState y parseo de duraciones.
- Pruebas unitarias de callbacks y del parseo de duracion.
