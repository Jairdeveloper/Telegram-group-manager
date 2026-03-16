# Debug Guide - Robot Telegram

## El bot no responde a comandos

### 1. Verificar que el servidor está corriendo

```bash
# Ver procesos en ejecución
ps aux | grep uvicorn
# o
lsof -i :9000
```

Si no está corriendo, iniciarlo:
```bash
cd /mnt/c/Users/1973b/zpa/Projects/manufacturing/robot
uvicorn app.webhook.entrypoint:app --host 0.0.0.0 --port 9000
```

---

### 2. Verificar configuración del webhook en Telegram

El webhook debe apuntar a tu servidor público. Para desarrollo local, usa ngrok:

```bash
# Iniciar ngrok
ngrok http 9000

# Obtener URL pública (ej: https://abc123.ngrok.io)
```

**Verificar webhook actual:**
```bash
curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"
```

**Configurar webhook:**
```bash
curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" \
  -d "url=https://TU-DOMINIO/webhook/mysecretwebhooktoken"
```

**Eliminar webhook (si hay conflictos):**
```bash
curl -X POST "https://api.telegram.org/bot<TOKEN>/deleteWebhook"
```

Reemplaza `<TOKEN>` con: `8588716358:AAGw3RX94SyEeM1UxM-3sGPPs83n3IM2qJw`

---

### 3. Verificar variables de entorno

El servidor debe tener estas variables configuradas:

| Variable | Valor en .env |
|----------|---------------|
| `TELEGRAM_BOT_TOKEN` | `8588716358:AAGw3RX94SyEeM1UxM-3sGPPs83n3IM2qJw` |
| `WEBHOOK_TOKEN` | `mysecretwebhooktoken` |
| `CHATBOT_API_URL` | `http://127.0.0.1:8000/api/v1/chat` |
| `PROCESS_ASYNC` | `false` |

**Verificar en runtime:**
```python
from app.config.settings import load_webhook_settings
settings = load_webhook_settings()
print(f"Bot token: {settings.telegram_bot_token}")
print(f"Webhook token: {settings.webhook_token}")
```

---

### 4. Verificar logs del servidor

Busca mensajes relevantes:

```bash
# Logs del servidor
grep -E "webhook|dispatch|telegram" logs/*.log

# O en stdout del servidor
```

**Eventos clave a buscar:**
- `webhook.received` - Telegram envió un update
- `webhook.forbidden` - Token de webhook incorrecto
- `webhook.dedup.duplicate` - Update duplicado
- `telegram.dispatch.*` - Clasificación del update
- `webhook.ops_service.ok` - Comando OPS procesado
- `webhook.enterprise_service.ok` - Comando Enterprise procesado
- `webhook.telegram_send.*` - Respuesta enviada

---

### 5. Probar manualmente el endpoint

```bash
# Simular un mensaje de Telegram
curl -X POST "http://127.0.0.1:9000/webhook/mysecretwebhooktoken" \
  -H "Content-Type: application/json" \
  -d '{
    "update_id": 123456789,
    "message": {
      "message_id": 1,
      "from": {"id": 123456789, "is_bot": false, "first_name": "Test"},
      "chat": {"id": 123456789, "type": "private"},
      "date": 1234567890,
      "text": "/start"
    }
  }'
```

---

### 6. Debug con breakpoints

**Puntos de interrupción recomendados:**

| Archivo | Línea | Función | Propósito |
|---------|-------|---------|-----------|
| `app/webhook/entrypoint.py` | 108 | `webhook()` | **INICIO** - Receive POST |
| `app/webhook/handlers.py` | 252 | `handle_webhook_impl()` | Valida token |
| `app/webhook/handlers.py` | 34 | `process_update_impl()` | Procesa update |
| `app/telegram/dispatcher.py` | 34 | `dispatch_telegram_update()` | **CLASIFICA** tipo |
| `app/webhook/handlers.py` | 228 | `telegram_client.send_message()` | **ENVÍA** respuesta |

---

### 7. Verificar comandos disponibles

**Comandos OPS** (definidos en `app/telegram/services.py`):
- `/start` - Iniciar bot
- `/health` - Estado del sistema
- `/logs` - Ver logs
- `/e2e` - Prueba E2E
- `/webhookinfo` - Info del webhook

**Comandos Enterprise** (definidos en `app/enterprise/transport/dispatcher.py`):
- `/echo` - Eco del mensaje
- `/id` - Info del chat/usuario
- `/ping` - Ping
- Y otros definidos en el sistema

---

### 8. Casos comunes de problemas

| Síntoma | Causa probable | Solución |
|---------|---------------|----------|
| "Forbidden" en curl | Token incorrecto | Verificar `WEBHOOK_TOKEN` coincide |
| 404 en endpoint | Servidor no corriendo | Iniciar uvicorn |
| Bot no responde | Webhook no configurado | Configurar con setWebhook |
| Responde 2 veces | Webhook duplicado | Usar `deleteWebhook` primero |
| localhost no funciona | Telegram necesita URL pública | Usar ngrok |

---

### 9. Comandos de verificación rápida

```bash
# 1. Ver estado del bot
curl "https://api.telegram.org/bot8588716358:AAGw3RX94SyEeM1UxM-3sGPPs83n3IM2qJw/getMe"

# 2. Ver webhook info
curl "https://api.telegram.org/bot8588716358:AAGw3RX94SyEeM1UxM-3sGPPs83n3IM2qJw/getWebhookInfo"

# 3. Ver actualizaciones pendientes (si hay polling activo)
curl "https://api.telegram.org/bot8588716358:AAGw3RX94SyEeM1UxM-3sGPPs83n3IM2qJw/getUpdates"
```

**Importante:** Si hay otro proceso usando `getUpdates` (polling), el webhook no recibirá mensajes. Eliminar webhook y detener polling primero.

---

### 10. Iniciar en modo debug

```bash
cd /mnt/c/Users/1973b/zpa/Projects/manufacturing/robot
LOG_LEVEL=DEBUG uvicorn app.webhook.entrypoint:app --host 0.0.0.0 --port 9000 --reload
```

---

## Checklist de diagnóstico

- [ ] Servidor corriendo en puerto 9000
- [ ] Webhook configurado en Telegram con URL pública
- [ ] Token de webhook coincide (`mysecretwebhooktoken`)
- [ ] No hay otro bot en polling (ejecutar `deleteWebhook`)
- [ ] Logs muestran `webhook.received` al enviar mensaje
- [ ] Logs muestran `dispatch_telegram_update` con tipo correcto
- [ ] Logs muestran `telegram_send.ok` al final
