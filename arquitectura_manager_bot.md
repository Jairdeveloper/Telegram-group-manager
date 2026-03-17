# Arquitectura de manager_bot

**Estado Actual**
- El modulo `app/manager_bot` define un dispatcher modular (ManagerBot + ModuleRegistry) y un sistema de menus con inline keyboards (MenuEngine, CallbackRouter, MenuRegistry).
- El flujo real del webhook hoy usa `app/telegram/dispatcher.py` y `app/enterprise/transport/handlers.py`, no `app/manager_bot/_transport/telegram/router.py`.
- El comando `/config` devuelve `{"status": "menu", "menu_id": "main"}` y el webhook intenta enviar el menu via `MenuEngine.send_menu_message`.
- La inicializacion del menu ocurre en `app/webhook/bootstrap.py` (create_menu_engine). Si esa inicializacion falla, el menu no se muestra.

**Estructura Del Modulo**
- `app/manager_bot/core.py` define `ManagerBot`, `Module`, `ModuleContract` y el registro de modulos base.
- `app/manager_bot/registry.py` gestiona el `ModuleRegistry` (registro, habilitacion, handlers).
- `app/manager_bot/_application/` contiene modulos de dominio:
- `app/manager_bot/_application/ops/__init__.py` comandos operativos (/health, /logs, etc).
- `app/manager_bot/_application/enterprise/__init__.py` comandos enterprise (/config, /antispam, etc) y handler de menu.
- `app/manager_bot/_application/agent/` gateway hacia servicio externo.
- `app/manager_bot/_config/` modelos y storage de configuracion por grupo (memory/postgres/redis).
- `app/manager_bot/_features/` handlers de callbacks por feature (antispam, welcome, filters, etc).
- `app/manager_bot/_menus/` definiciones de menus (main, moderation, antispam, welcome, etc).
- `app/manager_bot/_menu_service.py` fabrica global de MenuEngine, RateLimiter y ConversationState.
- `app/manager_bot/_transport/telegram/` router y motores de menu/teclado para Telegram.
- `app/manager_bot/_telemetry/` captura de eventos internos.

**Flujo De Datos (General)**
1. El webhook recibe un update y llama `dispatch_telegram_update` en `app/telegram/dispatcher.py`.
2. Si es comando enterprise, `app/webhook/handlers.py` invoca `handle_enterprise_command`.
3. Para `/config`, el handler devuelve `{"status": "menu"}`.
4. `app/webhook/handlers.py` obtiene el `MenuEngine` global y llama `send_menu_message`.
5. `MenuEngine` consulta `ConfigStorage`, construye `InlineKeyboardMarkup` y envia el mensaje via `TelegramClient`.

**Flujo /config -> Menu (Paso A Paso)**
1. Telegram envia update con texto `/config`.
2. `app/telegram/dispatcher.py` detecta `enterprise_command` (usa `app/enterprise/transport/dispatcher.py`).
3. `app/webhook/handlers.py` ejecuta `handle_enterprise_command` (en `app/enterprise/transport/handlers.py`).
4. El handler retorna `{"status": "menu", "menu_id": "main"}`.
5. `app/webhook/handlers.py` llama `get_menu_engine()` (de `app/manager_bot/_menu_service.py`).
6. `MenuEngine.send_menu_message` busca `main` en `MenuRegistry`, arma el teclado y envia el mensaje.

**Flujo Callback (Botones del Menu)**
1. Usuario toca un boton y Telegram envia `callback_query`.
2. `app/telegram/dispatcher.py` crea un dispatch `callback_query`.
3. `app/webhook/handlers.py` aplica rate limit con `RateLimiter`.
4. `MenuEngine.handle_callback_query_raw` crea un callback falso y llama `CallbackRouter.handle`.
5. `CallbackRouter` busca el handler por patron y ejecuta la feature correspondiente.
6. La feature actualiza `ConfigStorage` y re-renderiza el menu con `edit_message_text`.

**Menu Inline (Inline Keyboard)**
- El sistema actual implementa inline keyboards (callback_query), no el modo inline de Telegram (inline queries con `@bot`).
- El menu principal se define en `app/manager_bot/_menus/main_menu.py` y se registra en `register_all_menus`.
- La navegacion se maneja con callbacks `nav:*` registrados en `MenuEngine._setup_navigation_callbacks`.
- Cada feature registra sus callbacks en `_register_features` dentro de `app/manager_bot/_menu_service.py`.

**Mejoras Propuestas (Prioridad Alta)**
1. Unificar dispatcher: usar `app/manager_bot/_transport/telegram/router.py` en webhook o eliminar duplicidad con `app/telegram/dispatcher.py` para evitar rutas divergentes.
2. Asegurar inicializacion del menu: log y healthcheck en startup cuando `create_menu_engine` falla, y fallback a enviar un mensaje claro al usuario.
3. Corregir `extract_callback_data` en `app/telegram/dispatcher.py`: usa `message.get("id")` pero Telegram envia `message_id`.
4. Revisar deteccion de cliente en `MenuEngine.send_menu_message`: si el cliente no es async y no tiene `_bot_token`, el `await` fallara.
5. Consistencia de storage: `MENU_STORAGE_TYPE` vs `STORAGE_TYPE` pueden quedar desalineados; consolidar en una sola variable.

**Mejoras Propuestas (Inline Mode Real)**
- Si el objetivo es modo inline de Telegram, falta implementar handlers de `inline_query` y `chosen_inline_result`, ademas de habilitar inline en BotFather.
- Se puede crear un modulo `InlineQueryService` que use los mismos menus pero responda con `InlineQueryResultArticle`.

**Hipotesis De Por Que No Se Muestra El Menu**
- `MenuEngine` no se inicializa o falla en `app/webhook/bootstrap.py` (excepcion silenciada -> menu_engine None).
- `enterprise_enabled` esta en false en `EnterpriseSettings`, entonces `/config` retorna deshabilitado.
- El `TelegramClient` no acepta `reply_markup` en el formato esperado o el envio falla silenciosamente.
- No hay `MenuRegistry` cargado (error en `register_all_menus`) y `menu_id` no existe.
