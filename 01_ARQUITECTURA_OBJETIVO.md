# 02_ARQUITECTURA_OBJETIVO - Phase 2: NLP/LLM, Knowledge Base & Analytics

> **Estado**: En Planificación
> **Proyecto**: Chatbot Asistente Manufacturing
> **Pre-requisitos**: Fases 0-5 completadas (ARQUITECTURA_OBJETIVO.md)

---

## Propósito

Extender la arquitectura existente con las funcionalidades que faltan para completar el asistente conversacional:

1. **NLP/LLM Service** - Integración con modelos de lenguaje
2. **Knowledge Base** - Sistema de embeddings y búsqueda vectorial
3. **Analytics Service** - Métricas y observabilidad avanzada

**No es una migración a microservicios** - El monolito modular actual está bien estructurado. Estas son adiciones funcionales sobre la base existente.

---

## Estado Actual del Proyecto

### Stack implementado
- Python 3.11 + FastAPI
- PostgreSQL + pgvector
- Redis (cache + cola)
- PTB para Telegram
- Docker + Kubernetes
- GitHub Actions CI/CD

### Arquitectura actual
```
Telegram → Webhook → Dispatcher → Chat/OPS Services → Worker → Redis/PostgreSQL
```

### Fases completadas
| Fase | Descripción | Estado |
|------|-------------|--------|
| 0 | Congelación de arquitectura operativa | ✅ |
| 1 | Dispatcher de Telegram | ✅ |
| 2 | Servicios de aplicación extraídos | ✅ |
| 3 | Integración dispatcher-servicios | ✅ |
| 4 | Deprecar runtimes legacy | ✅ |
| 5 | Endurecimiento contratos y observabilidad | ✅ |

---

## Objetivos de esta fase

### 1. NLP/LLM Service
- Integrar Ollama para inferencia on-premise
- Integrar OpenAI como fallback
- Abstraer el provider de LLM
- Manejo de streaming de respuestas
- Rate limiting y quotas por usuario

### 2. Knowledge Base
- Sistema de embeddings con sentence-transformers
- Almacenamiento vectorial en pgvector
- Búsqueda semántica de documentos
- Indexación de manuales, FAQs, procedimientos
- Actualización de embeddings

### 3. Analytics Service
- Métricas de uso (mensajes, usuarios, sesiones)
- Latencia de respuestas
- Tracking de conversaciones
- Dashboards operativos
- Alertas de comportamiento anómalo

---

## Arquitectura Objetivo Extendida

```
┌─────────────────────────────────────────────────────────────────┐
│                        TELEGRAM                                  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    app.webhook.entrypoint                       │
└──────────────────────────┬──────────────────────────────────────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
            ▼              ▼              ▼
    ┌───────────┐  ┌───────────┐  ┌───────────┐
    │  Chat     │  │   OPS     │  │ Analytics │
    │  Service  │  │  Service  │  │  Service  │
    └─────┬─────┘  └───────────┘  └─────┬─────┘
          │                              │
          ▼                              ▼
    ┌───────────┐                ┌───────────┐
    │   Agent   │                │  Metrics  │
    │   /Brain  │                │  Collector│
    └─────┬─────┘                └───────────┘
          │
┌─────────┼─────────────────────────────────────────────────────┐
│         │          chat_service/                              │
│         ▼                                                       │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │  Pattern    │    │  Knowledge  │    │    LLM      │      │
│  │  Engine     │    │   Base      │    │   Service   │      │
│  └─────────────┘    └──────┬──────┘    └─────────────┘      │
│                            │                                   │
│                     ┌──────▼──────┐                            │
│                     │  Embeddings │                            │
│                     │  (pgvector) │                            │
│                     └─────────────┘                            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    INFRAESTRUCTURA                              │
│  PostgreSQL + pgvector  │  Redis  │  Ollama (opcional)          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Plan de Implementación

### Fase 7: LLM Service

#### Objetivo
Integrar capacidad de procesamiento de lenguaje natural con modelos de lenguaje.

#### Componentes a crear

```
chat_service/
├── llm/
│   ├── __init__.py
│   ├── base.py          # Interfaz abstracta
│   ├── ollama.py       # Proveedor Ollama
│   ├── openai.py       # Proveedor OpenAI
│   └── factory.py      # Factory de proveedores
```

#### Interfaces

```python
# chat_service/llm/base.py
from abc import ABC, abstractmethod
from typing import AsyncIterator

class LLMProvider(ABC):
    @abstractmethod
    async def generate(
        self, 
        prompt: str, 
        context: list[dict] = None,
        stream: bool = False
    ) -> str | AsyncIterator[str]:
        pass
    
    @abstractmethod
    async def get_embedding(self, text: str) -> list[float]:
        pass
```

#### Configuración

```python
# app/config/settings.py - agregar
class Settings(BaseSettings):
    # LLM
    LLM_PROVIDER: str = "ollama"  # ollama | openai
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4"
    
    # Embeddings
    EMBEDDINGS_PROVIDER: str = "local"  # local | openai
    EMBEDDINGS_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
```

#### Criterio de salida
- El chat service puede generar respuestas via LLM
- Se puede cambiar de proveedor sin cambiar código de dominio
- Streaming funciona para respuestas largas

---

### Fase 8: Knowledge Base

#### Objetivo
Sistema de búsqueda semántica sobre documentación interna.

#### Componentes a crear

```
chat_service/
├── knowledge/
│   ├── __init__.py
│   ├── models.py       # Document, Chunk, SearchResult
│   ├── repository.py   # Persistencia en pgvector
│   ├── indexer.py      # Creación de embeddings
│   ├── search.py       # Búsqueda semántica
│   └── loader.py       # Carga de documentos (PDF, MD, TXT)
```

#### Modelo de datos

```python
# chat_service/knowledge/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime
from pgvector.sqlalchemy import Vector

class Document(Base):
    __tablename__ = "knowledge_documents"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(500))
    content = Column(Text)
    source = Column(String(255))  # archivo, url, manual
    created_at = Column(DateTime, default=datetime.utcnow)

class DocumentChunk(Base):
    __tablename__ = "knowledge_chunks"
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    content = Column(Text)
    embedding = Column(Vector(384))  # dimensíon según modelo
    created_at = Column(DateTime, default=datetime.utcnow)
```

#### Flujo de indexación

1. Cargar documento (PDF, Markdown, TXT)
2. Chunking (splitter de texto)
3. Generar embeddings por chunk
4. Almacenar en pgvector
5. Guardar metadatos

#### Flujo de búsqueda

1. Embedding de query del usuario
2. Búsqueda vectorial en pgvector (cosine similarity)
3. Retornar top-k chunks relevantes
4. Construir contexto para LLM

#### Criterio de salida
- Documentos se pueden indexar y buscar
- Búsqueda semántica retorna resultados relevantes
- Contexto se inyecta en prompts de LLM

---

### Fase 9: Analytics Service

#### Objetivo
Observabilidad y métricas del sistema.

#### Componentes a crear

```
app/
├── analytics/
│   ├── __init__.py
│   ├── models.py       # Conversation, Message, Session
│   ├── repository.py   # Persistencia
│   ├── metrics.py      # Cálculo de métricas
│   └── collector.py    # Recolección de eventos
```

#### Métricas a implementar

| Métrica | Descripción | Destino |
|---------|-------------|---------|
| `messages_total` | Mensajes procesados | Prometheus |
| `response_latency` | Latencia de respuesta | Prometheus |
| `conversations_active` | Conversaciones activas | Prometheus |
| `llm_tokens_used` | Tokens consumidos | PostgreSQL |
| `knowledge_hits` | Búsquedas en KB exitosas | PostgreSQL |
| `errors_total` | Errores por tipo | Sentry + Prometheus |

#### Modelo de datos

```python
# app/analytics/models.py
class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(UUID, primary_key=True)
    chat_id = Column(Integer, index=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    message_count = Column(Integer, default=0)

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(UUID, primary_key=True)
    conversation_id = Column(UUID, ForeignKey("conversations.id"))
    role = Column(String(20))  # user, assistant
    content = Column(Text)
    latencies_ms = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
```

#### Integración con webhook actual

```python
# En app/webhook/handlers.py - agregar post-procesamiento
from app.analytics.collector import AnalyticsCollector

analytics = AnalyticsCollector()

async def process_update_impl(update: dict):
    # ... flujo existente ...
    
    # Post-procesamiento analytics
    await analytics.track_message(
        chat_id=chat_id,
        role="user",
        content=text,
        latency_ms=latency
    )
```

#### Criterio de salida
- Métricas básicas disponibles en Prometheus/Grafana
- Conversaciones se almacenan para análisis
- Dashboard operativo creado

---

## Orden de Implementación Recomendado

```
Fase 7 (LLM) → Fase 8 (KB) → Fase 9 (Analytics)
```

**Justificación:**
1. LLM es la base para el asistente
2. Knowledge Base complementa LLM con contexto
3. Analytics proporciona observabilidad sobre las fases anteriores

---

## Backlog de Archivos

### Crear

```
chat_service/
├── llm/
│   ├── base.py
│   ├── ollama.py
│   ├── openai.py
│   └── factory.py
├── knowledge/
│   ├── models.py
│   ├── repository.py
│   ├── indexer.py
│   ├── search.py
│   └── loader.py
app/
├── analytics/
│   ├── models.py
│   ├── repository.py
│   ├── metrics.py
│   └── collector.py
```

### Modificar

```
app/config/settings.py       # Agregar configuración LLM/KB
app/webhook/handlers.py       # Integrar analytics
chat_service/agent.py         # Integrar LLM
chat_service/brain.py         # Usar knowledge base
docker-compose.yml            # Agregar Ollama (opcional)
deploy/k8s/                   # Agregar servicios si es necesario
```

---

## Testing Strategy

### Unit tests
- LLM providers (mock de respuestas)
- Knowledge base search (mock de embeddings)
- Analytics collector

### Integración
- LLM con Ollama local
- Búsqueda en pgvector
- Flujo completo webhook → LLM → respuesta

### Contract tests
- API de chat con LLM
- Endpoint de métricas

---

## Risks y Mitigations

| Riesgo | Mitigación |
|--------|------------|
| Latencia alta en LLM | Streaming, caching, fallback a respuestas predefinidas |
| Embeddings costosos | Usar modelo local (sentence-transformers) |
| pgvector no escala | Plan de migración a Milvus/Weaviate futuro |
| Datos sensibles en analytics | Encryption at rest, GDPR compliance |

---

## Definition of Done

Esta fase se considera completada cuando:

1. ✅ El chatbot puede generar respuestas via LLM (Ollama + OpenAI)
2. ✅ La Knowledge Base permite búsqueda semántica
3. ✅ Las métricas básicas están disponibles en Prometheus/Grafana
4. ✅ Los componentes tienen tests unitarios
5. ✅ La configuración permite cambio de proveedor sin código
6. ✅ La arquitectura sigue siendo monolito modular

---

## Costos Estimados

| Componente | Costo mensual | Notas |
|------------|---------------|-------|
| PostgreSQL (existente) | $0 | Ya en uso |
| Redis (existente) | $0 | Ya en uso |
| Ollama (on-prem) | $0 | Hardware existente |
| OpenAI (fallback) | $20-50/mes | Pay-per-use |
| Prometheus/Grafana | $0 | Self-hosted o free tier |

**Costo incremental**: $0-50/mes dependiendo uso de OpenAI

---

## Siguiente paso

Iniciar **Fase 7: LLM Service** - Crear la interfaz abstracta y el proveedor Ollama como implementación primary.
