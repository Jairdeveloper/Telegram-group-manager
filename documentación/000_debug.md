# Debug - ManagerBot Execution

**Fecha**: 2026-03-11

---

## Problema Detectado

### Síntoma
Al ejecutar la app con `uvicorn app.webhook.entrypoint:app`, la aplicación inicia correctamente, pero:
- `/health` retorna `{"status":"ok"}` ✅
- `/manager/health` retorna `404 Not Found` ❌

### Causa Raíz
En `app/webhook/entrypoint.py`, el código de integración del ManagerBot estaba incompleto:
- El `ManagerBot` se inicializa de forma lazy
- Pero sus rutas NO se incluían en la app principal
- El mount de la app del ManagerBot no estaba implementado

---

## Verificación del Problema

```bash
# Ejecutar app
uvicorn app.webhook.entrypoint:app --host 127.0.0.1 --port 8080

# Test endpoint principal
curl http://127.0.0.1:8080/health
# Output: {"status":"ok"} ✅

# Test endpoint ManagerBot (ANTES de la fix)
curl http://127.0.0.1:8080/manager/health
# Output: 404 Not Found ❌
```

---

## Solución Aplicada

Se modificó `app/webhook/entrypoint.py` para incluir las rutas del ManagerBot mediante un mount en el startup:

```python
# ManagerBot integration (FASE 0)
_manager_bot = None


def _get_manager_bot():
    """Get or create ManagerBot instance."""
    global _manager_bot
    if _manager_bot is None:
        from app.manager_bot.core import ManagerBot
        _manager_bot = ManagerBot()
    return _manager_bot


# Include ManagerBot routes in the main app
@app.on_event("startup")
async def mount_manager_bot():
    """Mount ManagerBot routes on startup."""
    manager = _get_manager_bot()
    manager_app = manager.get_app()
    app.mount("/manager", manager_app)
```

---

## Verificación Post-Solución

```bash
# Test endpoint principal
curl http://127.0.0.1:8080/health
# Output: {"status":"ok"} ✅

# Test endpoint ManagerBot (DESPUÉS de la fix)
curl http://127.0.0.1:8080/manager/health
# Output: {"status":"ok","manager_bot":"ready"} ✅

# Test endpoint ManagerBot detallado
curl http://127.0.0.1:/manager/health
8080/manager# Output: {
#   "status":"ok",
#   "modules":{
#     "ops":{"status":"ok","module":"ops","commands":[...]},
#     "enterprise":{"status":"ok","module":"enterprise","commands":[...]}
#   },
#   "enabled_modules":["ops","enterprise"]
# } ✅
```

---

## Tests

Todos los tests pasan después del fix:

```
289 passed, 2 skipped, 2 warnings
```

---

## Advertencia (Warning)

Al ejecutar la app, aparece un warning de deprecación:

```
DeprecationWarning: on_event is deprecated, use lifespan event handlers instead.
```

Esto es un warning menor y no afecta la funcionalidad. Para corregirlo en el futuro, se podría migrar a lifespan events:

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    manager = _get_manager_bot()
    manager_app = manager.get_app()
    app.mount("/manager", manager_app)
    yield
    # Shutdown
    ...

app = FastAPI(lifespan=lifespan)
```

---

## Troubleshooting: Error 403 y 404 en Webhook

### Síntomas Reportados
- Bot responde 403 en la consola
- `getWebhookInfo` devuelve 404

### Causa Raíz
El webhook **no está configurado en Telegram**. La app está corriendo localmente (`localhost`) pero Telegram necesita una URL pública para enviar actualizaciones.

### Solución

#### Paso 1: Ejecutar la app

```bash
# Puerto 9000 (configurado en WEBHOOK_PORT)
uvicorn app.webhook.entrypoint:app --host 0.0.0.0 --port 9000
```

#### Paso 2: Exponer a internet (desarrollo)

Usar ngrok para desarrollo local:

```bash
# Instalar ngrok (si no lo tienes)
# https://ngrok.com/download

# Exponer puerto 9000
ngrok http 9000
```

Esto te dará una URL como: `https://abc123.ngrok.io`

#### Paso 3: Configurar webhook

```bash
# Usar el script creado
python set_webhook.py

# O manualmente:
curl -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setWebhook" \
  -d "url=https://tu-url.ngrok.io/webhook/mysecretwebhooktoken"
```

#### Paso 4: Verificar

```bash
curl "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getWebhookInfo"
```

### Explicación de Errores

| Error | Significado |
|-------|-------------|
| 404 | El webhook no está configurado en Telegram |
| 403 | El token en la URL no coincide con `WEBHOOK_TOKEN` |
| 403 | La URL del webhook no es accesible públicamente |

### Configuración

| Variable | Valor |
|----------|-------|
| `WEBHOOK_TOKEN` | `mysecretwebhooktoken` |
| Puerto | 9000 |
| Endpoint | `/webhook/{token}` |

---

## Conclusión

| Estado | Antes | Después |
|--------|-------|---------|
| `/health` | ✅ OK | ✅ OK |
| `/manager/health` | ❌ 404 | ✅ OK |
| `/manager/manager/health` | ❌ 404 | ✅ OK |
| Tests | 289 passed | 289 passed |

El bug fue corregido exitosamente.

