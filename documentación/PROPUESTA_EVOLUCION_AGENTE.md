# PROPUESTA_EVOLUCION_AGENTE.md

> **Fecha**: 2026-03-09
> **Proyecto**: Chatbot Manufacturing
> **Estado actual**: Rule-based chatbot con arquitectura modular

---

## 1. Análisis del Estado Actual

### 1.1 Componentes Implementados

| Componente | Estado | Descripción |
|------------|--------|-------------|
| `chat_service/agent.py` | ✅ Funcional | Agente rule-based con pattern matching |
| `chat_service/brain.py` | ✅ Funcional | Patrones de respuesta predefinidos |
| `chat_service/pattern_engine.py` | ✅ Funcional | Motor de regex para matching |
| `app/planner/planner.py` | ✅ Estructura | Planificador con steps |
| `app/tools/router.py` | ✅ Estructura | Router de herramientas |
| `app/tools/registry.py` | ✅ Estructura | Registro de herramientas |
| `app/tools/builtins.py` | ⚠️ Placeholder | Tools simuladas (no reales) |
| `app/guardrails/` | ✅ Funcional | Filtrado de contenido |
| `app/policies/engine.py` | ✅ Funcional | Rate limiting, quotas, ACL |
| `app/webhook/handlers.py` | ✅ Funcional | Procesamiento de Telegram |
| `app/telegram/dispatcher.py` | ✅ Funcional | Clasificación de mensajes |

### 1.2 Flujo Actual

```
Telegram → Webhook → Dispatcher → Agent (Pattern Matching) → Brain (Responses)
                                    ↓
                              Tool Router → Tools (placeholders)
                                    ↓
                              Policy Engine → Guardrails
```

### 1.3 Limitaciones Identificadas

1. **Agente es puramente reactivo**: Solo responde a patrones predefinidos, no razona
2. **LLM no integrado**: El tool "llm" es un placeholder que retorna texto fijo
3. **Sin memoria de conversación**: No mantiene contexto entre mensajes
4. **Sin RAG**: No busca en documentación técnica
5. **Tools simuladas**: Calculator, search, weather no funcionan realmente
6. **Sin reasoning chain**: No puede encadenar pensamientos
7. **Sin agentic loops**: No puede ejecutar múltiples pasos automáticamente

---

## 2. Visión: Agente IA Autónomo

### 2.1 Definición del Target

Un **Agente IA** que:
- Entienda intención del usuario via LLM
- Mantenga contexto de conversación (memory)
- Busque información en documentación (RAG)
- Ejecute acciones concretas via herramientas
- Planifique multi-step para tareas complejas
- Razone sobre sus decisiones (chain-of-thought)
- Aprenda de interacciones (feedback loop)

### 2.2 Comparativa

| Capacidad | Actual | Objetivo |
|-----------|--------|----------|
| Pattern matching | Regex | LLM + embeddings |
| Respuestas | Predefinidas | Generativas |
| Contexto | Stateless | Memory vector store |
| Herramientas | Placeholder | APIs reales |
| Planificación | Basic steps | ReAct / CoT |
| Documentación | N/A | RAG + pgvector |
| Observabilidad | Basic events | Full metrics |

---

## 3. Arquitectura Propuesta

### 3.1 Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              TELEGRAM                                        │
│                    (Voice / Text / Commands)                                │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         app.webhook.entrypoint                              │
│                    (Auth, Rate Limit, Dedup)                                │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      app.telegram.dispatcher                                │
│              (Clasificar: chat / ops / unsupported)                        │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
              ▼                  ▼                  ▼
     ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
     │  Chat Flow   │   │  OPS Flow    │   │ Agent Flow   │
     └──────┬───────┘   └──────────────┘   └──────┬───────┘
            │                                     │
            ▼                    ┌────────────────┼────────────────┐
     chat_service/agent          │                │                │
            │                    ▼                ▼                ▼
            │          ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
            │          │   Intent     │  │   Memory     │  │    Tools     │
            │          │   Router     │  │   System     │  │   Executor   │
            │          └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
            │                 │                 │                 │
            │                 └─────────────────┼─────────────────┘
            │                                   │
            │                                   ▼
            │                    ┌────────────────────────────────┐
            │                    │        AGENT CORE              │
            │                    │  ┌────────┐  ┌─────────────┐  │
            │                    │  │ Reason │  │   Planner    │  │
            │                    │  │  (CoT) │  │  (ReAct)     │  │
            │                    │  └────────┘  └─────────────┘  │
            │                    └──────────────┬────────────────┘
            │                                   │
            │                    ┌───────────────┼───────────────┐
            │                    ▼               ▼               ▼
            │          ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
            │          │     LLM      │  │    RAG       │  │   Tool       │
            │          │   Service    │  │   Service    │  │   Service    │
            │          └──────────────┘  └──────┬───────┘  └──────────────┘
            │                                   │
            │                          ┌────────┴────────┐
            │                          ▼                 ▼
            │                  ┌──────────────┐  ┌──────────────┐
            │                  │  pgvector    │  │  External   │
            │                  │  (Knowledge) │  │    APIs     │
            │                  └──────────────┘  └──────────────┘
            │
            ▼
      Telegram Response

┌─────────────────────────────────────────────────────────────────────────────┐
│                           INFRASTRUCTURE                                    │
│  PostgreSQL + pgvector  │  Redis  │  Ollama/OpenAI  │  Prometheus       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Componentes Nuevos

#### A. Intent Router (Reemplaza dispatcher para chat)

```python
# app/agent/intent_router.py
class IntentRouter:
    """Clasifica intención del usuario y decide flujo"""
    
    def route(self, message: str, context: ConversationContext) -> Intent:
        # 1. Reglas simples para comandos
        if message.startswith("/"):
            return Intent.COMMAND
            
        # 2. Clasificación LLM para queries
        intent = await self.llm_classify(message, context)
        
        # 3. Detectar si necesita herramientas
        if await self.needs_tools(message):
            return Intent.AGENT_TASK
            
        return Intent.CHAT
```

#### B. Memory System

```python
# app/agent/memory.py
class MemorySystem:
    """Gestión de contexto conversacional"""
    
    def __init__(self, vector_store, max_tokens=4000):
        self.vector_store = vector_store  # pgvector
        self.max_tokens = max_tokens
        self.conversations: Dict[str, ConversationBuffer] = {}
    
    async def add_message(self, session_id: str, role: str, content: str):
        """Agregar mensaje a la conversación"""
        
    async def get_context(self, session_id: str, query: str) -> str:
        """Obtener contexto relevante para el query"""
        
    async def summarize_old_messages(self, session_id: str):
        """Comprimir historial viejo a summary"""
```

#### C. Agent Core (Reasoning + Planning)

```python
# app/agent/core.py
class AgentCore:
    """Agente IA con reasoning chain-of-thought"""
    
    async def process(self, message: str, context: MemoryContext) -> AgentResponse:
        # 1. Thought: Analizar la situación
        thought = await self.think(message, context)
        
        # 2. Action: Decidir acción
        action = await self.plan(thought)
        
        # 3. Execute: Ejecutar acción
        result = await self.execute(action)
        
        # 4. Observe: Analizar resultado
        observation = await self.observe(result)
        
        # 5. Repeat si es necesario
        return await self.format_response(thought, result)
```

#### D. RAG Service

```python
# app/agent/rag.py
class RAGService:
    """Retrieval Augmented Generation"""
    
    def __init__(self, vector_store, llm_service):
        self.vector_store = vector_store
        self.llm = llm_service
    
    async def search(self, query: str, top_k: int = 5) -> List[Document]:
        """Búsqueda semántica en documentación"""
        
    async def generate_with_context(self, query: str, context: str) -> str:
        """Generar respuesta con contexto de documentos"""
```

#### E. Tool Executor

```python
# app/agent/tool_executor.py
class ToolExecutor:
    """Ejecutor de herramientas reales"""
    
    def __init__(self, tool_registry):
        self.registry = tool_registry
    
    async def execute(self, tool_call: ToolCall) -> ToolResult:
        """Ejecutar tool con retries y validación"""
        
    async def execute_plan(self, plan: Plan) -> List[ToolResult]:
        """Ejecutar plan multi-step"""
```

### 3.3 Flujo Detallado del Agente

```
USER: "Busca el manual de operación del robot modelo X"

┌─────────────────────────────────────────────────────────────┐
│ 1. INTENT ROUTER                                           │
│    → Detecta: AGENT_TASK (necesita tools + RAG)           │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. MEMORY SYSTEM                                           │
│    → Carga historial de conversación                       │
│    → max 4000 tokens context window                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. AGENT CORE (ReAct Pattern)                              │
│                                                             │
│    Thought: El usuario quiere información técnica.         │
│             Necesito buscar en la base de conocimiento.    │
│                                                             │
│    Action: search_knowledge_base(query="manual robot X")   │
│                                                             │
│    Observation: Encontré 3 documentos relevantes            │
│                                                             │
│    Thought: Tengo los documentos. Ahora genero respuesta   │
│             con el LLM usando RAG.                          │
│                                                             │
│    Action: rag_generate(query, documents)                  │
│                                                             │
│    Observation: Respuesta generada ✓                       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. GUARDRAILS + POLICIES                                   │
│    → Validar respuesta antes de enviar                     │
│    → Rate limiting                                         │
│    → Content filter                                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. RESPONSE                                                │
│    → Guardar en memoria                                    │
│    → Enviar a Telegram                                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Plan de Implementación

### Fase 10: LLM Integration

**Objetivo**: Integrar LLM real como cerebro del agente

**Entregables**:
- `chat_service/llm/providers/ollama.py`
- `chat_service/llm/providers/openai.py`
- `chat_service/llm/factory.py`
- `chat_service/llm/chat.py` (streaming chat)

**Cambios en código**:
```python
# Reemplazar app/tools/builtins.py - LLM handler real
async def llm_handler(prompt: str, model: str = "llama3") -> str:
    llm = LLMFactory.get_provider(model)
    return await llm.generate(prompt)
```

**Criterio de salida**: El agente puede generar respuestas via LLM real

---

### Fase 11: Memory System

**Objetivo**: Mantener contexto entre mensajes

**Entregables**:
- `app/agent/memory.py` - Buffer de conversación
- `app/agent/context.py` - Gestión de context window
- Actualizar schema PostgreSQL para conversations

**Modelo de datos**:
```python
class Conversation(Base):
    id: UUID
    chat_id: int
    started_at: DateTime
    messages: List[Message]
    summary: Optional[str]  # Para conversaciones largas

class Message(Base):
    id: UUID
    conversation_id: UUID
    role: str  # user, assistant, system
    content: Text
    tokens: int
    created_at: DateTime
```

**Criterio de salida**: El agente recuerda lo que dijo el usuario en mensajes anteriores

---

### Fase 12: RAG / Knowledge Base

**Objetivo**: Búsqueda semántica en documentación técnica

**Entregables**:
- `app/agent/rag.py` - Servicio RAG
- `app/agent/embeddings.py` - Generación de embeddings
- `app/knowledge/indexer.py` - Indexador de documentos
- Migration para vector store

**Integración con existentes**:
-复用 `chat_service/knowledge/` si ya existe
- Usar pgvector existente

**Criterio de salida**: "Busca el manual de..." retorna documentos relevantes

---

### Fase 13: Agent Core (ReAct)

**Objetivo**: Reasoning chain y tool execution

**Entregables**:
- `app/agent/core.py` - Agent con ReAct
- `app/agent/reasoning.py` - Chain-of-thought
- `app/agent/planner.py` - Planificador mejorado

**Patrón ReAct**:
```python
async def react_loop(self, task: str, max_iterations=5):
    thought = ""
    for i in range(max_iterations):
        # Think
        thought = await self.reason(task, thought)
        
        # Decide action
        action = await self.decide(thought)
        
        # Execute
        result = await self.execute(action)
        
        # Observe
        if self.is_complete(result):
            return result
        
        thought += f"\nObservation: {result}"
```

**Criterio de salida**: El agente puede encadenar múltiples tools para una tarea

---

### Fase 14: Real Tools

**Objetivo**: Implementar herramientas reales

| Tool | Implementación | API Externa |
|------|----------------|-------------|
| `search` | DuckDuckGo API | ✅ |
| `weather` | OpenWeatherMap | ✅ |
| `calculator` | Ya funciona | ✅ |
| `database` | Query PostgreSQL | ✅ |
| `webhook_trigger` | HTTP requests | ✅ |
| `file_search` | RAG existente | ✅ |

**Criterio de salida**: Las tools devuelven datos reales

---

### Fase 15: Observability & Analytics

**Objetivo**: Métricas completas del agente

**Entregables**:
- Métricas Prometheus:
  - `agent_thoughts_total`
  - `agent_actions_total`
  - `rag_retrieval_latency`
  - `llm_tokens_used`
  - `tool_execution_duration`
- Dashboards Grafana
- Tracing con OpenTelemetry

**Criterio de salida**: Dashboard operativo con métricas del agente

---

## 5. Backlog de Archivos

### Crear

```
app/agent/
├── __init__.py
├── core.py              # Agent ReAct principal
├── intent_router.py     # Clasificación de intents
├── memory.py           # Sistema de memoria
├── context.py          # Gestión de contexto
├── rag.py              # RAG service
├── embeddings.py       # Embeddings service
├── reasoning.py        # Chain-of-thought
├── planner.py          # Planificador avanzado
├── tool_executor.py   # Ejecutor de tools
└── metrics.py          # Métricas del agente

chat_service/llm/
├── __init__.py
├── base.py             # Interfaz abstracta
├── factory.py          # Factory de providers
├── chat.py             # Chat with streaming
└── providers/
    ├── __init__.py
    ├── ollama.py
    └── openai.py

app/knowledge/
├── __init__.py
├── indexer.py          # Indexador de docs
├── loader.py           # Carga de archivos
└── chunks.py           # Text splitting
```

### Modificar

```
chat_service/agent.py      # Integrar con Agent Core
app/tools/builtins.py     # Implementar tools reales
app/webhook/handlers.py    # Integrar nuevo flujo
app/config/settings.py     # Agregar LLM config
```

---

## 6. Testing Strategy

### Unit Tests
- Intent router con múltiples queries
- Memory context window management
- RAG retrieval accuracy
- Tool executor con mocks

### Integration Tests
- LLM con Ollama local
- RAG con pgvector
- Flujo completo agente

### E2E Tests
- "Busca información en docs" → RAG → Respuesta
- "Haz cálculo de..." → Calculator → Respuesta
- "Planifica..." → Multi-step → Resultado

---

## 7. Riesgos y Mitigaciones

| Riesgo | Impacto | Mitigación |
|--------|---------|------------|
| Latencia LLM | Alta | Streaming, caching, fallback a respuestas simples |
| Context window | Limite | Memory compression, summarization |
| RAG accuracy | Calidad | Evaluar retrieval, fine-tune embeddings |
| Tool security | Crítico | Sandboxing, policy engine, rate limiting |
| Costos LLM | $ | Rate limits, caching, Ollama on-prem |

---

## 8. Definition of Done - Agente IA

El sistema es un Agente IA cuando:

1. ✅ Puede generar respuestas generativas (no solo patrones)
2. ✅ Mantiene contexto de conversación
3. ✅ Busca en documentación (RAG)
4. ✅ Ejecuta herramientas reales
5. ✅ Razona sobre sus decisiones (CoT/ReAct)
6. ✅ Encadena múltiples pasos para tareas complejas
7. ✅ Tiene métricas observables
8. ✅ Pasa tests de integración end-to-end

---

## 9. Cronograma Sugerido

| Fase | Duración | Entregable |
|------|----------|------------|
| LLM Integration | 1 semana | Chat funcional con LLM |
| Memory System | 1 semana | Contexto entre mensajes |
| RAG | 1 semana | Búsqueda en docs |
| Agent Core | 2 semanas | ReAct loop |
| Real Tools | 1 semana | APIs integradas |
| Observability | 1 semana | Dashboard |

**Total estimado**: 7 semanas

---

## 10. Recomendación de Inicio

**Iniciar por Fase 10 (LLM Integration)** porque:
1. Es la base para todo lo demás
2. Tiene alto impacto inmediato (chat generativo)
3.验证 el stack técnico (Ollama/OpenAI)
4. Permite iterar rápidamente

**Primer paso concreto**:
1. Crear `chat_service/llm/factory.py`
2. Implementar provider Ollama
3. Integrar en `chat_service/agent.py`
4. Probar con conversation simple
