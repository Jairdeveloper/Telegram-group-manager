# Debug: Bot no responde y endpoints responden "No autorizado"

## Diagnóstico

### Problemas identificados

#### 1. El webhook valida contra el TOKEN de Telegram, no contra WEBHOOK_TOKEN

El código en `app/webhook/handlers.py:85`:
```python
if token != bot_token:
    raise HTTPException(status_code=403, detail="Invalid token")
```

El `bot_token` es el **token de Telegram** (`TELEGRAM_BOT_TOKEN`), NO el `WEBHOOK_TOKEN`.

#### 2. Settings busca variable incorrecta

En `app/config/settings.py:41`:
```python
telegram_bot_token: Optional[str] = None
```

El setting busca `TELEGRAM_BOT_TOKEN` en el .env, pero debido a `case_sensitive=False`, debería funcionar. Verificar con:

```bash
python -c "from app.config.settings import load_webhook_settings; s = load_webhook_settings(); print(s.telegram_bot_token)"
```

#### 3. El bot usa polling, no webhook

El `telegram_adapter.py` usa:
```python
app.run_polling()  # No usa webhook
```

Esto significa que el bot debería responder mensajes directamente sin necesidad de configurar webhook en Telegram.

---

## Pasos de Debug

### 1. Verificar que el token de Telegram es correcto

```bash
curl -s "https://api.telegram.org/bot8588716358:AAGw3RX94SyEeM1UxM-3sGPPs83n3IM2qJw/getMe"
```

Debe responder con datos del bot.

### 2. Verificar que la API está corriendo

```bash
curl -s http://127.0.0.1:8000/health
```

### 3. Verificar que el webhook está corriendo

```bash
curl -s http://127.0.0.1:8001/health
```

### 4. Probar el webhook con el token de Telegram

```bash
curl -X POST "http://127.0.0.1:8001/webhook/8588716358:AAGw3RX94SyEeM1UxM-3sGPPs83n3IM2qJw" \
  -H "Content-Type: application/json" \
  -d '{"update_id":123456789, "message":{"message_id":1,"chat":{"id":123},"text":"hola","date":1234567890}}'
```

### 5. Verificar webhook en Telegram

```bash
curl -s "https://api.telegram.org/bot8588716358:AAGw3RX94SyEeM1UxM-3sGPPs83n3IM2qJw/getWebhookInfo"
```

Si muestra URL configurada, el webhook está activo.

### 6. Verificar si hay errores de entrega

```bash
curl -s "https://api.telegram.org/bot8588716358:AAGw3RX94SyEeM1UxM-3sGPPs83n3IM2qJw/getWebhookInfo" | jq .result.last_error_message
```

---

## Solución

### Opción A: Usar el adapter con polling (recomendado para desarrollo)

1. Asegúrate de que **NO** hay webhook configurado:
```bash
curl -X POST "https://api.telegram.org/bot8588716358:AAGw3RX94SyEeM1UxM-3sGPPs83n3IM2qJw/deleteWebhook"
```

2. Ejecutar el adapter:
```bash
python telegram_adapter.py
```

3. Enviar mensaje al bot `@cmb_robot`

### Opción B: Usar webhook en producción

1. Configurar ngrok:
```bash
ngrok http 8001
```

2. Registrar webhook:
```bash
python set_telegram_webhook.py "https://<ngrok-url>/webhook/8588716358:AAGw3RX94SyEeM1UxM-3sGPPs83n3IM2qJw"
```

3. Verificar:
```bash
curl -s "https://api.telegram.org/bot8588716358:AAGw3RX94SyEeM1UxM-3sGPPs83n3IM2qJw/getWebhookInfo"
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

El archivo `.env` tiene `WEBHOOK_TOKEN=mysecretwebhooktoken` pero el código del webhook valida contra `TELEGRAM_BOT_TOKEN`.

**Para corregir esto** (si deseas usar un token diferente para el webhook):

1. Actualizar `app/config/settings.py` para agregar `webhook_token`
2. Actualizar `app/webhook/bootstrap.py` para usar el nuevo setting

---

## Verificar logs

Para ver qué está pasando:

```bash
# Ver logs del adapter
python telegram_adapter.py

# Ver logs del webhook
python -m uvicorn app.webhook.entrypoint:app --host 127.0.0.1 --port 8001 --log-level debug
```
