# Debug: Bot responde "No autorizado"

## Problema identificado

El `.env` tenía:
```
ADMIN_CHAT_IDS=REPLACE_WITH_YOUR_CHAT_ID
```

Este valor NO es un Chat ID válido. La lógica de `is_admin()` en `app/telegram_ops/entrypoint.py`:

```python
def is_admin(chat_id: int) -> bool:
    if not ADMIN_CHAT_IDS or ADMIN_CHAT_IDS == [""]:
        return True  # Permite todos si está vacío
    return str(chat_id) in ADMIN_CHAT_IDS  # Verifica si está en la lista
```

Como `REPLACE_WITH_YOUR_CHAT_ID` es una cadena no vacía, el bot verifica si tu Chat ID es igual a esa cadena, lo cual nunca será cierto.

---

## ✅ Solución aplicada

Se corrigió el `.env`:
```
ADMIN_CHAT_IDS=
```

Ahora está vacío, lo que permite que **todos los usuarios usen los comandos**.

---

## Cómo obtener tu Chat ID

### Método 1: Visitar URL

1. Envía `/start` al bot `@cmb_robot`
2. Visita: `https://api.telegram.org/bot8588716358:AAGw3RX94SyEeM1UxM-3sGPPs83n3IM2qJw/getUpdates`
3. Busca `"chat":{"id":TU_NUMERO` en la respuesta

### Método 2: Eliminar temporalmente webhook

```bash
# Eliminar webhook para usar getUpdates
curl -X POST "https://api.telegram.org/bot8588716358:AAGw3RX94SyEeM1UxM-3sGPPs83n3IM2qJw/deleteWebhook"

# Obtener updates
curl -s "https://api.telegram.org/bot8588716358:AAGw3RX94SyEeM1UxM-3sGPPs83n3IM2qJw/getUpdates"
```

---

## Configurar ADMIN_CHAT_IDS

Una vez obtenido tu Chat ID, actualiza `.env`:

```env
ADMIN_CHAT_IDS=123456789
```

Para múltiples admins:
```env
ADMIN_CHAT_IDS=123456789,987654321
```

---

## Bots disponibles

| Bot | Archivo | Comando | Función |
|-----|---------|---------|---------|
| Adapter | `telegram_adapter.py` | `python telegram_adapter.py` | Responde a mensajes |
| E2E Ops | `app/telegram_ops/entrypoint.py` | `python -m app.telegram_ops.entrypoint` | Comandos /health, /e2e, /webhookinfo, /logs |

---

## Comandos del bot E2E

- `/start` - Mensaje de bienvenida
- `/health` - Estado de API + Webhook
- `/e2e` - Checks E2E completos
- `/webhookinfo` - Info del webhook de Telegram
- `/logs` - Últimos eventos

---

## Pasos para ejecutar

### Terminal 1 - API

```bash
python -m uvicorn app.api.entrypoint:app --host 127.0.0.1 --port 8000
```

### Terminal 2 - Bot E2E

```bash
python -m app.telegram_ops.entrypoint
```

### Terminal 3 - Webhook (opcional)

```bash
python -m uvicorn app.webhook.entrypoint:app --host 127.0.0.1 --port 8001
```

---

## Tabla de tokens

| Variable | Valor | Usado por |
|----------|-------|-----------|
| TELEGRAM_BOT_TOKEN | `8588716358:AAGw3RX94SyEeM1UxM-3sGPPs83n3IM2qJw` | Ambos bots |
| WEBHOOK_TOKEN | `mysecretwebhooktoken` | Webhook |
| ADMIN_CHAT_IDS | (vacío = permite todos) | telegram_ops |

---

## Verificación de estado

```bash
# Token Telegram
curl -s "https://api.telegram.org/bot8588716358:AAGw3RX94SyEeM1UxM-3sGPPs83n3IM2qJw/getMe"

# API
curl -s http://127.0.0.1:8000/health

# Webhook
curl -s http://127.0.0.1:8001/health

# Webhook info
curl -s "https://api.telegram.org/bot8588716358:AAGw3RX94SyEeM1UxM-3sGPPs83n3IM2qJw/getWebhookInfo"
```
