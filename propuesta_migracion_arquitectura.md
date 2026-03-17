# Propuesta de migracion y arquitectura (manager_bot + robot_ptb_compat)

**Objetivo**
- Documentar el flujo actual desde `/config` hasta el menu de navegacion.
- Proponer una migracion para que `manager_bot` use la libreria `robot_ptb_compat`.
- Identificar mejoras para aumentar compatibilidad entre ambos.

**Estado actual de manager_bot (resumen)**
- `manager_bot` define un dispatcher modular (`ManagerBot`, `ModuleRegistry`) y un sistema de menus con inline keyboards (`MenuEngine`, `CallbackRouter`, `MenuRegistry`).
- El runtime del webhook usa `app/telegram/dispatcher.py` + `app/webhook/handlers.py` y no el router de `manager_bot/_transport/telegram/router.py`.
- La funcionalidad de bienvenida (welcome) ya existe con menu principal y menu de personalizacion.

**Flujo de navegacion /config -> menu (actual)**
1. Telegram envia update con `/config`.
2. `app/telegram/dispatcher.py` clasifica como `enterprise_command`.
3. `app/webhook/handlers.py` llama `handle_enterprise_command`.
4. `/config` retorna `{status: menu, menu_id: main}`.
5. `MenuEngine.send_menu_message` envia el menu principal con inline keyboard.
6. El usuario pulsa el boton de `welcome`.
7. Llega `callback_query`, `MenuEngine.handle_callback_query_raw` lo procesa.
8. `CallbackRouter` ejecuta `WelcomeFeature` y muestra el menu `welcome`.
9. `Personalizar mensaje` abre `welcome_customize` para texto/multimedia.

**Finalidad del flujo (usando Welcome como ejemplo)**
- El menu es un panel de configuracion guiado.
- Se navega por submenus para modificar parametros del grupo sin comandos largos.
- En welcome, el objetivo es activar/desactivar y personalizar el mensaje con texto y multimedia.

**Analisis de robot_ptb_compat (resumen)**
- `runtime` ofrece `CompatApplicationBuilder`, `WebhookRunner` y `WebhookHandler`.
- `transport.TelegramClient` encapsula el bot PTB con metodos async.
- `bridge` convierte `Update`, `Message`, `CallbackQuery` a dict interno.
- `compat.handlers` provee adaptadores para comandos, callbacks e inline.

**Propuesta de refactor para usar robot_ptb_compat**

**Arquitectura objetivo**
- Usar `robot_ptb_compat.runtime.CompatApplicationBuilder` como factory de runtime.
- Convertir updates PTB a dict interno con `robot_ptb_compat.bridge.UpdateBridge`.
- Reemplazar el envio directo en `app/webhook/infrastructure.py` por `robot_ptb_compat.transport.TelegramClient`.
- Registrar handlers del ManagerBot con `compat.handlers` (CommandAdapter / CallbackAdapter).

**Refactor sugerido (pasos)**
1. Crear un adapter `ManagerBotPtbAdapter` (nuevo archivo sugerido):
- Recibe `ManagerBot` y registra handlers PTB a partir de `ModuleRegistry`.
- Usa `CommandAdapter` para comandos (ej: `/config`).
- Usa `CallbackAdapter` para callbacks (menu).
2. Reemplazar `dispatch_telegram_update` por `UpdateBridge.to_internal` cuando exista PTB.
3. En `app/webhook/bootstrap.py`, construir el runtime con `CompatApplicationBuilder` y usar `WebhookHandler` para parsear updates.
4. Ajustar `MenuEngine.send_menu_message` para aceptar `robot_ptb_compat.transport.TelegramClient` como cliente principal.
5. Unificar un solo router (el de manager_bot) y eliminar duplicidad con `app/telegram/dispatcher.py`.

**Mejoras propuestas para robot_ptb_compat**
- Agregar un helper de routing de callbacks con prefijos (similar a `CallbackRouter`).
- Proveer un metodo `to_internal` que garantice `message_id` en callback_query (evita bugs de id vs message_id).
- Incluir un wrapper sync opcional en `TelegramClient` para usos no async (compatibilidad con webhook legacy).
- Agregar un `MenuBridge` para convertir `InlineKeyboardMarkup` a dict si se usa cliente HTTP.
- Exportar un `parse_command` oficial para unificar logica con manager_bot.

**Mejoras propuestas para manager_bot**
- Consolidar el flujo de dispatch en un solo modulo (usar manager_bot router o robot_ptb_compat adapters, no ambos).
- Separar claramente transport (PTB/webhook) de dominio (MenuEngine + FeatureModule).
- Definir una interfaz `BotClient` con metodos async y sync; usarla en `MenuEngine`.
- Normalizar encoding y textos (evitar cadenas con caracteres corruptos).
- Agregar pruebas para `/config` y `welcome` con callbacks.

**Compatibilidad mutua (resumen)**
- `robot_ptb_compat` debe exponer conversiones estables a dict interno.
- `manager_bot` debe aceptar un `TelegramClient` async como dependencia.
- Los adapters PTB deben poder registrar handlers desde `ModuleRegistry`.

**Resultado esperado tras migracion**
- El flujo `/config` y los menus (welcome incluido) funcionan igual en webhook y polling.
- Menos duplicidad de routers y handlers.
- Un solo punto de integracion PTB con soporte a menus inline.
