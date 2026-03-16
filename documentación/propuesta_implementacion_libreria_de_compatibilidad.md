# Propuesta: Librería de Compatibilidad PTB


### Flujo de Ejecución
```
1. REQUEST (HTTP Webhook/Polling)
2. HELPERS (telegram.helpers)
3. CONSTANTS (telegram.constants)
4. VERSION (telegram._version)
5. PTB CORE (telegram)
6. UTILS (telegram._utils)
7. EXT/APPLICATION (telegram.ext)
8. USER CALLBACK FUNCTION
```
---
## Propuesta de Arquitectura
### Objetivo
Crear `robot-ptb-compat` para:
1. Compatibilidad directa con PTB
2. Wrapper de abstracción
3. Bridge PTB ↔ App
### Estructura Propuesta



---
Plan de Implementación: robot-ptb-compat
1. Análisis del Ciclo de Ejecución PTB
REQUEST (HTTP Webhook/Polling)
    │
    ▼
telegram.request (httpx) ──────────────┐
    │                                  │
    ▼                                  │
telegram.helpers ◄──────────────────────┘
    │ (effective_message_type, escape_markdown, mention_html)
    ▼
telegram.constants
    │ (BOT_API_VERSION: "9.3", FloodLimit, MessageLimit)
    ▼
telegram._version / telegram._utils
    │ (__version__: "22.6.0")
    ▼
telegram (Core: Update, Message, Bot, User, Chat)
    │ Parsing y validación
    ▼
telegram.ext._utils (asyncio, logging, webhookhandler)
    │
    ▼
telegram.ext (Application, Handlers, Filters)
    │ (CommandHandler, MessageHandler, CallbackQueryHandler)
    ▼
USER CALLBACK FUNCTION
---
2. Estructura de la Librería
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
│   │   (TelegramError, BadRequest, NetworkError, etc.)
│   └── app_errors.py              # Errores específicos app
│
├── helpers/                       # HELPERS COMPATIBLES
│   ├── __init__.py
│   ├── ptb_helpers.py            # Re-export helpers PTB
│   │   (escape_markdown, mention_html, etc.)
│   └── app_helpers.py            # Helpers propios
│
├── runtime/                       # RUNTIME DE EJECUCIÓN
│   ├── __init__.py
│   ├── application_builder.py     # Builder compatible PTB
│   ├── webhook_runner.py         # Runner para webhooks
│   ├── polling_runner.py         # Runner para polling
│   └── runtime_config.py         # Configuración runtime
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
---
### 3. Fases de Implementación
#### Fase 1: Fundamentos (Semana 1)
- [ ] Crear estructura de directorios
- [ ] Implementar `constants/ptb_limits.py` - re-export de constantes PTB
- [ ] Implementar `errors/telegram_errors.py` - re-export de errores
- [ ] Implementar `helpers/ptb_helpers.py` - re-export de helpers
- [ ] Implementar `version.py` - version info
#### Fase 2: Bridges (Semana 2)
- [ ] Implementar `bridge/update_bridge.py`
- [ ] Implementar `bridge/message_bridge.py`
- [ ] Implementar `bridge/user_bridge.py`
- [ ] Implementar `bridge/chat_bridge.py`
- [ ] Implementar `bridge/callback_bridge.py`
- [ ] Implementar `bridge/context_bridge.py`
#### Fase 3: Handlers Adapters (Semana 3)
- [ ] Implementar `compat/handlers/base_adapter.py`
- [ ] Implementar `compat/handlers/command_adapter.py`
- [ ] Implementar `compat/handlers/message_adapter.py`
- [ ] Implementar `compat/handlers/callback_adapter.py`
- [ ] Implementar `compat/handlers/filters_adapter.py`
- [ ] Implementar `compat/application_bridge.py`
#### Fase 4: Runtime (Semana 4)
- [ ] Implementar `runtime/application_builder.py`
- [ ] Implementar `runtime/webhook_runner.py`
- [ ] Implementar `runtime/polling_runner.py`
- [ ] Implementar `transport/telegram_client.py`
- [ ] Integrar con `app.manager_bot`
#### Fase 5: Testing y Documentación (Semana 5)
- [ ] Tests unitarios para cada módulo
- [ ] Tests de integración con PTB
- [ ] Documentación de API
- [ ] Ejemplos de uso
---
4. Mapeo de Módulos App → PTB
Módulo App
app.webhook
app.telegram
app.ops
app.manager_bot
app.auth
app.guardrails
app.policies
---
5. Interfaces Clave
# bridge/update_bridge.py
class UpdateBridge:
    @staticmethod
    def to_internal(update: "telegram.Update") -> dict: ...
    @staticmethod
    def from_internal(data: dict) -> "telegram.Update": ...
# compat/handlers/command_adapter.py  
class CommandAdapter:
    async def handle(self, update: "telegram.Update", context) -> Any: ...
# runtime/application_builder.py
class CompatApplicationBuilder:
    def token(self, token: str) -> "CompatApplicationBuilder": ...
    def manager_bot(self, mb: "ManagerBot") -> "CompatApplicationBuilder": ...
    def build(self) -> "telegram.ext.Application": ...
---
6. Uso Esperado
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
---
## Mapeo de Módulos
| Módulo App | Correspondencia PTB |
|------------|---------------------|
| app.webhook | telegram.ext._updater |
| app.telegram | telegram.Bot |
| app.ops | telegram.ext.CommandHandler |
| app.manager_bot | Handlers adaptados |
| app.auth | Middleware PTB |
| app.guardrails | telegram.ext.filters |
| app.policies | Custom filters/middleware |
ENDFILE


## Mapeo

| App | PTB |
|-----|-----|
| app.webhook | telegram.ext._updater |
| app.telegram | telegram.Bot |
| app.ops | telegram.ext.CommandHandler |
| app.manager_bot | Handlers adaptados |
| app.auth | Middleware PTB |
| app.guardrails | telegram.ext.filters |
