# Robot - Análisis de Arquitectura e Implementación

> **Fecha**: 2026-03-26
> **Versión**: 1.0

---

## 1. Estructura del Proyecto

### 1.1 Visión General

El proyecto **Robot** es una aplicación de chatbot para Telegram enfocada en manufacturing, construida con una arquitectura de **monolito modular** que unifica múltiples responsabilidades en un único entrypoint.

```
Telegram → Webhook (8000) → Dispatcher → Chat/OPS Services → Worker → Redis/PostgreSQL
```

### 1.2 Arquitectura Actual

```
┌─────────────────────────────────────────────────────────────────┐
│                    robot (Puerto 8000 - FastAPI)               │
├─────────────────────────────────────────────────────────────────┤
│  ├── /webhook/{token}    → Telegram Updates                    │
│  ├── /health             → Health check                        │
│  ├── /metrics            → Prometheus metrics                  │
│  └── /manager/*          → ManagerBot (OPS + Enterprise)       │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     chat_service/                               │
│  ├── agent.py         → Orquestador de respuestas              │
│  ├── pattern_engine.py→ Motor de matching de patrones          │
│  ├── brain.py         → Lógica de negocio                     │
│  └── storage.py       → Persistencia                           │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ManagerBot (Módulos)                        │
│  ├── OPS Module       → Comandos operativos (/health, /e2e)   │
│  ├── Enterprise Module→ Gestión de grupos y moderación        │
│  └── Agent Module     → Agente autónomo (experimental)        │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 Estructura de Directorios

```
robot/
├── app/
│   ├── webhook/              # Entrypoint principal
│   │   ├── entrypoint.py     # FastAPI app + CLI main()
│   │   ├── handlers.py      # Procesamiento de updates
│   │   ├── bootstrap.py     # Runtime configuration
│   │   └── infrastructure.py # Dependencias (Redis, dedup)
│   ├── manager_bot/          # Sistema de módulos
│   │   ├── core.py          # ManagerBot + ModuleRegistry
│   │   ├── registry.py      # Registro de módulos
│   │   ├── _application/    # Módulos (ops, enterprise, agent)
│   │   ├── _menus/          # Menús de configuración
│   │   ├── _features/      # Features (antiflood, antilink, etc)
│   │   └── _transport/     # Adaptadores Telegram
│   ├── ops/                 # Servicios operativos legacy
│   ├── enterprise/          # Módulo enterprise (moderación)
│   ├── telegram/            # Cliente Telegram
│   ├── config/              # Configuración
│   ├── auth/                # Autenticación
│   ├── billing/            # Facturación
│   ├── audit/              # Auditoría
│   └── guardrails/         # Middleware de seguridad
├── chat_service/            # Servicio de chat/NLP
│   ├── agent.py            # Orquestador principal
│   ├── pattern_engine.py   # Matching de patrones
│   ├── brain.py            # Lógica de negocio
│   └── storage.py          # Persistencia
├── worker.py               # RQ worker para tareas async
├── webhook_tasks.py        # Tareas para el worker
├── pyproject.toml          # Paquete instalable
├── migrations/             # Alembic migrations
└── tests/                 # Suite de tests
```

### 1.4 Entry Points

| Comando | Módulo | Descripción |
|---------|--------|-------------|
| `robot` | `app.webhook.entrypoint:main` | Servidor completo (Puerto 8000) |
| `robot-worker` | `worker:main` | Worker de tareas async |

---

## 2. Diseño y Patrones Observados

### 2.1 Patrones de Arquitectura

| Patrón | Aplicación |
|--------|------------|
| **Monolito Modular** | Un único entrypoint que agrupa webhook, API, y ManagerBot |
| **Module Registry** | `ManagerBot` usa registro de módulos cargables dinámicamente |
| **Feature Flags** | Módulos controlados por variables de entorno (`MANAGER_ENABLE_*`) |
| **Dependency Injection** | Configuración centralizada en `bootstrap.py` |
| **Async Workers** |RQ para procesamiento asíncrono de tareas |
| **Deduplicación** | Store en memoria para evitar procesamiento duplicate |

### 2.2 Patrones de Diseño en Código

| Patrón | Ubicación | Descripción |
|--------|-----------|-------------|
| **Strategy** | `chat_service/pattern_engine.py` | Matching de patrones con múltiples estrategias |
| **Factory** | `app/api/factory.py` | Creación de componentes |
| **Registry** | `app/manager_bot/registry.py` | Registro de módulos |
| **Adapter** | `app/manager_bot/_transport/telegram/ptb_adapter.py` | Bridge PTB ↔ ManagerBot |
| **Template Method** | `app/manager_bot/_menus/base.py` | Menús base con extensiones |
| **Observer** | Métricas Prometheus | Emisión de métricas |

### 2.3 Stack Tecnológico

- **Framework**: FastAPI + Uvicorn
- **Lenguaje**: Python 3.10+
- **Telegram**: python-telegram-bot (PTB)
- **Base de datos**: PostgreSQL + SQLAlchemy
- **Colas**: Redis + RQ (Redis Queue)
- **Métricas**: Prometheus client
- **Container**: Docker + Kubernetes
- **CI/CD**: GitHub Actions

---

## 3. Fortalezas Actuales

### 3.1 Arquitectura Sólida

- **Un único entrypoint**: Elimina la complejidad de múltiples puertos y procesos
- **Puerto 8000**: Evita problemas de permisos en Windows
- **Paquete instalable**: `pip install -e .` resuelve definitivamente los imports

### 3.2 Sistema de Módulos

- **Extensibilidad**: Los módulos se registran dinámicamente via `ModuleRegistry`
- **Feature flags**: Control granular de qué módulos están activos
- **Separación de responsabilidades**: OPS, Enterprise, y Agent son módulos independientes

### 3.3 Observabilidad

- **Métricas Prometheus**: `/metrics` endpoint
- **Health checks**: `/health` y `/manager/health`
- **Deduplicación**: Evita procesamiento duplicate de updates
- **Logging estructurado**: Runtime configurable

### 3.4 Developer Experience

- **Scripts de instalación**: `install.sh` (Linux/Mac) y `install.bat` (Windows)
- **Configuración VS Code**: `launch.json` para debug
- **Pyproject.toml unificado**: Dependencias y entry points en un solo archivo

### 3.5 Compatibilidad

- **Legacy bridges**: `robot_ptb_compat` para backwards compatibility
- **Múltiples modos**: Webhook (producción) y Polling (desarrollo)

---

## 4. Limitaciones Técnicas

### 4.1 Funcionalidades Pendientes

Según `01_ARQUITECTURA_OBJETIVO.md`, las siguientes funcionalidades están **pendientes**:

| Fase | Componente | Estado |
|------|------------|--------|
| 7 | LLM Service (Ollama/OpenAI) | No implementado |
| 8 | Knowledge Base (pgvector) | No implementado |
| 9 | Analytics Service | Parcial (solo métricas Prometheus básicas) |

### 4.2 Limitaciones Observadas

- **Chat sin LLM**: El agente usa pattern matching simple, sin capacidades de NLP/LLM
- **Sin búsqueda vectorial**: No hay Knowledge Base para búsqueda semántica
- **Métricas limitadas**: Solo Prometheus básico, sin dashboards operativas
- **Deprecaciones legacy**: Hay archivos marcados como deprecated que podrían limpiarse

### 4.3 Consideraciones de Escalabilidad

- **Deduplicación in-memory**: No escala horizontalmente (solo funciona con 1 instancia)
- **Worker único**: Un solo proceso RQ puede ser bottleneck
- **Sin cache avanzado**: Redis usado solo para colas, no para caché de respuestas

---

## 5. Resumen Ejecutivo

El proyecto **Robot** es un chatbot de Telegram para manufacturing con una arquitectura de monolito modular bien estructurada. Tras la migración completada (`02_MIGRACION_ARQUITECTURA_PLAN_DETALLADO_COMPLETADO.md`), el proyecto cuenta con:

- ✅ **Un único entrypoint** (`robot` en puerto 8000)
- ✅ **Paquete instalable** via `pyproject.toml`
- ✅ **ManagerBot** con módulos OPS, Enterprise y Agent
- ✅ **Sistema de métricas** Prometheus
- ✅ **Scripts de instalación** cross-platform
- ✅ **Worker async** para tareas pesadas

**Pendiente de implementación**:
- LLM Service (Fase 7)
- Knowledge Base con embeddings (Fase 8)  
- Analytics avanzado (Fase 9)

La arquitectura es sólida y mantenible, siguiendo patrones de industria. El siguiente paso natural sería implementar las fases 7-9 para completar el asistente conversacional con capacidades de NLP.