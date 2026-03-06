# Debug - Fase 1: Servicios y Conectividad

## Objetivo
Verificar que los servicios estén corriendo y respondiendo correctamente.

## Estado: ⏳ PENDIENTE DE EJECUTAR

---

## DIAGNÓSTICO ACTUAL (Pre-Fase)

### Problemas resueltos previamente
| Problema | Estado |
|----------|--------|
| ADMIN_CHAT_IDS | ✅ RESUELTO |
| check_webhook_local() usa TELEGRAM_TOKEN | ✅ CORREGIDO |
| WEBHOOK_PORT | ✅ CORREGIDO |

### Estado de servicios
| Servicio | Puerto | Estado |
|----------|--------|--------|
| API | 8000 | ⏳ Por verificar |
| Webhook | 8001 | ⏳ Por verificar |

**Los servicios deben estar levantados para que el bot funcione.**

---

## TAREA 1: Levantar los servicios

### IMPORTANTE: Usar el entorno virtual (.venv)

#### En Windows (PowerShell):

```powershell
# Terminal 1: API
.\.venv\Scripts\python.exe -m uvicorn app.api.entrypoint:app --host 127.0.0.1 --port 8000

# Terminal 2: Webhook  
.\.venv\Scripts\python.exe -m uvicorn app.webhook.entrypoint:app --host 127.0.0.1 --port 8001

# Terminal 3: Bot telegram_adapter
.\.venv\Scripts\python.exe telegram_adapter.py

# O Terminal 3: Bot telegram_ops
.\.venv\Scripts\python.exe -m app.telegram_ops.entrypoint
```

#### En Linux/Mac:

```bash
# Terminal 1: API
.venv/bin/python -m uvicorn app.api.entrypoint:app --host 127.0.0.1 --port 8000

# Terminal 2: Webhook
.venv/bin/python -m uvicorn app.webhook.entrypoint:app --host 127.0.0.1 --port 8001

# Terminal 3: Bot
.venv/bin/python -m app.telegram_ops.entrypoint
```

---

## TAREA 2: Verificar servicios

Después de levantar, ejecutar:

```bash
# Verificar API
curl http://127.0.0.1:8000/health
# Esperado: {"status":"ok"}

# Verificar Webhook
curl http://127.0.0.1:8001/health
# Esperado: {"status":"ok"}
```

---

## TAREA 3: Probar webhook manualmente

```bash
curl -X POST "http://127.0.0.1:8001/webhook/<TELEGRAM_BOT_TOKEN>" `
  -H "Content-Type: application/json" `
  -d "{\"update_id\":123456789,\"message\":{\"message_id\":1,\"chat\":{\"id\":123},\"text\":\"hola\",\"date\":1234567890}}"
```

---

## TAREA 4: Verificar token cargado

```bash
.\.venv\Scripts\python.exe -c "import os; from dotenv import load_dotenv; load_dotenv(); print('TELEGRAM_TOKEN:', os.getenv('TELEGRAM_BOT_TOKEN'))"
```

---

## RESULTADOS ESPERADOS

| Prueba | Esperado |
|--------|----------|
| API health | {"status":"ok"} |
| Webhook health | {"status":"ok"} |
| Webhook POST | {"ok":true} |
| Token cargado | Token visible |

---

## SI LOS SERVICIOS NO ARRANCAN

### Error de puerto en uso:
```bash
# Buscar proceso usando el puerto
netstat -ano | findstr :8000
```

### Error de permisos (Windows):
Intentar ejecutar como Administrador o usar puerto diferente.

### Error de módulo no encontrado:
Verificar que el entorno virtual tiene las dependencias:
```bash
.\.venv\Scripts\pip.exe install -r requirements.txt
```

---

## Referencia
- Fase previa: debug/00_debug.md
