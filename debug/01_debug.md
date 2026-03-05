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
| WEBHOOK_PORT=8443 → 8001 | ✅ CORREGIDO |

### Estado de servicios
| Servicio | Puerto | Estado |
|----------|--------|--------|
| API | 8000 | ❌ NO_CORRIENDO |
| Webhook | 8001 | ❌ NO_CORRIENDO |

**Los servicios deben estar levantados para que el bot funcione.**

---

## TAREA 1: Levantar los servicios

### Terminal 1: API
```bash
python -m uvicorn app.api.entrypoint:app --host 127.0.0.1 --port 8000
```

### Terminal 2: Webhook
```bash
python -m uvicorn app.webhook.entrypoint:app --host 127.0.0.1 --port 8001
```

### Terminal 3: Bot (Elige uno)

**Opción A: Bot de mensajes (telegram_adapter)**
```bash
python telegram_adapter.py
```

**Opción B: Bot E2E (telegram_ops)**
```bash
python -m app.telegram_ops.entrypoint
```

---

## TAREA 2: Verificar servicios

Después de levantar, ejecutar:

```bash
# Verificar API
curl -s http://127.0.0.1:8000/health
# Esperado: {"status":"ok"}

# Verificar Webhook
curl -s http://127.0.0.1:8001/health
# Esperado: {"status":"ok"}
```

---

##: Probar webhook TAREA 3 manualmente

```bash
curl -X POST "http://127.0.0.1:8001/webhook/8588716358:AAGw3RX94SyEeM1UxM-3sGPPs83n3IM2qJw" \
  -H "Content-Type: application/json" \
  -d '{"update_id":123456789,"message":{"message_id":1,"chat":{"id":123},"text":"hola","date":1234567890}}'
# Esperado: {"ok":true}
```

---

## TAREA 4: Verificar token cargado

```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('TELEGRAM_TOKEN:', os.getenv('TELEGRAM_BOT_TOKEN'))"
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

## SI FALLA DESPUÉS DE LEVANTAR

Revisar logs de cada terminal para identificar errores específicos.

## Referencia
- Fase previa: debug/00_debug.md
