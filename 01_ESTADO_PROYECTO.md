# ESTADO DEL PROYECTO - ROBOT MANUFACTURERO
Fecha: 2026-03-30
Versión: 2.0

## Estado Canónico
Este documento representa el estado actual auténtico del proyecto robot manufacturero. Documenta la arquitectura real, las capacidades implementadas, las brechas críticas y el plan de evolución del sistema NLP/IA.

---

## Resumen Ejecutivo

El proyecto cuenta con una **arquitectura modular bien estructurada** con componentes enterprise implementados (policy engine, guardrails, planner, tool routing, multi-tenant, billing, audit, monitoring, API pública). Sin embargo, el **sistema NLP es extremadamente débil** - basado únicamente en patrones de palabras clave con confianza limitada, sin capacidad para procesar entrada de voz, sin embeddings contextuales robustos, ni razonamiento multi-paso verdadero.

El estado crítico es que mientras la **gobernanza y orquestación** están avanzadas, el **núcleo de comprensión del lenguaje natural y agencia inteligente** está en fase alpha. La brecha principal es la falta de:
- Procesamiento robusto de lenguaje natural (tokenización, lemmatización, análisis sintáctico profundo)
- Entrada de voz (speech-to-text)
- Embeddings contextuales avanzados (transformers)
- Razonamiento multi-paso con memoria conversacional
- Tools reales integradas y ejecutables

---

## Ventajas Competitivas del Código Actual

### 1. Arquitectura Enterprise (IMPLEMENTADA)
- **Policy Engine**: Control de acceso, cuotas, budgets y guardrails
- **Multi-tenant**: Aislamiento de datos por tenant con soporte Postgres
- **Billing & Audit**: Tracking de uso, eventos y cambios
- **Health Checks & Monitoring**: Métricas de agente, observabilidad
- **API Pública**: Entrypoints canonicos (FastAPI, Telegram, Webhook)
- **Autenticación & Autorización**: Middleware de seguridad

### 2. Integración LLM Flexible
- Soporta OpenAI y Ollama (con fallback automático)
- Factory pattern con caching para eficiencia
- Configuración dinámica por provider
- LLM completamente opcional (fallback a reglas)

### 3. RAG Preparado
- Vector store con Postgres + pgvector (producción-ready)
- Embeddings con sentence-transformers
- Chunking inteligente de documentos
- Búsqueda semántica configurable
- Fallback a memoria local

### 4. Tool Routing & Planner
- Registro centralizado de tools
- Router con policy checking
- Planner con gestión de planes
- Acción executor (aunque incompleto)

### 5. Persistencia & Resilencia
- Postgres + Alembic migrations
- JSON fallback para compatibilidad
- Manejo de errores graceful
- Tests unitarios ya instalados (78+ tests)

### 6. Modularidad Real
- Componentes desacoplados e intercambiables
- Inyección de dependencias
- Interfaces claras entre capas
- Sin lock-in a un single runtime

---

## Brechas Frente a la Proyección

### 1. **NLP - CRÍTICO**
| Componente | Estado Actual | Requerido |
|-----------|---------------|-----------|
| **Tokenización** | Spliteo simple por espacios | Tokenización lingüística con spaCy/NLTK |
| **Normalización** | Limpieza básica | Lemmatización, destemming, caso normalizador |
| **Análisis Sintáctico** | Ninguno implementado | POS tagging, dependencias, parse trees |
| **Named Entity Recognition** | spaCy básico + regex | NER profundo con contexto |
| **Embeddings** | Word vectors estáticos | Embeddings contextuales (BERT, RoBERTa) |
| **Intent Classification** | Patrones regex (50% exactitud) | ML classifier con contexto |
| **Confidence Scoring** | Heurístico simple | ML-based confidence calibration |

### 2. **Speech Input - NO IMPLEMENTADO**
- Sin ASR (Automatic Speech Recognition)
- Sin soporte para audio input
- Sin transcripción a texto
- Requerimientos: Whisper, Google Speech-to-Text, o similar

### 3. **Razonamiento & Agencia - INCOMPLETO**
| Aspecto | Estado | Target |
|--------|--------|--------|
| **Multi-step Reasoning** | Básico (ReAct rule-based) | ReAct + CoT + planning |
| **Memory Conversacional** | Almacenamiento básico | Context window + long-term memory |
| **Tool Execution** | Stubs | Tools reales (search, http, db, compute) |
| **Error Recovery** | Mínimo | Retry logic, fallback strategies |
| **Explanation** | Ninguno | Chain-of-thought explicable |

### 4. **Knowledge Integration - PARCIAL**
- RAG implementado pero sin indexación automática
- Sin sincronización con base de conocimiento viva
- Sin re-ranking semántico
- Sin fusion de RAG + LLM en pipeline

### 5. **Entrenamiento de Modelos - NO IMPLEMENTADO**
- Sin fine-tuning de modelos
- Sin feedback loop de aprendizaje
- Sin dataset de entrenamiento curado
- Sin evaluación de modelos

---

## Inconsistencias Técnicas Detectadas

### 1. **NLP Pipeline vs Reality**
**Problema**: `pipeline.py` describe una arquitectura completa pero muchos componentes retornan valores dummy o placeholders.
- `IntentClassifier` basado solo en regex (máximo 90% confianza)
- `EntityExtractor` depende de spaCy (no siempre disponible)
- `ActionMapper` falla silenciosamente sin feedback

**Línea**: [app/nlp/pipeline.py](app/nlp/pipeline.py#L95-L125) muestra fallback a LLM pero el LLM fallback es inestable.

### 2. **LLM Fallback Poco Confiable**
**Problema**: `_llm_fallback` en pipeline usa `ActionParser._llm_parse()` que puede no estar disponible.
- Sin verificación explícita de disponibilidad LLM
- Sin timeout graceful
- Sin logging de fallos

**Línea**: [app/nlp/pipeline.py](app/nlp/pipeline.py#L155-L165)

### 3. **Razonamiento Demasiado Simplista**
**Problema**: `ReActReasoner` solo usa heurísticas de palabras clave (`_TOOL_HINTS`)
- No usa LLM para razonamiento real
- No genera chain-of-thought
- No explora alternatives

**Línea**: [app/agent/reasoning.py](app/agent/reasoning.py#L30-L60)

### 4. **Tool Execution Incompleto**
**Problema**: `_process_actions_sync` retorna `None` (stubbed out)
- Actions parser existe pero no integrado en flow
- Tool executor existe pero sin tools reales
- No hay ejecución multi-step

**Línea**: [app/agent/core.py](app/agent/core.py#L245-L250)

### 5. **Memory Sin Contexto Conversacional**
**Problema**: Los exchanges se guardan pero no se usan en contexto de razonamiento
- Sin sliding window de contexto
- Sin resumen de conversaciones largas
- Sin extracción de datos relevantes

### 6. **RAG Sin Integración Real**
**Problema**: RAG indexer existe pero sin trigger automático
- Sin carga de documentos automática
- Sin actualización de índices
- Sin soporte para documentos dinámicos

**Línea**: [app/knowledge/indexer.py](app/knowledge/indexer.py) - no se invoca desde pipeline principal

---

## Recomendaciones de Alineación

### CORTO PLAZO (2-4 semanas) - Mejorar NLP Existente

#### Fase 1: Mejorar Tokenización & Normalización
```
Objetivo: Incrementar precisión de NLP de 50% a 75%
Implementación:
  1. Reemplazar spaCy load() lazy con eager + caching
  2. Agregar lemmatización en TokenResult
  3. Mejorar normalización: diacríticos, contracciones, typos
  4. Agregar POS tagging a output
```

#### Fase 2: Mejorar Intent Classification
```
Objetivo: Pasar de regex patterns a ML classifier simple
Implementación:
  1. Entrenar classifier con 50+ ejemplos de cada intent
  2. Usar Naive Bayes o Logistic Regression
  3. Guardar modelo en joblib/pickle
  4. Integrar como primera opción (fallback a regex)
  5. Track precision/recall por intent
```

#### Fase 3: Mejorar Confianza & Fallback
```
Objetivo: Hacer el pipeline más robusto
Implementación:
  1. Calibrar confianza con probabilidades del classifier
  2. Implementar weighted ensemble (regex + ML + LLM)
  3. Timeout robusto para LLM fallback (2s max)
  4. Logging de confidence scores por paso
```

### MEDIANO PLAZO (4-8 semanas) - Agregar Capacidades Críticas

#### Fase 4: Speech-to-Text
```
Objetivo: Soportar entrada de voz
Implementación:
  1. Integrar Whisper (OpenAI) para ASR
  2. Agregar endpoints de audio en webhook
  3. Pipeline: audio → WAV → text → NLP
  4. Cache de transcripciones
```

#### Fase 5: Memory Conversacional Real
```
Objetivo: Mantener contexto en conversaciones largas
Implementación:
  1. Sliding window de últimos N exchanges
  2. Resumen automático para contexto > X tokens
  3. Extracción de facts relevantes
  4. Timeline de eventos mencionados
  5. Referencia handling (pronouns → entities)
```

#### Fase 6: Razonamiento Multi-Step
```
Objetivo: Razonamiento verdadero tipo ReAct
Implementación:
  1. Generar CoT (chain-of-thought) con LLM
  2. Definir plan antes de ejecutar tools
  3. Verificación y corrección de pasos
  4. Max 5 iteraciones con timeout
  5. Explicación final generada
```

### LARGO PLAZO (8-16 semanas) - Evolución Completa

#### Fase 7: Tools Reales
```
Objetivo: Integrar tools ejecutables reales
Herramientas:
  - Búsqueda: DuckDuckGo, Google Search
  - HTTP: GET/POST a APIs externas
  - Cálculo: evaluador seguro de expresiones
  - SQL: queries contra base de datos interna
  - Archivo: lectura/búsqueda en documentos
```

#### Fase 8: Fine-tuning de Modelos
```
Objetivo: Entrenar modelos específicos del dominio
Implementación:
  1. Curar dataset de 500+ ejemplos reales
  2. Fine-tune sentence-transformers para dominio
  3. Entrenar intent classifier específico
  4. Evaluar con F1, precision, recall
```

#### Fase 9: Observabilidad & Analytics
```
Objetivo: Entender comportamiento del sistema
Implementación:
  1. Pipeline de eventos → (SQL + Elasticsearch)
  2. Dashboard de métricas de NLP
  3. Analysis de fallos más comunes
  4. A/B testing de cambios
```

---

## Plan de Implementación Priorizado

```
SEMANA 1-2: Fase 1 (Tokenización) + Fase 2 (ML Classifier)
SEMANA 3-4: Fase 3 (Confianza) + Fase 4 (Speech-to-Text)
SEMANA 5-8: Fase 5 (Memory) + Fase 6 (Razonamiento Multi-step)
SEMANA 9-16: Fase 7 (Tools) + Fase 8 (Fine-tuning) + Fase 9 (Analytics)
```

---

## Métricas de Éxito

| Métrica | Actual | Target (30 días) | Target (90 días) |
|---------|--------|------------------|-----------------|
| Intent Classification Accuracy | 50% | 75% | 90% |
| Entity Extraction F1 | 0.45 | 0.70 | 0.85 |
| Speech-to-Text Support | No | Sí | Optimizado |
| Memory Context Window | 3 msgs | 10 msgs | Dynamic |
| Tools Ejecutables | 0 | 2-3 | 5+ |
| Average Response Time | 2.5s | 2.0s | 1.5s |
| User Satisfaction (NPS) | 30 | 50 | 70+ |

---

## Riesgos & Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|--------|-----------|
| Cambios rompen tests existentes | Alta | Alto | Test-driven development, CI/CD |
| Model training datos insuficientes | Media | Alto | Data augmentation, transfer learning |
| LLM no disponible en producción | Media | Medio | Fallback a heurísticas + cache |
| Performance degradation | Media | Medio | Profiling, benchmarking, optimization |
| User adoption bajo | Baja | Bajo | MVP feedback, iteración rápida |

---

## Conclusión

El proyecto tiene una **excelente base de infraestructura** pero un **núcleo de IA muy débil**. La estrategia es:

1. **Corto plazo**: Fortalecer NLP existente (75% accuracy)
2. **Mediano plazo**: Agregar capacidades críticas (voz, memoria, razonamiento)
3. **Largo plazo**: Especialización con tools reales y fine-tuning

La estimación es **3-4 meses** para alcanzar un sistema robusto, agentic y multi-modal. El costo es principalmente time engineering, no infraestructura.
