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
