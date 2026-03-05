# Arranque del Proyecto (Dev y Produccion)

## 1. Requisitos

- Python 3.11+
- Dependencias instaladas:

```bash
pip install -r requirements.txt
```

- (Opcional para modo produccion recomendado) Docker y Docker Compose

## 2. Variables de entorno

Crea un archivo `.env` en la raiz del proyecto con valores como estos:

```env
TELEGRAM_BOT_TOKEN=123456:ABC_REEMPLAZAR
CHATBOT_API_URL=http://127.0.0.1:8000/api/v1/chat
REDIS_URL=redis://redis:6379/0
PROCESS_ASYNC=true
DEDUP_TTL=86400
API_HOST=127.0.0.1
API_PORT=8000
LOG_LEVEL=INFO
```

Para local sin Docker Compose, usa:

```env
REDIS_URL=redis://127.0.0.1:6379/0
```

`redis://redis:6379/0` aplica cuando el webhook/worker corren dentro de la red de Docker Compose.

## 3. Modo Dev (local)

### 3.1 Validar tests antes de arrancar

```bash
pytest -q
```

### 3.2 Levantar API

```bash
uvicorn app.api.entrypoint:app --host 127.0.0.1 --port 8000
```

API disponible en:
- `http://127.0.0.1:8000`
- Health: `GET /health`
- Docs: `GET /docs`

Nota: el entrypoint canonico de API es `app.api.entrypoint:app` (Paso C elimino entrypoints legacy).

### 3.3 Levantar webhook (otra terminal)

```bash
uvicorn app.webhook.entrypoint:app --host 127.0.0.1 --port 8001 --timeout-keep-alive 30 --timeout-graceful-shutdown 30
```

Webhook disponible en:
- `POST /webhook/{token}`
- `GET /health`
- `GET /metrics`

Nota: en Docker Compose el contenedor escucha en `80` y se publica como `8001:80`. En local es recomendable usar `8001` para evitar puertos privilegiados.

### 3.4 Levantar worker (si `PROCESS_ASYNC=true`)

```bash
python worker.py
```

## 4. Modo Produccion (recomendado con Docker Compose)

### 4.1 Construir y arrancar

```bash
docker compose up --build
```

### 4.2 Verificar estado

- API: `GET http://localhost:8000/health`
- Webhook: `GET http://localhost:8001/health`
- Metrics webhook: `GET http://localhost:8001/metrics`

### 4.3 Registrar webhook en Telegram

Con dominio publico y TLS:

```bash

$env:TELEGRAM_BOT_TOKEN=(Get-Content .env | ? { $_ -like 'TELEGRAM_BOT_TOKEN=*' } | % { $_.Split('=')[1] })
python set_webhook_prod.py set "https://sulkiest-unworkmanlike-shondra.ngrok-free.dev/webhook/$env:TELEGRAM_BOT_TOKEN"

```

### 4.4 Auto-sync webhook con ngrok (cambio de URL)

Cuando ngrok cambia la URL publica, ejecuta:

```bash
powershell -ExecutionPolicy Bypass -File scripts/sync_ngrok_webhook.ps1
```

El script:
- lee la URL HTTPS activa desde `http://127.0.0.1:4040/api/tunnels`
- construye `/webhook/<TELEGRAM_BOT_TOKEN>`
- ejecuta `setWebhook` y valida `getWebhookInfo`

## 5. Pruebas rapidas de contrato

### 5.0 webhook state
```bash
curl "https://api.telegram.org/bot$env:TELEGRAM_BOT_TOKEN/getWebhookInfo"

 ```

### 5.1 API chat

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/chat?message=hola&session_id=s1"
```

### 5.2 Webhook token invalido

```bash
curl -X POST "http://127.0.0.1:8001/webhook/token-invalido" -H "Content-Type: application/json" -d "{\"update_id\":1}"
```

Esperado: `403 Invalid token`.

## 6. Troubleshooting basico

- Si falla import/config: revisa `.env` y `app/config/settings.py`.
- Si webhook no procesa en async: valida `REDIS_URL` y que `worker.py` este corriendo.
- Si Telegram no entrega updates: revisar `set_webhook_prod.py`, dominio publico y certificado TLS.

## 7. Canonical entrypoints (Fase 4)

- Webhook canonico: `app.webhook.entrypoint:app`
- API canonica: `app.api.entrypoint:app`
- Paso C (2026-03-04): entrypoints legacy eliminados (usar solo rutas canonicas).
