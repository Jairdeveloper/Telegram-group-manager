# Arranque del Proyecto (Dev y Produccion)

## 1. Requisitos

- Python 3.11+
- Dependencias instaladas:

```bash
pip install -r requirements.txt
```

- Opcional para modo produccion recomendado: Docker y Docker Compose

## 2. Variables de entorno

Crea un archivo `.env` en la raiz del proyecto con valores como estos:

```env
TELEGRAM_BOT_TOKEN=123456:ABC_REEMPLAZAR
CHATBOT_API_URL=http://127.0.0.1:8000/api/v1/chat
REDIS_URL=redis://127.0.0.1:6379/0
PROCESS_ASYNC=false
DEDUP_TTL=86400
API_HOST=127.0.0.1
API_PORT=8000
WEBHOOK_PORT=8001
LOG_LEVEL=INFO
ADMIN_CHAT_IDS=
WEBHOOK_TOKEN=mysecretwebhooktoken
```

Notas operativas:

- `PROCESS_ASYNC=false`: no usa worker ni Redis. Es el modo recomendado para aislar bugs.
- `PROCESS_ASYNC=true`: requiere `REDIS_URL` valido y `python worker.py`.
- En Docker Compose suele usarse `REDIS_URL=redis://redis:6379/0`.
- En local sin Docker Compose suele usarse `REDIS_URL=redis://127.0.0.1:6379/0`.
- El webhook canonico ahora valida contra `WEBHOOK_TOKEN` si esta configurado; si no, usa `TELEGRAM_BOT_TOKEN` (legacy).
- Se recomienda usar `WEBHOOK_TOKEN` en produccion para no exponer el `TELEGRAM_BOT_TOKEN` en la URL publica.

## 3. Canonical entrypoints

- API canonica: `app.api.entrypoint:app`
- Webhook canonico: `app.webhook.entrypoint:app`
- Worker: `worker.py`
- Telegram OPS transitorio (deprecated): `app.telegram_ops.entrypoint`

Importante:

- No ejecutar en paralelo más de un runtime Telegram para el mismo `TELEGRAM_BOT_TOKEN`.
- El flujo normal de mensajes y comandos OPS entra por `app.webhook.entrypoint:app`.
- `app.telegram_ops.entrypoint` está deprecated; ya no es necesario ya que el webhook ahora procesa:
  - Mensajes conversacionales normales
  - Comandos OPS (`/health`, `/logs`, `/e2e`, `/webhookinfo`)

## Definition of Done
## 4. Modo Dev (local)

### 4.1 Validar tests antes de arrancar

```bash
pytest -q
```

### 4.2 Levantar API

```bash
python -m uvicorn app.api.entrypoint:app --host 127.0.0.1 --port 8000
```

API disponible en:

- `http://127.0.0.1:8000`
- Health: `GET /health`
- Docs: `GET /docs`

### 4.3 Levantar webhook

```bash
python -m uvicorn app.webhook.entrypoint:app --host 127.0.0.1 --port 8001 --timeout-keep-alive 30 --timeout-graceful-shutdown 30
```

Webhook disponible en:

- `POST /webhook/{token}`
- `GET /health`
- `GET /metrics`

Nota:

- En local usa `8001`.
- El puerto `80` aplica al contenedor o al proxy frontal, no al arranque local recomendado.
- La ruta valida local y publica es `/webhook/<WEBHOOK_TOKEN>` si esta configurado; de lo contrario, usa `/webhook/<TELEGRAM_BOT_TOKEN>` (legacy).

### 4.4 Levantar worker (solo si `PROCESS_ASYNC=true`)

```bash
python worker.py
```

### 4.5 Levantar Telegram OPS transitorio (DEPRECATED - opcional)

```bash
python -m app.telegram_ops.entrypoint
```

**Nota**: Este runtime está deprecated. El webhook canónico ahora procesa todos los comandos OPS (`/health`, `/e2e`, `/webhookinfo`, `/logs`). Ya no es necesario arrancarlo por separado.

Comandos disponibles en ese runtime (solo si decide ejecutarlo):

- `/health`
- `/e2e`
- `/webhookinfo`
- `/logs`

Configuracion requerida:

1. Obtener tu Chat ID.
2. Configurarlo en `.env`:

```env
ADMIN_CHAT_IDS=123456789
```

3. Enviar `/start` al bot.

## 5. Smoke tests locales

### 5.1 Health API

```bash
curl.exe http://127.0.0.1:8000/health
```

Esperado:

```json
{"status":"ok","version":"2.1"}
```

### 5.2 Health webhook

```bash
curl.exe http://127.0.0.1:8001/health
```

Esperado:

```json
{"status":"ok"}
```

### 5.3 Chat API aislada

```bash
curl.exe -X POST "http://127.0.0.1:8000/api/v1/chat?message=hola&session_id=s1"
```

Si esto falla, Telegram no es el problema principal: la falla esta en la API.

### 5.4 Webhook local manual

```bash
curl.exe -X POST "http://127.0.0.1:8001/webhook/<WEBHOOK_TOKEN>" ^
  -H "Content-Type: application/json" ^
  -d "{\"update_id\":12345,\"message\":{\"chat\":{\"id\":999},\"text\":\"hola\"}}"
```

O si usas el token legacy:

```bash
curl.exe -X POST "http://127.0.0.1:8001/webhook/<TELEGRAM_BOT_TOKEN>" ^
  -H "Content-Type: application/json" ^
  -d "{\"update_id\":12345,\"message\":{\"chat\":{\"id\":999},\"text\":\"hola\"}}"
```

Esperado:

```json
{"ok":true}
```

Ademas deberias ver en `logs/ops_events.jsonl` una secuencia como:

- `webhook.received`
- `webhook.process_start`
- `webhook.chat_api.ok`
- `webhook.telegram_send.ok`

### 5.5 Token invalido

```bash
curl.exe -X POST "http://127.0.0.1:8001/webhook/token-invalido" -H "Content-Type: application/json" -d "{\"update_id\":1}"
```

Esperado: `403 Invalid token`.

## 6. Registro del webhook en Telegram

**Importante**: Sin configurar el webhook, Telegram no enviara los mensajes a tu servidor.

### 6.1 Con ngrok (desarrollo local)

1. Inicia ngrok:

```bash
ngrok 8001
```

2. Copia la URL HTTPS que te da ngrok (ej: `https://abc123.ngrok.io`)

3. Configura el webhook:

```bash
python set_webhook_prod.py set "https://TU_URL_NGROK/webhook/<WEBHOOK_TOKEN>"
```

O si usas el token legacy:

```bash
python set_webhook_prod.py set "https://TU_URL_NGROK/webhook/<TELEGRAM_BOT_TOKEN>"
```

Opcionalmente:

```bash
python set_telegram_webhook.py "https://TU_URL_NGROK/webhook/<WEBHOOK_TOKEN>"
```

### 6.2 Con dominio público (producción)

```bash
python set_webhook_prod.py set "https://TU_DOMINIO_PUBLICO/webhook/<WEBHOOK_TOKEN>"
```

### 6.3 Verificación

Después de configurar:

```bash
curl.exe "https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/getWebhookInfo"
```

Revisar:

- `url` - NO debe estar vacía
- `pending_update_count` - Debe ser 0
- `last_error_message` - Debe ser null/empty

Importante:

- Si `url` está vacía, Telegram NO está deliverando mensajes al webhook.
- La URL debe terminar en `/webhook/<WEBHOOK_TOKEN>` o `/webhook/<TELEGRAM_BOT_TOKEN>` (legacy).

### 6.4 Sincronización automática con ngrok

Si usas ngrok y la URL cambia frecuentemente:

```bash
powershell -ExecutionPolicy Bypass -File scripts/sync_ngrok_webhook.ps1
```

Ese script:

- Lee la URL HTTPS activa desde `http://127.0.0.1:4040/api/tunnels`
- Construye `/webhook/<WEBHOOK_TOKEN>` (o `/webhook/<TELEGRAM_BOT_TOKEN>` si no hay WEBHOOK_TOKEN)
- Ejecuta `setWebhook`
- Valida `getWebhookInfo`

## 7. Modo Produccion (Docker Compose)

### 7.1 Construir y arrancar

```bash
docker compose up --build
```

### 7.2 Verificar estado

- API: `GET http://localhost:8000/health`
- Webhook: `GET http://localhost:8001/health`
- Metrics webhook: `GET http://localhost:8001/metrics`

Nota:

- Dentro del contenedor el webhook puede escuchar en `80`.
- Desde fuera, el puerto publicado en la documentacion actual sigue siendo `8001`.

## 8. Troubleshooting básico

- Si falla import/config: revisa `.env` y `app/config/settings.py`.
- Si webhook no procesa en async: valida `REDIS_URL` y que `worker.py` este corriendo.
- Si `PROCESS_ASYNC=true` y no hay Redis, el webhook puede intentar fallback sync, pero seguiras teniendo ruido operacional.
- Si Telegram no entrega updates: revisa `set_webhook_prod.py`, dominio público, TLS y que `getWebhookInfo` tenga `url` no vacía.
- Si tienes `WEBHOOK_TOKEN` configurado, la URL del webhook debe usar ese token: `/webhook/<WEBHOOK_TOKEN>`.
- Si no tienes `WEBHOOK_TOKEN` configurado, el sistema usa `TELEGRAM_BOT_TOKEN` (legacy) para validar el webhook.
- Si envías comandos como `/health` al webhook canónico, hoy no se procesan como chat normal; quedan clasificados como comandos OPS o comandos no soportados según el texto.

## 9. Runbook de debug

Para un proceso detallado de aislamiento de bugs en mensajes de texto del bot, ver:

- `11_debug.md`
