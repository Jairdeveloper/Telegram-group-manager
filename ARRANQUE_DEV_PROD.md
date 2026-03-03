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

## 3. Modo Dev (local)

### 3.1 Validar tests antes de arrancar

```bash
pytest -q
```

### 3.2 Levantar API

```bash
python chatbot_monolith.py --mode api
```

API disponible en:
- `http://127.0.0.1:8000`
- Health: `GET /health`
- Docs: `GET /docs`

### 3.3 Levantar webhook (otra terminal)

```bash
uvicorn telegram_webhook_prod:app --host 0.0.0.0 --port 80
```

Webhook disponible en:
- `POST /webhook/{token}`
- `GET /health`
- `GET /metrics`

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
- Webhook: `GET http://localhost:<puerto_webhook>/health`
- Metrics webhook: `GET /metrics`

### 4.3 Registrar webhook en Telegram

Con dominio publico y TLS:

```bash
python set_webhook_prod.py set https://<tu-dominio>/webhook/<TELEGRAM_BOT_TOKEN>
```

## 5. Pruebas rapidas de contrato

### 5.1 API chat

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/chat?message=hola&session_id=s1"
```

### 5.2 Webhook token invalido

```bash
curl -X POST "http://127.0.0.1/webhook/token-invalido" -H "Content-Type: application/json" -d "{\"update_id\":1}"
```

Esperado: `403 Invalid token`.

## 6. Troubleshooting basico

- Si falla import/config: revisa `.env` y `app/config/settings.py`.
- Si webhook no procesa en async: valida `REDIS_URL` y que `worker.py` este corriendo.
- Si Telegram no entrega updates: revisar `set_webhook_prod.py`, dominio publico y certificado TLS.
