# Guía de Debug con VS Code

## Flujo de Ejecución

```
1. entrypoint.py:main()           → Inicia uvicorn server
2. entrypoint.py:webhook()        → Receives POST from Telegram
3. handlers.py:handle_webhook_impl() → Valida token, deduplicación
4. handlers.py:process_update_impl() → Clasifica y procesa update
5. dispatcher.py:dispatch_telegram_update() → Clasifica tipo de mensaje
6. services.py:handle_ops_command() o handle_chat_message() → Procesa comando
```

---

## Puntos de Interrupción Estratégicos

### 1. Inicio de la App
| Archivo | Línea | Función | Propósito |
|---------|-------|---------|-----------|
| `app/webhook/entrypoint.py` | 149 | `uvicorn.run()` | Punto de entrada del servidor |
| `app/webhook/entrypoint.py` | 72 | `mount_manager_bot()` | Mount ManagerBot routes |
| `app/webhook/entrypoint.py` | 80 | `dedup_update()` | Verifica si update es nuevo |

### 2. Recepción de Webhook
| Archivo | Línea | Función | Propósito |
|---------|-------|---------|-----------|
| `app/webhook/entrypoint.py` | 108-121 | `webhook()` | Endpoint `/webhook/{token}` - **INICIO AQUÍ** |
| `app/webhook/handlers.py` | 252-356 | `handle_webhook_impl()` | Valida token, extrae update |
| `app/webhook/handlers.py` | 280 | `request.json()` | Extrae JSON del request |
| `app/webhook/handlers.py` | 293 | `dedup_update(update_id)` | Deduplicación - evita procesar duplicados |

### 3. Clasificación del Update
| Archivo | Línea | Función | Propósito |
|---------|-------|---------|-----------|
| `app/webhook/handlers.py` | 34-106 | `process_update_impl()` | **PUNTO CLAVE** - Procesa el update |
| `app/webhook/handlers.py` | 51 | `dispatch_telegram_update()` | Clasifica el tipo de mensaje |
| `app/telegram/dispatcher.py` | 34 | `dispatch_telegram_update()` | **AQUÍ SE CLASIFICA** - callback, chat, ops, enterprise |

### 4. Procesamiento de Comandos OPS
| Archivo | Línea | Función | Propósito |
|---------|-------|---------|-----------|
| `app/ops/services.py` | 242 | `handle_ops_command()` | **AQUÍ SE PROCESAN COMANDOS OPS** |
| `app/ops/services.py` | 260 | `check_permissions()` | Verifica permisos |
| `app/ops/services.py` | 280 | `execute_command()` | Ejecuta el comando |

### 5. Procesamiento de Comandos Enterprise
| Archivo | Línea | Función | Propósito |
|---------|-------|---------|-----------|
| `app/webhook/handlers.py` | 148-186 | `handle_enterprise_command()` | Comandos enterprise |
| `app/enterprise/__init__.py` | - | `handle_enterprise_command()` | Procesa comandos de empresa |

### 6. Mensajes de Chat (No comandos)
| Archivo | Línea | Función | Propósito |
|---------|-------|---------|-----------|
| `app/webhook/handlers.py` | 206 | `handle_chat_message()` | **AQUÍ SE PROCESAN MENSAJES DE CHAT** |
| `chat_service/agent.py` | - | `process_message()` | Chat con IA |

### 7. Callback Queries (Botones inline)
| Archivo | Línea | Función | Propósito |
|---------|-------|---------|-----------|
| `app/webhook/handlers.py` | 91-128 | `callback_query` handling | Procesa clicks en botones |
| `app/manager_bot/menu_service.py` | - | `handle_callback_query_raw()` | Maneja callbacks del menú |

### 8. Envío de Respuesta
| Archivo | Línea | Función | Propósito |
|---------|-------|---------|-----------|
| `app/webhook/handlers.py` | 228-246 | `telegram_client.send_message()` | **ENVÍA RESPUESTA A TELEGRAM** |

---

## Configuración de launch.json

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Robot Webhook",
            "type": "debugpy",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "app.webhook.entrypoint:app",
                "--host", "0.0.0.0",
                "--port", "8000",
                "--reload"
            ],
            "env": {
                "PYTHONPATH": "${workspaceFolder}",
                "BOT_TOKEN": "${env:BOT_TOKEN}",
                "WEBHOOK_TOKEN": "${env:WEBHOOK_TOKEN}",
                "CHATBOT_API_URL": "${env:CHATBOT_API_URL}",
                "DATABASE_URL": "${env:DATABASE_URL}"
            },
            "console": "integratedTerminal",
            "justMyCode": true
        },
        {
            "name": "Python: Current File",
            "type": "debugpy",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal"
        }
    ]
}
```

---

## Variables de Entorno Requeridas

确保 tener estas variables en tu `.env` o configuradas en VS Code:

```
BOT_TOKEN=tu_bot_token
WEBHOOK_TOKEN=tu_webhook_token
CHATBOT_API_URL=http://localhost:8000/api/v1
DATABASE_URL=sqlite:///robot.db
PORT=8000
HOST=0.0.0.0
```

---

## Flujo Recomendado para Debug

1. **Inicia el debugger** en `app/webhook/entrypoint.py:149` (uvicorn.run)
2. **Envía un mensaje** a tu bot de Telegram
3. **El flujo llegará a:**
   - `entrypoint.py:108` → `webhook()`
   - `handlers.py:252` → `handle_webhook_impl()`
   - `handlers.py:34` → `process_update_impl()`
   - `dispatcher.py:34` → `dispatch_telegram_update()` ← **Clasifica el tipo**
4. **Dependiendo del tipo:**
   - `OPS command` → `ops/services.py:242` → `handle_ops_command()`
   - `Enterprise command` → `handlers.py:148`
   - `Chat message` → `handlers.py:206` → `handle_chat_message()`
   - `Callback query` → `handlers.py:91`
5. **Respuesta** → `handlers.py:228` → `telegram_client.send_message()`

---

## Commands OPS Disponibles

En `app/telegram/services.py` → `OPS_COMMANDS`:
- `/start` - Iniciar bot
- `/help` - Ayuda
- `/status` - Estado del sistema
- `/ping` - Verificar conexión
- (otros definidos en el sistema)

---

## Tips de Debug

1. **Watch expressions útiles:**
   - `update` - El mensaje completo de Telegram
   - `dispatch.kind` - Tipo de update (chat_message, ops_command, etc.)
   - `chat_id` - ID del chat
   - `reply` - Texto de respuesta

2. **Condiciones de breakpoint:**
   - Breakpoint en `handlers.py:34` con condición: `update.get("message", {}).get("text", "").startswith("/")`
   - Breakpoint en `handlers.py:228` con condición: `chat_id == TU_CHAT_ID`

3. **Logs relevantes:**
   - Busca en la consola: `webhook.received`, `webhook.process_start`, `telegram.dispatch.*`
