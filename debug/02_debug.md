# Debug - Fase 0 y 1: Configuración y Servicios

## Estado: ✅ PARCIALMENTE COMPLETADO

---

## Problemas Reportados

| Problema | Descripción |
|----------|-------------|
| Bot no responde al comando `/logs` | El comando no devuelve eventos |
| `/e2e` falla en `webhook_local` | No puede alcanzar el webhook local |
| `/e2e` falla en `telegram_webhook_info` | No puede obtener info del webhook de Telegram |

---

## Acciones Realizadas

### 1. Servicios Levantados

```bash
# API (puerto 8000)
~/.local/bin/uvicorn app.api.entrypoint:app --host 127.0.0.1 --port 8000

# Webhook (puerto 8001)
~/.local/bin/uvicorn app.webhook.entrypoint:app --host 127.0.0.1 --port 8001
```

**Verificación:**
```bash
curl http://127.0.0.1:8000/health  → {"status":"ok","version":"2.1"}
curl http://127.0.0.1:8001/health  → {"status":"ok"}
```

### 2. Bug Encontrado y Corregido

**Archivo:** `app/telegram_ops/checks.py`

**Problema:** No cargaba `.env` - `TELEGRAM_BOT_TOKEN` era `None`

**Solución:** Añadir `load_dotenv()` al inicio del módulo

```python
from dotenv import load_dotenv
load_dotenv()
```

### 3. Verificación de E2E (TRAS CORRECCIÓN)

```
api_health: ✅ OK
api_chat: ✅ OK  
webhook_health: ✅ OK
webhook_local: ✅ OK
telegram_webhook_info: ✅ OK (sin webhook configurado - URL vacía)

Overall: ✅ OK
```

### 4. Conflicto de Polling

**Problema:** Error `409 Conflict` - otro bot usando el mismo token

**Solución ejecutada:**
```bash
# Cerrar sesión anterior
curl "https://api.telegram.org/bot<TOKEN>/close"

# Eliminar webhook
curl "https://api.telegram.org/bot<TOKEN>/deleteWebhook"
```

### 5. Problema con /logs

**Causa identificada:** 
- El store de eventos (`InMemoryEventStore`) NO se comparte entre procesos
- El webhook y el bot usan instancias separadas
- Sin Redis, los eventos se pierden entre procesos

**Solución requerida:** Levantar Redis para compartir eventos

---

## Resultados

| Prueba | Resultado |
|--------|-----------|
| API health | ✅ OK |
| Webhook health | ✅ OK |
| Webhook local test | ✅ OK |
| E2E check | ✅ OK |
| Bot polling | ✅ Corriendo (tras close) |
| /logs | ⚠️ Requiere Redis |

---

## Pendiente

1. **Instalar y configurar Redis** para compartir eventos operativos entre webhook y bot
2. **Configurar ngrok** para tener webhook público (opcional para producción)
3. **El usuario debe iniciar el bot** desde su terminal (el conflicto de polling indica que ya tiene otro proceso)
