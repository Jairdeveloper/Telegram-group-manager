# Solución: Error Telegram "message text is empty"

## Problema

El error `Exception: Telegram API error 400: {"ok":false,"error_code":400,"description":"Bad Request: message text is empty"}` ocurre cuando el handler intenta enviar un mensaje a Telegram con `text` vacío o `None`.

## Causa raíz

En `app/webhook/handlers.py`, la variable `reply` puede quedar sin valor o vacía en ciertos flujos:
- Cuando `ActionParser` ejecuta una acción que retorna `message=""` o `None`
- Cuando los handlers de estados (`waiting_*`) no asignan un valor a `reply`
- En casos de error donde `action_result.response_text` es vacío

## Solución aplicada

Se agregó una validación antes de enviar el mensaje a Telegram en la línea 760-763 de `handlers.py`:

```python
logger.info(f"About to send reply: {reply!r}")
if not reply or not reply.strip():
    logger.warning("webhook.empty_reply", extra=log_ctx)
    reply = "(sin respuesta)"
try:
    await _maybe_await(telegram_client.send_message(chat_id=chat_id, text=reply))
```

Ahora si `reply` está vacío o contiene solo espacios en blanco, se reemplaza por un mensaje por defecto `"(sin respuesta)"` y se registra un warning para facilitar debugging.

## Alternativas consideradas

1. **Retornar early si no hay respuesta**: Podría evitar enviar innecesariamente, pero algunos casos pueden requerir confirmar al usuario.
2. **Usar callback.answer() para callbacks vacíos**: No aplica para mensajes de chat regulares.