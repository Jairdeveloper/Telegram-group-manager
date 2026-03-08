# Debug - Fase 10: Comandos `/logs` y `/e2e` respondidos por el brain (2026-03-06)

## Sintoma observado

Cuando se envian comandos como `/logs` o `/e2e`, el bot responde como si fueran mensajes normales del chatbot y devuelve respuestas del `brain`, en lugar de ejecutar los comandos OPS.

## Causa raiz

El webhook esta procesando cualquier `message.text` recibido como entrada de chat y lo reenvia al endpoint `POST /api/v1/chat`.

No existe un filtro para comandos Telegram en el flujo del webhook.

Ademas, el webhook y el bot OPS usan el mismo `TELEGRAM_BOT_TOKEN`. Por tanto, cuando Telegram entrega updates al webhook, esos comandos tambien entran en el flujo conversacional general.

## Evidencia en codigo

### 1. El webhook extrae cualquier texto sin distinguir comandos

Archivo: `app/webhook/handlers.py`

- `extract_chat_payload()` devuelve `chat_id` y `text` directamente desde `message.text`.
- `process_update_impl()` toma ese `text` y siempre llama:

```python
reply = chat_api_client.ask(message=text, session_id=session_id)
```

No hay ninguna condicion tipo:

- `text.startswith("/")`
- whitelist/blacklist de comandos
- dispatch de comandos antes del chat API

### 2. El adaptador legado si excluye comandos

Archivo: `telegram_adapter.py`

El handler se registra asi:

```python
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
```

Eso evita que `/logs`, `/e2e`, etc. se manden al chatbot.

### 3. El bot OPS si define esos comandos, pero en un runtime distinto

Archivo: `app/telegram_ops/entrypoint.py`

El bot OPS registra:

- `CommandHandler("e2e", e2e_command)`
- `CommandHandler("logs", logs_command)`
- `CommandHandler("health", health_command)`
- `CommandHandler("webhookinfo", webhookinfo_command)`

Es decir, los comandos existen, pero solo dentro del runtime `telegram_ops`.

## Evidencia en logs

Archivo: `logs/ops_events.jsonl`

Se observan updates del mismo `chat_id` del usuario OPS (`7821094774`) entrando por el webhook y siendo enviados al chat API:

- `webhook.received`
- `webhook.process_start`
- `webhook.chat_api.ok`
- `webhook.telegram_send.ok`

Ejemplos recientes:

- `update_id = 136122931`, `chat_id = 7821094774`, `text_len = 4`
- `update_id = 136122932`, `chat_id = 7821094774`, `text_len = 4`

Esto confirma que el webhook recibio mensajes del chat OPS y los proceso como conversacion normal.

## Interpretacion operativa

El comportamiento aparece cuando Telegram esta entregando los updates al webhook y no al runtime de polling del bot OPS.

Entonces ocurre esto:

1. El usuario envia `/e2e` o `/logs`.
2. Telegram entrega el update al webhook.
3. El webhook no reconoce comandos.
4. El webhook manda el texto `/e2e` o `/logs` a `POST /api/v1/chat`.
5. El `brain` responde como si fuera una frase cualquiera.
6. El webhook envia esa respuesta de vuelta a Telegram.

## Conclusion

El problema no esta en `brain.py`.

El problema es de enrutamiento y separacion de responsabilidades:

- el webhook conversacional no filtra comandos Telegram
- el bot OPS y el webhook comparten el mismo token

Por eso los comandos se tratan como texto normal cuando el update entra por el webhook.

## Recomendacion

Hay dos caminos correctos:

1. Separar bots:
   - un token para chatbot conversacional
   - otro token para bot OPS

2. O filtrar comandos en el webhook antes de llamar al chat API:
   - ignorar textos que empiecen por `/`
   - o despacharlos a un manejador de comandos especifico

La opcion mas limpia es separar los bots por token.
