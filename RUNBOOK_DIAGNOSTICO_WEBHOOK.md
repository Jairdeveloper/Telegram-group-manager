# Runbook rapido - Diagnostico webhook (<=10 min)

Objetivo: aislar fallas de procesamiento de mensajes de Telegram usando logs, metricas y estado de webhook.

## 1) Health local

```powershell
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8001/health
```

## 2) Estado Telegram

```powershell
curl "https://api.telegram.org/bot$env:TELEGRAM_BOT_TOKEN/getWebhookInfo"
```

Revisar:
- `result.url` debe apuntar a `/webhook/<TOKEN>`.
- `last_error_message` y `last_error_date`.
- `pending_update_count`.

## 3) Prueba de webhook manual

```powershell
$payload=@{ update_id=123456; message=@{ chat=@{ id=999 }; text='hola diagnostico' } } | ConvertTo-Json -Compress
curl -X POST "http://127.0.0.1:8001/webhook/$env:TELEGRAM_BOT_TOKEN" -H "Content-Type: application/json" -d $payload
```

Esperado: `{"ok":true}`.

## 4) Metricas webhook

```powershell
curl http://127.0.0.1:8001/metrics
```

Revisar:
- `telegram_webhook_requests_total{status="ok"}`
- `telegram_webhook_requests_total{status="error"}`
- `telegram_webhook_requests_total{status="duplicate"}`

## 5) Logs clave (mensajes estandarizados)

- `webhook.enqueued_update` -> update encolada (incluye `update_id`, `chat_id`, `job_id`)
- `webhook.duplicate_update` -> update duplicada ignorada
- `webhook.async_queue_unavailable` -> PROCESS_ASYNC activo sin cola disponible
- `webhook.chat_api_error` -> fallo llamando Chat API
- `webhook.telegram_send_error` -> fallo enviando respuesta a Telegram
- `webhook.handle_error` -> excepcion general en flujo webhook
- `webhook.no_message` -> payload sin `message`/`edited_message`

## 6) Diagnostico rapido por sintoma

- Telegram muestra 502/404 y local funciona:
  - problema de tunel/ingress/TLS/ruta publica.
- `webhook.async_queue_unavailable`:
  - falta Redis/worker o config de cola.
- `webhook.chat_api_error`:
  - revisar `CHATBOT_API_URL` y conectividad entre servicios.
- `webhook.telegram_send_error`:
  - revisar token bot, conectividad saliente y rate limits de Telegram.
