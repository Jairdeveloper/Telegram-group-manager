# Propuesta de Refactorización/Migración - Integración de Nueva Arquitectura

---

**Fecha:** 04/04/2026  
**version:** 1.0  
**referencia:** 
- ANALISIS_IMPORTACIONES.md
- IMPLEMENTACION_MEJORA_ARQUITECTURA_COMPLETADA.md

---

## 1. Estado Actual

### Problema identificado

Los módulos `processors`, `state` y `response` fueron creados pero **no están integrados** en el flujo principal.

| Componente | Estado | Uso actual |
|------------|--------|------------|
| `app.webhook.processors` | ✓ Creado | Solo uso interno en chat_message.py |
| `app.webhook.state` | ✓ Creado | Solo uso interno en chat_message.py |
| `app.webhook.response` | ✓ Creado | Sin uso |
| `handlers.py` | ⏳ Monolítico | ~700 líneas, flujo original |

### Flujo actual vs esperado

```
ACTUAL (Monolítico):                    ESPERADO (Pipeline):
┌─────────────────────┐                ┌─────────────────────┐
│  Telegram Update    │                │  Telegram Update    │
└──────────┬──────────┘                └──────────┬──────────┘
           │                                     │
           ▼                                     ▼
┌─────────────────────┐                ┌─────────────────────┐
│  handlers.py        │                │  ProcessorFactory   │
│  (~700 líneas)     │──────►         │  (delegación)       │
│  Todo junto        │                └──────────┬──────────┘
└─────────────────────┘                           │
                                                  ▼
                                         ┌─────────────────────┐
                                         │  MessageProcessor   │
                                         │  (específico)       │
                                         └──────────┬──────────┘
                                                    │
                                      ┌─────────────┴─────────────┐
                                      ▼                           ▼
                            ┌─────────────────┐          ┌─────────────────┐
                            │ Conversation    │          │ ResponseBuilder │
                            │ StateManager    │          │ TelegramSender  │
                            └─────────────────┘          └─────────────────┘
```

---

## 2. Objetivo de la Migración

Transformar `handlers.py` de ~700 líneas monolíticas a ~50 líneas de orchestration que deleguen a los módulos especializados.

---

## 3. Plan de Migración

### Paso 1: Crear contexto de procesamiento

```python
# En handlers.py, crear función auxiliar para construir contexto
def build_processor_context(
    telegram_client,
    logger,
    handle_chat_message_fn,
    handle_ops_command_fn,
    handle_enterprise_command_fn,
    handle_enterprise_moderation_fn,
    is_admin_fn,
    rate_limit_check,
):
    return {
        "telegram_client": telegram_client,
        "logger": logger,
        "handle_chat_message_fn": handle_chat_message_fn,
        "handle_ops_command_fn": handle_ops_command_fn,
        "handle_enterprise_command_fn": handle_enterprise_command_fn,
        "handle_enterprise_moderation_fn": handle_enterprise_moderation_fn,
        "is_admin_fn": is_admin_fn,
        "rate_limit_check": rate_limit_check,
    }
```

### Paso 2: Refactorizar process_update_impl

**ANTES (actual):**
```python
async def process_update_impl(update, *, telegram_client, logger, ...):
    # ~700 líneas con todo el procesamiento
    if dispatch.kind == "callback_query":
        # manejo inline
    elif dispatch.kind == "chat_message":
        # manejo inline con estados, action parser, NLP, etc.
    elif dispatch.kind == "ops_command":
        # manejo inline
    # ...
```

**DESPUÉS (migrado):**
```python
async def process_update_impl(update, *, telegram_client, logger, ...):
    # Routing (ya existe)
    dispatch = get_dispatch(update)
    
    # Construcción de contexto
    context = build_processor_context(telegram_client, logger, ...)
    
    # Obtener procesador
    processor = ProcessorFactory.get_processor(dispatch.kind, context)
    
    # Procesar
    result = await processor.process(dispatch, context)
    
    # Construir respuesta
    response = ResponseBuilder.build_from_processor_result(result)
    
    # Enviar respuesta
    sender = TelegramResponseSender(telegram_client, logger)
    await sender.send_response(
        chat_id=dispatch.chat_id,
        text=response.text,
        menu_id=response.menu_to_show,
        update_id=dispatch.update_id,
    )
```

### Paso 3: Migrar lógica de respuesta

La lógica actual de respuesta en `handlers.py`:
```python
# Líneas 761-798
logger.info(f"About to send reply: {reply!r}")
if not reply or not reply.strip():
    logger.warning("webhook.empty_reply", extra=log_ctx)
    reply = "(sin respuesta)"
try:
    await telegram_client.send_message(chat_id=chat_id, text=reply)
    # ... event recording
except Exception:
    # ... error handling

if menu_to_show:
    menu_engine = get_menu_engine()
    # ... send menu
```

Se reemplaza por:
```python
sender = TelegramResponseSender(telegram_client, logger)
await sender.send_response(
    chat_id=chat_id,
    text=reply,
    menu_id=menu_to_show,
    update_id=update_id,
    send_message_metric=telegram_send_error_metric,
)
```

---

## 4. Tabla de Tareas de Migración

| # | Tarea | Descripción | Estado |
|---|-------|-------------|--------|
| 1 | Crear `build_processor_context()` | Función helper para construir contexto | ⏳ Pendiente |
| 2 | Importar ProcessorFactory | Agregar imports necesarios | ⏳ Pendiente |
| 3 | Importar ResponseBuilder | Agregar imports necesarios | ⏳ Pendiente |
| 4 | Importar TelegramResponseSender | Agregar imports necesarios | ⏳ Pendiente |
| 5 | Refactorizar rama `callback_query` | Usar CallbackProcessor | ⏳ Pendiente |
| 6 | Refactorizar rama `chat_message` | Usar ChatMessageProcessor | ⏳ Pendiente |
| 7 | Refactorizar rama `ops_command` | Usar OpsCommandProcessor | ⏳ Pendiente |
| 8 | Refactorizar rama `enterprise_command` | Usar EnterpriseCommandProcessor | ⏳ Pendiente |
| 9 | Refactorizar rama `chat_member` | Usar ChatMemberProcessor | ⏳ Pendiente |
| 10 | Migrar lógica de respuesta | Usar TelegramResponseSender | ⏳ Pendiente |
| 11 | Mantener manejo de errores | Preservar try/except global | ⏳ Pendiente |
| 12 | Validar tests existentes | Ejecutar suite de tests | ⏳ Pendiente |

---

## 5. Código Propuesto para Migración

### app/webhook/handlers.py - Versión migrada

```python
"""Webhook domain logic decoupled from infrastructure libraries."""

import inspect
import json
import logging
import time
from typing import Any, Callable, Dict, Optional

from fastapi import HTTPException, Request

from app.telegram.dispatcher import dispatch_telegram_update
from app.telegram.services import extract_chat_payload
from app.ops.events import record_event
from app.manager_bot._menu_service import get_menu_engine

from .ports import ChatApiClient, DedupStore, TaskQueue, TelegramClient
from .processors import ProcessorFactory, ProcessorResult
from .response import ResponseBuilder, TelegramResponseSender


async def _maybe_await(result):
    if inspect.isawaitable(result):
        return await result
    return result


def _get_manager_bot_router():
    from app.manager_bot.core import ManagerBot
    return ManagerBot().get_router()


def build_processor_context(
    telegram_client: TelegramClient,
    logger,
    handle_chat_message_fn,
    handle_ops_command_fn,
    handle_enterprise_command_fn,
    handle_enterprise_moderation_fn,
    is_admin_fn,
    rate_limit_check,
) -> Dict[str, Any]:
    """Build context dict for processors."""
    return {
        "telegram_client": telegram_client,
        "logger": logger,
        "handle_chat_message_fn": handle_chat_message_fn,
        "handle_ops_command_fn": handle_ops_command_fn,
        "handle_enterprise_command_fn": handle_enterprise_command_fn,
        "handle_enterprise_moderation_fn": handle_enterprise_moderation_fn,
        "is_admin_fn": is_admin_fn,
        "rate_limit_check": rate_limit_check,
    }


async def process_update_impl(
    update: Dict[str, Any],
    *,
    telegram_client: TelegramClient,
    logger,
    process_time_metric=None,
    chat_api_error_metric=None,
    telegram_send_error_metric=None,
    handle_chat_message_fn: Callable = None,
    handle_ops_command_fn: Callable = None,
    handle_enterprise_command_fn: Callable = None,
    handle_enterprise_moderation_fn: Callable = None,
    is_admin_fn: Callable[[int], bool] = None,
    rate_limit_check: Callable[[int], Any] = None,
) -> None:
    """Process update using pipeline architecture."""
    from app.ops.services import handle_chat_message
    from app.ops.policies import check_rate_limit, is_admin
    from app.enterprise import handle_enterprise_command, handle_enterprise_moderation
    
    start = time.time()
    
    # Routing
    if update.get("callback_query"):
        dispatch = dispatch_telegram_update(update)
    else:
        router = _get_manager_bot_router()
        dispatch = router.route_update(update).to_legacy_dispatch()
    
    update_id = dispatch.update_id
    chat_id = dispatch.chat_id
    log_ctx = {"update_id": update_id, "chat_id": chat_id}

    if dispatch.kind == "unsupported":
        logger.info("webhook.unsupported_update", extra=log_ctx)
        record_event(
            component="telegram",
            event="telegram.dispatch.unsupported",
            update_id=update_id,
            chat_id=chat_id,
            reason=dispatch.reason,
        )
        return

    record_event(
        component="telegram",
        event=f"telegram.dispatch.{dispatch.kind}",
        update_id=update_id,
        chat_id=chat_id,
    )

    # Build context
    context = build_processor_context(
        telegram_client=telegram_client,
        logger=logger,
        handle_chat_message_fn=handle_chat_message_fn or handle_chat_message,
        handle_ops_command_fn=handle_ops_command_fn or handle_ops_command,
        handle_enterprise_command_fn=handle_enterprise_command_fn or handle_enterprise_command,
        handle_enterprise_moderation_fn=handle_enterprise_moderation_fn or handle_enterprise_moderation,
        is_admin_fn=is_admin_fn or is_admin,
        rate_limit_check=rate_limit_check or check_rate_limit,
    )

    try:
        # Get processor
        processor = ProcessorFactory.get_processor(dispatch.kind, context)
        
        # Process
        result = await processor.process(dispatch, context)
        
        # Build response
        response = ResponseBuilder.build_from_processor_result(result)
        
        # Send response
        sender = TelegramResponseSender(telegram_client, logger)
        await sender.send_response(
            chat_id=chat_id,
            text=response.text,
            menu_id=response.menu_to_show,
            update_id=update_id,
            send_message_metric=telegram_send_error_metric,
        )
        
    except Exception:
        logger.exception("webhook.service_error", extra=log_ctx)
        record_event(
            component="webhook",
            event="webhook.service.error",
            level="ERROR",
            update_id=update_id,
            chat_id=chat_id,
        )
        if chat_api_error_metric is not None:
            chat_api_error_metric.inc()
        
        # Send error response
        sender = TelegramResponseSender(telegram_client, logger)
        await sender.send_reply(chat_id, "(internal error)", update_id)

    if process_time_metric is not None:
        process_time_metric.observe(time.time() - start)


# Mantener handle_webhook_impl sin cambios (lógica de entrada)


async def handle_webhook_impl(
    *,
    token: str,
    request: Request,
    bot_token: Optional[str],
    webhook_token: Optional[str],
    dedup_update: Callable[[int], bool],
    process_async: bool,
    task_queue: Optional[TaskQueue],
    process_update_sync: Callable[[Dict[str, Any]], None],
    requests_metric,
    logger,
    ptb_webhook_handler: Optional[Any] = None,
) -> Dict[str, Any]:
    # ... código existente sin cambios
    pass
```

---

## 6. Consideraciones

### Compatibilidad hacia atrás
- Mantener la firma de `process_update_impl` idéntica
- Los parámetros opcionales usan valores por defecto del módulo original
- El comportamiento externo debe ser idéntico

### Manejo de errores
- Preservar el try/except global alrededor del procesamiento
- Continuar grabando eventos en los mismos puntos
- Mantener métricas existentes

### Testing
- Los tests existentes deben seguir pasando
- Los nuevos módulos ya tienen tests unitarios pendientes
- Considerar tests de integración del pipeline

---

## 7. Beneficios de la Migración

| Métrica | Antes | Después |
|---------|-------|---------|
| Líneas en handlers.py | ~700 | ~100 |
| Acoplamiento | Alto | Bajo |
| Testabilidad | Difícil | Fácil |
| Nuevos tipos de mensaje | Modificar handlers.py | Registrar processor |
| Estados conversacionales | if/elif anidados | Registrar handler |

---

## 8. Riesgos y Mitigación

| Riesgo | Mitigación |
|--------|------------|
| Romper funcionalidad existente | Mantener código original en rama alternativa hasta validar |
| Pérdida de eventos | Verificar que record_event() se llame en los mismos puntos |
| performance regresión | Benchmark antes/después |
| Importación circular | Usar import lazy donde sea necesario |
