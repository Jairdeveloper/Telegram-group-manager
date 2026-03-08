# 11_debug.md

## Objetivo

Aislar y detectar bugs en el procesamiento de mensajes de texto del bot Telegram.

Este runbook esta orientado a responder una pregunta concreta:

- el fallo esta en Telegram
- el fallo esta en el webhook
- el fallo esta en la API de chat
- el fallo esta en Redis/worker
- o el fallo esta solo en el envio de respuesta a Telegram

## 1. Definir el modo de ejecucion

Revisa `.env`:

```env
PROCESS_ASYNC=false
```

Interpretacion:

- `PROCESS_ASYNC=false`: no usa worker ni Redis.
- `PROCESS_ASYNC=true`: necesitas Redis y `python worker.py`.

Regla de debug:

- empieza siempre con `PROCESS_ASYNC=false`
- haz funcionar el flujo completo asi
- activa async solo despues

Despues de cualquier cambio en `.env`, reinicia API, webhook y worker.

## 2. Variables minimas para debug local

Usa como base:

```env
TELEGRAM_BOT_TOKEN=...
CHATBOT_API_URL=http://127.0.0.1:8000/api/v1/chat
PROCESS_ASYNC=false
API_HOST=127.0.0.1
API_PORT=8000
WEBHOOK_PORT=8001
```

Si vas a probar async:

```env
REDIS_URL=redis://127.0.0.1:6379/0
PROCESS_ASYNC=true
```

Notas:

- En local normal suele ser `127.0.0.1`, no `redis`.
- El webhook canonico actual valida la ruta con `TELEGRAM_BOT_TOKEN`.
- Para pruebas de `POST /webhook/{token}`, usa `/webhook/<TELEGRAM_BOT_TOKEN>`.

## 3. Entry points reales del repo

Usa estos procesos:

### API

```bash
python -m uvicorn app.api.entrypoint:app --host 127.0.0.1 --port 8000
```

### Webhook

```bash
python -m uvicorn app.webhook.entrypoint:app --host 127.0.0.1 --port 8001
```

### Worker

```bash
python worker.py
```

Solo si `PROCESS_ASYNC=true`.

No uses para este repo:

- `chatbot_monolith.py`
- `telegram_webhook_prod.py`

Esos nombres no son los entrypoints canonicos actuales.

## 4. Health checks

### API

```bash
curl.exe http://127.0.0.1:8000/health
```

Esperado:

```json
{"status":"ok","version":"2.1"}
```

### Webhook

```bash
curl.exe http://127.0.0.1:8001/health
```

Esperado:

```json
{"status":"ok"}
```

Nota:

- `http://127.0.0.1/health` no aplica al arranque local recomendado.
- El puerto `80` aplica al contenedor o al proxy frontal, no al proceso uvicorn local de este repo.

## 5. Probar la API de chat aislada

```bash
curl.exe -X POST "http://127.0.0.1:8000/api/v1/chat?message=hola&session_id=test1"
```

Si esto falla:

- Telegram no es el problema principal
- el bug esta en API, imports, brain o storage

Si esto funciona:

- la API de chat esta sana
- pasa al webhook

## 6. Probar el webhook local manualmente

```bash
curl.exe -X POST "http://127.0.0.1:8001/webhook/<TELEGRAM_BOT_TOKEN>" ^
  -H "Content-Type: application/json" ^
  -d "{\"update_id\":12345,\"message\":{\"chat\":{\"id\":999},\"text\":\"hola\"}}"
```

Esperado:

```json
{"ok":true}
```

Esperado en logs operativos:

- `webhook.received`
- `webhook.process_start`
- `telegram.dispatch.chat` (mensaje conversacional)
- `telegram.dispatch.ops` (comando OPS)
- `telegram.dispatch.unsupported` (update no soportado)
- `webhook.chat_service.ok`
- `webhook.ops_service.ok`
- `webhook.telegram_send.ok`

Si esto falla:

- el problema esta en el webhook o en su conexion con la API

## 7. Revisar logs donde importa

Archivo principal:

- `logs/ops_events.jsonl`

Buscar eventos:

- `webhook.received`
- `webhook.process_start`
- `telegram.dispatch.chat`
- `telegram.dispatch.ops`
- `telegram.dispatch.unsupported`
- `webhook.chat_service.ok`
- `webhook.ops_service.ok`
- `webhook.chat_api.ok` (legacy, ya no se usa)
- `webhook.service.error`
- `webhook.telegram_send.ok`
- `webhook.telegram_send.error`
- `webhook.enqueue.ok`
- `webhook.enqueue.error`
- `webhook.enqueue.unavailable`
- `webhook.dedup.duplicate`
- `webhook.forbidden`
- `ops.command.completed`
- `ops.command.failed`

Archivos utiles:

- `app/webhook/handlers.py`
- `app/webhook/infrastructure.py`
- `app/telegram/dispatcher.py`
- `worker.py`
- `webhook_tasks.py`

Interpretacion rapida:

- `webhook.forbidden`: token de la ruta incorrecto.
- `webhook.chat_service.ok`: el webhook procesó mensaje conversacional correctamente.
- `webhook.ops_service.ok`: el webhook procesó comando OPS correctamente.
- `telegram.dispatch.ops`: el dispatcher clasificó el update como comando OPS.
- `telegram.dispatch.chat`: el dispatcher clasificó el update como mensaje conversacional.
- `telegram.dispatch.unsupported`: el update no tiene texto o es comando no soportado.
- `webhook.telegram_send.error`: la API respondió, pero falló el envío a Telegram.
- `webhook.service.error`: error en el servicio de dominio.
- `webhook.enqueue.error`: hay modo async, pero la cola falló.
- `webhook.enqueue.unavailable`: `PROCESS_ASYNC=true` pero no hay cola disponible.
- `webhook.dedup.duplicate`: el `update_id` ya fue visto.

## 8. Casos tipicos y su significado

### Caso A: API OK, webhook OK, Telegram no manda nada

Suele significar:

- webhook no registrado
- URL publica incorrecta
- TLS invalido
- proxy no enruta a `127.0.0.1:8001`

### Caso B: `403 Invalid token`

Suele significar:

- estas usando `/webhook/<WEBHOOK_TOKEN>`
- el codigo actual espera `/webhook/<TELEGRAM_BOT_TOKEN>`

### Caso C: `/health` o `/logs` no responden como chat

Ya no es un bug.

Desde la Fase 3, el webhook canonico procesa comandos OPS directamente:

- comandos OPS conocidos (`/health`, `/logs`, `/e2e`, `/webhookinfo`) se clasifican como `ops_command`
- se ejecutan via `handle_ops_command`
- se registra `telegram.dispatch.ops` y `webhook.ops_service.ok`

Si estos comandos no funcionan:
- revisa `logs/ops_events.jsonl` para `ops.command.completed` o `ops.command.failed`
- verifica que `ADMIN_CHAT_IDS` esta configurado en `.env`

### Caso D: `PROCESS_ASYNC=true` y no responde

Revisar:

- Redis arriba
- `REDIS_URL` correcto
- `python worker.py` corriendo

Para aislar:

- volver a `PROCESS_ASYNC=false`

### Caso E: `webhook.telegram_send.ok` pero el usuario no ve mensaje

No asumas que el envio fue realmente exitoso.

El adaptador actual no valida explicitamente `status_code >= 400` como error fuerte.
Si hace falta confirmar envio real:

- inspecciona respuesta HTTP a Telegram
- revisa logs detallados
- repite con un `chat_id` conocido

## 9. Verificar webhook registrado en Telegram

```bash
curl.exe "https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/getWebhookInfo"
```

Revisar:

- `url`
- `pending_update_count`
- `last_error_message`

Esperado:

- `url` no vacia
- apuntando a `https://.../webhook/<TELEGRAM_BOT_TOKEN>`

Si `url` esta vacia:

- Telegram no esta enviando updates al webhook

## 10. Estrategia recomendada para aislar

1. Pon `PROCESS_ASYNC=false`.
2. Arranca solo API + webhook.
3. Verifica `/health` en ambos.
4. Prueba `/api/v1/chat` directo.
5. Prueba webhook local manual.
6. Revisa `logs/ops_events.jsonl`.
7. Solo cuando eso funcione, registra webhook publico en Telegram.
8. Solo cuando eso funcione, activa `PROCESS_ASYNC=true`.
9. Anade Redis + worker.

## 11. Arquitectura actual (post-Fase 5)

El flujo actual es:

```
Telegram ──► app.webhook.entrypoint:app
                    │
                    ├── dispatcher (clasifica: chat_message / ops_command / unsupported)
                    │       │
                    │       ├── telegram.dispatch.chat
                    │       ├── telegram.dispatch.ops
                    │       └── telegram.dispatch.unsupported
                    │
                    ├── chat_message ──► handle_chat_message ──► chat API
                    │                           │
                    │                           └── webhook.chat_service.ok
                    │
                    └── ops_command ──► handle_ops_command ──► webhook.ops_service.ok
                                        │
                                        └── ops.command.completed / ops.command.failed
```

Componentes deprecated (no usar):
- `telegram_adapter.py`
- `app.telegram_ops.entrypoint.py` (ya no necesario)

## 12. Resultado esperado del debug

Debes poder responder con evidencia una de estas conclusiones:

- la API falla antes de Telegram
- el webhook no recibe updates
- el webhook recibe pero no llama bien a la API
- el webhook llama a la API pero falla el envio a Telegram
- el problema aparece solo en modo async
- el problema aparece solo desde Telegram publico

Si no puedes ubicar el fallo con este runbook, el siguiente paso razonable es capturar:

- salida del proceso API
- salida del proceso webhook
- ultimas lineas de `logs/ops_events.jsonl`
- resultado de `getWebhookInfo`
