# robot-ptb-compat

Librería de compatibilidad para integrar los módulos de la aplicación robot con el runtime de python-telegram-bot (PTB).

## Instalación

```bash
pip install robot-ptb-compat
```

## Uso Básico

### Webhook

```python
from robot_ptb_compat.runtime import CompatApplicationBuilder

app = (
    CompatApplicationBuilder(token=os.getenv("TELEGRAM_BOT_TOKEN"))
    .build()
)

app.run_webhook(
    listen="0.0.0.0",
    port=8080,
    url_path="webhook",
    webhook_url=os.getenv("WEBHOOK_URL"),
)
```

### Polling

```python
from robot_ptb_compat.runtime import CompatApplicationBuilder

app = (
    CompatApplicationBuilder(token=os.getenv("TELEGRAM_BOT_TOKEN"))
    .build()
)

app.run_polling()
```

## Módulos

### Bridge

Convierte entre formatos PTB y formato interno de la app:

```python
from robot_ptb_compat.bridge import UpdateBridge, MessageBridge, UserBridge, ChatBridge

# Convertir Update PTB a dict interno
update_dict = UpdateBridge.to_internal(update)

# Convertir Message PTB a dict interno
message_dict = MessageBridge.to_internal(message)
```

### Handlers

Adaptadores para handlers PTB:

```python
from robot_ptb_compat.compat.handlers import CommandAdapter, MessageAdapter, CallbackAdapter

# Crear un command handler
async def start_command(update, context):
    await update.message.reply_text("Hello!")

handler = CommandAdapter(
    commands=["start"],
    callback=start_command
)
```

### Filters

Filtros compatibles con PTB:

```python
from robot_ptb_compat.compat.handlers import FiltersAdapter

text_filter = FiltersAdapter.text()
photo_filter = FiltersAdapter.photo()
combined_filter = text_filter & photo_filter
```

### Constants

Constantes de PTB re-exportadas:

```python
from robot_ptb_compat.constants import ptb_limits, app_limits

print(ptb_limits.MAX_MESSAGE_LENGTH)
print(app_limits.RATE_LIMIT_SECONDS)
```

### Errors

Errores de PTB y de la app:

```python
from robot_ptb_compat.errors import telegram_errors, app_errors

# Errores PTB
raise telegram_errors.BadRequest("Invalid request")

# Errores propios de la app
raise app_errors.PolicyViolationError("Policy violated")
```

### Helpers

Helpers de PTB y propios:

```python
from robot_ptb_compat.helpers import ptb_helpers, app_helpers

# Helpers PTB
escaped = ptb_helpers.escape_markdown("Hello *world*")

# Helpers propios
command, args = app_helpers.parse_command("/start arg1 arg2")
```

### Telegram Client

Wrapper para el Bot de PTB:

```python
from robot_ptb_compat.transport import TelegramClient

client = TelegramClient(token="YOUR_TOKEN")

# Enviar mensaje
await client.send_message(chat_id=123, text="Hello!")

# Responder callback
await client.answer_callback_query(callback_query_id="xxx", text="Done!")
```

## Tests

```bash
pytest robot_ptb_compat/tests/
```

## Licencia

MIT
