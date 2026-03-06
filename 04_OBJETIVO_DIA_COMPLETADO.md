# 04 - OBJETIVO DÍA COMPLETADO: Telegram E2E Log App

---

## Fase 1: Alcance y contratos ✅ COMPLETADO

**Estado:** Completado

**Criterios "E2E OK" definidos:**
| Componente | Criterio |
|------------|----------|
| API | `GET /health` OK + `POST /api/v1/chat` OK |
| Webhook | `GET /health` OK + `POST /webhook/{token}` OK |
| Telegram | `getWebhookInfo` sin errores recientes + `pending_update_count` estable |

**Comandos MVP definidos:**
| Comando | Descripción |
|---------|-------------|
| `/health` | Estado de API + Webhook |
| `/e2e` | Secuencia completa (API → Webhook local → Webhook público → Telegram) |
| `/webhookinfo` | Resumen de `getWebhookInfo` |
| `/logs` | Últimos N eventos relevantes |

**Formato de reporte:**
- Timestamp UTC
- Resultado por etapa: `OK/FAIL`
- Error corto + "pista" (qué revisar)

---

## Fase 2: Bot de Telegram (credenciales y seguridad) ✅ COMPLETADO

**Estado:** Completado

**Configuración en `.env`:**
| Variable | Valor |
|----------|-------|
| TELEGRAM_BOT_TOKEN | `8588...qJw` |
| ADMIN_CHAT_IDS | (vacío = permite todos) |
| WEBHOOK_TOKEN | `mysecretwebhooktoken` |

**Archivos creados/modificados:**
- `.env` - Actualizado
- `app/telegram_ops/__init__.py` - Módulo creado
- `app/telegram_ops/checks.py` - Funciones de verificación
- `app/telegram_ops/entrypoint.py` - Bot con comandos

**Seguridad implementada:**
- ✅ Verificación de ADMIN_CHAT_IDS en handlers
- ✅ Rate limiting (30s entre /e2e)
- ✅ Enmascaramiento de tokens en respuestas
- ✅ Verificación de acceso antes de procesar comandos

**Comandos implementados:**
- `/start` - Mensaje de bienvenida
- `/health` - Estado de API y Webhook
- `/e2e` - Checks E2E completos
- `/webhookinfo` - Info del webhook de Telegram
- `/logs` - Últimos eventos operativos (Fase 5)

---

## Fase 3: Punto de ejecución ✅ COMPLETADO

**Estado:** Completado

**Opción seleccionada:** Opción A - Servicio separado `telegram_ops`

**Estructura creada:**
```
app/telegram_ops/
├── __init__.py
├── checks.py      # Funciones de verificación
└── entrypoint.py  # Bot de Telegram
```

**Ejecución:**
```bash
python -m app.telegram_ops.entrypoint
```

---

## Fase 4: Implementar "checks" (funciones puras) ✅ COMPLETADO

**Estado:** Completado

**Funciones implementadas en `app/telegram_ops/checks.py`:**

| Función | Descripción | Timeout |
|---------|-------------|---------|
| `check_api_health()` | GET /health de API | 5s |
| `check_api_chat()` | POST /api/v1/chat | 10s |
| `check_webhook_health()` | GET /health de Webhook | 5s |
| `check_webhook_local()` | POST /webhook/{token} local | 10s |
| `check_webhook_public(ngrok_url)` | POST /webhook/{token} público (ngrok) | 15s |
| `get_webhook_info()` | GET getWebhookInfo de Telegram | 10s |
| `run_e2e_check()` | Ejecución completa de todos los checks | - |

**Características:**
- ✅ Timeouts agresivos (2-5s para health, 10-15s para checks)
- ✅ Retorna objetos estructurados (Dict) con captura de excepciones
- ✅ Enmascaramiento de tokens en respuestas
- ✅ Todas las funciones son async

---

## Fase 5: Captura de logs "operativos" ✅ COMPLETADO

**Estado:** Completado

### 5.1 Eventos mínimos registrados

| Evento | Descripción | Campos |
|--------|-------------|--------|
| `webhook.received` | Update recibido desde Telegram | `update_id`, `chat_id`, `process_async` |
| `webhook.dedup.duplicate` | Update duplicado detectado | `update_id`, `chat_id` |
| `webhook.process_start` | Inicio de procesamiento | `update_id`, `chat_id`, `text_len` |
| `webhook.chat_api.ok` | Chat API respondió OK | `update_id`, `chat_id`, `reply_len` |
| `webhook.chat_api.error` | Chat API falló | `update_id`, `chat_id` |
| `webhook.telegram_send.ok` | Mensaje enviado a Telegram | `update_id`, `chat_id` |
| `webhook.telegram_send.error` | Envío a Telegram falló | `update_id`, `chat_id` |
| `webhook.enqueue.ok` | Update encolado async | `update_id`, `chat_id`, `job_id` |
| `webhook.enqueue.error` | Enqueue falló | `update_id`, `chat_id` |
| `webhook.enqueue.unavailable` | Cola no disponible | `update_id`, `chat_id` |
| `webhook.forbidden` | Token inválido | - |
| `webhook.no_message` | Update sin mensaje | `update_id` |

### 5.2 Backend de logs

**Arquitectura dual:**

| Backend | Cuándo se usa | Características |
|---------|---------------|------------------|
| `InMemoryEventStore` | Sin `REDIS_URL` | Ring buffer, thread-safe, max 500 eventos |
| `RedisEventStore` | Con `REDIS_URL` | Lista Redis con TTL y trim automático |

**Configuración mediante variables de entorno:**

| Variable | Default | Descripción |
|----------|---------|-------------|
| `REDIS_URL` | - | URL de Redis (si vacía → usa memoria) |
| `OPS_EVENTS_MAX` | `1000` | Máximo eventos a retener |
| `OPS_EVENTS_TTL_SECONDS` | `604800` (7 días) | TTL de eventos en Redis |
| `OPS_EVENTS_REDIS_KEY` | `ops:events` | Key de lista en Redis |

### 5.3 Función para tail de eventos

```python
from app.ops.events import get_recent_events

# Últimos 50 eventos
events = get_recent_events(limit=50)

# Filtrar por chat_id
events = get_recent_events(limit=50, chat_id=123456789)

# Filtrar por update_id
events = get_recent_events(limit=50, update_id=123456)
```

### 5.4 Mejores prácticas aplicadas

**Thread-Safety:**
- `InMemoryEventStore` usa `threading.Lock` para operaciones concurrentes
- `RedisEventStore` usa pipelines atómicos (lpush + ltrim + expire)
- Singleton con `_STORE_LOCK` para inicialización perezosa

**Seguridad - Sanitización de Secretos:**

```python
# Claves eliminadas automáticamente: token, secret, password (case-insensitive)
# Valores enmascarados: TELEGRAM_BOT_TOKEN, WEBHOOK_TOKEN

sanitize_event({
    "telegram_bot_token": "123456:ABC-DEF1234ghIkl",  # Eliminado
    "detail": "Using token 123456:ABC-DEF1234ghIkl",  # Enmascarado → "1234...ghIkI"
})
```

**Best-Effort:** Nunca rompe el flujo principal si el store falla.

**Estructura de eventos:**

```python
{
    "ts_utc": "2026-03-06T12:34:56.789012+00:00",  # ISO 8601 UTC
    "component": "webhook",                          # Componente origen
    "event": "webhook.received",                    # Tipo de evento
    "level": "INFO",                                # INFO|WARN|ERROR|DEBUG
    "update_id": 123456,
    "chat_id": 123456789,
}
```

### 5.5 Integración

**En webhook handlers (`app/webhook/handlers.py`):**

```python
from app.ops.events import record_event

# Al recibir webhook
record_event(component="webhook", event="webhook.received", 
             update_id=update_id, chat_id=chat_id)

# Después de chat API
record_event(component="webhook", event="webhook.chat_api.ok",
             level="INFO", update_id=update_id, chat_id=chat_id, reply_len=len(reply))
```

**Comando `/logs` en bot:**

```
/logs 50              → Últimos 50 eventos
/logs 100 chat 12345 → Filtrar por chat_id
```

### 5.6 Tests unitarios

| Test | Descripción |
|------|-------------|
| `test_mask_token_short` | Tokens ≤8 chars → `***` |
| `test_mask_token_long` | Tokens >8 chars → `xxxx...yyyy` |
| `test_sanitize_event_drops_token_keys_and_masks_values` | Sanitización completa |
| `test_inmemory_store_tail_returns_newest_first` | Orden correcto |

### 5.7 Archivos creados/modificados

- `app/ops/events.py` - Store de eventos (InMemory + Redis)
- `app/ops/__init__.py` - Módulo exportado
- `app/webhook/handlers.py` - Emisión de eventos
- `app/telegram_ops/entrypoint.py` - Comando `/logs`
- `tests/test_ops_events_unit.py` - Tests unitarios

---

## Resumen de progreso

| Fase | Estado | Porcentaje |
|------|--------|------------|
| Fase 1: Alcance y contratos | ✅ Completado | 100% |
| Fase 2: Bot de Telegram | ✅ Completado | 100% |
| Fase 3: Punto de ejecución | ✅ Completado | 100% |
| Fase 4: Implementar "checks" | ✅ Completado | 100% |
| Fase 5: Logs operativos | ✅ Completado | 100% |
| Fase 6-10 | ⏳ Pendiente | 0% |

---

## Siguiente paso

**Fase 6:** Ejecución desde Telegram (comandos)
- Mejorar UX: ack rápido para `/e2e` (respuesta inmediata + resultado final)
- Correlación: introducir `run_id` y propagarlo a eventos/salida
- Expandir `/logs` con filtros por `run_id` (opcional)

---

## Notas

- El bot está configurado para ejecutarse con polling
- Para usar webhooks en producción, modificar `app.run_polling()` a `app.run_webhook()`
- ADMIN_CHAT_IDS vacío permite que todos los usuarios usen los comandos
