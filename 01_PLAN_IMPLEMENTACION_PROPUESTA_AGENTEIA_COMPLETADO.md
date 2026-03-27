Fecha: 2026-03-26
version: 1.0
referencia: 01_PLAN_IMPLEMENTACION_PROPUESTA_AGENTEIA.md

Resumen de la implementacion

Se ejecuto la Fase 1 creando el catalogo de acciones y la capa unificada de ejecucion. Se agrego el Action Registry, el Action Executor, una politica basica de permisos y un servicio reutilizable para modificar la configuracion del grupo. Se migraron acciones piloto (welcome.toggle, welcome.set_text, antispam.toggle) para demostrar el flujo end-to-end con schemas y validacion.

Arquitectura final (Fase 1)

- `app/agent/actions/`: incluye `registry.py`, `executor.py`, `permissions.py`, `types.py` y `pilot_actions.py`.
- `app/manager_bot/services/group_config_service.py`: servicio reutilizable para lectura/actualizacion de `GroupConfig`.

Tabla de tareas (Fase 1)

Fase:
Fase 1 - Catalogo de acciones y capa unificada de ejecucion
OBjetivo fase:
Centralizar acciones y su ejecucion para reutilizar la logica de ManagerBot desde menu, comandos y NL.
Implementacion fase:
- Se creo `app/agent/actions/` con Action Registry y Action Executor.
- Cada accion expone un schema (pydantic) y se valida en el executor.
- Se agrego una politica de permisos desacoplada.
- Se extrajo la logica de configuracion a `GroupConfigService`.
- Acciones piloto migradas: `welcome.toggle`, `welcome.set_text`, `antispam.toggle`.

Archivos creados/modificados:
- `app/agent/actions/types.py`
- `app/agent/actions/permissions.py`
- `app/agent/actions/registry.py`
- `app/agent/actions/executor.py`
- `app/agent/actions/pilot_actions.py`
- `app/agent/actions/__init__.py`
- `app/manager_bot/services/group_config_service.py`
- `app/manager_bot/services/__init__.py`

Validacion

No se agregaron tests en esta fase. Validacion manual sugerida:
- Crear un `ActionExecutor` con `get_default_registry()`.
- Ejecutar `welcome.set_text` con rol admin y verificar update en `GroupConfig`.
- Ejecutar `antispam.toggle` y confirmar el estado en el menu Antispam.

Fase:
Fase 2 - NLU -> Action (parser estructurado)
OBjetivo fase:
Convertir texto libre en `action_id` y `payload` validados con schemas, con fallback rule-based.
Implementacion fase:
- Se creo `ActionParser` con reglas base y opcion LLM (`app/agent/actions/parser.py`).
- Se agrego soporte de configuracion para habilitar/deshabilitar LLM (`ACTION_PARSER_LLM_ENABLED`).
- Se integro `ActionParser` en el flujo del Agent Core para resolver acciones desde lenguaje natural.
- Se agregaron validaciones de payload y mensajes de error estandarizados en el executor.
- Se incluyeron tests unitarios de parser y flujo de acciones.

Archivos creados/modificados:
- `app/agent/actions/parser.py`
- `app/agent/actions/__init__.py`
- `app/agent/core.py`
- `app/config/settings.py`
- `.env.example`
- `tests/agent/test_actions_unit.py`
- `tests/agent/test_actions_phases_unit.py`

Validacion

Validacion manual sugerida:
- Activar `AGENT_ACTIONS_ENABLED=true` y `ACTION_PARSER_LLM_ENABLED=false`.
- Enviar texto libre como "activar antispam" y verificar `action_id=antispam.toggle`.
- Enviar "bienvenida: Hola equipo" y verificar `action_id=welcome.set_text`.

Fase:
Fase 3 - Flujos conversacionales guiados (slots)
OBjetivo fase:
Gestionar parametros faltantes y guiar al usuario con preguntas y botones de completado.
Implementacion fase:
- Se creo `SlotResolver` para detectar parametros faltantes y proponer prompts.
- Se agrego soporte de estado de acciones con `ActionStateProvider` para construir UI coherente.
- Se integro resolucion de slots en el flujo de acciones para devolver `status=confirm` o `status=preview` segun el caso.
- Se agregaron tests de slots y flujo de acciones para cobertura basica.

Archivos creados/modificados:
- `app/agent/actions/slots.py`
- `app/agent/actions/state_provider.py`
- `app/agent/actions/__init__.py`
- `tests/agent/test_actions_unit.py`
- `tests/agent/test_actions_phases_unit.py`

Validacion

Validacion manual sugerida:
- Ejecutar una accion sin payload completo (ej: `welcome.set_text` sin `text`) y verificar que se solicite el dato faltante.
- Ejecutar `dry_run` y confirmar que `data.current/next` reflejan el estado real via `ActionStateProvider`.

Fase:
Fase 4 - Confirmaciones, auditoria y seguridad
OBjetivo fase:
Asegurar acciones sensibles con confirmacion explicita, auditoria y politica de permisos consistente.
Implementacion fase:
- Se extendio `ActionDefinition` con `snapshot`, `undo`, `dry_run` y `requires_confirmation`.
- Se implemento `rollback()` en `ActionExecutor` para revertir cambios seguros.
- Se integro auditoria de acciones con `app.agent.actions.audit` (registro de previous_state).
- Se reforzo la politica de permisos con `ActionPermissionPolicy` y normalizacion de roles.

Archivos creados/modificados:
- `app/agent/actions/registry.py`
- `app/agent/actions/executor.py`
- `app/agent/actions/audit.py`
- `app/agent/actions/permissions.py`
- `app/agent/actions/pilot_actions.py`
- `tests/agent/test_actions_unit.py`
- `tests/agent/test_actions_phases_unit.py`

Validacion

Validacion manual sugerida:
- Ejecutar `welcome.set_text` y verificar `status=confirm` cuando `requires_confirmation=True`.
- Ejecutar una accion con `roles=[]` y validar `status=denied`.
- Ejecutar una accion y luego `rollback()` con `previous_state` para verificar que revierte el cambio.

Fase:
Fase 5 - Sincronizacion UI/UX con estado real
OBjetivo fase:
Reflejar el estado real de cada feature en la descripcion del menu y evitar modales informativos innecesarios.
Implementacion fase:
- Se dejo disponible `ActionStateProvider` para consultar estado actual por accion.
- Se estandarizaron respuestas en `ActionExecutor` para que la UI pueda renderizar cambios inline.
- Se definio la base para que los menus consulten estado real y actualicen descripciones sin modales.

Archivos creados/modificados:
- `app/agent/actions/state_provider.py`
- `app/agent/actions/templates.py`
- `app/agent/actions/executor.py`

Validacion

Validacion manual sugerida:
- Consultar estado via `ActionStateProvider` y verificar que refleja la configuracion actual.
- Ejecutar una accion y comprobar que la respuesta devuelve datos para actualizar la descripcion del menu.
