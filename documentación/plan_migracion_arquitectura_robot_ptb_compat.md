# Plan de Migración de Arquitectura: robot-ptb-compat

## 1. Estado Actual de la Aplicación

### 1.1 Estructura Actual

```
app/
├── webhook/                    # Webhook entrypoint (FastAPI)
│   ├── entrypoint.py          # app.webhook.entrypoint:app
│   ├── infrastructure.py       # TelegramClient (requests)
│   ├── handlers.py            # Handlers de webhook
│   ├── bootstrap.py            # Runtime builder
│   └── ports.py                # Interfaces
│
├── telegram/                   # Módulo de Telegram
│   ├── dispatcher.py           # Dispatcher de updates
│   ├── services.py            # Servicios
│   └── models.py              # Modelos
│
├── telegram_ops/               # Bot OPS (polling - DEPRECATED)
│   └── entrypoint.py
│
├── manager_bot/               # Gestor de módulos
│   ├── core.py                # ManagerBot
│   ├── registry.py            # Registro de módulos
│   └── application/           # Módulos
│       ├── ops/
│       ├── enterprise/
│       └── agent/
│
├── ops/                       # Servicios OPS
│   ├── services.py
│   ├── events.py
│   └── checks.py
│
├── enterprise/                # Handlers Enterprise
│   └── handlers.py
│
├── tools/                     # Herramientas
│   ├── router.py
│   ├── registry.py
│   └── builtins.py
│
├── policies/                  # Políticas
├── guardrails/                # Filtros de contenido
├── planner/                   # Planificador
├── auth/                      # Autenticación
├── billing/                   # Facturación
├── audit/                     # Auditoría
└── monitoring/                # Monitoreo
```

### 1.2 Puntos de Integración con Telegram

| Módulo | Tecnología | Estado |
|--------|-----------|--------|
| `app.webhook` | FastAPI + requests | **ACTIVO** |
| `app.telegram_ops` | PTB polling | DEPRECATED |
| `app.telegram` | requests | Legacy |

### 1.3 Problemas Identificados

1. **Cliente Telegram manual**: Usa `requests` en lugar de PTB
2. **Sin integración PTB**: No usa el runtime de PTB
3. **Código duplicado**: Lógica similar en webhook y telegram_ops
4. **Acoplamiento fuerte**: TelegramClient mezclado con lógica de negocio

---

## 2. Arquitectura Objetivo con robot-ptb-compat

### 2.1 Estructura Propuesta

```
app/
├── webhook/                    # Webhook entrypoint (PTB)
│   ├── entrypoint.py          # Integración con robot-ptb-compat
│   ├── handlers.py            # Handlers adaptados
│   └── ...
│
├── telegram/                   # Módulo Telegram (refactorizado)
│   ├── client.py              # Wrapper usando TelegramClient
│   └── services.py
│
├── compat/                     # NUEVO: Capa de compatibilidad
│   ├── handlers/             # Handlers PTB adaptados
│   └── middleware/            # Middleware de integración
│
├── manager_bot/               # Gestor de módulos
│   ├── core.py
│   ├── registry.py
│   └── application/
│       ├── ops/
│       ├── enterprise/
│       └── agent/
│
├── ops/                       # Servicios OPS
├── enterprise/                # Handlers Enterprise
├── tools/                     # Herramientas
├── policies/                  # Políticas
├── guardrails/                # Filtros de contenido
├── planner/                   # Planificador
├── auth/                      # Autenticación
├── billing/                   # Facturación
├── audit/                     # Auditoría
└── monitoring/                # Monitoreo
```

### 2.2 Flujo de Migración

```
ACTUAL                          FUTURO
────────                        ──────
FastAPI + requests        →    FastAPI + robot-ptb-compat
                                │
                                ├── CompatApplicationBuilder
                                ├── TelegramClient (PTB)
                                └── Handlers adaptados
```

---

## 3. Plan de Migración (Fases)

### Fase 1: Integración Básica (Semana 1)

| # | Tarea | Descripción |
|---|-------|-------------|
| 1.1 | Agregar dependencia | Añadir `robot-ptb-compat` a requirements.txt |
| 1.2 | Crear cliente compat | Reemplazar `RequestsTelegramClient` por `TelegramClient` de robot-ptb-compat |
| 1.3 | Test de smoke | Verificar que el cliente funciona |

**Cambios esperados:**

```python
# ANTES (app/webhook/infrastructure.py)
from app.webhook.infrastructure import RequestsTelegramClient

client = RequestsTelegramClient(bot_token=token)

# DESPUÉS
from robot_ptb_compat.transport import TelegramClient

client = TelegramClient(token=token)
```

### Fase 2: Adaptadores de Handlers (Semana 2)

| # | Tarea | Descripción |
|---|-------|-------------|
| 2.1 | Crear handlers compat | Crear `app/compat/handlers/` |
| 2.2 | Migrar handlers webhook | Adaptar handlers existentes |
| 2.3 | Test de handlers | Verificar funcionamiento |

**Cambios esperados:**

```python
# ANTES (app/webhook/handlers.py)
async def handle_update(update: dict):
    # lógica

# DESPUÉS
from robot_ptb_compat.compat.handlers import CommandAdapter, MessageAdapter

async def handle_command(update, context):
    # lógica con robot-ptb-compat
```

### Fase 3: Runtime PTB (Semana 3)

| # | Tarea | Descripción |
|---|-------|-------------|
| 3.1 | Integrar Application Builder | Usar `CompatApplicationBuilder` |
| 3.2 | Configurar webhook runner | Integrar `WebhookRunner` |
| 3.3 | Test E2E | Verificar flujo completo |

**Cambios esperados:**

```python
# ANTES (app/webhook/bootstrap.py)
def build_webhook_runtime(...):
    # configuración manual

# DESPUÉS
from robot_ptb_compat.runtime import CompatApplicationBuilder

app = (
    CompatApplicationBuilder(token=os.getenv("TELEGRAM_BOT_TOKEN"))
    .build()
)
```

### Fase 4: Limpieza (Semana 4)

| # | Tarea | Descripción |
|---|-------|-------------|
| 4.1 | Eliminar código legacy | Quitar `RequestsTelegramClient` |
| 4.2 | Actualizar imports | Migrar a robot-ptb-compat |
| 4.3 | Documentar cambios | Actualizar RUNBOOKs |

---

## 4. Detalle de Cambios por Módulo

### 4.1 app/webhook/infrastructure.py

| Antes | Después |
|-------|---------|
| `RequestsTelegramClient` | `TelegramClient` de robot-ptb-compat |
| `RequestsChatApiClient` | Sin cambios (lógica de negocio) |
| `RedisDedupStore` | Sin cambios |

### 4.2 app/webhook/entrypoint.py

| Antes | Después |
|-------|---------|
| FastAPI directo | FastAPI + PTB Application |
| `handle_webhook_impl` | `WebhookRunner` |
| `process_update_impl` | Handlers adaptados |

### 4.3 app/manager_bot/core.py

| Antes | Después |
|-------|---------|
| FastAPI mount | Integración via `ApplicationBridge` |
| Registro manual | Registro via handlers compat |

### 4.4 app/telegram/ (DEPRECATED)

| Antes | Después |
|-------|---------|
| Módulo completo | Eliminar (funcionalidad migrada) |

---

## 5. Código de Ejemplo: Después de Migración

```python
# app/webhook/entrypoint.py (versión migrada)
from robot_ptb_compat.runtime import CompatApplicationBuilder
from robot_ptb_compat.transport import TelegramClient
from robot_ptb_compat.compat.handlers import CommandAdapter, MessageAdapter
from robot_ptb_compat.bridge import UpdateBridge

# Configuración
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Crear aplicación con robot-ptb-compat
app = (
    CompatApplicationBuilder(token=TELEGRAM_TOKEN)
    .add_handler(CommandAdapter(
        commands=["start", "help"],
        callback=handle_command
    ))
    .add_handler(MessageAdapter(
        callback=handle_message,
        filters=FiltersAdapter.text()
    ))
    .build()
)

# Usar TelegramClient directamente
async def send_message(chat_id: int, text: str):
    client = TelegramClient(token=TELEGRAM_TOKEN)
    await client.send_message(chat_id=chat_id, text=text)
```

---

## 6. Riesgos y Mitigaciones

| Riesgo | Impacto | Mitigación |
|--------|---------|------------|
| Breaking changes en PTB | Alto | Usar fallbacks de robot-ptb-compat |
| Tests fallando | Medio | Actualizar tests en paralelo |
| downtime | Alto | Migración gradual (blue-green) |

---

## 7. Criterios de Éxito

- [ ] Cliente Telegram funciona con robot-ptb-compat
- [ ] Handlers migrados funcionan correctamente
- [ ] Runtime usa CompatApplicationBuilder
- [ ] Código legacy eliminado
- [ ] Tests pasan sin errores
- [ ] Documentación actualizada
