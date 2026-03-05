# Debug: Bot no responde y endpoints responden "No autorizado"

## Estado de las pruebas de debug

### ✅ 1. Token de Telegram verificado

```json
{"ok":true,"result":{"id":8588716358,"is_bot":true,"first_name":"manager-bot","username":"cmb_robot"}}
```

**Resultado:** Token válido, bot activo.

---

### ❌ 2. API no está corriendo

```bash
curl -s http://127.0.0.1:8000/health
# Resultado: Connection refused
```

**Solución:** Levantar la API:
```bash
python -m uvicorn app.api.entrypoint:app --host 127.0.0.1 --port 8000
```

---

### ❌ 3. Webhook no está corriendo

```bash
curl -s http://127.0.0.1:8001/health
# Resultado: Connection refused
```

**Solución:** Levantar el webhook:
```bash
python -m uvicorn app.webhook.entrypoint:app --host 127.0.0.1 --port 8001
```

---

### ✅ 4. Webhook de Telegram NO configurado

```json
{"ok":true,"result":{"url":"","has_custom_certificate":false,"pending_update_count":0}}
```

**Resultado:** No hay webhook configurado - el bot funciona en modo polling.

---

## Pasos para ejecutar

### Paso 1: Levantar la API

```bash
# Terminal 1
python -m uvicorn app.api.entrypoint:app --host 127.0.0.1 --port 8000
```

Verificar:
```bash
curl -s http://127.0.0.1:8000/health
# Debe responder: {"status":"ok"}
```

### Paso 2: Levantar el bot (polling)

```bash
# Terminal 2
python telegram_adapter.py
```

Ver logs:
```
INFO: Started Telegram adapter (python-telegram-bot, long-polling)
```

### Paso 3: Probar el bot

1. Enviar `/start` al bot `@cmb_robot`
2. El bot debe responder

---

## Troubleshooting adicional

### Si el bot no responde después de levantar

1. **Verificar que no hay conflicto de webhook:**
   ```bash
   curl -X POST "https://api.telegram.org/bot8588716358:AAGw3RX94SyEeM1UxM-3sGPPs83n3IM2qJw/deleteWebhook"
   ```

2. **Verificar que el adapter tiene el token correcto:**
   ```bash
   grep -n "TELEGRAM_TOKEN" telegram_adapter.py
   # Debe mostrar: 8588716358:AAGw3RX94SyEeM1UxM-3sGPPs83n3IM2qJw
   ```

3. **Verificar la API:**
   ```bash
   curl -X POST "http://127.0.0.1:8000/api/v1/chat?message=hola&session_id=test"
   ```

---

## Diagrama de flujo

```
┌─────────────────────────────────────────────────────────────┐
│                     MODO POLLING                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Telegram ──► Bot (@cmb_robot) ──► telegram_adapter.py    │
│                    (run_polling)    │                        │
│                                       ▼                        │
│                               API (puerto 8000)              │
│                               /api/v1/chat                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                     MODO WEBHOOK                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Telegram ──► Internet ──► ngrok (8001) ──► webhook        │
│                    (webhook URL)        app (puerto 8001)   │
│                                       │                        │
│                                       ▼                        │
│                               API (puerto 8000)              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Tabla de tokens

| Variable | Valor correcto | Usado por |
|----------|---------------|-----------|
| TELEGRAM_BOT_TOKEN | `8588716358:AAGw3RX94SyEeM1UxM-3sGPPs83n3IM2qJw` | telegram_adapter.py, webhook (validación) |
| WEBHOOK_TOKEN | `mysecretwebhooktoken` | No usado actualmente (ver Issue #1) |
| ADMIN_CHAT_IDS | Tu Chat ID | telegram_ops (solo para comandos) |

---

## Issue #1: WEBHOOK_TOKEN no se usa

**Problema:** El `.env` tiene `WEBHOOK_TOKEN=mysecretwebhooktoken` pero el código del webhook valida contra `TELEGRAM_BOT_TOKEN`.

**Solución implementada:** Corregido el código para usar `WEBHOOK_TOKEN` en validación.

---

## Comandos completos de arranque

```bash
# Terminal 1 - API
python -m uvicorn app.api.entrypoint:app --host 127.0.0.1 --port 8000

# Terminal 2 - Bot (polling)
python telegram_adapter.py

# Terminal 3 - Webhook (opcional, solo si usas webhook)
python -m uvicorn app.webhook.entrypoint:app --host 127.0.0.1 --port 8001

# Terminal 4 - ngrok (si usas webhook)
ngrok http 8001
```
