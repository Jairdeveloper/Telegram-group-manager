# ARQUITECTURA_APP.md

## Resumen

La carpeta `app/` contiene los runtimes y servicios principales del bot:
- API HTTP para chat y lectura de historial.
- Webhook de Telegram para recibir updates.
- Worker RQ para procesamiento async.
- Modulos de OPS (health, logs, e2e).
- Modulos Enterprise (permisos, contenido, moderacion, utilidades).
- Capa de storage (Postgres o JSON).
- Observabilidad basica (eventos OPS y metricas).

## Entrypoints principales

- `app/api/entrypoint.py`: FastAPI de la API de chat.
- `app/webhook/entrypoint.py`: FastAPI del webhook de Telegram.
- `worker.py`: worker RQ para `PROCESS_ASYNC=true`.

Entrypoints legacy o no recomendados:
- `app/telegram_ops/entrypoint.py` (polling legacy).
- `chatbot_monolith.py`, `telegram_webhook_prod.py`.

## Flujo de datos (API)

```
Cliente HTTP
  -> /api/v1/chat
    -> app/api/routes.py
      -> chat_service/agent.py (patrones + respuestas)
      -> app/database (StorageAdapter -> repositorio)
      -> respuesta JSON
```

## Flujo de datos (Webhook Telegram)

```
Telegram
  -> /webhook/{token}
    -> validacion token (WEBHOOK_TOKEN o TELEGRAM_BOT_TOKEN)
    -> dedup (InMemory o Redis)
    -> dispatch_telegram_update (ops / enterprise / chat / unsupported)
       -> ops_command
          -> app/ops/services.py
          -> ops/events.py (eventos)
          -> response text -> sendMessage
       -> enterprise_command
          -> app/enterprise/transport/handlers.py
          -> app/enterprise/application/services.py
          -> response text -> sendMessage
       -> chat_message
          -> enterprise moderation (antispam/blacklist/antichannel)
          -> app/ops/services.handle_chat_message
          -> chat_service.Agent + storage
          -> response text -> sendMessage
```

## Flujo async (cuando PROCESS_ASYNC=true)

```
Webhook
  -> enqueue en RQ (si Redis disponible)
  -> worker.py consume job
  -> webhook_tasks.process_update
  -> process_update_impl (mismo flujo de arriba)
```

Si `PROCESS_ASYNC=true` pero no hay Redis/worker, el webhook registra
`webhook.enqueue.unavailable` y procesa en modo sync como fallback.

## Modulos y responsabilidades (app/)

- `app/api`: FastAPI y rutas REST de chat.
- `app/webhook`: webhook, dedup, metrics, y coordinacion del flujo.
- `app/telegram`: parsing y clasificacion de updates.
- `app/ops`: comandos OPS y store de eventos (`logs/ops_events.jsonl` o Redis).
- `app/enterprise`: comandos, moderacion, utilidades, y repositorios enterprise.
- `app/database`: repositorio de conversaciones (Postgres o JSON).
- `app/audit`, `app/guardrails`, `app/policies`: gobierno y seguridad de contenido.
- `app/monitoring`: soporte de metricas (via /metrics en webhook).
- `app/auth`, `app/billing`, `app/tools`, `app/planner`: modulos auxiliares (no todos se usan en los entrypoints actuales).

## Storage actual

Conversaciones: Postgres si `DATABASE_URL` es PostgreSQL, JSON (`conversations.json`) como fallback.

Eventos OPS: Redis si `REDIS_URL` disponible, archivo `logs/ops_events.jsonl` por defecto.

## Dependencias externas

- Telegram Bot API (`sendMessage`).
- Redis + RQ para async.
- SpamWatch y Sibyl (moderacion).
- AniList (utilidades).

## Configuracion relevante (.env)

- `TELEGRAM_BOT_TOKEN`
- `WEBHOOK_TOKEN` (si existe, reemplaza el token del webhook)
- `PROCESS_ASYNC`, `REDIS_URL`
- `CHATBOT_API_URL`, `API_HOST`, `API_PORT`, `WEBHOOK_PORT`
- `ADMIN_CHAT_IDS` (OPS)
- `ENTERPRISE_*` (features enterprise)
