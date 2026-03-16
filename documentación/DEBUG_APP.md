# DEBUG_APP.md

## Objetivo

Depurar el flujo completo del bot (API, webhook, ops, enterprise, envio a Telegram).
Este runbook sigue la arquitectura actual en `app/`.

## 1) Preflight de entorno

Verifica `.env`:
- `TELEGRAM_BOT_TOKEN`
- `WEBHOOK_TOKEN` (si existe, es el token valido del webhook)
- `PROCESS_ASYNC` y `REDIS_URL`
- `API_HOST`, `API_PORT`, `WEBHOOK_PORT`
- `ADMIN_CHAT_IDS` si vas a usar OPS desde Telegram

## 2) Arrancar API

```bash
python -m uvicorn app.api.entrypoint:app --host 127.0.0.1 --port 8000
```

Health:

```bash
curl.exe http://127.0.0.1:8000/health
```

## 3) Arrancar Webhook

```bash
python -m uvicorn app.webhook.entrypoint:app --host 127.0.0.1 --port 8001
```

Health:

```bash
curl.exe http://127.0.0.1:8001/health
```

## 4) Smoke test de API (chat)

```bash
curl.exe -X POST "http://127.0.0.1:8000/api/v1/chat?message=hola&session_id=debug1"
```

Si falla aqui, el problema esta en `chat_service` o storage (app/database).

## 5) Smoke test de webhook local

Token valido: `WEBHOOK_TOKEN` si existe en `.env`, si no existe usa `TELEGRAM_BOT_TOKEN`.

```bash
curl.exe -X POST "http://127.0.0.1:8001/webhook/8588716358:AAGw3RX94SyEeM1UxM-3sGPPs83n3IM2qJw" ^
  -H "Content-Type: application/json" ^
  -d "{\"update_id\":12345,\"message\":{\"chat\":{\"id\":999},\"text\":\"hola\"}}"
```

Esperado:

```json
{"ok":true}
```

## 6) Revisar eventos y logs

Archivo principal:
- `logs/ops_events.jsonl`

Eventos clave:
- `webhook.received`
- `telegram.dispatch.chat_message`
- `webhook.chat_service.ok`
- `webhook.telegram_send.ok` o `webhook.telegram_send.error`
- `webhook.forbidden`
- `webhook.enqueue.unavailable` o `webhook.enqueue.error`

Comando util:

```bash
Get-Content -Path logs\\ops_events.jsonl -Tail 50
```

## 7) Validar envio a Telegram

Si `webhook.chat_service.ok` aparece pero `webhook.telegram_send.error` tambien:
- revisa conectividad a `https://api.telegram.org`
- valida `TELEGRAM_BOT_TOKEN`
- prueba con un `chat_id` real

El adaptador actual no marca error si el HTTP status es >= 400, solo registra evento.

## 8) Modo async (si aplica)

Para `PROCESS_ASYNC=true` necesitas:
- `REDIS_URL` activo
- `python worker.py` corriendo

Si falta Redis o worker, veras `webhook.enqueue.unavailable` o `webhook.enqueue.error`.

## 9) OPS y Enterprise

OPS: comandos `/health`, `/logs`, `/e2e`, `/webhookinfo`, `/start`. Valida `ADMIN_CHAT_IDS` si quieres restringir.

Enterprise: valida `ENTERPRISE_ENABLED` y `ENTERPRISE_MODERATION_ENABLED`, revisa `ENTERPRISE_OWNER_IDS` y feature flags `ENTERPRISE_FEATURE_*`.

## 10) Evidencia minima para escalar

Adjunta:
- salida de API y webhook
- ultimas lineas de `logs/ops_events.jsonl`
- resultado de `/health` y `/api/v1/chat`
- resultado del POST a `/webhook/<TOKEN_VALIDO>`
