# Debug - Fase 5: Soluciones y Procedimientos

## Estado: ⚠️ VERIFICADO CON INCIDENCIAS (2026-03-06)

---
## Error :
- telegram.error.Conflict: Conflict: terminated by other getUpdates request; make sure that only one bot instance is running
- El bot no responde al comando /e2e

## Resumen Ejecutivo

Esta fase documenta las soluciones implementadas y los procedimientos de debug utilizados para solucionar los problemas del bot de Telegram.

La verificacion ejecutada el 2026-03-06 muestra que varias correcciones siguen presentes en el codigo, pero el sistema no esta completamente sano:
- la API en `127.0.0.1:8000` no responde
- el webhook en `127.0.0.1:8001` si responde
- el bot presenta conflicto de polling en Telegram (`409 Conflict`)
- `/e2e` falla actualmente por dependencia de API caida

---

## Verificacion Ejecutada el 2026-03-06

### Resultado de los checks

| Verificacion | Resultado observado |
|-------------|---------------------|
| `GET http://127.0.0.1:8000/health` | FAIL - "No es posible conectar con el servidor remoto" |
| `GET http://127.0.0.1:8001/health` | OK - `{"status":"ok"}` |
| `POST /webhook/<TELEGRAM_BOT_TOKEN>` | OK - `{"ok":true}` |
| `get_recent_events(limit=8)` | OK - eventos recientes en `logs/ops_events.jsonl` |
| `run_e2e_check()` | FAIL |

### Salida observada de `run_e2e_check()`

```json
{
  "timestamp": "2026-03-06T11:46:14.765064Z",
  "checks": {
    "api_health": { "status": "FAIL", "error": "All connection attempts failed" },
    "api_chat": { "status": "FAIL", "error": "All connection attempts failed" },
    "webhook_health": { "status": "OK", "code": 200, "response": { "status": "ok" } },
    "webhook_local": { "status": "OK", "code": 200 },
    "telegram_webhook_info": { "status": "FAIL", "error": "All connection attempts failed" }
  },
  "overall": "FAIL"
}
```

### Evidencia adicional

- `bot.log` sigue mostrando `Conflict: terminated by other getUpdates request`
- el webhook manual deja eventos nuevos en `logs/ops_events.jsonl`
- se ejecuto la limpieza operativa de Telegram:
  - `close`: OK
  - `deleteWebhook`: OK

### Diagnostico actual

1. El bot puede dejar de responder a comandos si existe otra instancia activa haciendo polling con el mismo token.
2. Aunque el bot reciba `/e2e`, el comando ahora falla de verdad porque la API en `8000` no esta disponible.
3. `telegram_webhook_info` falla dentro de este entorno por falta de salida de red del sandbox; no debe interpretarse por si solo como fallo de configuracion del bot.

---

## Problemas Identificados y Soluciones

### Problema 1: ADMIN_CHAT_IDS inválido

| Aspecto | Detalle |
|---------|---------|
| **Síntoma** | Bot no respondía a ningún comando |
| **Causa** | ADMIN_CHAT_IDS tenía valor inválido en .env |
| **Solución** | Cambiado a vacío (permite todos los usuarios) |
| **Archivo** | `.env` |

```bash
# Antes
ADMIN_CHAT_IDS=invalid_value

# Después
ADMIN_CHAT_IDS=
```

---

### Problema 2: check_webhook_local() usaba WEBHOOK_TOKEN

| Aspecto | Detalle |
|---------|---------|
| **Síntoma** | Error 403 Forbidden en webhook_local |
| **Causa** | Función usaba WEBHOOK_TOKEN en lugar de TELEGRAM_BOT_TOKEN |
| **Solución** | Corregido a usar TELEGRAM_TOKEN |
| **Archivo** | `app/telegram_ops/checks.py` |

---

### Problema 3: WEBHOOK_PORT incorrecto

| Aspecto | Detalle |
|---------|---------|
| **Síntoma** | Webhook no accesible |
| **Causa** | WEBHOOK_PORT configurado como 8443 |
| **Solución** | Corregido a 8001 |
| **Archivo** | `.env` |

---

### Problema 4: checks.py no cargaba .env

| Aspecto | Detalle |
|---------|---------|
| **Síntoma** | TELEGRAM_BOT_TOKEN era None, todos los checks fallaban |
| **Causa** | Módulo no invocaba load_dotenv() |
| **Solución** | Añadido load_dotenv() al inicio del módulo |
| **Archivo** | `app/telegram_ops/checks.py` |

```python
# Añadido al inicio de app/telegram_ops/checks.py
from dotenv import load_dotenv
load_dotenv()
```

---

### Problema 5: /logs no respondía (sin eventos)

| Aspecto | Detalle |
|---------|---------|
| **Síntoma** | Comando /logs no devolvía eventos |
| **Causa** | InMemoryEventStore no se compartía entre procesos |
| **Solución** | Implementado FileEventStore |
| **Archivo** | `app/ops/events.py` |

**Implementación de FileEventStore:**

```python
class FileEventStore:
    def __init__(self, *, filepath: str = "logs/ops_events.jsonl", max_events: int = 500):
        self._filepath = filepath
        self._max_events = max_events
        self._lock = threading.Lock()
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)

    def publish(self, event: Dict[str, Any]) -> None:
        with self._lock:
            with open(self._filepath, "a") as f:
                f.write(json.dumps(event, ensure_ascii=False) + "\n")
            self._trim()

    def tail(self, limit: int) -> List[Dict[str, Any]]:
        # Lee eventos del archivo (más reciente primero)
        ...
```

---

### Problema 6: Redis no disponible

| Aspecto | Detalle |
|---------|---------|
| **Síntoma** | Errores de conexión a Redis en logs |
| **Causa** | REDIS_URL configurado pero Redis no corriendo |
| **Solución** | Comentado REDIS_URL en .env |
| **Archivo** | `.env` |

---

### Problema 7: Fase 6 - Ack rápido y run_id

| Aspecto | Detalle |
|---------|---------|
| **Síntoma** | /e2e no mostraba progreso ID ni de correlación |
| **Causa** | No implementado |
| **Solución** | Implementado ack rápido + run_id con uuid |
| **Archivo** | `app/telegram_ops/entrypoint.py` |

**Implementación:**

```python
import uuid

# Ack rápido
ack_msg = await update.message.reply_text(
    f"🔄 E2E check iniciado... (run_id: `{run_id}`)",
    parse_mode="Markdown"
)

# Editar con resultado
await ack_msg.edit_text(response, parse_mode="Markdown")
```

---

## Procedimientos de Debug

### Procedimiento 1: Verificar servicios

```bash
# Terminal
curl http://127.0.0.1:8000/health  # API
curl http://127.0.0.1:8001/health  # Webhook
```

**Esperado:**
- API: `{"status":"ok","version":"2.1"}`
- Webhook: `{"status":"ok"}`

---

### Procedimiento 2: Probar webhook manualmente

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

# O desde Python
from app.ops.events import get_recent_events
events = get_recent_events(limit=10)
```

---

### Procedimiento 4: Ejecutar E2E check

```python
from app.telegram_ops.checks import run_e2e_check
import asyncio

async def test():
    result = await run_e2e_check()
    print(f'Overall: {result["overall"]}')

asyncio.run(test())
```

---

### Procedimiento 5: Reiniciar todos los servicios

```bash
# Matar procesos
pkill -f "uvicorn"
pkill -f "telegram_ops"

# Iniciar servicios
.venv/bin/python -m uvicorn app.api.entrypoint:app --host 127.0.0.1 --port 8000 &
.venv/bin/python -m uvicorn app.webhook.entrypoint:app --host 127.0.0.1 --port 8001 &
.venv/bin/python -m app.telegram_ops.entrypoint &
```

---

### Procedimiento 6: Resolver conflicto de polling

```bash
# Cerrar sesión anterior del bot
curl "https://api.telegram.org/bot<TOKEN>/close"

# Eliminar webhook
curl "https://api.telegram.org/bot<TOKEN>/deleteWebhook"
```

---

## Comandos de Inicio Rápido

### Windows (PowerShell)

```powershell
# Terminal 1: API
.\.venv\Scripts\python.exe -m uvicorn app.api.entrypoint:app --host 127.0.0.1 --port 8000

# Terminal 2: Webhook
.\.venv\Scripts\python.exe -m uvicorn app.webhook.entrypoint:app --host 127.0.0.1 --port 8001

# Terminal 3: Bot
.\.venv\Scripts\python.exe -m app.telegram_ops.entrypoint
```

### Linux/Mac

```bash
# Terminal 1: API
.venv/bin/python -m uvicorn app.api.entrypoint:app --host 127.0.0.1 --port 8000

# Terminal 2: Webhook
.venv/bin/python -m uvicorn app.webhook.entrypoint:app --host 127.0.0.1 --port 8001

# Terminal 3: Bot
.venv/bin/python -m app.telegram_ops.entrypoint
```

---

## Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `.env` | ADMIN_CHAT_IDS vacío, WEBHOOK_PORT=8001, REDIS_URL comentado |
| `app/telegram_ops/checks.py` | Añadido load_dotenv() |
| `app/ops/events.py` | Añadido FileEventStore |
| `app/telegram_ops/entrypoint.py` | Ack rápido + run_id |

---

## Estado Final

| Servicio | Puerto | Estado |
|----------|--------|--------|
| API | 8000 | ❌ No responde |
| Webhook | 8001 | ✅ Corriendo |
| Bot | - | ⚠️ Con conflicto de polling en logs |

---

## Verificación

```
E2E Check:
- api_health: FAIL
- api_chat: FAIL
- webhook_health: ✅ OK
- webhook_local: ✅ OK
- telegram_webhook_info: FAIL dentro del sandbox
Overall: FAIL
```

## Accion operativa requerida

1. Levantar la API:
   `.\.venv\Scripts\python.exe -m uvicorn app.api.entrypoint:app --host 127.0.0.1 --port 8000`
2. Dejar una sola instancia del bot:
   `.\.venv\Scripts\python.exe -m app.telegram_ops.entrypoint`
3. Si reaparece el conflicto:
   `curl "https://api.telegram.org/bot<TOKEN>/close"`
   `curl "https://api.telegram.org/bot<TOKEN>/deleteWebhook"`

---

## Referencias

- Tokens: `.env`
- Eventos: `logs/ops_events.jsonl`
- Debug general: `debug.md`
- Objetivos: `04_OBJETIVO_DIA.md`
- Completado: `04_OBJETIVO_DIA_COMPLETADO.md`
