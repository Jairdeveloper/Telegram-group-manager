# Arquitectura de ChatBot Evolution

## Diagrama de Capas

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTACIÓN                              │
│  ┌──────────────┐              ┌──────────────────────────┐  │
│  │  CLI Mode    │              │  REST API (FastAPI)      │  │
│  │             │              │  - Chat endpoint         │  │
│  │ Interactive │              │  - History               │  │
│  │ Mode        │              │  - Statistics            │  │
│  └──────────────┘              └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────┐
│                   LÓGICA DE NEGOCIO                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  ACTOR (Brain)                                       │   │
│  │  - Procesa entrada                                  │   │
│  │  - Matchea patrones                                 │   │
│  │  - Traduce pronombres                               │   │
│  │  - Genera respuestas                                │   │
│  └──────────────────────────────────────────────────────┘   │
│                              ▲                                │
│          ┌───────────────────┼───────────────────┐           │
│          ▼                   ▼                   ▼            │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐    │
│  │ NLP Engine   │   │ Embeddings   │   │ LLM Fallback │    │
│  │              │   │              │   │              │    │
│  │ - Patterns   │   │ - Semantic   │   │ - OpenAI     │    │
│  │ - Tokenizer  │   │   search     │   │ - Ollama     │    │
│  │ - Pronouns   │   │              │   │              │    │
│  └──────────────┘   └──────────────┘   └──────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────┐
│                    DATA ACCESS LAYER                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │Conversation  │  │ Knowledge    │  │ Embedding    │      │
│  │Repository    │  │ Repository   │  │ Repository   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                              ▲                                │
│               ┌──────────────┴──────────────┐               │
│               ▼                             ▼               │
│         SQLAlchemy ORM          
│  ┌────────────────────────────────────────────────────┐    │
│  │            Database Layer                          │    │
│  │  (SQLite / PostgreSQL / MySQL)                     │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Flujo de Procesamiento

```
┌─────────────┐
│ User Input  │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Tokenizer      │  (Limpia, tokeniza)
└────────┬────────┘
         │
         ▼
┌────────────────────┐
│ Pattern Matching   │  (Intenta matching con patrones)
└──────┬─────────────┘
       │
       ├─ NO MATCH ─────────────────────┐
       │                                │
       │ MATCH                          │ DEFAULT
       │   │                            │
       ▼   ▼                            │
   ┌─────────────────┐                 │
   │ Pronoun Translate   │                 │
   └────────┬────────┘                 │
            │                          │
            ▼                          │
   ┌─────────────────┐                 │
   │ Build Reply     │                 │
   └────────┬────────┘                 │
            │                          │
            └──────────┬───────────────┘
                       │
                       ▼
            ┌──────────────────┐
            │ LLM Fallback     │  (Si confidence < threshold)
            │ (opcional)       │
            └────────┬─────────┘
                     │
                     ▼
            ┌──────────────────┐
            │ Final Response   │
            └────────┬─────────┘
                     │
                     ▼
            ┌──────────────────┐
            │ Save to Database │  (Persistencia)
            └────────┬─────────┘
                     │
                     ▼
            ┌──────────────────┐
            │ Return Response  │  (CLI o API)
            └──────────────────┘
```

## Componentes Principales

### 1. NLP Engine (`src/nlp/`)

**PatternEngine**
- Compila patrones a regex
- Realiza matching eficiente
- Caching de patrones compilados
- Extrae bindings de variables

**Tokenizer**
- Tokenización básica
- Normalización case
- Eliminación de caracteres especiales

**PronounTranslator**
- Mapeo de pronombres
- Traducción de referencias
- Personalizable

### 2. Brain (`src/brain/`)

**Agent**
- Orquestador principal
- Integra todos los módulos
- Mantiene estado de sesión (usuario actual)
- Genera respuestas estructuradas

### 3. Storage (`src/storage/`)

**Database**
- Gestión de conexión SQLAlchemy
- Inicialización de esquemas
- Pool de conexiones

**Models**
- Conversation (histórico)
- Knowledge (patrones)
- Embedding (vectores)
- User (perfiles)

**Repository**
- ConversationRepository (CRUD conversaciones)
- KnowledgeRepository (CRUD conocimiento)
- EmbeddingRepository (CRUD embeddings)
- UserRepository (CRUD usuarios)

### 4. Embeddings (`src/embeddings/`)

**EmbeddingService**
- Integración Sentence Transformers
- Embedding de textos
- Búsqueda semántica (top-k)
- Cálculo de similitud
- Clustering de respuestas

### 5. LLM Fallback (`src/llm/`)

**LLMProvider (Interfaz)**
- OpenAIProvider (GPT-3.5/4)
- OllamaProvider (modelos locales)

**LLMFallback**
- Auto-inicialización de providers
- Fallback automático
- Context injection

### 6. API (`src/api/`)

**FastAPI Routes**
- POST `/api/v1/chat` - Procesar mensaje
- GET `/api/v1/chat/history/{session_id}` - Historial
- GET `/api/v1/stats/user/{username}` - Estadísticas
- GET `/api/v1/health` - Health check
- GET `/docs` - Swagger UI

## Flujo de Datos

```
User Input
    ↓
[CLI/API Layer]
    ↓
[Actor.process()]
    ├─ Tokenizer.tokenize()
    ├─ PatternEngine.match()
    ├─ PronounTranslator.translate()
    ├─ Actor.build_reply()
    └─ (Fallback a LLM si necesario)
    ↓
Response Object
    ├─ text
    ├─ confidence
    ├─ pattern_matched
    ├─ source (pattern/default/llm/embedding)
    └─ metadata
    ↓
[Repository.save()]
    ↓
Database
    ├─ Conversation table
    ├─ Knowledge table
    ├─ Embedding table
    └─ User table
    ↓
[Return Response]
```

## Escalabilidad

### Configuración Local (Desarrollo)
```
Actor + SQLite + Default patterns
├─ Perfecto para: pruebas, desarrollo, prototipado
└─ Performance: ~100 req/s
```

### Configuración Microservicios (Producción)
```
[Load Balancer]
    ↓
[FastAPI Servers (múltiples)]
    ├─ PostgreSQL (centralizado)
    ├─ Redis Cache (opcional)
    ├─ Ollama/OpenAI (asyncronous)
    └─ Embeddings GPU (opcional)

Performance: ~1000+ req/s
```

### Kubernetes (Enterprise)
```
[Ingress Controller]
    ↓
[ChatBot API Pods] (autoscaling)
    ├─ [Embeddings Service Pods]
    ├─ [PostgreSQL StatefulSet]
    └─ [Redis Pods]

Performance: ~10000+ req/s
```

## Testing Architecture

```
Unit Tests (src/)
    ├─ test_pattern_engine    (NLP)
    ├─ test_actor            (Brain)
    ├─ test_storage          (Persistencia)
    └─ test_embeddings       (Vectores)

Integration Tests
    ├─ API endpoints
    ├─ Database persistence
    └─ End-to-end conversations

Load Testing (opcional)
    └─ Apache Locust / k6
```

---

**Última actualización**: 2024
**Versión**: 1.0.0
**Python**: 3.10+
