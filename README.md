# Robot Chatbot - Plan de Debug

Este README define un plan operativo para debuguear el proyecto actual sin romper contratos.

## 0. Estado operativo canonico

Ingreso canonico de Telegram:
- `app.webhook.entrypoint:app` (procesa mensajes y comandos OPS)

Runtimes deprecated:
- `telegram_adapter.py` -> deprecated
- `app.telegram_ops.entrypoint.py` -> deprecated (funcionalidad integrada en webhook)

Regla operativa:
- no ejecutar en paralelo mas de un runtime Telegram para el mismo `TELEGRAM_BOT_TOKEN`

**Nota**: Desde la Fase 4, el webhook canónico procesa todos los mensajes y comandos OPS. Ya no es necesario ejecutar `telegram_adapter.py` ni `app.telegram_ops.entrypoint.py`.

Checklist rapido de arranque canonico:
1. levantar API en `app.api.entrypoint:app`
2. levantar webhook en `app.webhook.entrypoint:app`
3. exponer `8001` por ngrok o ingress equivalente
4. registrar webhook Telegram hacia `/webhook/<TELEGRAM_BOT_TOKEN>`
5. NO arrancar `telegram_adapter.py` (deprecated)
6. NO arrancar `app.telegram_ops.entrypoint.py` (deprecated)

## 1. Objetivo del debug

Validar y aislar fallos en:
- API (`/api/v1/chat`)
- Webhook (`/webhook/{token}`)
- Flujo dedup (`update_id`)
- Integracion Chat API <-> Telegram
- Cableado modular (`app/api`, `app/webhook`) vs entrypoints legacy

Referencia de contratos:
- `design/contratos.md`

## 2. Baseline rapido

1. Verificar entorno Python y dependencias.
2. Ejecutar suite completa:

```bash
pytest -q
```

3. Si falla, ejecutar modulo por modulo:

```bash
pytest -q tests/test_api_contract.py
pytest -q tests/test_webhook_contract.py
pytest -q tests/test_modular_entrypoints.py
pytest -q tests/test_webhook_handlers_unit.py
pytest -q tests/test_agent_unit.py tests/test_pattern_engine_unit.py
```

## 3. Variables de entorno clave

Para webhook/API:
- `TELEGRAM_BOT_TOKEN`
- `CHATBOT_API_URL` (default `http://127.0.0.1:8000/api/v1/chat`)
- `REDIS_URL` (opcional)
- `PROCESS_ASYNC` (`true/false`)
- `DEDUP_TTL` (default `86400`)

Para API monolith wrapper:
- `API_HOST`
- `API_PORT`
- `LOG_LEVEL`

Comprobacion rapida (PowerShell):

```powershell
$env:TELEGRAM_BOT_TOKEN
$env:CHATBOT_API_URL
$env:REDIS_URL
$env:PROCESS_ASYNC
$env:DEDUP_TTL
```

## 4. Plan de debug por capa

### 4.1 API

Archivos foco:
- `app/api/factory.py`
- `app/api/routes.py`


Pasos:
1. Confirmar contrato `POST /api/v1/chat` con test de contrato.
2. Verificar validacion de `message` vacio (`400 message required`).
3. Revisar dependencias inyectadas (`actor`, `storage`).

### 4.2 Webhook

Archivos foco:

- `app/webhook/handlers.py`
- `app/webhook/entrypoint.py`

Pasos:
1. Token invalido debe devolver `403`.
2. Token ausente en config debe devolver `500`.
3. `update_id` repetido debe no reprocesar y devolver `{"ok": true}`.
4. Confirmar camino sync (`PROCESS_ASYNC=false`) y async (`PROCESS_ASYNC=true` + queue).

### 4.3 Infra (requests/redis/rq)

Archivos foco:

- `webhook_tasks.py`
- `worker.py`

Pasos:
1. Simular sin Redis (`REDIS_URL` vacio) y validar fallback dedup en memoria.
2. Simular con Redis y validar `setnx + expire`.
3. En async, validar enqueue en cola `telegram_tasks`.

## 5. Casos negativos minimos a repetir

1. Chat API caido o timeout -> webhook no debe romper contrato de respuesta.
2. Error al enviar a Telegram -> registrar error y continuar.
3. Payload sin `message` ni `edited_message` -> no explotar.
4. Duplicado de `update_id` -> no reprocesar.

## 6. Comandos utiles de diagnostico

Estado de cambios antes de debug:

```bash
git status --short --branch
git diff --name-status
```

Correr una prueba concreta con detalle:

```bash
pytest -q tests/test_webhook_contract.py -k deduplicates -vv
```

## 7. Checklist de cierre

- [ ] `pytest -q` en verde.
- [ ] Contratos HTTP siguen intactos (`design/contratos.md`).
- [ ] No hay cambios no relacionados en el commit.
- [ ] README y documentos de migracion actualizados si hubo cambios de comportamiento.

## 8. Riesgos conocidos actuales

- Configuracion distribuida en varios archivos (`os.getenv` disperso).
- Acoplamiento directo a infraestructura en adapters actuales.
- Codigo legacy aun activo (transicion no cerrada).

## 9. Siguiente mejora recomendada

Ejecutar la migracion Semana 2-3 pendiente:
1. Centralizar settings.
2. Aislar interfaces de infraestructura.
3. Aumentar pruebas negativas de webhook.
4. Plan de retiro progresivo de legacy.


