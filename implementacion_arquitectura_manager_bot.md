Fecha: 2026-03-17
version: 1.0
referencia: propuesta_migracion_arquitectura.md

Resumen de la migracion:
Migrar el flujo de transporte Telegram para que ManagerBot use robot_ptb_compat como capa de compatibilidad PTB, unificar el router y eliminar duplicidades entre dispatchers. El resultado esperado es un solo punto de integracion para comandos y callbacks (menus), con soporte consistente en webhook y polling.

Arquitectura final:
- Runtime construido con `robot_ptb_compat.runtime.CompatApplicationBuilder`.
- Ingreso de updates via `robot_ptb_compat.runtime.WebhookHandler` o polling.
- Conversor de updates usando `robot_ptb_compat.bridge.UpdateBridge`.
- Registro de comandos/callbacks con `robot_ptb_compat.compat.handlers`.
- Dominio de menus y features permanece en `manager_bot` (MenuEngine + FeatureModule).
- Cliente Telegram principal usando `robot_ptb_compat.transport.TelegramClient`.

Tabla de tareas:
Fase: 1 - Fundaciones de compatibilidad
OBjetivo fase: Alinear el runtime y el pipeline de updates para que PTB sea la fuente de verdad.
Implementacion fase:
1. Incorporar `CompatApplicationBuilder` en `app/webhook/bootstrap.py`.
2. Integrar `WebhookHandler` para parsear updates PTB.
3. Agregar `UpdateBridge.to_internal` como entrada oficial para el dispatcher.

Fase: 2 - Adapter ManagerBot
OBjetivo fase: Conectar ManagerBot con handlers PTB sin duplicar routers.
Implementacion fase:
1. Crear `ManagerBotPtbAdapter` para registrar comandos y callbacks desde `ModuleRegistry`.
2. Usar `CommandAdapter` para `/config` y otros comandos enterprise.
3. Usar `CallbackAdapter` para callbacks de menus.

Fase: 3 - Cliente Telegram unificado
OBjetivo fase: Usar un solo cliente Telegram compatible con async.
Implementacion fase:
1. Reemplazar `RequestsTelegramClient` por `robot_ptb_compat.transport.TelegramClient`.
2. Ajustar `MenuEngine.send_menu_message` para aceptar el cliente PTB.
3. Normalizar `reply_markup` usando un helper comun.

Fase: 4 - Consolidacion de router
OBjetivo fase: Eliminar duplicidad entre `app/telegram/dispatcher.py` y `manager_bot`.
Implementacion fase:
1. Redirigir la clasificacion de updates al adapter de ManagerBot.
2. Remover o desactivar el router legacy.
3. Asegurar que `/config` y `welcome` funcionan en webhook y polling.

Fase: 5 - Mejoras de compatibilidad
OBjetivo fase: Mejorar interoperabilidad y estabilidad.
Implementacion fase:
1. Agregar routing por prefijo en `robot_ptb_compat` para callbacks.
2. Garantizar `message_id` en callbacks convertidos.
3. Definir interfaz `BotClient` (async/sync) en `manager_bot`.
4. Agregar pruebas E2E para `/config` + menus.

Ejecucion Fase 1 (2026-03-17):
- `robot_ptb_compat/runtime/webhook_runner.py`: se agrego `parse_update` y `to_internal` en `WebhookHandler` para convertir updates PTB a dict interno.
- `app/webhook/bootstrap.py`: se inicializa `CompatApplicationBuilder` y `WebhookHandler` y se exponen en `WebhookRuntime`.
- `app/webhook/entrypoint.py`: se pasa `ptb_webhook_handler` a `handle_webhook_impl`.
- `app/webhook/handlers.py`: se usa `ptb_webhook_handler.to_internal` y `UpdateBridge` como entrada oficial del dispatcher (fallback a JSON nativo si no hay PTB).

Ejecucion Fase 2 (2026-03-17):
- `app/manager_bot/_transport/telegram/ptb_adapter.py`: se creo `ManagerBotPtbAdapter` que registra `CommandAdapter` y `CallbackAdapter` y delega a `process_update_sync` usando `UpdateBridge`.
- `app/webhook/entrypoint.py`: se agrego el registro automatico de handlers PTB cuando existe `ptb_application`.

Ejecucion Fase 3 (2026-03-17):
- `app/webhook/handlers.py`: se agrego `_maybe_await` y se ajustaron `send_message` y `answer_callback_query` para soportar clientes async (robot_ptb_compat).
- `app/manager_bot/_transport/telegram/menu_engine.py`: se agrego `_maybe_await` en el flujo de callbacks raw para compatibilidad con `TelegramClient` async.
- `app/webhook/bootstrap.py`: se actualizo el tipo de `telegram_client` en runtime y se elimino dependencia explicita de `RequestsTelegramClient`.

Ejecucion Fase 4 (2026-03-17):
- `app/webhook/handlers.py`: se redirigio la clasificacion de updates (no callback) al router de `manager_bot` y se mantiene `dispatch_telegram_update` solo para callbacks.
- `app/manager_bot/_transport/telegram/router.py`: se elimino duplicidad de comandos OPS usando `OPS_COMMANDS` desde `app.telegram.services`.

Ejecucion Fase 5 (2026-03-17):
- `robot_ptb_compat/compat/handlers/callback_adapter.py`: se agrego helper de routing por prefijo (`prefix_pattern`) y `CallbackPrefixAdapter`.
- `robot_ptb_compat/compat/handlers/__init__.py`: se exportaron los nuevos helpers de callbacks.
- `app/telegram/dispatcher.py`: se corrigio `message_id` en callbacks (fallback a `message_id` o `id`).
- `app/manager_bot/_transport/telegram/bot_client.py`: se agrego interfaz `BotClient` (sync/async).
- `app/manager_bot/_transport/telegram/menu_engine.py`: se tipa `send_menu_message` con `BotClient`.
- `tests/test_menu_flow.py`: pruebas E2E basicas para `/config` y registro de `welcome_customize`.
