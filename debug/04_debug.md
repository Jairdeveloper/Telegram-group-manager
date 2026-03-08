# Debug - Fase 4: Problemas y Soluciones

## Estado: ✅ COMPLETADO

---

## Resumen de Problemas y Soluciones

### Problema 1: Bot no responde al comando `/logs`

**Síntoma:** El comando `/logs` no devolvía eventos

**Causa raíz:**
- El store de eventos (`InMemoryEventStore`) usaba memoria local del proceso
- Los procesos de webhook y bot eran instancias separadas
- No había forma de compartir eventos entre procesos

**Solución implementada:**
- Implementado `FileEventStore` en `app/ops/events.py`
- Eventos ahora se guardan en archivo `logs/ops_events.jsonl`
- Compartido entre todos los procesos

**Archivo modificado:** `app/ops/events.py`

---

### Problema 2: `/e2e` fallaba en `webhook_local`

**Síntoma:** `webhook_local: FAIL` con error 403

**Causa raíz:**
- `app/telegram_ops/checks.py` no cargaba `.env`
- `TELEGRAM_BOT_TOKEN` era `None`
- El webhook rechazaba el request por token inválido

**Solución implementada:**
- Añadido `load_dotenv()` al inicio de `app/telegram_ops/checks.py`

**Archivo modificado:** `app/telegram_ops/checks.py`

---

### Problema 3: `/e2e` fallaba en `telegram_webhook_info`

**Síntoma:** Error "TELEGRAM_BOT_TOKEN not set"

**Causa raíz:** Mismo problema que el anterior - `.env` no se cargaba

**Solución:** Misma que el problema 2

---

### Problema 4: Redis no disponible

**Síntoma:** Errores de conexión a Redis en logs

**Causa raíz:**
- `REDIS_URL=redis://127.0.0.1:6379/0` en `.env`
- Redis no estaba corriendo

**Solución implementada:**
- Comprobado `REDIS_URL` en `.env` (comentado)
- Ahora usa `FileEventStore` por defecto

**Archivo modificado:** `.env`

---

### Problema 5: Conflicto de polling en Telegram

**Síntoma:** Error `409 Conflict: terminated by other getUpdates request`

**Causa raíz:**
- Otra instancia del bot estaba corriendo
- O una sesión anterior no se cerró correctamente

**Solución implementada:**
```bash
# Cerrar sesión anterior
curl "https://api.telegram.org/bot<TOKEN>/close"

# Eliminar webhook si existe
curl "https://api.telegram.org/bot<TOKEN>/deleteWebhook"
```

---

## Procedimientos de Debug

### Procedimiento 1: Verificar servicios

```bash
# Verificar API
curl http://127.0.0.1:8000/health

# Verificar Webhook
curl http://127.0.0.1:8001/health
```

**Esperado:**
- API: `{"status":"ok","version":"2.1"}`
- Webhook: `{"status":"ok"}`

---

### Procedimiento 2: Probar webhook local

```bash
curl -X POST "http://127.0.0.1:8001/webhook/<TELEGRAM_BOT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"update_id":999999999,"message":{"message_id":1,"chat":{"id":123},"text":"test","date":1234567890}}'
```

**Esperado:** `{"ok":true}`

---

### Procedimiento 3: Verificar eventos operativos

```bash
# Ver archivo de eventos
cat logs/ops_events.jsonl
```

**Esperado:** Lista de eventos JSON

---

### Procedimiento 4: Verificar E2E

```python
from app.telegram_ops.checks import run_e2e_check
import asyncio

async def test():
    result = await run_e2e_check()
    print(result['overall'])

asyncio.run(test())
```

---

### Procedimiento 5: Reiniciar servicios

```bash
# Matar procesos existentes
pkill -f "uvicorn"
pkill -f "telegram_ops"

# Iniciar servicios
.venv/bin/python -m uvicorn app.api.entrypoint:app --host 127.0.0.1 --port 8000 &
.venv/bin/python -m uvicorn app.webhook.entrypoint:app --host 127.0.0.1 --port 8001 &
.venv/bin/python -m app.telegram_ops.entrypoint &
```

---

## Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `app/telegram_ops/checks.py` | Añadido `load_dotenv()` |
| `app/ops/events.py` | Añadido `FileEventStore` |
| `.env` | Comprobado `REDIS_URL` |
| `app/telegram_ops/entrypoint.py` | Implementado ack rápido y run_id |

---

## Verificación Final

| Prueba | Resultado |
|--------|-----------|
| API health | ✅ OK |
| Webhook health | ✅ OK |
| Webhook local test | ✅ OK |
| E2E check | ✅ OK |
| Eventos en archivo | ✅ OK |
| /logs desde bot | ✅ OK |

---

## Estado de Servicios

| Servicio | Puerto | Estado |
|----------|--------|--------|
| API | 8000 | ✅ Corriendo |
| Webhook | 8001 | ✅ Corriendo |
| Bot | - | ✅ Corriendo (polling) |

---

## Referencia

- Tokens en: `.env`
- Eventos en: `logs/ops_events.jsonl`
- Debug general: `debug.md`
