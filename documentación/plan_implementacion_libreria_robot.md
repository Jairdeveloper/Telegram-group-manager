# Plan de Implementación: Librería robot-ptb-compat

## 1. Resumen del Proyecto

**Objetivo:** Crear una librería de compatibilidad que permita integrar los módulos existentes de la app con el runtime de python-telegram-bot (PTB), manteniendo la arquitectura actual mientras se beneficia del ecosistema PTB.

**Nombre:** `robot-ptb-compat`

---

## 2. Análisis del Ciclo de Ejecución PTB

```
REQUEST (HTTP Webhook/Polling)
    │
    ▼
telegram.request (httpx)
    │
    ▼
telegram.helpers (effective_message_type, escape_markdown)
    │
    ▼
telegram.constants (BOT_API_VERSION, FloodLimit, MessageLimit)
    │
    ▼
telegram._version / telegram._utils (__version__: "22.6.0")
    │
    ▼
telegram (Core: Update, Message, Bot, User, Chat)
    │
    ▼
telegram.ext._utils (asyncio, logging, webhookhandler)
    │
    ▼
telegram.ext (Application, Handlers, Filters)
    │
    ▼
USER CALLBACK FUNCTION
```

---

## 3. Estructura de la Librería

```
robot_ptb_compat/
├── __init__.py                    # Exports principales
├── version.py                     # Version info
│
├── bridge/                        # PUENTE PTB ↔ APP
│   ├── __init__.py
│   ├── update_bridge.py           # Update PTB → Formato interno
│   ├── message_bridge.py          # Message PTB → Formato interno
│   ├── user_bridge.py             # User PTB → Formato interno
│   ├── chat_bridge.py             # Chat PTB → Formato interno
│   ├── callback_bridge.py         # CallbackQuery PTB → Formato interno
│   └── context_bridge.py          # CallbackContext → Contexto app
│
├── compat/                        # COMPATIBILIDAD DIRECTA
│   ├── __init__.py
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── base_adapter.py        # BaseHandler adapter
│   │   ├── command_adapter.py      # CommandHandler → app commands
│   │   ├── message_adapter.py     # MessageHandler → app chat
│   │   ├── callback_adapter.py    # CallbackQueryHandler → app callbacks
│   │   ├── inline_adapter.py      # InlineQueryHandler
│   │   └── filters_adapter.py     # PTB Filters → app filters
│   └── application_bridge.py      # Application PTB → App
│
├── constants/                     # CONSTANTES COMPATIBLES
│   ├── __init__.py
│   ├── ptb_limits.py              # Re-export límites PTB
│   ├── app_limits.py              # Límites propios app
│   └── version_info.py            # Version info
│
├── errors/                        # ERRORES COMPATIBLES
│   ├── __init__.py
│   ├── telegram_errors.py         # Re-export de errores PTB
│   └── app_errors.py              # Errores específicos app
│
├── helpers/                       # HELPERS COMPATIBLES
│   ├── __init__.py
│   ├── ptb_helpers.py            # Re-export helpers PTB
│   └── app_helpers.py            # Helpers propios
│
├── runtime/                       # RUNTIME DE EJECUCIÓN
│   ├── __init__.py
│   ├── application_builder.py     # Builder compatible PTB
│   ├── webhook_runner.py          # Runner para webhooks
│   ├── polling_runner.py          # Runner para polling
│   └── runtime_config.py          # Configuración runtime
│
├── transport/                     # CAPA DE TRANSPORTE
│   ├── __init__.py
│   ├── telegram_client.py        # Wrapper PTB Bot
│   ├── webhook_handler.py        # Handler de webhook
│   └── request_adapter.py        # Adapter para requests
│
└── utils/                         # UTILIDADES
    ├── __init__.py
    ├── logging.py                # Configuración de logs
    ├── async_utils.py            # Utilidades async
    └── serialization.py          # Serialización de updates
```

---

## 4. Fases de Implementación

### Fase 1: Fundamentos (Semana 1)

| # | Tarea | Archivo | Descripción |
|---|-------|---------|-------------|
| 1.1 | Crear estructura | - | Crear directorio `robot_ptb_compat/` |
| 1.2 | Implementar constants | `constants/ptb_limits.py` | Re-export de límites PTB (FloodLimit, MessageLimit, etc.) |
| 1.3 | Implementar errors | `errors/telegram_errors.py` | Re-export de errores PTB |
| 1.4 | Implementar helpers | `helpers/ptb_helpers.py` | Re-export de helpers PTB |
| 1.5 | Implementar version | `version.py` | Version info de la librería |

### Fase 2: Bridges (Semana 2)

| # | Tarea | Archivo | Descripción |
|---|-------|---------|-------------|
| 2.1 | Update Bridge | `bridge/update_bridge.py` | Convierte Update PTB → dict interno |
| 2.2 | Message Bridge | `bridge/message_bridge.py` | Convierte Message PTB → dict interno |
| 2.3 | User Bridge | `bridge/user_bridge.py` | Convierte User PTB → dict interno |
| 2.4 | Chat Bridge | `bridge/chat_bridge.py` | Convierte Chat PTB → dict interno |
| 2.5 | Callback Bridge | `bridge/callback_bridge.py` | Convierte CallbackQuery → dict interno |
| 2.6 | Context Bridge | `bridge/context_bridge.py` | Convierte CallbackContext → contexto app |

### Fase 3: Handlers Adapters (Semana 3)

| # | Tarea | Archivo | Descripción |
|---|-------|---------|-------------|
| 3.1 | Base Adapter | `compat/handlers/base_adapter.py` | Clase base para adapters |
| 3.2 | Command Adapter | `compat/handlers/command_adapter.py` | CommandHandler → app commands |
| 3.3 | Message Adapter | `compat/handlers/message_adapter.py` | MessageHandler → app chat |
| 3.4 | Callback Adapter | `compat/handlers/callback_adapter.py` | CallbackQueryHandler → app callbacks |
| 3.5 | Filters Adapter | `compat/handlers/filters_adapter.py` | PTB Filters → app filters |
| 3.6 | Application Bridge | `compat/application_bridge.py` | Application PTB → App |

### Fase 4: Runtime (Semana 4)

| # | Tarea | Archivo | Descripción |
|---|-------|---------|-------------|
| 4.1 | Application Builder | `runtime/application_builder.py` | Builder compatible PTB |
| 4.2 | Webhook Runner | `runtime/webhook_runner.py` | Runner para webhooks |
| 4.3 | Polling Runner | `runtime/polling_runner.py` | Runner para polling |
| 4.4 | Telegram Client | `transport/telegram_client.py` | Wrapper PTB Bot |
| 4.5 | Integración | - | Integrar con `app.manager_bot` |

### Fase 5: Testing y Documentación (Semana 5)

| # | Tarea | Descripción |
|---|-------|-------------|
| 5.1 | Tests unitarios | Tests para cada módulo |
| 5.2 | Tests integración | Tests de integración con PTB |
| 5.3 | Documentación | Documentación de API |
| 5.4 | Ejemplos | Ejemplos de uso |

---

## 5. Mapeo de Módulos App → PTB

| Módulo App | Correspondencia PTB | Archivo Compat |
|------------|---------------------|----------------|
| `app.webhook` | `telegram.ext._updater` | `transport/webhook_handler` |
| `app.telegram` | `telegram.Bot` | `transport/telegram_client` |
| `app.ops` | `telegram.ext.CommandHandler` | `compat/handlers/command_adapter` |
| `app.manager_bot` | Handlers | `compat/application_bridge` |
| `app.auth` | Middleware | `runtime/middleware` |
| `app.guardrails` | `telegram.ext.filters` | `compat/handlers/filters_adapter` |
| `app.policies` | Custom filters | `compat/handlers/policy_adapter` |

---

## 6. Interfaces Clave

### bridge/update_bridge.py

```python
class UpdateBridge:
    @staticmethod
    def to_internal(update: "telegram.Update") -> dict: ...
    @staticmethod
    def from_internal(data: dict) -> "telegram.Update": ...
```

### compat/handlers/command_adapter.py

```python
class CommandAdapter:
    async def handle(self, update: "telegram.Update", context) -> Any: ...
```

### runtime/application_builder.py

```python
class CompatApplicationBuilder:
    def token(self, token: str) -> "CompatApplicationBuilder": ...
    def manager_bot(self, mb: "ManagerBot") -> "CompatApplicationBuilder": ...
    def build(self) -> "telegram.ext.Application": ...
```

---

## 7. Uso Esperado

```python
from robot_ptb_compat import CompatApplicationBuilder
from app.manager_bot import ManagerBot

manager_bot = ManagerBot()

app = (
    CompatApplicationBuilder(token=os.getenv("TELEGRAM_BOT_TOKEN"))
    .manager_bot(manager_bot)
    .build()
)

app.run_webhook(
    listen="0.0.0.0",
    port=8080,
    url_path="webhook",
    webhook_url=os.getenv("WEBHOOK_URL"),
)
```

---

## 8. Dependencias

```
python-telegram-bot>=22.0
fastapi
pydantic
pydantic-settings
httpx
```

---

## 9. Criterios de Éxito

- [ ] La librería re-exporta correctamente las constantes de PTB
- [ ] Los bridges convierten correctamente entre formatos PTB y app
- [ ] Los handlers adapters delegan correctamente a la lógica de la app
- [ ] El Application Builder crea una Application PTB funcional
- [ ] La integración con ManagerBot funciona correctamente
- [ ] Los tests unitarios cubren al menos el 80% del código
- [ ] Los tests de integración verifican el flujo completo
