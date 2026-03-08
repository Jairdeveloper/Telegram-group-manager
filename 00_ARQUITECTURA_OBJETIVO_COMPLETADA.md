# 00_ARQUITECTURA_OBJETIVO_COMPLETADA

## Estado

Quedan registradas como completadas:

- Fase 0: Congelacion de arquitectura operativa
- Fase 1: Introducir dispatcher de Telegram
- Fase 2: Extraer servicios de aplicacion
- Fase 3: Integrar el dispatcher con los servicios
- Fase 4: Deprecar runtimes legacy
- Fase 5: Endurecimiento de contratos y observabilidad

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

## Fase 3 completada

### Objetivo

Completar el flujo final:

- webhook -> dispatcher -> servicio correcto -> respuesta Telegram

para que un mismo runtime webhook responda:

- mensajes conversacionales
- comandos OPS

sin depender operativamente de `app.telegram_ops.entrypoint.py`.

### Cambios implementados

#### Nuevos archivos

- `app/ops/policies.py`

#### Refactor aplicado

Archivos modificados:

- `app/webhook/handlers.py`
- `app/webhook/entrypoint.py`
- `webhook_tasks.py`
- `app/telegram_ops/entrypoint.py`
- `app/ops/checks.py`
- `tests/test_webhook_handlers_unit.py`
- `tests/test_webhook_contract.py`

### Integracion del webhook con los servicios

Archivo refactorizado:

- `app/webhook/handlers.py`

Cambios:

1. `process_update_impl()` pasa a ser asincrona.
2. El webhook deja de usar el flujo directo `chat_api_client.ask(...)` para mensajes normales.
3. El dispatcher sigue siendo el punto de decision, pero ahora:
   - `chat_message` -> `handle_chat_message(...)`
   - `ops_command` -> `handle_ops_command(...)`
4. Se elimina el comportamiento `webhook.command_ignored` como camino normal para comandos OPS.
5. Se mantienen los contratos del webhook:
   - token valido -> `{"ok": true}`
   - dedup -> no reprocesa el mismo `update_id`
   - si falla la cola async -> fallback sync
   - si falla el servicio de dominio -> sigue devolviendo `{"ok": true}` y responde `(internal error)`

### Politicas OPS compartidas

Nuevo archivo:

- `app/ops/policies.py`

Se extraen de `app.telegram_ops.entrypoint.py` las politicas de:

- autorizacion por `ADMIN_CHAT_IDS`
- rate limit para comandos OPS costosos

Con esto:

- el webhook puede ejecutar OPS usando la misma politica que el runtime transitorio
- `app.telegram_ops.entrypoint.py` deja de ser el unico lugar donde existia esa logica

### Runtime canonico y worker alineados

#### Webhook canonico

Archivo modificado:

- `app/webhook/entrypoint.py`

Cambios:

1. `process_update_sync(...)` ahora llama al flujo compartido asincrono.
2. El entrypoint canonico inyecta:
   - `handle_chat_message`
   - `handle_ops_command`
   - `is_admin`
   - `check_rate_limit`

#### Worker

Archivo modificado:

- `webhook_tasks.py`

Cambio:

- el worker deja de mantener un flujo paralelo basado en `RequestsChatApiClient`
- ahora ejecuta el mismo `process_update_impl(...)` compartido que usa el webhook

Resultado:

- no hay divergencia funcional entre procesamiento sync y async

### Ajuste adicional detectado durante la fase

Archivo modificado:

- `app/ops/checks.py`

Cambio:

- `build_probe_update(...)` pasa a generar `update_id` realmente unico en cada invocacion

Motivo:

- un test de regresion detecto colision de `update_id` en checks locales consecutivos

### Comportamiento resultante

#### Mensaje conversacional

- se clasifica como `chat_message`
- se resuelve con `handle_chat_message(...)`
- se envia la respuesta a Telegram desde el mismo runtime webhook

#### Comando OPS conocido

- se clasifica como `ops_command`
- se resuelve con `handle_ops_command(...)`
- se envia la respuesta OPS a Telegram desde el mismo runtime webhook

#### Update no soportado

- se clasifica como `unsupported`
- se registra como `webhook.unsupported_update`
- no intenta ejecutar servicios de dominio ni enviar mensaje

### Eventos operativos resultantes

El webhook pasa a registrar eventos mas alineados con el servicio realmente ejecutado:

- `webhook.process_start`
- `webhook.chat_service.ok`
- `webhook.ops_service.ok`
- `webhook.service.error`
- `webhook.telegram_send.ok`
- `webhook.telegram_send.error`

Se mantienen:

- `webhook.received`
- `webhook.dedup.duplicate`
- `webhook.enqueue.ok`
- `webhook.enqueue.error`
- `webhook.enqueue.unavailable`
- `webhook.handle_error`

### Cobertura actualizada

#### Tests de handlers

Archivo actualizado:

- `tests/test_webhook_handlers_unit.py`

Cambios cubiertos:

- mensaje normal usa servicio compartido de chat
- comando OPS ejecuta servicio compartido y responde por Telegram
- update no soportado sigue sin enviar respuesta
- error en servicio de dominio responde `(internal error)`

#### Tests de contrato

Archivo actualizado:

- `tests/test_webhook_contract.py`

Cambios cubiertos:

- `POST /webhook/{token}` con mensaje normal -> respuesta conversacional desde servicio compartido
- `POST /webhook/{token}` con `/logs` -> respuesta OPS desde el mismo webhook
- fallback sync se mantiene cuando falla enqueue
- fallo de envio a Telegram no rompe el contrato HTTP del webhook

### Tests ejecutados

Comando:

```powershell
pytest -q tests/test_webhook_handlers_unit.py tests/test_webhook_contract.py tests/test_ops_services_unit.py tests/test_telegram_dispatcher_unit.py tests/test_modular_entrypoints.py tests/test_telegram_ops_entrypoint_unit.py
```

Resultado:

- `31 passed`
- `1 warning`

Warning observado:

- `PytestCacheWarning` por permisos sobre `.pytest_cache`, sin impacto funcional

### Resultado arquitectonico de la fase

Queda resuelto:

- el webhook ya no ignora comandos OPS como camino normal
- el webhook ya no depende de llamar al chat API como adaptador primario para texto normal
- un mismo runtime canonico procesa chat y OPS
- el worker async y el flujo sync comparten el mismo procesamiento de dominio

Con esto se cumple el criterio de salida de la Fase 3:

- un mismo runtime webhook responde tanto chat como OPS

---

## Fase 4 completada

### Objetivo

Deprecar los runtimes legacy y eliminar la ambiguedad operacional:

- `telegram_adapter.py`
- `app/telegram_ops.entrypoint.py`

### Cambios implementados

#### Deprecacion de telegram_adapter.py

Archivo modificado:

- `telegram_adapter.py`

Cambios:

1. Se actualizo el docstring para marcarlo como DEPRECATED
2. Se addedo nota de que se debe usar `app.webhook.entrypoint:app` como unico punto de entrada

#### Documentacion actualizada

Archivos modificados:

- `estructura.md`
- `ARRANQUE_DEV_PROD.md`
- `README.md`

Cambios en `estructura.md`:

1. Se renombro "Modo Polling (desarrollo)" a "Legacy: Modo Polling (deprecated)"
2. Se reordeno para que el modo Webhook sea el primero (canonico)
3. Se actualizo la referencia a telegram_adapter.py como DEPRECATED

Cambios en `ARRANQUE_DEV_PROD.md`:

1. Se actualizo la seccion de entrypoints canónicos
2. Se marco `telegram_ops` como deprecated
3. Se explico que el webhook ahora procesa mensajes y comandos OPS

Cambios en `README.md`:

1. Se actualizo el checklist de arranque para incluir que NO se deben ejecutar los runtimes deprecated
2. Se marcaron ambos runtimes legacy como deprecated

### Resultado de la fase

Se cumple el criterio de salida de la Fase 4:

- no queda ningun flujo operativo recomendado que dependa de polling legacy
- la documentacion refleja que el webhook canonico es el unico punto de entrada Telegram
- los componentes legacy (`telegram_adapter.py`, `telegram_ops.entrypoint.py`) estan marcados como deprecated

### Smoke test de arranque canonico

El flujo de arranque canonico ahora es:

1. levantar API en `app.api.entrypoint:app`
2. levantar webhook en `app.webhook.entrypoint:app`
3. exponer `8001` por ngrok o ingress equivalente
4. registrar webhook hacia `/webhook/<TELEGRAM_BOT_TOKEN>`
5. NO arrancar `telegram_adapter.py` (deprecated)
6. NO arrancar `app.telegram_ops.entrypoint.py` (deprecated)

---

## Estado tras Fase 0 + Fase 4

Se ha resuelto:

- la ambiguedad operacional sobre que runtime es el canonico
- la ausencia de una pieza formal de clasificacion de updates
- la duplicacion principal de logica OPS dentro del bot de polling
- la falta de una capa de servicios reutilizable para chat y operaciones
- la ejecucion de comandos OPS desde el webhook canonico
- la unificacion de chat y OPS dentro del mismo runtime
- la alineacion funcional entre el flujo sync y el flujo async del webhook
- la deprecacion operativa de componentes legacy

La Fase 5 (Endurecimiento de contratos y observabilidad) es la siguiente fase pendiente.

---

## Fase 5 completada

### Objetivo

Cerrar la arquitectura con observabilidad y contratos estables.

### Cambios implementados

#### Eventos operativos agregados

Archivos modificados:

- `app/webhook/handlers.py`
- `app/ops/services.py`

Nuevos eventos registrados:

1. **Eventos de dispatch Telegram** (en `handlers.py`):
   - `telegram.dispatch.chat` - cuando se dispatcha un mensaje de chat
   - `telegram.dispatch.ops` - cuando se dispatcha un comando OPS
   - `telegram.dispatch.unsupported` - cuando el update no es soportado

2. **Eventos de comando OPS** (en `services.py`):
   - `ops.command.completed` - cuando un comando OPS se completa exitosamente
   - `ops.command.failed` - cuando un comando OPS falla

#### Tests actualizados

Archivo modificado:

- `tests/test_ops_services_unit.py`

Cambios:
- `test_handle_ops_command_logs_filters_and_records_event` ahora verifica el evento `ops.command.completed`
- `test_execute_e2e_command_records_success_in_plain_text` ahora verifica el evento `ops.command.completed`

#### Revision de settings

Se revisaron los settings dispersos en el codigo:

- `app/ops/checks.py` - usa API_HOST, API_PORT, WEBHOOK_PORT para health checks
- `app/ops/policies.py` - usa ADMIN_CHAT_IDS, OPS_RATE_LIMIT_SECONDS
- `app/ops/events.py` - usa TELEGRAM_BOT_TOKEN para masking, y settings de eventos

La configuracion principal ya esta centralizada en `app/config/settings.py`:
- `ApiSettings` para API
- `WebhookSettings` para Webhook
- `WorkerSettings` para Worker

Los usages restantes son aceptables porque:
- `events.py` necesita acceso directo a tokens para masking/redaccion
- `policies.py` es un modulo de politicas independiente
- `checks.py` necesita las URLs para health checks

### Resultado de la fase

Se cumple el criterio de salida de la Fase 5:

- cualquier fallo funcional puede rastrearse desde logs operativos
- los eventos de dispatch permiten trazabilidad completa del flujo Telegram
- los eventos de comando permiten monitoreo de operaciones

### Tests ejecutados

Comando:

```bash
pytest -q tests/test_webhook_handlers_unit.py tests/test_webhook_contract.py tests/test_ops_services_unit.py tests/test_telegram_dispatcher_unit.py
```

Resultado:

- `31 passed`

---

## Estado tras Fase 0 + Fase 5

Se ha resuelto:

- la ambiguedad operacional sobre que runtime es el canonico
- la ausencia de una pieza formal de clasificacion de updates
- la duplicacion principal de logica OPS dentro del bot de polling
- la falta de una capa de servicios reutilizable para chat y operaciones
- la ejecucion de comandos OPS desde el webhook canonico
- la unificacion de chat y OPS dentro del mismo runtime
- la alineacion funcional entre el flujo sync y el flujo async del webhook
- la deprecacion operativa de componentes legacy
- la observabilidad completa del flujo Telegram con eventos de dispatch
- el registro de eventos de comando OPS completados y fallidos

La Fase 6 (Separacion opcional en dos bots) es la siguiente fase pendiente.

---

## Siguiente paso recomendado

Ejecutar la Fase 6 (opcional):

- introducir soporte explicito para TELEGRAM_CHATBOT_TOKEN y TELEGRAM_OPS_TOKEN
- aislar configuracion y handlers por bot
- decidir si el bot OPS sigue en el mismo webhook o pasa a otro ingress
