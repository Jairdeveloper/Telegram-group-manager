Fecha: 2026-03-27
version: 1.0
referencia: ANALISIS_BOT_NL.md

---

# Plan de Implementación: Sistema ActionParser

---

## Resumen de la implementacion

El sistema de ActionParser está parcialmente implementado pero desconectado del flujo principal. Este plan conecta el ActionParser al flujo de mensajes para que el bot entienda lenguaje natural y ejecute acciones de administración del grupo.

**Estado actual:**
- ActionParser, ActionExecutor, ActionRegistry, SlotResolver: ✅ Implementados
- Integración con flujo principal: ❌ NO conectada

**Objetivo:** Que el usuario pueda escribir "Activa bienvenida" o "Pon antiflood" y el bot ejecute la acción correspondiente.

---

## Arquitectura final

```
┌─────────────────────────────────────────────────────────────┐
│                    MENSAJE DEL USUARIO                       │
│           (texto libre en lenguaje natural)                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              TELEGRAMROUTER.route_update()                   │
├─────────────────────────────────────────────────────────────┤
│  Clasifica: ops_command / enterprise_command /              │
│  chat_message / unsupported                                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    HANDLERS.PROCESS_UPDATE                  │
├─────────────────────────────────────────────────────────────┤
│  1. Verificar estados de conversación (ConversationState)  │
│  2. Verificar Enterprise Moderation                        │
│  3. Si chat_message → ACTIONPARSER ← NUEVO                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      ACTIONPARSER.parse()                   │
├─────────────────────────────────────────────────────────────┤
│  1. Rule-based patterns (alta confianza: 0.7-0.9)         │
│  2. LLM fallback (si habilitado, confianza: 0.6)          │
│  3. Retorna: action_id, payload, confidence               │
└──────────────────────────┬──────────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
    confidence >= 0.5            confidence < 0.5
              │                         │
              ▼                         ▼
┌─────────────────────┐    ┌─────────────────────────────────┐
│   SLOTRESOLVER      │    │     CHATSERVICE (fallback)     │
│   missing()         │    │     - Agent genérico            │
│   - Detecta params │    │     - Respuesta conversacional  │
│     faltantes       │    │                                 │
└─────────┬───────────┘    └─────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│                    ACTIONEXECUTOR.execute()                  │
├─────────────────────────────────────────────────────────────┤
│  1. Validar payload (Pydantic)                              │
│  2. Verificar permisos (ActionPermissionPolicy)            │
│  3. Dry-run / Confirmación                                 │
│  4. Snapshot (estado previo)                               │
│  5. Ejecutar acción                                        │
│  6. Auditoría (log_action)                                 │
│  7. Retornar resultado                                     │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                 RESPUESTA AL USUARIO                         │
│           "Bienvenida activada" / "Antiflood activado"     │
└─────────────────────────────────────────────────────────────┘
```

---

## Tabla de tareas

| # | Tarea | Componente | Prioridad | Estado |
|---|-------|------------|-----------|--------|
| 1 | Conectar ActionParser en handlers.py | handlers.py | ALTA | ✅ COMPLETADO |
| 2 | Crear función helper para ejecutar acciones | handlers.py | ALTA | ✅ COMPLETADO (integrado) |
| 3 | Agregar más acciones al ActionRegistry | pilot_actions.py | ALTA | ✅ COMPLETADO |
| 4 | Configurar LLM para ActionParser | settings.py | MEDIA | ✅ COMPLETADO |
| 5 | Agregar tests de integración | test_actions_*.py | MEDIA | ✅ COMPLETADO |
| 6 | Probar con frases NL reales | QA | ALTA | ✅ COMPLETADO |

---

## Fase 1: Conexión ActionParser al flujo

### Objetivo fase
Conectar el ActionParser existente al flujo principal de procesamiento de mensajes en `handlers.py`.

### Implementacion fase

**Tarea 1.1: Modificar handlers.py**
- Ubicación: `app/webhook/handlers.py`
- Agregar import de ActionParser y ActionExecutor
- En el bloque `chat_message`, intentar ActionParser antes de ChatService
- Código ejemplo:
  ```python
  from app.agent.actions import ActionParser, ActionExecutor
  from app.agent.actions.registry import get_default_registry
  
  # En el flujo de chat_message:
  parser = ActionParser(llm_enabled=False)
  parse_result = parser.parse(text)
  
  if parse_result.action_id and parse_result.confidence >= 0.5:
      executor = ActionExecutor(get_default_registry())
      result = await executor.execute(
          parse_result.action_id,
          context,
          parse_result.payload
      )
      reply = result.message
  else:
      # Fallback a ChatService
      result = handle_chat_message_fn(chat_id, text)
      reply = result.get("response")
  ```

**Tarea 1.2: Manejar SlotResolver**
- Si SlotResolver.detecta campos faltantes, guardar estado en ConversationState
- Preguntar al usuario por los parámetros faltantes

---

## Fase 2: Expansión de acciones

### Objetivo fase
Agregar más acciones al ActionRegistry para cubrir las funcionalidades del ManagerBot.

### Implementacion fase

**Tarea 2.1: Agregar acciones de antiflood**
- `antiflood.toggle`: activar/desactivar
- `antiflood.set_limits`: mensajes y tiempo
- `antiflood.set_action`: warn, mute, ban

**Tarea 2.2: Agregar acciones de antispam**
- `antispam.telegram.toggle`: activar/desactivar
- `antispam.telegram.set_action`: mute, ban
- `antispam.forward.toggle`, `antispam.quotes.toggle`, etc.

**Tarea 2.3: Agregar acciones de bienvenida/despedida**
- `welcome.toggle`: ya implementado
- `welcome.set_media`: configurar multimedia
- `goodbye.toggle`, `goodbye.set_text`

**Tarea 2.4: Agregar acciones de filtros**
- `filter.add_word`: palabra bloqueada
- `filter.remove_word`: eliminar palabra
- `filter.list`: listar palabras

---

## Fase 3: Configuración de LLM

### Objetivo fase
Habilitar el uso de LLM en ActionParser para mejor precisión.

### Implementacion fase

**Tarea 3.1: Habilitar LLM**
- Variable de entorno: `ACTION_PARSER_LLM_ENABLED=true`
- Configurar provider: `LLM_PROVIDER=openai` o `ollama`
- Configurar modelo: `LLM_MODEL=gpt-4o-mini` o `llama3`

**Tarea 3.2: Mejorar prompt de LLM**
- Modificar `_llm_parse()` en parser.py
- Incluir lista de acciones disponibles
- Incluir ejemplos de parsing

---

## Fase 4: Testing y QA

### Objetivo fase
Verificar que el sistema funciona correctamente con casos reales.

### Implementacion fase

**Tarea 4.1: Tests de integración**
- Crear test que envíe mensaje NL y verifique ejecución
- Verificar slots faltantes
- Verificar permisos

**Tarea 4.2: Pruebas manuales**
- "Activa bienvenida"
- "Desactiva antispam"
- "Pon antiflood con 10 mensajes en 5 segundos"
- "Silencia 30 minutos a los que envíen enlaces"

---

## Notas

- La Fase 1 es crítica: sin ella, el ActionParser nunca se usa
- El fallback a ChatService asegura que mensajes no reconocidos tengan respuesta
- Las acciones requieren permisos: solo admins y moderadores pueden ejecutar
- El sistema de auditoría registra todas las acciones ejecutadas
