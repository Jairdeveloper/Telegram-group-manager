# Debug: Aplicacion/Bot no responde

## FALLA
# Descripcion falla:
*Se reporto que el comando `/e2e` no respondia aunque API y webhook estaban usando los entrypoints canonicos. Tras la verificacion del 2026-03-06, el flujo `/e2e` funciona a nivel de codigo y de servicios. La incidencia operativa observable en logs es un conflicto `409 Conflict` de Telegram cuando hay mas de una instancia del bot en polling.*

## Estado: ✅ COMPLETADO Y VERIFICADO

## Causa de la falla:
- `/e2e` requiere que el bot de Telegram este ejecutandose.
- El codigo de checks ya estaba corregido: `load_dotenv()` en `app/telegram_ops/checks.py`, webhook local con `TELEGRAM_BOT_TOKEN` y `FileEventStore` para `/logs`.
- La evidencia mas reciente en `bot.log` apunta a un problema operativo distinto del inicialmente documentado: multiples instancias del bot usando `getUpdates`, causando `409 Conflict`.

## Solución aplicada:
1. Mantener unicamente una instancia del bot: `.\.venv\Scripts\python.exe -m app.telegram_ops.entrypoint`
2. Si hay conflicto de polling: ejecutar `https://api.telegram.org/bot<TOKEN>/close`
3. Si hubiera webhook remoto configurado y se desea operar por polling: ejecutar `https://api.telegram.org/bot<TOKEN>/deleteWebhook`

## Estado: ✅ COMPLETADO (Fase 6)

### Archivos de debug por fase

| Fase | Archivo | Estado |
|------|---------|--------|
| Fase 0 | debug/00_debug.md | ✅ Completado |
| Fase 1 | debug/01_debug.md | ✅ Completado |
| Fase 2 | debug/02_debug.md | ✅ Verificado y actualizado |
| Fase 3 | debug/03_debug.md | ✅ Completado |
| Fase 4 | debug/04_debug.md | ✅ Completado |
| Fase 5 | debug/05_debug.md | ✅ Completado |
| Fase 6 | 04_OBJETIVO_DIA_COMPLETADO.md | ✅ Completado |

---

## Resumen de problemas resueltos

### Problemas resueltos
| Problema | Solución |
|----------|----------|
| ADMIN_CHAT_IDS inválido | Cambiado a vacío (permite todos) |
| check_webhook_local() usaba WEBHOOK_TOKEN | Corregido a TELEGRAM_TOKEN |
| WEBHOOK_PORT=8443 | Corregido a 8001 |
| checks.py no cargaba .env | Añadido load_dotenv() |
| /logs no respondía (sin eventos) | Implementado FileEventStore |
| Redis no disponible | Comentado REDIS_URL en .env |
| Fase 6: ack rápido /e2e | Implementado en entrypoint.py |
| Fase 6: run_id correlación | Implementado con uuid |

---

## Estado actual

| Servicio | Puerto | Estado |
|----------|--------|--------|
| API | 8000 | ✅ Corriendo |
| Webhook | 8001 | ✅ Corriendo |
| Bot | - | ✅ Corriendo (polling) |

## Verificacion ejecutada el 2026-03-06

```text
Health API:                OK    -> http://127.0.0.1:8000/health
Health Webhook:            OK    -> http://127.0.0.1:8001/health
run_e2e_check.api_health:  OK
run_e2e_check.api_chat:    OK
run_e2e_check.webhook_health: OK
run_e2e_check.webhook_local:  OK
Telegram getWebhookInfo:   OK    -> ok=true, url="", pending_update_count=0
/logs store compartido:    OK    -> eventos presentes en logs/ops_events.jsonl
```

## Observacion operativa

- `bot.log` contiene errores `409 Conflict: terminated by other getUpdates request`.
- Esto no invalida las correcciones de codigo, pero si explica por que el bot puede dejar de responder si hay otra instancia activa con el mismo token.

---

## Cambios realizados

### 1. app/telegram_ops/checks.py
- Añadido `load_dotenv()` al inicio del módulo

### 2. app/ops/events.py
- Añadido `FileEventStore` para compartir eventos entre procesos
- Modificado `get_event_store()` para usar FileEventStore por defecto

### 3. .env
- Comprobado `REDIS_URL` (comentado porque Redis no está disponible)

---

### 4. Resumen de comandos:

```powershell
# Terminal 1: API
.\.venv\Scripts\python.exe -m uvicorn app.api.entrypoint:app --host 127.0.0.1 --port 8000

# Terminal 2: Webhook
.\.venv\Scripts\python.exe -m uvicorn app.webhook.entrypoint:app --host 127.0.0.1 --port 8001

# Terminal 3: Bot
.\.venv\Scripts\python.exe -m app.telegram_ops.entrypoint
```

## Verificación

```
E2E Check:
- api_health: OK
- api_chat: OK
- webhook_health: OK
- webhook_local: OK
- telegram_webhook_info: OK
Overall: OK

Eventos operativos: ✅ Guardados en logs/ops_events.jsonl
```
## Tabla de variables

| Variable | Valor |
|----------|-------|
| TELEGRAM_BOT_TOKEN | configurado en `.env` |
| WEBHOOK_TOKEN | configurado en `.env` |
| ADMIN_CHAT_IDS | (vacio = permite todos) |

---

## Si sigue sin funcionar

1. Verificar que el entorno virtual tiene las dependencias:
   ```bash
   .\.venv\Scripts\pip.exe install -r requirements.txt
   ```

2. Verificar que no hay errores en los logs de las terminales
