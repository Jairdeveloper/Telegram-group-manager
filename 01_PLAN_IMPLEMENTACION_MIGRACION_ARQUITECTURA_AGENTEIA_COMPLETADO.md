Fecha: 2026-03-26
version: 1.0
referencia: 01_PLAN_IMPLEMENTACION_MIGRACION_ARQUITECTURA_AGENTEIA.md

Resumen de la implementacion

Se ejecutó la Fase 1 creando la base del Action Registry y un executor de acciones. Se agregó una capa mínima de permisos desacoplada y un servicio reutilizable para actualizar el `GroupConfig` desde acciones. Además, se migraron 3 acciones piloto (welcome.toggle, welcome.set_text, antispam.toggle) usando el nuevo servicio y registrándolas en el Action Registry.

Arquitectura final (Fase 1)

- `app/agent/actions/`:
  - `registry.py`: registro de acciones y `get_default_registry`.
  - `executor.py`: ejecución centralizada con validación.
  - `permissions.py`: verificación de roles.
  - `types.py`: `ActionContext` y `ActionResult`.
  - `pilot_actions.py`: acciones piloto registradas.
- `app/manager_bot/services/group_config_service.py`: servicio reutilizable para lectura/actualización de `GroupConfig`.

Tabla de tareas (Fase 1)

Fase:
Fase 1 - Action Registry base
OBjetivo fase:
Definir el contrato de acciones y centralizar la ejecución desde un único registro.
Implementacion fase:
- Se creó el Action Registry con validación de duplicados y acceso centralizado.
- Se agregó ActionExecutor con validación de payload (pydantic) y permisos.
- Se incorporó una capa básica de permisos desacoplada.
- Se creó `GroupConfigService` para reutilizar updates sobre la configuración de grupo.
- Se migraron 3 acciones piloto:
  - `welcome.toggle`
  - `welcome.set_text`
  - `antispam.toggle`

Archivos creados/modificados:
- `app/agent/actions/types.py`
- `app/agent/actions/permissions.py`
- `app/agent/actions/registry.py`
- `app/agent/actions/executor.py`
- `app/agent/actions/pilot_actions.py`
- `app/agent/actions/__init__.py`
- `app/agent/__init__.py`
- `app/manager_bot/services/group_config_service.py`
- `app/manager_bot/services/__init__.py`

Validación

No se añadieron tests en esta fase. Para validación manual:
- Crear un `ActionExecutor` con `get_default_registry()`.
- Ejecutar `welcome.set_text` y verificar actualización en `GroupConfig`.
- Ejecutar `antispam.toggle` y confirmar el estado en el menú Antispam.

Fase:
Fase 2 - Permisos desacoplados
OBjetivo fase:
Separar la validación de permisos del flujo de ejecución y estandarizar los errores.
Implementacion fase:
- Se creó `ActionPermissionPolicy` con jerarquía de roles y alias.
- Se normalizaron roles (admin/moderator/user + aliases).
- Se integró la política en `ActionExecutor` con validación previa.
- Se devolvieron respuestas estandarizadas cuando falta permiso (`status=denied`).
- Se agregaron mensajes de error consistentes para payload inválido.

Archivos modificados:
- `app/agent/actions/permissions.py`
- `app/agent/actions/executor.py`

Validación

Para validar manualmente:
- Ejecutar una acción con `context.roles=[]` y verificar `status=denied`.
- Ejecutar una acción con `roles=["admin"]` y verificar `status=ok`.

Fase:
Fase 3 - Dry-run y previsualización
OBjetivo fase:
Permitir simular cambios y mostrar impacto antes de confirmar.
Implementacion fase:
- Se extendió `ActionDefinition` con `dry_run` y `requires_confirmation`.
- Se agregó soporte en `ActionExecutor` para:
  - ejecutar dry-run (`status=preview`)
  - exigir confirmación (`status=confirm`) cuando corresponde.
- Se implementó previsualización en las 3 acciones piloto:
  - `welcome.toggle`
  - `welcome.set_text` (requiere confirmación)
  - `antispam.toggle`

Archivos modificados:
- `app/agent/actions/registry.py`
- `app/agent/actions/executor.py`
- `app/agent/actions/pilot_actions.py`

Validación

Para validar manualmente:
- Ejecutar `dry_run=True` y verificar `status=preview` con `data.current/next`.
- Ejecutar `welcome.set_text` sin confirmación y validar `status=confirm`.

Fase:
Fase 4 - Rollback básico
OBjetivo fase:
Revertir acciones críticas cuando exista operación inversa segura.
Implementacion fase:
- Se extendió `ActionDefinition` con `snapshot` y `undo`.
- Se agregó `rollback()` en `ActionExecutor`.
- Se agregó logging de auditoría con `previous_state` usando `app.audit`.
- Se implementó rollback para las 3 acciones piloto:
  - `welcome.toggle`
  - `welcome.set_text`
  - `antispam.toggle`

Archivos modificados/creados:
- `app/agent/actions/registry.py`
- `app/agent/actions/executor.py`
- `app/agent/actions/audit.py`
- `app/agent/actions/pilot_actions.py`

Validación

Para validar manualmente:
- Ejecutar una acción y verificar que `previous_state` queda en `ActionResult.data`.
- Ejecutar `rollback()` con el `previous_state` y confirmar que el valor vuelve al estado anterior.

Fase:
Fase 5 - Plantillas de respuesta centralizadas
OBjetivo fase:
Normalizar respuestas y estados de UI para todos los canales.
Implementacion fase:
- Se creó `ActionTemplateEngine` con plantillas base para estados (`error`, `denied`, `confirm`, `preview`).
- Se integró el motor de plantillas en `ActionExecutor` para respuestas estandarizadas.
- Se exportó el motor en `app/agent/actions/__init__.py` para uso transversal.

Archivos modificados/creados:
- `app/agent/actions/templates.py`
- `app/agent/actions/executor.py`
- `app/agent/actions/__init__.py`

Validación

Para validar manualmente:
- Ejecutar una acción inválida y verificar mensaje estándar de error.
- Ejecutar una acción con `requires_confirmation` y verificar mensaje estándar de confirmación.

Fase:
Fase 6 - Integración completa con NL y menús
OBjetivo fase:
Hacer que NL, comandos y menús disparen la misma acción.
Implementacion fase:
- Se creó `ActionParser` (reglas + opción LLM) para convertir NL a `action_id` + `payload`.
- Se agregó `SlotResolver` para resolver parámetros faltantes.
- Se creó `ActionStateProvider` para consultar estado actual por acción.
- Se integró `ActionParser` → `ActionExecutor` en `AgentCore.process_async`.
- Se ajustó webhook para usar `process_async` cuando está disponible.
- Se agregaron flags de configuración: `AGENT_ACTIONS_ENABLED` y `ACTION_PARSER_LLM_ENABLED`.

Archivos modificados/creados:
- `app/agent/actions/parser.py`
- `app/agent/actions/slots.py`
- `app/agent/actions/state_provider.py`
- `app/agent/actions/__init__.py`
- `app/agent/core.py`
- `app/webhook/handlers.py`
- `app/config/settings.py`
- `.env.example`

Validación

Para validar manualmente:
- Activar `AGENT_ACTIONS_ENABLED=true`.
- Enviar “activar antispam” y verificar ejecución vía Action Registry.
- Enviar “bienvenida: Hola equipo” y validar `welcome.set_text`.
