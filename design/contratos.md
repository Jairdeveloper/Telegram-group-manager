# Contratos observados del proyecto

## 1) Contratos HTTP

### API de chat (FastAPI)
Origen: `app/api/routes.py`, `tests/test_api_contract.py`

- `POST /api/v1/chat`
  - Query params:
    - `message: str` (requerido)
    - `session_id: str` (opcional, se autogenera si no llega)
  - Reglas:
    - Si `message` vacio o solo espacios -> `400` con `detail="message required"`.
  - Respuesta `200`:
    - `session_id: str`
    - `message: str`
    - `response: str`
    - `confidence: float`
    - `source: str`
    - `pattern_matched: bool`

- `GET /api/v1/history/{session_id}`
  - Respuesta `200`:
    - `session_id: str`
    - `history: list`

- `GET /api/v1/stats`
  - Respuesta `200`:
    - `app_name: str`
    - `version: str`
    - `total_sessions: int`
    - `total_messages: int`

- `GET /health` (API app factory)
  - Respuesta `200`: `{"status": "ok", "version": <app_version>}`

### Webhook Telegram (FastAPI)
Origen: `app/webhook/entrypoint.py`, `app/webhook/handlers.py`, `tests/test_webhook_contract.py`

- `POST /webhook/{token}`
  - Validaciones:
    - Si `BOT_TOKEN` no configurado -> `500`, `detail="BOT_TOKEN not configured"`.
    - Si `token` de ruta != `BOT_TOKEN` -> `403`, `detail="Invalid token"`.
  - Deduplicacion:
    - Si `update_id` repetido -> respuesta `200` con `{"ok": true}` y no reprocesa.
  - Flujo:
    - Si `PROCESS_ASYNC=true` y hay `queue`, encola trabajo.
    - Si no, procesa en linea.
  - Errores internos:
    - Se devuelve `200` con `{"ok": true}` para evitar retry storm del proveedor.

- `GET /health` (webhook app)
  - Respuesta `200`: `{"status": "ok"}`

- `GET /metrics`
  - Respuesta `200` texto Prometheus (`CONTENT_TYPE_LATEST`).

## 2) Contratos de modulo (internos)

### Factory API
Origen: `app/api/factory.py`

- `create_api_app(*, app_name, app_version, app_description, actor, storage) -> FastAPI`
- Dependencias esperadas:
  - `actor.process(message) -> objeto con text/confidence/source/pattern_matched`
  - `storage.save(session_id, message, response_text)`
  - `storage.get_history(session_id)`
  - `storage.data` (para stats)

### Router API
Origen: `app/api/routes.py`

- `create_chat_router(actor, storage, app_name, app_version) -> APIRouter`
- Contrato implicito de `actor` y `storage` definido arriba.

### Handlers Webhook
Origen: `app/webhook/handlers.py`

- `dedup_update_impl(update_id, *, redis_client, dedup_ttl, memory_store, logger) -> bool`
  - `True` = nuevo, `False` = duplicado.

- `send_message_impl(*, bot_token, chat_id, text, requests_module) -> dict`
  - Devuelve `{"status_code": int, "text": str}`.

- `process_update_sync_impl(update, *, chat_api, send_message, requests_module, process_time_metric, logger) -> None`
  - Espera payload Telegram con `message` o `edited_message`.

- `handle_webhook_impl(*, token, request, bot_token, dedup_update, process_async, queue, process_update_sync, requests_metric, logger) -> dict`
  - Devuelve `{"ok": true}` en ruta feliz y errores internos controlados.
  - Puede lanzar `HTTPException` en token invalido o token no configurado.

### Entrypoint modular de webhook
Origen: `app/webhook/entrypoint.py`, `app/webhook/__init__.py`

- `create_webhook_app() -> FastAPI`
- Debe exponer una app operativa con `POST /webhook/{token}`.

## 3) Contratos operativos (env vars)

Origen: `app/webhook/entrypoint.py`, `worker.py`, `webhook_tasks.py`, `app/api/entrypoint.py`

- Webhook/API runtime:
  - `TELEGRAM_BOT_TOKEN`
  - `CHATBOT_API_URL` (default `http://127.0.0.1:8000/api/v1/chat`)
  - `REDIS_URL` (opcional)
  - `PROCESS_ASYNC` (default `true`)
  - `DEDUP_TTL` (default `86400`)

- API monolith wrapper:
  - `API_HOST` (default `127.0.0.1`)
  - `API_PORT` (default `8000`)
  - `LOG_LEVEL`
  - `OPENAI_API_KEY` (si se usa fallback OpenAI)

## 4) Contratos de prueba (fuente de verdad actual)

- `tests/test_api_contract.py`: valida contrato de `/api/v1/chat` y validacion de `message` vacio.
- `tests/test_webhook_contract.py`: valida token invalido, aceptacion token valido, deduplicacion `update_id`.
- `tests/test_modular_entrypoints.py`: valida que los wrappers modulares exponen apps operativas.
- `tests/test_webhook_handlers_unit.py`: valida dedup en memoria y rechazo por token invalido en handler.

## 5) Notas para evolucion

- Estos contratos deben tratarse como baseline para la migracion a arquitectura modular completa.
- Si se cambia algun contrato HTTP o de modulo, actualizar primero tests de contrato y luego consumidores.


