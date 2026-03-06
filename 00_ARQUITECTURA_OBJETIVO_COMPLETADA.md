# 00_ARQUITECTURA_OBJETIVO_COMPLETADA

## Estado

Quedan registradas como completadas:

- Fase 0: Congelacion de arquitectura operativa
- Fase 1: Introducir dispatcher de Telegram
- Fase 2: Extraer servicios de aplicacion

---

## Fase 0 completada

### Objetivo

Estabilizar el punto de entrada Telegram antes de seguir con la migracion arquitectonica.

### Decision aplicada

Se declara como ingress canonico de Telegram:

- `app.webhook.entrypoint:app`

Se marcan como no canonicos:

- `telegram_adapter.py` -> runtime legacy
- `app.telegram_ops.entrypoint.py` -> runtime transitorio

### Cambios implementados

#### Senalizacion en codigo

Se actualizaron los docstrings de:

- `telegram_adapter.py`
- `app/telegram_ops/entrypoint.py`

para dejar explicito que no deben ejecutarse en paralelo con `app.webhook.entrypoint:app` para el mismo `TELEGRAM_BOT_TOKEN`.

#### Documentacion operativa

Se actualizo:

- `README.md`
- `TELEGRAM_E2E_LOG_APP.md`

con estas reglas:

1. `app.webhook.entrypoint:app` es el unico ingreso canonico de Telegram.
2. `telegram_adapter.py` queda como legacy.
3. `app.telegram_ops.entrypoint.py` queda como transitorio.
4. no se deben ejecutar varios runtimes Telegram para el mismo token.

#### Checklist canonico fijado

Se deja fijado este flujo de arranque:

1. levantar API
2. levantar webhook
3. exponer `8001`
4. registrar webhook hacia `/webhook/<TELEGRAM_BOT_TOKEN>`
5. no arrancar `telegram_adapter.py`
6. no arrancar `app.telegram_ops.entrypoint.py` con el mismo token

### Resultado de la fase

La Fase 0 no modifica el dominio ni los contratos HTTP.

Su objetivo era congelar la arquitectura operativa y eliminar ambiguedad de uso. Ese objetivo queda cumplido a nivel de documentacion y senalizacion de runtime.

---

## Fase 1 completada

### Objetivo

Mover la clasificacion de updates al webhook y dejar de depender de logica inline dispersa para distinguir:

- comandos OPS
- mensajes conversacionales
- updates no soportados

### Cambios implementados

#### Nuevos archivos

- `app/telegram/__init__.py`
- `app/telegram/models.py`
- `app/telegram/services.py`
- `app/telegram/dispatcher.py`

#### Refactor aplicado

Archivo modificado:

- `app/webhook/handlers.py`

Cambios:

1. Se elimino la deteccion inline de comandos basada en `text.startswith("/")`.
2. Se introdujo `dispatch_telegram_update(update)` como clasificador canonico.
3. `process_update_impl()` ahora opera sobre un `DispatchResult`.
4. Los updates se clasifican en:
   - `ops_command`
   - `chat_message`
   - `unsupported`
5. El webhook registra eventos mas expresivos:
   - `webhook.unsupported_update`
   - `webhook.command_ignored`

### Comportamiento resultante

#### Mensaje conversacional

- se clasifica como `chat_message`
- sigue el flujo normal hacia `chat_api_client.ask(...)`

#### Comando OPS conocido

- se clasifica como `ops_command`
- en esta fase todavia no se ejecuta desde webhook
- por ahora se ignora de forma controlada y trazable

#### Update no soportado

- se clasifica como `unsupported`
- no intenta llamar al chat API
- no intenta enviar mensaje a Telegram

### Tests ejecutados

Comando:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_telegram_dispatcher_unit.py tests\test_webhook_handlers_unit.py tests\test_webhook_contract.py tests\test_telegram_ops_entrypoint_unit.py
```

Resultado:

- `23 passed`

### Cobertura anadida

#### Nuevo archivo de tests

- `tests/test_telegram_dispatcher_unit.py`

Casos cubiertos:

- comando OPS conocido
- mensaje conversacional
- update sin mensaje
- comando desconocido

#### Tests ampliados

- `tests/test_webhook_handlers_unit.py`

Nuevo caso:

- update no soportado no llama al chat API ni envia mensaje

### Resultado arquitectonico de la fase

La clasificacion de updates ya no esta acoplada al webhook como logica ad hoc.

Ahora existe una pieza reutilizable y testeada que servira como base para:

- Fase 2: extraer servicios de aplicacion
- Fase 3: despachar comandos OPS desde el mismo webhook

## Fase 2 completada

### Objetivo

Separar la logica de chat y de operaciones del transporte Telegram para que:

- el runtime OPS deje de contener logica de aplicacion inline
- los checks y comandos sean reutilizables desde otros ingress
- el webhook pueda consumir esa capa en la siguiente fase sin depender de polling

### Cambios implementados

#### Nuevos archivos

- `app/ops/checks.py`
- `app/ops/services.py`
- `tests/test_ops_services_unit.py`

#### Refactor aplicado

Archivos modificados:

- `app/ops/__init__.py`
- `app/telegram_ops/checks.py`
- `app/telegram_ops/entrypoint.py`
- `tests/test_telegram_ops_entrypoint_unit.py`

### Servicios extraidos

#### Checks OPS reutilizables

`app/ops/checks.py` pasa a ser la ubicacion canonica de:

- `check_api_health`
- `check_api_chat`
- `check_webhook_health`
- `check_webhook_local`
- `get_webhook_info`
- `check_webhook_public`
- `run_e2e_check`

El archivo `app/telegram_ops/checks.py` queda como wrapper de compatibilidad durante la migracion.

#### Servicios de aplicacion

`app/ops/services.py` concentra ahora:

- `handle_chat_message(chat_id, text)`
- `handle_ops_command(chat_id, command, args)`
- `execute_e2e_command(chat_id, ...)`

Tambien se consolidaron los formatters y el parseo de `/logs` para que no sigan embebidos en el entrypoint transitorio.

### Runtime transitorio simplificado

Archivo refactorizado:

- `app/telegram_ops/entrypoint.py`

Cambios:

1. `/health`, `/logs` y `/webhookinfo` delegan a `handle_ops_command(...)`.
2. `/e2e` conserva el acuse y `edit_text(...)`, pero la ejecucion real la hace `execute_e2e_command(...)`.
3. El entrypoint deja de contener:
   - formatters propios
   - parseo propio de `/logs`
   - ejecucion inline del flujo E2E

### Cobertura anadida

#### Nuevo archivo de tests

- `tests/test_ops_services_unit.py`

Casos cubiertos:

- `handle_chat_message` devuelve respuesta estructurada y persiste conversacion
- `handle_ops_command` resuelve `/health`
- `handle_ops_command` resuelve `/logs` con filtros
- `execute_e2e_command` registra eventos de inicio y fin
- autorizacion denegada en comandos OPS

#### Tests actualizados

- `tests/test_telegram_ops_entrypoint_unit.py`

Cambio:

- el test de `check_webhook_local` pasa a validar el modulo canonico `app.ops.checks`

### Tests ejecutados

Comando:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_ops_services_unit.py tests\test_telegram_ops_entrypoint_unit.py tests\test_telegram_dispatcher_unit.py tests\test_webhook_handlers_unit.py tests\test_webhook_contract.py
```

Resultado:

- `28 passed`
- `1 warning`

Warning observado:

- `PytestCacheWarning` por permisos sobre `.pytest_cache`, sin impacto funcional en el codigo

### Resultado arquitectonico de la fase

Queda resuelto:

- la logica reusable de OPS ya no vive en el polling bot
- existe una capa de aplicacion reusable para chat y comandos
- `app.telegram_ops.entrypoint.py` queda reducido a wrapper transitorio

Todavia queda pendiente para Fase 3:

- conectar `app.webhook.handlers` con `handle_chat_message(...)`
- conectar `app.webhook.handlers` con `handle_ops_command(...)`
- hacer que un unico runtime webhook responda chat y OPS

---

## Estado tras Fase 0 + Fase 2

Se ha resuelto:

- la ambiguedad operacional sobre que runtime es el canonico
- la ausencia de una pieza formal de clasificacion de updates
- la duplicacion principal de logica OPS dentro del bot de polling
- la falta de una capa de servicios reutilizable para chat y operaciones

Todavia no se ha resuelto:

- ejecutar comandos OPS desde el webhook canonico
- retirar completamente `app.telegram_ops.entrypoint.py`
- unificar chat y OPS dentro del mismo runtime

---

## Siguiente paso recomendado

Ejecutar la Fase 3:

- conectar el dispatcher del webhook con `handle_chat_message(...)`
- conectar el dispatcher del webhook con `handle_ops_command(...)`
- reemplazar el `command_ignored` por despacho real de comandos OPS
- validar por contrato que un solo runtime webhook responde mensajes y comandos
