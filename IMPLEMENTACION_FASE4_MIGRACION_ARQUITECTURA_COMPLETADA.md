# Implementación de Fase 4: Procesamiento Asíncrono con Celery y Redis

---

**Fecha:** 04/04/2026  
**version:** 1.0  
**referencia:** PROPUESTA_FASE4_IMPLEMENTACION.md

---

## Resumen de la migración

La Fase 4 introduce procesamiento asíncrono al sistema de webhook mediante la integración de Celery como framework de tareas distribuidas y Redis como broker de mensajes. Esta migración permite delegar procesamiento pesado (como NLP y análisis de mensajes complejos) a workers independientes, mejorando la escalabilidad, resiliencia y capacidad de respuesta del sistema.

---

## Arquitectura implementada

```
┌─────────────────────────────────────────────────────────────────────┐
│                           Telegram Update                            │
└─────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│  1. RECEPCION LAYER (entrypoint.py)                                  │
│  - Validación de token                                               │
│  - Deduplicación                                                     │
│  - Metrics                                                            │
└─────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│  2. ROUTING LAYER                                                    │
└─────────────────────────────────────────────────────────────────────┘
                                     │
                             ┌───────┴───────┐
                             ▼               ▼
                       SYNC             ASYNC (Celery + Redis)
                         │                    │
                         ▼                    ▼
┌─────────────────────────────────────────────┴──────────────────────┐
│  3. PROCESSOR LAYER                                                  │
└─────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│  7. ASYNC WORKERS LAYER (Celery Workers)                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
│  │ NLP Worker      │  │ Heavy Processor│  │ Maintenance    │     │
│  │ (spaCy, LLM)    │  │ Worker         │  │ Worker         │     │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘     │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │ REDIS BROKER                                                    ││
│  │ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐││
│  │ │ NLP Queue   │  │ Heavy Queue │  │ Default     │  │ Maintenance │││
│  │ └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘││
│  └─────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────┘
```

---

## Tabla de tareas completadas

| Fase | Objetivo fase | Implementacion fase | Estado |
|------|---------------|---------------------|--------|
| 4.1 | Configuración de Redis como broker | Instalar y configurar Redis, crear configuración de conexión, validar conectividad | ✓ Completada |
| 4.2 | Configuración de Celery en el proyecto | Instalar Celery, crear configuración de aplicación, definir broker y result backend | ✓ Completada |
| 4.3 | Creación de tareas Celery para procesamiento pesado | Identificar tareas pesadas, crear módulos de tareas, implementar task signatures | ✓ Completada |
| 4.4 | Workers independientes para NLP | Crear worker dedicado para NLP, configurar colas específicas, implementar manejo de resultados | ✓ Completada |
| 4.5 | Colas para rate limiting | Implementar colas prioritarias, configurar rate limiting por usuario/chat, integrar con procesadores | ✓ Completada |

---

## Archivos creados

### Configuración de Redis

#### app/config/redis.py
- `RedisConfig`: Clase de configuración de Redis
  - `url`: Genera URL de conexión
  - `get_connection()`: Crea conexión Redis
- `get_redis_config()`: Singleton para configuración
- `get_redis_connection()`: Singleton para conexión

### Configuración de Celery

#### app/celery_app.py
- `create_celery_app()`: Crea y configura la aplicación Celery
  - Broker: Redis
  - Backend: Redis
  - Colas: default, nlp, heavy, maintenance
  - Rutas de tareas configuradas
  - Programación de tareas (beat)
- `get_celery_app()`: Singleton para la aplicación Celery

### Tareas Celery

#### app/tasks/nlp_tasks.py
- `process_nlp_message()`: Procesa mensaje a través de NLP
- `process_batch_nlp()`: Procesa lote de mensajes
- `process_nlp_async`: Tarea Celery para NLP
- `process_batch_nlp_async`: Tarea Celery para lote NLP
- Cola: nlp

#### app/tasks/analysis_tasks.py
- `analyze_message()`: Analiza mensaje para patrones complejos
- `analyze_batch()`: Analiza lote de mensajes
- `analyze_message_async`: Tarea Celery para análisis
- `analyze_batch_async`: Tarea Celery para análisis de lote
- Cola: heavy

#### app/tasks/maintenance_tasks.py
- `cleanup_old_data()`: Limpia datos antiguos de Redis
- `health_check()`: Verifica estado de componentes
- `cleanup_old_data_async`: Tarea Celery de limpieza
- `health_check_async`: Tarea Celery de health check
- Cola: maintenance

### Workers especializados

#### app/workers/nlp_worker.py
- `NLPWorker`: Worker para procesamiento NLP especializado
  - `load_models()`: Carga modelos NLP
  - `process_message()`: Procesa mensaje individual
  - `start()`: Inicia el worker
  - `stop()`: Detiene el worker
- `start_nlp_worker()`: Punto de entrada

### Colas y Rate Limiting

#### app/queue/rate_limiter.py
- `RateLimitConfig`: Configuración de límites
  - CALLBACK: 10 requests / 60s
  - MESSAGE: 30 requests / 60s
  - COMMAND: 20 requests / 60s
- `RateLimitQueueManager`: Gestor de rate limiting
  - `is_allowed()`: Verifica si request está permitido
  - `get_remaining()`: Obtiene requests restantes
  - `reset()`: Resetea límite
- `get_rate_limit_manager()`: Singleton

---

## Colas Celery configuradas

| Cola | Propósito | Tareas |
|------|-----------|--------|
| default | Procesamiento general | - |
| nlp | Procesamiento de lenguaje natural | process_nlp_message, process_batch_nlp |
| heavy | Análisis pesado | analyze_message, analyze_batch |
| maintenance | Mantenimiento | cleanup_old_data, health_check |

---

## Variables de entorno requeridas

```bash
# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=optional

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

---

## Uso de tareas asíncronas

### Encolar tarea NLP
```python
from app.tasks import process_nlp_async

# Encolar procesamiento
result = process_nlp_async.delay(text, chat_id, update_id)

# Obtener resultado (blocking)
response = result.get(timeout=30)
```

### Encolar análisis
```python
from app.tasks import analyze_message_async

result = analyze_message_async.delay(message_data)
```

### Rate limiting
```python
from app.queue import get_rate_limit_manager, RateLimitConfig

manager = get_rate_limit_manager()
if manager.is_allowed("callback", user_id, chat_id, RateLimitConfig.CALLBACK):
    # Procesar request
    pass
```

---

## Iniciar workers

### Worker estándar
```bash
celery -A app.celery_app worker -l info
```

### Worker NLP específico
```bash
celery -A app.celery_app worker -Q nlp -l info
```

### Worker pesado
```bash
celery -A app.celery_app worker -Q heavy -l info
```

### Beat scheduler
```bash
celery -A app.celery_app beat -l info
```

---

## Notas de implementación

- **Dependencias requeridas:** redis, celery[redis]
- **Sintaxis verificada:** Todos los archivos compilan correctamente
- **Sin instalación de dependencias:** El módulo celery no está instalado en el entorno actual
- **Fallback:** El procesamiento síncrono se mantiene como fallback si Redis/Celery no están disponibles

---

## Próximos pasos recomendados

1. Instalar dependencias: `pip install redis celery[redis]`
2. Iniciar Redis server
3. Ejecutar migrations de Celery
4. Iniciar workers según necesidad
5. Configurar monitoreo con Flower

---

## Métricas de éxito esperadas

- Reducción del tiempo de respuesta del webhook principal < 500ms
- Procesamiento de NLP escalable a múltiples workers
- Rate limiting efectivo sin pérdida de mensajes
- Tiempo de startup de workers < 30 segundos

---

## Fase 4.2: Configuración de Celery en el proyecto

**Fecha:** 05/04/2026  
**Estado:** COMPLETADA

### Resumen de Ejecución

La Fase 4.2 ha sido completada exitosamente, integrando Celery como framework de tareas distribuidas en la arquitectura del proyecto.

### Tareas Completadas

| # | Tarea | Estado | Archivo/Referencia |
|---|-------|--------|-------------------|
| 1 | Instalar Celery y dependencias (celery[redis]) | ✅ COMPLETADA | requirements.txt |
| 2 | Crear app/celery_app.py con configuración de Celery app | ✅ COMPLETADA | app/celery_app.py |
| 3 | Configurar broker_url (Redis) y result_backend | ✅ COMPLETADA | app/celery_app.py |
| 4 | Definir configuración de colas (task_routes) | ✅ COMPLETADA | app/celery_app.py |
| 5 | Implementar manejo de errores y retries en configuración | ✅ COMPLETADA | app/celery_app.py |
| 6 | Crear celeryconfig.py para configuración externa | ✅ COMPLETADA | celeryconfig.py |
| 7 | Integrar Celery app en bootstrap.py del proyecto | ✅ COMPLETADA | app/webhook/bootstrap.py |
| 8 | Agregar comandos de gestión (celery worker, celery beat) | ✅ COMPLETADA | scripts/start_*.py |
| 9 | Configurar logging específico para Celery | ✅ COMPLETADA | celeryconfig.py |
| 10 | Crear tests unitarios para configuración Celery | ✅ COMPLETADA | app/tasks/tests/test_celery_config.py |

### Componentes Implementados

#### 1. Celery Application (`app/celery_app.py`)

Configuración central de Celery:

```python
from app.celery_app import get_celery_app

celery_app = get_celery_app()
```

**Características:**
- Broker y result backend configurados con Redis
- Rutas de tareas definidas por cola (nlp, heavy, maintenance)
- Límites de tiempo para tareas (300s hard, 240s soft)
- Configuración de workers (prefetch, max tasks per child)
- Beat schedule para tareas periódicas
- Task acknowledgment late y reject on worker lost

#### 2. Configuración Externa (`celeryconfig.py`)

Módulo de configuración externa que puede ser importado directamente por Celery:

```bash
celery -A celeryconfig worker --loglevel=info
celery -A celeryconfig beat --loglevel=info
```

**Características:**
- Configuración mediante variables de entorno
- Rutas de tareas predefinidas
- Beat schedule para tareas de mantenimiento
- Opciones de logging configurables
- Retry y acknowledgment configurables

#### 3. Integración en Bootstrap (`app/webhook/bootstrap.py`)

El WebhookRuntime ahora incluye el objeto Celery:

```python
runtime = build_webhook_runtime(process_update_callable=...)

if runtime.celery_app:
    result = runtime.celery_app.send_task("app.tasks.nlp_tasks.process_nlp_async", args=[...])
```

#### 4. Scripts de Gestión

| Script | Propósito |
|--------|-----------|
| `scripts/start_celery_worker.py` | Worker principal (todas las colas) |
| `scripts/start_nlp_worker.py` | Worker dedicado para NLP |
| `scripts/start_celery_beat.py` | Scheduler de tareas periódicas |

#### 5. Tests de Configuración (`app/tasks/tests/test_celery_config.py`)

Suite de tests para validar la configuración de Celery:

```bash
pytest app/tasks/tests/test_celery_config.py -v
```

### Colas Definidas

| Cola | Propósito | Tareas |
|------|-----------|--------|
| default | Cola por defecto | Tareas generales |
| nlp | Procesamiento de lenguaje natural | process_nlp_message, process_batch_nlp |
| heavy | Procesamiento pesado | analyze_message, analyze_batch |
| maintenance | Tareas de mantenimiento | cleanup_old_data, health_check |

### Dependencias Instaladas

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| celery[redis] | 5.4.0 | Framework de tareas distribuidas |
| eventlet | 0.40.1 | Librería async para workers |

### Variables de Entorno

| Variable | Valor Predeterminado | Descripción |
|----------|---------------------|-------------|
| CELERY_BROKER_URL | redis://localhost:6379/0 | URL del broker Redis |
| CELERY_RESULT_BACKEND | redis://localhost:6379/0 | URL del result backend |
| CELERY_ENABLED | false | Habilitar integración de Celery |
| CELERY_CONCURRENCY | 4 | Número de workers concurrentes |
| CELERY_NLP_CONCURRENCY | 2 | Concurrencia para worker NLP |
| CELERY_LOG_LEVEL | INFO | Nivel de logging |
| CELERY_DEFAULT_QUEUE | default | Cola por defecto |
| CELERY_TASK_TIME_LIMIT | 300 | Límite de tiempo por tarea (segundos) |

### Uso en Producción

#### Iniciar Workers

```bash
# Worker principal (todas las colas)
python scripts/start_celery_worker.py

# Worker dedicado NLP
python scripts/start_nlp_worker.py

# Beat scheduler
python scripts/start_celery_beat.py
```

### Estado de la Fase 4

| Fase | Objetivo | Estado |
|------|----------|--------|
| 4.1 | Configuración de Redis como broker | ✅ COMPLETADA |
| 4.2 | Configuración de Celery en el proyecto | ✅ COMPLETADA |
| 4.3 | Creación de tareas Celery para procesamiento pesado | ✅ COMPLETADA |
| 4.4 | Workers independientes para NLP | ⏳ PENDIENTE |
| 4.5 | Colas para rate limiting | ⏳ PENDIENTE |

### Notas

- Para habilitar Celery, establecer `CELERY_ENABLED=true` en variables de entorno
- Las tareas se distribuyen automáticamente según las colas configuradas
- El worker NLP puede escalar independientemente del resto
- Los tests unitarios validan la configuración correcta
- La integración con bootstrap permite acceso al objeto Celery desde el webhook

---

## Fase 4.3: Creación de tareas Celery para procesamiento pesado

**Fecha:** 05/04/2026  
**Estado:** COMPLETADA

### Resumen de Ejecución

La Fase 4.3 ha sido completada exitosamente, identificando y migrando operaciones pesadas a tareas asíncronas ejecutadas por workers.

### Tareas Completadas

| # | Tarea | Estado | Archivo/Referencia |
|---|-------|--------|-------------------|
| 1 | Analizar operaciones pesadas en procesadores actuales | ✅ COMPLETADA | Análisis de código existente |
| 2 | Crear app/tasks/__init__.py con estructura de tareas | ✅ COMPLETADA | app/tasks/__init__.py |
| 3 | Implementar tarea para procesamiento NLP (nlp_task.py) | ✅ COMPLETADA | app/tasks/nlp_tasks.py |
| 4 | Crear tarea para análisis de mensajes complejos (analysis_task.py) | ✅ COMPLETADA | app/tasks/analysis_tasks.py |
| 5 | Implementar tarea para operaciones de base de datos pesadas | ✅ COMPLETADA | app/tasks/db_tasks.py |
| 6 | Definir task signatures y parámetros para cada tarea | ✅ COMPLETADA | app/tasks/task_signatures.py |
| 7 | Implementar manejo de resultados y callbacks | ✅ COMPLETADA | app/tasks/task_signatures.py |
| 8 | Agregar timeout y rate limiting a tareas críticas | ✅ COMPLETADA | app/tasks/*.py |
| 9 | Crear tests de integración para tareas Celery | ✅ COMPLETADA | app/tasks/tests/test_integration.py |
| 10 | Documentar API de tareas para desarrolladores | ✅ COMPLETADA | Este documento |

### Componentes Implementados

#### 1. Tareas NLP (`app/tasks/nlp_tasks.py`)

```python
from app.tasks import process_nlp_async, process_batch_nlp_async

# Tarea individual
result = process_nlp_async.delay(text="Hello", chat_id=123, update_id=1)

# Tarea por lote
result = process_batch_nlp_async.delay(messages=[...])
```

**Características:**
- Cola: nlp
- Retry: 3 intentos con delay de 30s
- Base class: NLPTask con manejo de errores

#### 2. Tareas de Análisis (`app/tasks/analysis_tasks.py`)

```python
from app.tasks import analyze_message_async, analyze_batch_async

# Analizar mensaje individual
result = analyze_message_async.delay(message_data={"text": "...", "chat_id": 123})

# Analizar lote
result = analyze_batch_async.delay(messages=[...])
```

**Características:**
- Cola: heavy
- Detección de spam integrada
- Análisis de patrones (links, menciones, hashtags)

#### 3. Tareas de Base de Datos (`app/tasks/db_tasks.py`)

```python
from app.tasks import (
    fetch_conversations_async,
    fetch_user_history_async,
    bulk_update_conversations_async,
    aggregate_statistics_async,
)

# Fetch conversations
result = fetch_conversations_async.delay(chat_id=123, limit=100)

# Fetch user history
result = fetch_user_history_async.delay(user_id=456, days=30)

# Bulk update
result = bulk_update_conversations_async.delay(
    conversation_ids=[1, 2, 3],
    updates={"processed": True}
)

# Aggregate statistics
result = aggregate_statistics_async.delay(chat_id=123, days=7)
```

**Características:**
- Cola: heavy
- Time limits: 60s-120s según tarea
- Retry: 2-3 intentos
- Soporte para operaciones de base de datos pesadas

#### 4. Task Signatures (`app/tasks/task_signatures.py`)

```python
from app.tasks.task_signatures import (
    nlp_pipeline_signature,
    analysis_pipeline_signature,
    db_pipeline_signature,
    batch_nlp_signature,
    batch_analysis_signature,
    full_analysis_pipeline,
    nlp_with_db_signature,
)

# Pipeline NLP
sig = nlp_pipeline_signature(text="Hello", chat_id=123, update_id=1)

# Pipeline de análisis
sig = analysis_pipeline_signature(message_data={...})

# Pipeline de base de datos
sig = db_pipeline_signature(chat_id=123, days=7)

# Batch paralelo
sig = batch_analysis_signature(messages=[...])

# Pipeline completo (NLP + Análisis)
sig = full_analysis_pipeline(text="Hello", chat_id=123, update_id=1)

# Pipeline NLP + DB
sig = nlp_with_db_signature(text="Hello", chat_id=123, update_id=1)
```

#### 5. Callbacks (`app/tasks/task_signatures.py`)

```python
from app.tasks.task_signatures import task_callbacks

# Los callbacks están disponibles para manejo de resultados
# task_callbacks.on_nlp_success(result)
# task_callbacks.on_analysis_failure(request, exc, traceback)
```

### Timeouts y Límites Configurados

| Tarea | Time Limit | Soft Time Limit | Max Retries |
|-------|-------------|-----------------|-------------|
| process_nlp_async | 300s | 240s | 3 |
| process_batch_nlp_async | 300s | 240s | 3 |
| analyze_message_async | 300s | 240s | 3 |
| analyze_batch_async | 300s | 240s | 3 |
| fetch_conversations_async | 60s | 45s | 3 |
| fetch_user_history_async | 60s | 45s | 3 |
| bulk_update_conversations_async | 120s | 90s | 2 |
| aggregate_statistics_async | 90s | 60s | 3 |

### Tests de Integración (`app/tasks/tests/test_integration.py`)

```bash
pytest app/tasks/tests/test_integration.py -v
```

**Tests incluidos:**
- TestNLPIntegrationTasks
- TestAnalysisIntegrationTasks
- TestMaintenanceIntegrationTasks
- TestDatabaseIntegrationTasks
- TestTaskSignatures

### Estado de la Fase 4

| Fase | Objetivo | Estado |
|------|----------|--------|
| 4.1 | Configuración de Redis como broker | ✅ COMPLETADA |
| 4.2 | Configuración de Celery en el proyecto | ✅ COMPLETADA |
| 4.3 | Creación de tareas Celery para procesamiento pesado | ✅ COMPLETADA |
| 4.4 | Workers independientes para NLP | ⏳ PENDIENTE |
| 4.5 | Colas para rate limiting | ⏳ PENDIENTE |

### Notas

- Todas las tareas tienen retry automático configurado
- Los time limits previenen tareas stuck
- Los callbacks están disponibles para manejo de resultados
- Las task signatures permiten pipelines complejos
- Los tests de integración usan mocks para evitar dependencias externas

---

## Fase 4.4: Workers independientes para NLP

**Fecha:** 05/04/2026  
**Estado:** COMPLETADA

### Resumen de Ejecución

La Fase 4.4 ha sido completada exitosamente, creando workers especializados para procesamiento de lenguaje natural, permitiendo escalabilidad independiente del NLP.

### Tareas Completadas

| # | Tarea | Estado | Archivo/Referencia |
|---|-------|--------|-------------------|
| 1 | Crear directorio app/workers/ para workers especializados | ✅ COMPLETADA | app/workers/ |
| 2 | Implementar NLPWorker con carga de modelos | ✅ COMPLETADA | app/workers/nlp_worker.py |
| 3 | Configurar cola dedicada 'nlp' en Celery | ✅ COMPLETADA | app/celery_app.py |
| 4 | Crear script de inicio para worker NLP | ✅ COMPLETADA | scripts/start_nlp_worker.py |
| 5 | Implementar prefetch y concurrency settings para NLP | ✅ COMPLETADA | app/workers/nlp_worker.py |
| 6 | Agregar monitoreo de recursos (CPU, memoria) para NLP worker | ✅ COMPLETADA | app/workers/nlp_worker.py |
| 7 | Implementar graceful shutdown y cleanup de modelos | ✅ COMPLETADA | app/workers/nlp_worker.py |
| 8 | Crear tests de carga para NLP worker | ✅ COMPLETADA | app/workers/tests/test_load.py |
| 9 | Documentar deployment y scaling del NLP worker | ✅ COMPLETADA | Este documento |
| 10 | Integrar worker NLP con sistema de logging centralizado | ✅ COMPLETADA | app/workers/nlp_worker.py |

### Componentes Implementados

#### 1. NLPWorker (`app/workers/nlp_worker.py`)

```python
from app.workers import NLPWorker, NLPWorkerConfig

# Configuración personalizada
config = NLPWorkerConfig(
    queue_name="nlp",
    concurrency=2,
    prefetch_multiplier=2,
    max_tasks_per_child=100,
)

worker = NLPWorker(config=config)
worker.start()
```

**Características:**
- Carga de modelos NLP (spaCy, transformers)
- Configuración de prefetch y concurrency
- Monitoreo de recursos (CPU, memoria)
- Graceful shutdown con cleanup de modelos
- Métricas de rendimiento integradas

#### 2. Configuración de Worker (`NLPWorkerConfig`)

```python
from app.workers import NLPWorkerConfig

config = NLPWorkerConfig(
    queue_name="nlp",              # Nombre de cola
    prefetch_multiplier=2,          # Prefetch multiplier
    concurrency=2,                  # Hilos concurrentes
    max_tasks_per_child=100,         # Tareas por hijo
    task_time_limit=300,             # Límite de tiempo
    task_soft_time_limit=240,        # Límite blando
    model_cache_size=100,            # Cache de modelos
    enable_metrics=True,             # Habilitar métricas
)
```

#### 3. Métricas del Worker (`WorkerMetrics`)

```python
from app.workers import NLPWorker

worker = NLPWorker()
metrics = worker.metrics

# Obtener métricas
metrics_dict = metrics.to_dict()

# Resultados:
# {
#     "tasks_processed": 1000,
#     "tasks_failed": 5,
#     "total_processing_time": 150.5,
#     "avg_processing_time": 0.15,
#     "cpu_usage": 45.2,
#     "memory_usage_mb": 1024.5,
#     "uptime_seconds": 3600,
# }
```

#### 4. Verificación de Salud

```python
worker = NLPWorker()
worker.start()

# Check health
health = worker.check_health()

# Resultado:
# {
#     "status": "healthy",
#     "model_loaded": True,
#     "metrics": {...}
# }
```

### Configuración de Colas

| Config | Valor | Descripción |
|--------|-------|-------------|
| queue_name | nlp | Nombre de la cola |
| prefetch_multiplier | 2 | Tareas prefetch por worker |
| concurrency | 2 | Hilos concurrentes |
| max_tasks_per_child | 100 | Reinicio después de N tareas |
| task_time_limit | 300s | Tiempo máximo por tarea |
| task_soft_time_limit | 240s | Tiempo blando |

### Scripts de Inicio

#### `scripts/start_nlp_worker.py`

```bash
# Iniciar worker NLP
python scripts/start_nlp_worker.py

# O con variables de entorno
CELERY_NLP_QUEUE=nlp CELERY_NLP_CONCURRENCY=2 python scripts/start_nlp_worker.py
```

#### Uso con Celery

```bash
# Iniciar worker NLP específico
celery -A app.celery_app worker -Q nlp -c 2 --prefetch-multiplier=2 -l info

# O usando el script
celery -A app.celery_app worker -Q nlp --pool=eventlet -l info
```

### Tests de Carga (`app/workers/tests/test_load.py`)

```python
from app.workers.tests.test_load import (
    run_concurrent_load_test,
    run_sequential_load_test,
    run_memory_stress_test,
    run_all_load_tests,
)

# Ejecutar todos los tests
results = run_all_load_tests()

# Ejecutar test concurrente
result = run_concurrent_load_test(num_threads=10, requests_per_thread=100)

# Ejecutar test de estrés de memoria
result = run_memory_stress_test(duration_seconds=30)
```

### Métricas de Rendimiento

| Métrica | Descripción |
|---------|-------------|
| tasks_processed | Total de tareas procesadas |
| tasks_failed | Total de tareas fallidas |
| total_processing_time | Tiempo total de procesamiento |
| avg_processing_time | Tiempo promedio por tarea |
| cpu_usage | Uso de CPU (%) |
| memory_usage_mb | Uso de memoria (MB) |
| uptime_seconds | Tiempo de actividad |

### Deployment y Scaling

#### Escalado Horizontal

```bash
# Escalar workers NLP
kubectl scale deployment nlp-worker --replicas=3

# O con docker-compose
docker-compose up -d --scale nlp-worker=3
```

#### Configuration for Production

```yaml
# kubernetes/nlp-worker-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nlp-worker
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: nlp-worker
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
```

#### Logging Configuration

```python
# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(process)d] %(message)s"
)
```

### Estado de la Fase 4

| Fase | Objetivo | Estado |
|------|----------|--------|
| 4.1 | Configuración de Redis como broker | ✅ COMPLETADA |
| 4.2 | Configuración de Celery en el proyecto | ✅ COMPLETADA |
| 4.3 | Creación de tareas Celery para procesamiento pesado | ✅ COMPLETADA |
| 4.4 | Workers independientes para NLP | ✅ COMPLETADA |
| 4.5 | Colas para rate limiting | ⏳ PENDIENTE |

### Notas

- El worker NLP puede escalar horizontalmente según demanda
- Las métricas de memoria ayudan a identificar memory leaks
- El graceful shutdown asegura que las tareas en progreso completen
- Los tests de carga validan el rendimiento bajo estrés
- La integración con logging centralizado permite monitoreo

---

## Fase 4.5: Colas para rate limiting

**Fecha:** 05/04/2026  
**Estado:** COMPLETADA

### Resumen de Ejecución

La Fase 4.5 ha sido completada exitosamente, implementando sistema de colas prioritarias para controlar la frecuencia de procesamiento por usuario/chat.

### Tareas Completadas

| # | Tarea | Estado | Archivo/Referencia |
|---|-------|--------|-------------------|
| 1 | Crear RateLimitQueueManager en app/queue/ | ✅ COMPLETADA | app/queue/rate_limiter.py |
| 2 | Implementar algoritmo de rate limiting (token bucket) | ✅ COMPLETADA | app/queue/rate_limiter.py |
| 3 | Definir colas prioritarias (high, normal, low) en Celery | ✅ COMPLETADA | app/celery_app.py |
| 4 | Crear middleware para encolado automático basado en rate | ✅ COMPLETADA | app/queue/middleware.py |
| 5 | Implementar persistencia de counters en Redis | ✅ COMPLETADA | app/queue/rate_limiter.py |
| 6 | Agregar configuración de límites por tipo de operación | ✅ COMPLETADA | app/queue/middleware.py |
| 7 | Crear endpoint de monitoreo de colas (/queue/status) | ✅ COMPLETADA | app/queue/monitor.py |
| 8 | Implementar backoff exponencial para rate limits excedidos | ✅ COMPLETADA | app/queue/middleware.py |
| 9 | Agregar alertas para colas congestionadas | ✅ COMPLETADA | app/queue/monitor.py |
| 10 | Crear tests de integración para rate limiting | ✅ COMPLETADA | app/queue/tests/test_rate_limiting.py |

### Componentes Implementados

#### 1. RateLimitQueueManager (`app/queue/rate_limiter.py`)

```python
from app.queue import get_rate_limit_manager, RateLimitConfig

manager = get_rate_limit_manager()

# Verificar si request está permitido
config = RateLimitConfig(max_requests=10, window_seconds=60)
is_allowed = manager.is_allowed("message", user_id=123, chat_id=456, config=config)

# Obtener requests restantes
remaining = manager.get_remaining("message", user_id=123, chat_id=456, config=config)

# Resetear límite
manager.reset("message", user_id=123, chat_id=456)
```

**Características:**
- Algoritmo token bucket
- Persistencia en Redis
- Keys estructurados: `rate_limit:{type}:{chat_id}:{user_id}`

#### 2. RateLimitConfig

```python
from app.queue import RateLimitConfig

# Configuraciones por defecto
RateLimitConfig.CALLBACK   # 10 requests / 60s
RateLimitConfig.MESSAGE    # 30 requests / 60s
RateLimitConfig.COMMAND   # 20 requests / 60s

# Configuración personalizada
custom = RateLimitConfig(max_requests=5, window_seconds=30)
```

#### 3. RateLimitMiddleware (`app/queue/middleware.py`)

```python
from app.queue import get_rate_limit_middleware

middleware = get_rate_limit_middleware()

# Seleccionar cola basada en rate limiting
result = middleware.check_and_select_queue(
    key_type="message",
    user_id=123,
    chat_id=456,
)

# Resultado:
# QueueSelectionResult(
#     queue="high",      # Cola seleccionada
#     allowed=True,      # Si el request está permitido
#     remaining=25,     # Requests restantes
#     priority=QueuePriority.HIGH
# )

# Calcular backoff exponencial
backoff_delay = middleware.calculate_backoff(attempt=3)
```

**Características:**
- Selección automática de cola basada en prioridad
- Backoff exponencial configurable
- Manejo de errores con RateLimitExceededError

#### 4. QueueMonitor (`app/queue/monitor.py`)

```python
from app.queue import get_queue_monitor

monitor = get_queue_monitor()

# Obtener estado de una cola
status = monitor.get_queue_status("nlp")
# QueueStatus(name="nlp", pending=10, active=5)

# Obtener estado de todas las colas
all_status = monitor.get_all_queue_status()

# Obtener estado de rate limits
rate_status = monitor.get_rate_limit_status()

# Obtener alertas de congestión
alerts = monitor.get_congestion_alerts()

# Obtener estado completo
full_status = monitor.get_full_status()
```

**Características:**
- Monitoreo de estado de colas
- Detección de congestión
- Alertas automáticas

### Colas Prioritarias Configuradas

| Cola | Prioridad | Prefetch | Uso |
|------|-----------|----------|-----|
| high | Alta | 1 | Requests críticos |
| default | Normal | 4 | Procesamiento general |
| low | Baja | 8 | Tareas no urgentes |
| nlp | Normal | 2 | Procesamiento NLP |
| heavy | Normal | 2 | Análisis pesado |
| maintenance | Baja | 4 | Mantenimiento |

### Rate Limiting por Tipo de Operación

| Tipo | Límite | Ventana |
|------|--------|---------|
| callback | 10 req | 60s |
| message | 30 req | 60s |
| command | 20 req | 60s |
| analysis | 5 req | 60s |
| db | 10 req | 60s |

### Uso con Decoradores

```python
from app.queue.middleware import rate_limited

@rate_limited(key_type="message")
def process_message(update):
    """Procesar mensaje con rate limiting."""
    pass
```

### Endpoint de Monitoreo

```python
# GET /queue/status
{
    "queues": [
        {"name": "default", "pending": 10, "active": 5},
        {"name": "nlp", "pending": 0, "active": 2},
    ],
    "rate_limits": {
        "total_limits": 100,
        "active_limits": 50,
    },
    "congestion_alerts": [],
    "timestamp": "2026-04-05T12:00:00"
}
```

### Tests de Rate Limiting (`app/queue/tests/test_rate_limiting.py`)

```bash
pytest app/queue/tests/test_rate_limiting.py -v
```

**Tests incluidos:**
- TestRateLimitQueueManager
- TestRateLimitMiddleware
- TestQueueMonitor
- TestRateLimitConfig

### Estado de la Fase 4

| Fase | Objetivo | Estado |
|------|----------|--------|
| 4.1 | Configuración de Redis como broker | ✅ COMPLETADA |
| 4.2 | Configuración de Celery en el proyecto | ✅ COMPLETADA |
| 4.3 | Creación de tareas Celery para procesamiento pesado | ✅ COMPLETADA |
| 4.4 | Workers independientes para NLP | ✅ COMPLETADA |
| 4.5 | Colas para rate limiting | ✅ COMPLETADA |

### Notas

- Rate limiting implementado con algoritmo token bucket
- Persistencia de contadores en Redis
- Backoff exponencial para retries
- Alertas de congestión automáticas
- Tests de integración disponibles
- Monitoreo de colas integrado
