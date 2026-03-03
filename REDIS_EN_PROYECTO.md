# Redis en este proyecto

## Que es Redis (version corta)
Redis es una base de datos en memoria, muy rapida. En este proyecto se usa como:
- Cola de trabajos (RQ) para procesar mensajes de Telegram en segundo plano.
- Almacen temporal para evitar procesar updates duplicados del webhook.

## Como lo aplicamos aqui
Cuando `PROCESS_ASYNC=true`:
1. El webhook recibe el mensaje de Telegram.
2. En lugar de responder en el mismo request, encola el trabajo en Redis (`telegram_tasks`).
3. `worker.py` consume esa cola y ejecuta `process_update`.
4. El worker llama al Chat API y envia la respuesta a Telegram.

Archivos clave:
- `telegram_webhook_prod.py` (webhook + cola)
- `app/webhook/handlers.py` (flujo y enqueue)
- `worker.py` (consumidor de cola RQ)
- `webhook_tasks.py` (tarea que responde a Telegram)

## Como activarlo
### Opcion A: Docker Compose (recomendado)
Desde la raiz del proyecto:

```bash
docker compose up --build
```

Esto levanta:
- `redis` (servidor Redis)
- `webhook` (FastAPI webhook)
- `worker` (procesa la cola)
- `chatapi` (API de chat)

### Opcion B: Local manual
1. Arranca Redis local (ejemplo con Docker):

```bash
docker run --name redis-local -p 6379:6379 redis:7-alpine
```

2. En `.env` usa una URL valida para tu entorno:

```env
REDIS_URL=redis://127.0.0.1:6379/0
PROCESS_ASYNC=true
```

3. Levanta API, webhook y worker en terminales separadas:

```bash
python chatbot_monolith.py --mode api
uvicorn telegram_webhook_prod:app --host 0.0.0.0 --port 80
python worker.py
```

## Si no quieres usar Redis
Puedes desactivarlo con:

```env
PROCESS_ASYNC=false
```

Asi el webhook procesa y responde de forma sincrona (sin cola).

## Checklist rapido de errores tipicos
- `PROCESS_ASYNC=true` pero `worker.py` no esta corriendo.
- `REDIS_URL` apunta a `redis://redis:6379/0` fuera de Docker (en local normal suele ser `127.0.0.1`).
- Webhook activo pero Chat API caida.
