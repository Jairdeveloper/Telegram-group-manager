# Flujo de Datos del Módulo Agent

## Arquitectura General

El módulo `app.agent` implementa un sistema de procesamiento de mensajes con múltiples estrategias de respuesta:

```
Mensaje → IntentRouter → AgentCore → Respuesta
```

## Componentes Principales

### 1. AgentCore (core.py)
El componente central que orquesta el flujo de datos.

**Método principal:** `process(message, context)`

**Flujo interno:**
1. Construye el contexto de la sesión via `ContextBuilder`
2. Si `react_enabled`: ejecuta `_process_react()`
3. Si `rag_enabled`: busca en base de conocimientos
4. Si `llm_enabled`: genera respuesta con LLM
5. Fallback: usa `ChatService` via planner

### 2. IntentRouter (intent_router.py)
Clasifica mensajes entrantes para determinar el tipo de procesamiento.

**Método:** `route(message)` → `IntentDecision`

- **CHAT**: Conversación general → flujo estándar
- **AGENT_TASK**: Requiere herramientas → flujo de planning

**Estrategias:**
1. Rule-based: palabras clave (`buscar`, `calcula`, `clima`, etc.)
2. LLM classification: si está habilitado

### 3. ReActReasoner (reasoning.py)
Implementa el patrón Reason-Act para decidir la acción a tomar.

**Método:** `decide(message)` → `ReasoningDecision`

- **RESPOND**: Respuesta directa
- **PLAN**: Necesita ejecutar herramientas

### 4. AgentPlanner (planner.py)
Coordina la creación y ejecución de planes con herramientas.

**Métodos:**
- `create_plan(goal, context)`: Genera plan
- `execute_plan(plan_id)`: Ejecuta plan

**Dependencias:**
- `ToolRegistry`: Registro de herramientas disponibles
- `PolicyEngine`: Motor de políticas
- `ToolRouter`: Enrutador de herramientas

### 5. MemorySystem (memory.py)
Gestiona el historial de conversación por tenant/session.

**Métodos:**
- `add_exchange()`: Guarda mensaje y respuesta
- `get_history()`: Recupera historial

### 6. ContextBuilder (context.py)
Construye el contexto de la conversación para el LLM.

**Método:** `build(tenant_id, session_id)` → `ContextWindow`

### 7. RAGService (rag.py)
Sistema de Retrieval-Augmented Generation para conocimiento.

**Métodos:**
- `search()`: Búsqueda vectorial
- `generate_with_context()`: Generación con contexto

## Flujo de Datos Completo

```
                    ┌─────────────┐
                    │   Mensaje   │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   Context   │ ← MemorySystem
                    │   Builder   │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  ReAct      │
                    │  Reasoner   │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
        ┌─────▼─────┐  ┌────▼────┐  ┌────▼─────┐
        │ RESPOND   │  │  PLAN   │  │  NONE    │
        └─────┬─────┘  └────┬────┘  └────┬─────┘
              │             │            │
        ┌─────▼─────┐  ┌────▼────┐  ┌────▼─────┐
        │    LLM    │  │ Planner │  │   RAG   │
        │  Generate │  │ Execute │  │  Search  │
        └─────┬─────┘  └────┬────┘  └────┬─────┘
              │             │            │
              │             │            │
        ┌─────▼─────────────▼────────────▼─────┐
        │            AgentResponse              │
        └───────────────────────────────────────┘
```

## Integración con el Bot

### Entry Point: app/ops/services.py

```python
def handle_chat_message(chat_id, text, *, agent=None, storage=None):
    agent = agent or runtime.agent  # AgentCore
    response = agent.process(text)
    storage.save(session_id, text, response.text)
```

### Endpoint API: app/api/routes.py

```python
response = agent.process(message)
```

### Webhook Handler: app/webhook/handlers.py

```python
_agent_core = get_default_agent_core()
```

### Inicialización (app/api/bootstrap.py)

```python
from app.agent import get_default_agent_core

agent = get_default_agent_core()
```

## Flujo de Ejecución Típico

1. **Recepción**: El bot recibe un mensaje del usuario
2. **Enrutamiento**: Se determina si es CHAT o AGENT_TASK
3. **Procesamiento**:
   - Se construye el contexto de memoria
   - Se decide si responder directamente o planificar
   - Si planificar: se ejecutan herramientas y se genera respuesta
   - Si no: se usa RAG o LLM directamente
4. **Almacenamiento**: Se guarda el intercambio en memoria
5. **Respuesta**: Se devuelve `AgentResponse` con el texto y metadatos

## Flags de Configuración

- `llm_enabled`: Habilita generación con LLM
- `rag_enabled`: Habilita búsqueda en base de conocimientos
- `agent_react_enabled`: Habilita razonamiento ReAct
- `intent_router_llm_enabled`: Habilita clasificación LLM de intents