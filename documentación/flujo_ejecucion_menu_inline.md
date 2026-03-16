# Flujo de Ejecución - Menú Inline Telegram Bot

## Resumen Ejecutivo

Este documento describe el flujo completo de ejecución cuando un usuario presiona un botón en un menú inline de Telegram, desde que el webhook recibe la actualización hasta que el bot responde al usuario.

---

## Hilo Principal de Ejecución

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. TELEGRAM WEBHOOK                                                        │
│    Telegram envía POST con JSON (Update) al endpoint del webhook           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. handle_webhook_impl()                                                   │
│    app/webhook/handlers.py:253                                             │
│    - Valida token del webhook                                              │
│    - Extrae payload del chat                                                │
│    - Verifica si es update duplicado (dedup)                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 3. process_update_impl()                                                   │
│    app/webhook/handlers.py:34                                             │
│    - Dispatacha el tipo de update (callback_query, command, etc.)          │
│    - Usa dispatch_telegram_update() para clasificar                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                         ┌──────────────────────────────┐
                         │ DECISIÓN: dispatch.kind     │
                         └──────────────────────────────┘
                                    │
           ┌─────────────────────────┼─────────────────────────┐
           │                         │                         │
           ▼                         ▼                         ▼
    "callback_query"           "ops_command"           "enterprise_command"
    (Ir a Hilo A)             (Ir a Hilo B)           (Ir a Hilo C)
```

---

## Hilo A: Callback Query (Botones Inline)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ A1. handlers.py:91 - Detecta callback_query                                │
│     dispatch.kind == "callback_query"                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ A2. Obtiene servicios globales                                             │
│     - menu_engine = get_menu_engine()                                      │
│     - rate_limiter = get_rate_limiter()                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                         ┌──────────────────────────────┐
                         │ DECISIÓN: Rate Limit        │
                         └──────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
           Rate limitado                    Rate permitido
           (Ir a A2a)                       (Ir a A3)
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ A2a. Responder "Demasiadas solicitudes"                                    │
│     - answer_callback_query() con show_alert=True                          │
│     - Registrar evento y retornar                                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                              [FIN DEL HILO]
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ A3. Validar callback_data                                                 │
│     if menu_engine and callback_data:                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                         ┌──────────────────────────────┐
                         │ DECISIÓN: callback_data    │
                         └──────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
           callback_data existe           callback_data vacío
           (Ir a A4)                     (Ir A3a)
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ A4. menu_engine.handle_callback_query_raw()                                │
│     app/manager_bot/transport/telegram/menu_engine.py:201                │
│                                                                             │
│     Parámetros:                                                            │
│     - callback_data: "antispam:show", "antispam:toggle:on", etc.         │
│     - callback_query_id: ID real de Telegram para ответ                   │
│     - chat_id, message_id, user_id                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ A5. Crear FakeCallbackQuery y FakeBot (mock objects)                      │
│     - Simulan la API de Telegram para uso en webhook                      │
│     - callback_query_id se almacena correctamente (FIX Tarea 1)            │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ A6. callback_router.handle(callback, bot)                                 │
│     app/manager_bot/transport/telegram/callback_router.py:96               │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                         ┌──────────────────────────────┐
                         │ DECISIÓN: Matching         │
                         └──────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
           Handler encontrado              No encontrado
           (Ir a A7)                       (Ir a A6a)
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ A7. Ejecutar handler específico                                            │
│                                                                             │
│     Tipos de handlers registrados:                                         │
│     - handle_menu_show: Muestra menú (antispam:show, mod:show, etc.)      │
│     - handle_toggle: Cambia configuración (antispam:toggle:on)           │
│     - handle_back: Navegación atrás                                        │
│     - handle_home: Volver al menú principal                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                         ┌──────────────────────────────┐
                         │ DECISIÓN: Tipo handler      │
                         └──────────────────────────────┘
                                    │
           ┌─────────────────────────┼─────────────────────────┐
           │                         │                         │
           ▼                         ▼                         ▼
    Menú show (X:show)        Toggle (X:toggle)         Navegación
    (Ir a A7a)                (Ir A7b)                  (Ir A7c)
           │                         │                         │
           └─────────────────────────┴─────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ A8. Responder al usuario                                                   │
│     callback.answer(text, show_alert=True)                                 │
│                                                                             │
│     NOTA: Esto llama a FakeCallbackQuery.answer()                        │
│     que usa callback_query_id REAL (FIX Tarea 1)                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ A9. Actualizar mensaje del menú (si aplica)                               │
│     callback.edit_message_text(text, reply_markup)                        │
│     - Si falla, usa reply_text como fallback                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                              [FIN DEL HILO]
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ A6a. Fallback: "Acción no reconocida"                                     │
│     callback.answer("❓ Acción no reconocida")                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                              [FIN DEL HILO]

┌─────────────────────────────────────────────────────────────────────────────┐
│ A3a. Callback_data vacío                                                   │
│     - Responder "Acción no reconocida"                                    │
│     - No invoca menu_engine                                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                              [FIN DEL HILO]
```

---

## Hilo B: Enterprise Command (/config)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ B1. handlers.py:149 - enterprise_command                                   │
│     dispatch.kind == "enterprise_command"                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ B2. handle_enterprise_command()                                           │
│     app/enterprise/__init__.py                                            │
│     - Procesa comando (/config, /antispam, etc.)                          │
│     - Retorna resultado con response_text o status="menu"                │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                         ┌──────────────────────────────┐
                         │ DECISIÓN: resultado.status  │
                         └──────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
           status == "menu"               status != "menu"
           (Ir a B3)                       (Ir a B4)
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ B3. Mostrar menú inline                                                   │
│     menu_engine.send_menu_message(chat_id, bot, menu_id)                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                              [FIN DEL HILO]
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ B4. Responder con texto                                                   │
│     telegram_client.send_message(chat_id, reply)                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                              [FIN DEL HILO]
```

---

## Puntos de Decisión Clave

| Punto | Ubicación | Condición | Acción |
|-------|-----------|-----------|--------|
| 1 | handlers.py:91 | `dispatch.kind` | Dirigir a callback_query, ops, o enterprise |
| 2 | handlers.py:98 | `rate_limiter.is_allowed()` | Bloquear o continuar |
| 3 | handlers.py:114 | `callback_data` existe | Procesar o responder "no reconocida" |
| 4 | callback_router.py:105 | Handler encontrado | Ejecutar o fallback |
| 5 | menu_engine.py:71 | Tipo de callback | show menu, toggle, o navegación |
| 6 | menu_engine.py:181 | edit_message_text | Actualizar o enviar nuevo mensaje |

---

## Componentes Involucrados

```
app/
├── webhook/
│   ├── handlers.py              # Punto de entrada del webhook
│   ├── infrastructure.py        # RequestsTelegramClient
│   └── ports.py                 # Interfaces TelegramClient
│
└── manager_bot/
    ├── menu_service.py           # Factory del MenuEngine
    ├── transport/telegram/
    │   ├── menu_engine.py       # Motor de menús
    │   └── callback_router.py   # Router de callbacks
    ├── menus/
    │   ├── base.py              # MenuDefinition
    │   ├── registry.py          # Registro de menús
    │   ├── navigation.py        # Navegación
    │   └── main_menu.py         # Menú principal
    ├── features/
    │   ├── antispam/__init__.py # Feature antispam
    │   └── ...
    └── config/
        ├── storage.py           # ConfigStorage (memory/postgres/redis)
        └── group_config.py      # GrupoConfig
```

---

## Decisiones de Diseño Importantes

### 1. Registro de Handlers (Tarea 3)
- **Problema**: `register_prefix("antispam")` capturaba TODOS los callbacks
- **Solución**: Usar `register_exact("antispam:show")` para solo mostrar menú
- **Prioridad**: Los handlers de features se registran DESPUÉS de los de navegación

### 2. Callback Query ID (Tarea 1)
- **Problema**: Se usaba `callback_data` como `callback_query_id`
- **Solución**: Extraer `callback_query.id` del raw_update y pasarlo correctamente

### 3. Persistencia (Tarea 5)
- **Default**: InMemoryConfigStorage (se pierde al reiniciar)
- **Configurable**: PostgreSQL o Redis vía variables de entorno

### 4. Rate Limiting
- **Propósito**: Prevenir abuso de callbacks
- **Configurable**: RATE_LIMIT_CALLS, RATE_LIMIT_WINDOW

---

## Logging y Debugging

| Nivel | Ubicación | Información |
|-------|-----------|-------------|
| INFO | handlers.py:122 | Callback procesado |
| INFO | menu_engine.py:73 | handle_menu_show llamado |
| INFO | callback_router.py:102 | Callback recibido |
| DEBUG | menu_engine.py:157 | show_menu_by_callback |
| WARNING | callback_router.py:138 | No handler encontrado |
| ERROR | menu_engine.py:181 | Error editando mensaje |

---

## Casos de Prueba

### Caso 1: Mostrar menú
```
Usuario → Botón "🚫 Antispam" → "antispam:show"
→ handle_menu_show → show_menu_by_callback → edit_message_text
→ Usuario ve el menú de antispam
```

### Caso 2: Toggle configuración
```
Usuario → Botón "Activar Antispam" → "antispam:toggle:on"
→ AntispamFeature.handle_toggle → Actualizar config → answer("Antispam activado")
→ Usuario ve toast "Antispam activado"
```

### Caso 3: Rate limited
```
Usuario → Muchos clicks rápidos
→ rate_limiter.is_allowed() = False
→ answer_callback_query("Demasiadas solicitudes")
→ Usuario ve alert de rate limit
```

---

*Documento generado: 2026-03-13*
*Análisis del flujo de ejecución del menú inline*
