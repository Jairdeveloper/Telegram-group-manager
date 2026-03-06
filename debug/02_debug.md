# Debug - Fase 2: Verificacion de Configuracion y Servicios

## Estado: ✅ VERIFICADO Y ACTUALIZADO (2026-03-06)

---

## Problemas Reportados originalmente

| Problema | Descripción |
|----------|-------------|
| Bot no responde al comando `/logs` | El comando no devuelve eventos |
| `/e2e` falla en `webhook_local` | No puede alcanzar el webhook local |
| `/e2e` falla en `telegram_webhook_info` | No puede obtener info del webhook de Telegram |

---

## Verificacion ejecutada

### 1. Servicios accesibles

```bash
# API
curl http://127.0.0.1:8000/health

# Webhook
curl http://127.0.0.1:8001/health
```

**Verificación:**
```bash
curl http://127.0.0.1:8000/health  -> {"status":"ok","version":"2.1"}
curl http://127.0.0.1:8001/health  -> {"status":"ok"}
```

### 2. Estado del codigo verificado

**Archivo:** `app/telegram_ops/checks.py`

**Comprobado:**
- `load_dotenv()` esta presente al inicio del modulo
- `check_webhook_local()` usa `TELEGRAM_BOT_TOKEN`
- `run_e2e_check()` ejecuta los 5 checks esperados

**Archivo:** `app/ops/events.py`

**Comprobado:**
- `FileEventStore` esta implementado
- `get_event_store()` cae a `FileEventStore` por defecto
- `logs/ops_events.jsonl` contiene eventos recientes

### 3. Verificacion E2E local

```
api_health: OK
api_chat: OK
webhook_health: OK
webhook_local: OK
telegram_webhook_info: FAIL dentro del sandbox (sin salida de red)

Overall: FAIL dentro del sandbox
```

### 4. Verificacion E2E externa a Telegram

Se ejecuto `getWebhookInfo` fuera del sandbox para separar fallo real de limitacion de red local.

**Resultado real:**
```json
{"ok":true,"url":"","pending_update_count":0,"last_error_message":null}
```

Conclusion: `telegram_webhook_info` no esta fallando en Telegram; el fallo observado en el check local era por aislamiento de red del entorno de ejecucion.

### 5. Estado de `/logs`

**Resultado actual:**
- `logs/ops_events.jsonl` existe
- Contiene eventos de `webhook` y de `ops.logs_requested`
- El almacenamiento compartido entre procesos esta funcionando sin Redis

### 6. Riesgo operativo vigente

`bot.log` contiene errores `409 Conflict: terminated by other getUpdates request`.

Interpretacion:
- hay o hubo mas de una instancia del bot usando polling con el mismo token
- este conflicto puede hacer que el bot deje de responder a comandos aun cuando API, webhook y checks locales esten correctos

Mitigacion operativa:
```bash
curl "https://api.telegram.org/bot<TOKEN>/close"
curl "https://api.telegram.org/bot<TOKEN>/deleteWebhook"
```

Luego dejar una sola instancia del bot:

```powershell
.\.venv\Scripts\python.exe -m app.telegram_ops.entrypoint
```

---

## Resultados verificados

| Prueba | Resultado |
|--------|-----------|
| API health | ✅ OK |
| Webhook health | ✅ OK |
| API chat | ✅ OK |
| Webhook local test | ✅ OK |
| Telegram getWebhookInfo | ✅ OK |
| /logs con archivo compartido | ✅ OK |
| Riesgo de polling duplicado | ⚠️ Vigilar |

---

## Pendiente

1. Asegurar que solo haya una instancia del bot en polling
2. Rotar el token de Telegram expuesto en documentacion y `.env`
3. Configurar ngrok solo si se necesita webhook publico
