# Debug: Bot responde "No autorizado" y check_webhook_local()

---

## ✅ Problema 1: ADMIN_CHAT_IDS - RESUELTO

El `.env` tenía:
```
ADMIN_CHAT_IDS=REPLACE_WITH_YOUR_CHAT_ID
```

**Solución:** Se corrigió a `ADMIN_CHAT_IDS=` (vacío = permite todos).

---

## ✅ Problema 2: check_webhook_local() - RESUELTO

### Síntoma
La función `check_webhook_local()` fallaba porque usaba `WEBHOOK_TOKEN` (mysecretwebhooktoken), pero el webhook valida contra `TELEGRAM_BOT_TOKEN`.

### Causa
En `app/webhook/handlers.py:85`:
```python
if token != bot_token:  # bot_token = TELEGRAM_BOT_TOKEN
    raise HTTPException(status_code=403, detail="Invalid token")
```

### Solución aplicada
Se corrigió `app/telegram_ops/checks.py` para usar `TELEGRAM_TOKEN` en lugar de `WEBHOOK_TOKEN`:

```python
# Antes (incorrecto):
url = f"http://{API_BASE}:{WEBHOOK_PORT}/webhook/{WEBHOOK_TOKEN}"

# Después (correcto):
url = f"http://{API_BASE}:{WEBHOOK_PORT}/webhook/{TELEGRAM_TOKEN}"
```

---

## Tabla de tokens

| Variable | Valor | Usado por |
|----------|-------|-----------|
| TELEGRAM_BOT_TOKEN | `8588716358:AAGw3RX94SyEeM1UxM-3sGPPs83n3IM2qJw` | Webhook (validación), telegram_ops |
| WEBHOOK_TOKEN | `mysecretwebhooktoken` | No usado actualmente |

---

## Verificación

### 1. Levantar API
```bash
python -m uvicorn app.api.entrypoint:app --host 127.0.0.1 --port 8000
```

### 2. Levantar Webhook
```bash
python -m uvicorn app.webhook.entrypoint:app --host 127.0.0.1 --port 8001
```

### 3. Levantar Bot E2E
```bash
python -m app.telegram_ops.entrypoint
```

### 4. Probar manualmente
```bash
# Test webhook local
curl -X POST "http://127.0.0.1:8001/webhook/8588716358:AAGw3RX94SyEeM1UxM-3sGPPs83n3IM2qJw" \
  -H "Content-Type: application/json" \
  -d '{"update_id":123456789, "message":{"message_id":1,"chat":{"id":123},"text":"hola","date":1234567890}}'
```

---

## Bots disponibles

| Bot | Comando |
|-----|---------|
| E2E Ops | `python -m app.telegram_ops.entrypoint` |

## Comandos del bot

- `/start` - Bienvenida
- `/health` - Estado API + Webhook
- `/e2e` - Checks E2E completos
- `/webhookinfo` - Info webhook Telegram
- `/logs` - Últimos eventos
