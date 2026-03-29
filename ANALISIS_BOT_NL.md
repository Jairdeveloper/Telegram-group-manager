# Análisis: Bot no entiende lenguaje natural

**Fecha:** 2026-03-27

---

## Problema

El usuario escribe instrucciones en lenguaje natural al bot, pero el bot responde de forma aleatoria o no ejecuta las acciones esperadas.

---

## Flujo de datos actual

### 1. Recepción del mensaje

```
Usuario envía mensaje → Telegram Webhook → process_update_impl()
```

### 2. Clasificación del mensaje (router.py)

El `TelegramRouter.route_update()` clasifica el mensaje:

```
├── Si empieza con "/" y está en OPS_COMMANDS → "ops_command"
├── Si empieza con "/" y es enterprise_command → "enterprise_command"  
├── Si empieza con "/" pero no se reconoce → "unsupported"
└── Si NO empieza con "/" → "chat_message"  ← AQUÍ ESTÁ EL PROBLEMA
```

**Ubicación:** `app/manager_bot/_transport/telegram/router.py:163-170`

```python
return RouterDispatchResult(
    kind="chat_message",  # <- Todo mensaje sin "/" va aquí
    update_id=update_id,
    chat_id=chat_id,
    user_id=sender_id,
    text=text,
    raw_update=update,
)
```

### 3. Procesamiento del mensaje

En `handlers.py:504`:

```python
else:
    result = handle_chat_message_fn(chat_id, text)  # <- NO usa ActionParser
    reply = result.get("response", "(no response)")
```

**El flujo va a `handle_chat_message` que:**
- Usa el `agent` genérico del chat_service
- NO usa el ActionParser
- NO usa el ActionExecutor
- NO ejecuta acciones estructuradas

---

## Arquitectura actual (parcial)

```
┌─────────────────────────────────────────────────────────┐
│              Mensaje del usuario                         │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│            TelegramRouter.route_update()                 │
│  Clasifica: ops_command / enterprise_command /          │
│  chat_message / unsupported                              │
└─────────────────────┬───────────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
        ▼                           ▼
   "ops_command"             "chat_message"
   (comandos /)              (texto libre)
        │                           │
        ▼                           ▼
handle_ops_command()      handle_chat_message()  ← PROBLEMA
        │                           │
        ▼                           ▼
   Responder               ChatService Agent
                           (NO ActionParser)
```

---

## Por qué el bot no entiende NL

### Causa raíz

**El sistema tiene el ActionParser implementado pero NO está conectado al flujo principal.**

| Componente | Estado | Conectado al flujo principal |
|------------|--------|------------------------------|
| ActionParser | ✅ Implementado | ❌ NO |
| ActionExecutor | ✅ Implementado | ❌ NO |
| ActionRegistry | ✅ Implementado | ❌ NO |
| SlotResolver | ✅ Implementado | ❌ NO |
| ConversationState | ✅ Implementado | ❌ NO |

### El flujo actual vs flujo esperado

**Actual:**
```
Mensaje NL → router → "chat_message" → handle_chat_message() → ChatService Agent → Respuesta aleatoria
```

**Esperado:**
```
Mensaje NL → router → "chat_message" → ActionParser → SlotResolver → ActionExecutor → Acción ejecutada
```

---

## Factor del modelo de lenguaje

### Configuración actual (factory.py)

```python
llm_provider: "ollama"          # Por defecto
llm_model: "llama3"              # Por defecto
ollama_base_url: "http://localhost:11434"
action_parser_llm_enabled: False  # ← LLM DESHABILITADO
```

### Posibles problemas

1. **Ollama no está corriendo**: El servicio local no está disponible
2. **Modelo no descargado**: `llama3` no está instalado en Ollama
3. **ActionParser con LLM deshabilitado**: Solo usa rule-based (menos preciso)

### Verificar Ollama

```bash
# Ver si Ollama está corriendo
curl http://localhost:11434/api/tags

# Ver modelos disponibles
ollama list
```

---

## Solución propuesta

### Opción 1: Conectar ActionParser al flujo (recomendado)

Modificar `handlers.py` para que los mensajes `chat_message` pasen por ActionParser:

```python
# En handlers.py, después de verificar estados de conversación
else:
    # NUEVO: Intentar ActionParser primero
    parser = ActionParser(llm_enabled=False)  # rule-based
    parse_result = parser.parse(text)
    
    if parse_result.action_id and parse_result.confidence >= 0.5:
        # Ejecutar acción
        executor = ActionExecutor(get_default_registry())
        result = await executor.execute(
            parse_result.action_id,
            context,
            parse_result.payload
        )
        reply = result.message
    else:
        # Fallback: ChatService normal
        result = handle_chat_message_fn(chat_id, text)
        reply = result.get("response", "(no response)")
```

### Opción 2: Habilitar LLM en ActionParser

En `app/config/settings.py` o variable de entorno:

```bash
ACTION_PARSER_LLM_ENABLED=true
LLM_PROVIDER=openai  # o ollama
LLM_MODEL=gpt-4o-mini  # o llama3
```

### Opción 3: Crear nuevo dispatch kind

Agregar `"agent_task"` como tipo de dispatch para mensajes que deben ir al agente.

---

## Resumen de problemas

| # | Problema | Impacto | Prioridad |
|---|----------|---------|-----------|
| 1 | ActionParser no está conectado | Bot no ejecuta acciones | ALTA |
| 2 | Flujo va a ChatService genérico | Respuestas aleatorias | ALTA |
| 3 | LLM puede no estar configurado | Fallback rule-based limitado | MEDIA |
| 4 | action_parser_llm_enabled=False | Menos precisión | MEDIA |

---

## Próximos pasos recomendados

1. **Conectar ActionParser al flujo de chat_message** en `handlers.py`
2. **Verificar que Ollama esté corriendo** y el modelo disponible
3. **Habilitar LLM** si se desea mejor precisión en parsing
4. **Agregar más acciones** al ActionRegistry para funcionalidades del grupo
5. **Probar** con frases como "Activa bienvenida", "Pon antiflood", etc.
