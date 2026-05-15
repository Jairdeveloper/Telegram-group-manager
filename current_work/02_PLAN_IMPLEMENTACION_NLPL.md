# PLAN DETALLADO DE EVOLUCIÓN NLP - ROBOT MANUFACTURERO

Fecha: 2026-03-30
Versión: 1.0
Referencia: `01_ESTADO_PROYECTO.md`

---

## Resumen de la Migración

Se propone evolucionar el sistema NLP de **modelo basado en patrones regex** a **arquitectura híbrida robusta** que combine:
- Machine Learning classifier para intent detection
- Análisis lingüístico profundo (POS, dependencias, NER)
- Embeddings contextuales para similaridad semántica
- Memory conversacional con context window
- Razonamiento multi-step real con LLM
- Speech-to-Text para entrada de voz

**Impacto esperado:**
- Intent accuracy: 50% → 75% → 90%
- Cobertura de entrada: Texto → Voz + Texto
- Latencia: 2.5s → 2.0s (optimizado)
- Mantenibilidad: ↑↑ (código más limpio)

---

## Arquitectura Final

```
┌─────────────────────────────────────────────────────────────┐
│                    INPUT LAYER                              │
├─────────────────┬─────────────────┬──────────────────────────┤
│  Text Input     │  Speech Input    │   Context Input         │
│  (Telegram)     │  (Whisper API)   │   (Memory, Tenant)      │
└────────┬────────┴────────┬─────────┴──────────────────┬──────┘
         │                 │                             │
         └─────────────────┼─────────────────────────────┘
                           ▼
         ┌─────────────────────────────────────┐
         │   TEXT PREPROCESSING LAYER          │
         ├─────────────────────────────────────┤
         │ ✓ Tokenization (spaCy)              │
         │ ✓ Normalization (diacríticos, case)│
         │ ✓ Lemmatization                    │
         │ ✓ POS Tagging                      │
         │ ✓ Dependency Parsing                │
         └────────────┬────────────────────────┘
                      ▼
    ┌──────────────────────────────────────┐
    │   SEMANTIC UNDERSTANDING LAYER       │
    ├──────────────────────────────────────┤
    │ ┌────────────────────────────────┐  │
    │ │ Intent Classification          │  │
    │ │  - ML Classifier (primary)     │  │
    │ │  - Regex Fallback              │  │
    │ │  - LLM Fallback (confidence<.5)│  │
    │ └────────────────────────────────┘  │
    │ ┌────────────────────────────────┐  │
    │ │ Entity Recognition             │  │
    │ │  - spaCy NER                   │  │
    │ │  - Custom entity patterns      │  │
    │ │  - Contextual disambiguation   │  │
    │ └────────────────────────────────┘  │
    │ ┌────────────────────────────────┐  │
    │ │ Similarity & Relevance         │  │
    │ │  - Embeddings (sentence-bert)  │  │
    │ │  - Semantic similarity scores  │  │
    │ └────────────────────────────────┘  │
    └────────────┬─────────────────────────┘
                 ▼
    ┌──────────────────────────────────────┐
    │     CONTEXT & MEMORY LAYER           │
    ├──────────────────────────────────────┤
    │ • Conversation History (10 msgs)    │
    │ • Extracted Facts & Entities        │
    │ • User Profile & Preferences        │
    │ • Domain-specific Context           │
    └────────────┬─────────────────────────┘
                 ▼
    ┌──────────────────────────────────────┐
    │      REASONING LAYER (ReAct)         │
    ├──────────────────────────────────────┤
    │ 1. Thought (LLM reflection)          │
    │ 2. Action (select tool)              │
    │ 3. Observation (execute & observe)   │
    │ 4. Feedback loop (max 5 iterations)  │
    └────────────┬─────────────────────────┘
                 ▼
    ┌──────────────────────────────────────┐
    │       TOOL EXECUTION LAYER           │
    ├──────────────────────────────────────┤
    │ • Search Tools (DuckDuckGo)          │
    │ • HTTP Tools (API calls)             │
    │ • Compute Tools (evaluacion)         │
    │ • Database Tools (SQL queries)       │
    │ • File Tools (Document search)       │
    │ • RAG Tools (Knowledge retrieval)    │
    └────────────┬─────────────────────────┘
                 ▼
    ┌──────────────────────────────────────┐
    │       RESPONSE GENERATION LAYER      │
    ├──────────────────────────────────────┤
    │ • LLM-based generation with context  │
    │ • Template-based fallback            │
    │ • Explanation generation (CoT)       │
    │ • Response validation & formatting   │
    └────────────┬─────────────────────────┘
                 ▼
         ┌──────────────────┐
         │    OUTPUT        │
         │  Response + Meta │
         └──────────────────┘
```

---

## Tabla de Tareas

### FASE 1: Tokenización & Normalización Mejorada (Semanas 1-2)

| ID | Tarea | Prioridad | Asignee | Estimación | Status |
|---|---|---|---|---|---|
| T1.1 | Mejorar normalización: diacríticos, contracciones | Alta | - | 2d | TODO |
| T1.2 | Implementar lemmatización con spaCy | Alta | - | 2d | TODO |
| T1.3 | Agregar POS tagging a TokenizationResult | Alta | - | 1d | TODO |
| T1.4 | Implementar dependency parsing | Media | - | 2d | TODO |
| T1.5 | Crear cache de modelos spaCy | Media | - | 1d | TODO |
| T1.6 | Tests unitarios para tokenización | Alta | - | 2d | TODO |
| T1.7 | Benchmark de performance | Media | - | 1d | TODO |

**Deliverables:**
- `app/nlp/tokenizer.py` mejorada con lemmatización y POS
- `app/nlp/normalizer.py` refactorizada con más reglas
- Tests de cobertura 85%+
- Benchmark report

**Definición de Completado:**
```python
# Antes
TokenizationResult(
  tokens=['cambiar', 'bienvenida'],
  pos_tags=[('cambiar', 'VERB'), ('bienvenida', 'NOUN')],
  lemmas=['cambiar', 'bienvenida']
)

# Después (con mejoras)
TokenizationResult(
  tokens=['cambiar', 'bienvenida'],
  pos_tags=[('cambiar', 'VERB'), ('bienvenida', 'NOUN')],
  lemmas=['cambiar', 'bienvenido'],  # Lemmatización correcta
  deps=['nsubj', 'dobj'],            # Dependencias
  has_action=True,
  action_type='set_welcome'          # Early intent hint
)
```

---

### FASE 2: Machine Learning Intent Classifier (Semanas 2-3)

| ID | Tarea | Prioridad | Asignee | Estimación | Status |
|---|---|---|---|---|---|
| T2.1 | Curar dataset de 50+ ejemplos por intent | Alta | - | 3d | TODO |
| T2.2 | Implementar ML classifier (Logistic Regression) | Alta | - | 3d | TODO |
| T2.3 | Feature engineering (TF-IDF, embeddings) | Alta | - | 2d | TODO |
| T2.4 | Train/test split y validación cruzada | Alta | - | 2d | TODO |
| T2.5 | Guardar modelo en joblib | Media | - | 1d | TODO |
| T2.6 | A/B test: Regex vs ML vs Ensemble | Media | - | 2d | TODO |
| T2.7 | Confidence calibration (Platt scaling) | Media | - | 2d | TODO |
| T2.8 | Tests de regression | Alta | - | 1d | TODO |

**Deliverables:**
- Dataset curado: `data/intent_training_data.json`
- Modelo entrenado: `models/intent_classifier.joblib`
- Feature extractor: `app/nlp/features.py`
- Evaluación: `reports/intent_classifier_eval.md`

**Métricas de Éxito:**
```
Intent Accuracy: >= 75%
Precision: >= 0.80
Recall: >= 0.70
F1-Score: >= 0.75
```

**Comparativa:**
```
┌────────────────────┬──────────┬───────────┬────────┐
│ Método             │ Accuracy │ Inference │ Recall │
├────────────────────┼──────────┼───────────┼────────┤
│ Regex (baseline)   │ 50%      │ 10ms      │ 45%    │
│ ML (new)           │ 78%      │ 25ms      │ 75%    │
│ Ensemble           │ 82%      │ 40ms      │ 80%    │
└────────────────────┴──────────┴───────────┴────────┘
```

---

### FASE 3: Confianza & Fallback Robusto (Semana 3)

| ID | Tarea | Prioridad | Asignee | Estimación | Status |
|---|---|---|---|---|---|
| T3.1 | Implementar confidence calibration | Alta | - | 2d | TODO |
| T3.2 | Crear weighted ensemble (regex + ML + LLM) | Media | - | 2d | TODO |
| T3.3 | LLM fallback timeout robusto (2s max) | Alta | - | 1d | TODO |
| T3.4 | Logging de confidence scores | Media | - | 1d | TODO |
| T3.5 | Monitoring de fallback rate | Media | - | 1d | TODO |
| T3.6 | Tests de robustez | Alta | - | 2d | TODO |

**Implementación:**
```python
# Pipeline de confianza

confidence_scores = {
    'regex': classify_regex(text),        # 0.0-0.9
    'ml': classify_ml(text),               # 0.0-1.0 con probs
    'llm': classify_llm(text) if confidence<0.5 else None
}

# Ensemble weighted
final_confidence = (
    0.5 * confidence_scores['regex'] +
    0.5 * confidence_scores['ml']
)

if final_confidence < 0.5:
    attempt_llm_with_timeout(2.0)
```

**Deliverables:**
- Ensemble implementation
- Confidence calibration report
- Monitoring dashboard

---

### FASE 4: Speech-to-Text (Semanas 3-4)

| ID | Tarea | Prioridad | Asignee | Estimación | Status |
|---|---|---|---|---|---|
| T4.1 | Integrar Whisper API (OpenAI) | Alta | - | 2d | TODO |
| T4.2 | Audio preprocessing (noise reduction) | Media | - | 2d | TODO |
| T4.3 | Agregar endpoints de audio en webhook | Alta | - | 2d | TODO |
| T4.4 | Pipeline audio → WAV → text → NLP | Alta | - | 2d | TODO |
| T4.5 | Cache de transcripciones | Media | - | 1d | TODO |
| T4.6 | Tests de E2E con audio | Alta | - | 2d | TODO |
| T4.7 | Language detection automático | Media | - | 1d | TODO |

**Arquitectura:**
```
Audio Input
    ↓
┌─────────────────────┐
│ Audio Processing    │
│ - Format check      │
│ - Noise reduction   │
│ - Normalization     │
└────────┬────────────┘
         ↓
┌─────────────────────┐
│ Whisper API Call    │
│ - Chunking (25MB)   │
│ - Language detect   │
│ - Timeout (30s)     │
└────────┬────────────┘
         ↓
┌─────────────────────┐
│ Caching             │
│ - Hash audio        │
│ - Redis/DB store    │
└────────┬────────────┘
         ↓
Text ─→ NLP Pipeline
```

**Deliverables:**
- `app/audio/processor.py` - Audio processing
- `app/audio/transcriber.py` - Whisper integration
- `app/webhook/audio_handler.py` - Audio endpoint
- Tests y benchmarks

**Métricas:**
- WER (Word Error Rate): < 10%
- Latency: < 5s para audio 30s
- Accuracy: >= 95%

---

### FASE 5: Memory Conversacional (Semanas 4-5)

| ID | Tarea | Prioridad | Asignee | Estimación | Status |
|---|---|---|---|---|---|
| T5.1 | Implementar conversation history buffer | Alta | - | 2d | TODO |
| T5.2 | Sliding window context (últimos 10 msgs) | Alta | - | 1d | TODO |
| T5.3 | Resumen automático para contexto largo | Media | - | 2d | TODO |
| T5.4 | Extracción de facts relevantes | Media | - | 2d | TODO |
| T5.5 | Timeline de eventos | Media | - | 1d | TODO |
| T5.6 | Referencia resolution (pronouns → entities) | Media | - | 2d | TODO |
| T5.7 | Tests de coherencia conversacional | Alta | - | 2d | TODO |

**Implementación:**
```python
class ConversationMemory:
    """Mantiene contexto conversacional de sesión"""
    
    def __init__(self, max_messages=10):
        self.history: List[Message] = []
        self.max_messages = max_messages
        self.facts: Dict[str, Any] = {}
        self.timeline: List[Event] = []
    
    def add_exchange(self, user_msg, bot_response):
        # Sliding window
        if len(self.history) >= self.max_messages:
            self.history.pop(0)
        
        # Extrem facts
        facts = extract_facts(user_msg)
        self.facts.update(facts)
        
        # Timeline
        self.timeline.append(Event(timestamp, msg))
        
        # Resolve references
        resolved = resolve_pronouns(user_msg, self.facts)
        
    def get_context(self, for_llm=False):
        if for_llm:
            return render_context_for_llm(self.history, self.facts)
        return {
            'recent': self.history[-5:],
            'facts': self.facts,
            'timeline': self.timeline
        }
```

---

### FASE 6: Razonamiento Multi-Step (Semanas 5-6)

| ID | Tarea | Prioridad | Asignee | Estimación | Status |
|---|---|---|---|---|---|
| T6.1 | Chain-of-Thought generation con LLM | Alta | - | 3d | TODO |
| T6.2 | Plan generator antes de tool execution | Alta | - | 2d | TODO |
| T6.3 | Step verification y correction | Media | - | 2d | TODO |
| T6.4 | Max 5 iteraciones con timeout | Alta | - | 1d | TODO |
| T6.5 | Explicación final estructurada | Media | - | 2d | TODO |
| T6.6 | Tests de razonamiento complejo | Alta | - | 3d | TODO |
| T6.7 | Benchmarking de reasoning | Media | - | 1d | TODO |

**Flujo ReAct Mejorado:**
```
Entrada: "¿Cuál es la capital de Francia?"
         + Contexto de conversación

↓

PASO 1: Think
Prompt: "Reflexiona sobre cómo responder"
LLM Output: "Necesito datos de geografía, puedo usar búsqueda"

↓

PASO 2: Act
Seleccionar tool: search_tool("capital de Francia")

↓

PASO 3: Observe
Resultado: "París es la capital de Francia"

↓

PASO 4: Reflect
¿Es respuesta adecuada? Sí → Return
¿Necesita más info? No

↓

PASO 5: Generate Response
"La capital de Francia es París."
```

---

### FASE 7: Tools Reales (Semanas 6-8)

| ID | Tarea | Prioridad | Asignee | Estimación | Status |
|---|---|---|---|---|---|
| T7.1 | Search Tool (DuckDuckGo API) | Alta | - | 3d | TODO |
| T7.2 | HTTP Tool (GET/POST a APIs) | Alta | - | 2d | TODO |
| T7.3 | Compute Tool (evaluador seguro) | Media | - | 2d | TODO |
| T7.4 | Database Tool (SQL queries) | Alta | - | 3d | TODO |
| T7.5 | File Tool (búsqueda en documentos) | Media | - | 2d | TODO |
| T7.6 | RAG Tool (integración real) | Alta | - | 2d | TODO |
| T7.7 | Tool chaining (composición) | Media | - | 2d | TODO |
| T7.8 | Security & validation | Alta | - | 2d | TODO |

**Ejemplo - Search Tool:**
```python
class SearchTool(Tool):
    name = "search"
    description = "Search for information online"
    
    def execute(self, query: str, count: int = 3) -> List[Dict]:
        # Validación
        if len(query) > 200:
            raise ValueError("Query too long")
        
        # Búsqueda
        from duckduckgo_search import DDGS
        results = DDGS().text(query, max_results=count)
        
        # Formato
        return [
            {
                'title': r['title'],
                'url': r['link'],
                'snippet': r['snippet'],
                'relevance': score_relevance(r, query)
            }
            for r in results
        ]
```

---

### FASE 8: Fine-Tuning de Modelos (Semanas 8-10)

| ID | Tarea | Prioridad | Asignee | Estimación | Status |
|---|---|---|---|---|---|
| T8.1 | Curar dataset 500+ ejemplos reales | Alta | - | 3d | TODO |
| T8.2 | Anotar intents y entities | Alta | - | 3d | TODO |
| T8.3 | Fine-tune sentence-transformers | Media | - | 3d | TODO |
| T8.4 | Fine-tune intent classifier | Media | - | 2d | TODO |
| T8.5 | Fine-tune NER model | Media | - | 3d | TODO |
| T8.6 | Evaluación completa (F1, precision, recall) | Alta | - | 2d | TODO |
| T8.7 | A/B test vs modelos base | Media | - | 2d | TODO |

**Mejora esperada:**
```
┌──────────────────────┬─────────────┬─────────────┐
│ Métrica              │ Base Model  │ Fine-tuned  │
├──────────────────────┼─────────────┼─────────────┤
│ Intent F1            │ 0.78        │ 0.88        │
│ NER F1               │ 0.65        │ 0.82        │
│ Embedding Similarity │ 0.72        │ 0.85        │
│ Inference Time       │ 25ms        │ 28ms        │
└──────────────────────┴─────────────┴─────────────┘
```

---

### FASE 9: Observabilidad & Analytics (Semanas 10-12)

| ID | Tarea | Prioridad | Asignee | Estimación | Status |
|---|---|---|---|---|---|
| T9.1 | Event pipeline architecture | Alta | - | 2d | TODO |
| T9.2 | Logging mejorado con context | Alta | - | 2d | TODO |
| T9.3 | Métricas de NLP dashboard | Media | - | 3d | TODO |
| T9.4 | Error analysis workflow | Media | - | 2d | TODO |
| T9.5 | A/B testing framework | Media | - | 2d | TODO |
| T9.6 | Alerting para anomalías | Media | - | 1d | TODO |
| T9.7 | Documentation & runbooks | Media | - | 2d | TODO |

**Dashboard Metrics:**
```
┌─────────────────────────────────────┐
│ NLP System Health Dashboard         │
├─────────────────────────────────────┤
│                                     │
│ Intent Accuracy: 85% ↑              │
│ Average Latency: 1.8s ↓             │
│ Token Success Rate: 92% ↑           │
│ LLM Fallback Rate: 8% ↓             │
│ Tool Execution Success: 94% ↑       │
│                                     │
│ Top Intents (today):                │
│  - set_welcome: 250 calls ✓         │
│  - get_status: 180 calls ✓          │
│  - add_filter: 120 calls ✓          │
│                                     │
│ Error Distribution:                 │
│  - Timeout: 2%                      │
│  - Invalid entity: 3%               │
│  - LLM unavailable: 1%              │
│                                     │
└─────────────────────────────────────┘
```

---

## Arquitectura Técnica por Fase

### FASE 1-2: NLP Core
```
app/nlp/
├── pipeline.py         (mejorada)
├── tokenizer.py        (con lemmatización)
├── normalizer.py       (más rules)
├── intent_classifier.py
│   ├── regex_classifier
│   ├── ml_classifier   (NUEVO)
│   └── ensemble        (NUEVO)
├── ner.py              (mejorada)
├── features.py         (NUEVO - feature extraction)
├── models/
│   └── intent_classifier.joblib (NUEVO)
└── tests/
    └── test_nlp_core.py
```

### FASE 3-4: Audio & Confianza
```
app/
├── audio/              (NUEVO)
│   ├── processor.py
│   ├── transcriber.py
│   └── models.py
├── webhook/
│   ├── audio_handler.py (NUEVO)
│   └── handlers.py
└── nlp/
    ├── confidence.py   (NUEVO)
    └── ensemble.py     (NUEVO)
```

### FASE 5-6: Memory & Reasoning
```
app/agent/
├── memory.py           (mejorada)
│   ├── ConversationMemory (NUEVO)
│   ├── FactExtractor (NUEVO)
│   └── TimelineManager (NUEVO)
├── reasoning.py        (refactorizada)
│   ├── ChainOfThought (NUEVO)
│   ├── PlanGenerator (NUEVO)
│   └── ReActV2 (mejorada)
└── context.py          (mejorada)
```

### FASE 7: Tools
```
app/tools/              (mejorada)
├── builtins.py         (expandida)
├── search.py           (NUEVO)
├── http.py             (NUEVO)
├── compute.py          (NUEVO)
├── database.py         (NUEVO)
├── files.py            (NUEVO)
├── rag.py              (NUEVO)
└── validator.py        (NUEVO - security)
```

### FASE 8-9: ML & Observability
```
ml/                     (NUEVO)
├── training/
│   ├── dataset_builder.py
│   ├── trainer.py
│   └── evaluator.py
├── models/             (NUEVO)
│   ├── intent_classifier_finetuned.joblib
│   ├── embeddings_model/
│   └── ner_model/
└── experiments/
    └── tracking.yaml

monitoring/             (mejorada)
├── nlp_metrics.py      (NUEVO)
├── dashboards.py       (NUEVO)
└── alerts.py           (NUEVO)
```

---

## Propuesta de Cambios Código

### T1: Mejorar Tokenizer

**Archivo**: [app/nlp/tokenizer.py](app/nlp/tokenizer.py)

```python
@dataclass
class TokenizationResult:
    tokens: List[str]
    pos_tags: List[Tuple[str, str]]
    lemmas: List[str]           # NUEVO
    deps: List[str]              # NUEVO  
    text: str
    intent_hint: Optional[str] = None  # NUEVO
    
    # Métodos helper
    def get_nouns(self) -> List[str]:
        return [token for token, pos in self.pos_tags if pos == "NOUN"]
    
    def get_verbs(self) -> List[str]:
        return [token for token, pos in self.pos_tags if pos == "VERB"]
    
    def get_lemmas_for_nouns(self) -> List[str]:  # NUEVO
        """Retorna lemmas solo de sustantivos"""
        noun_indices = [i for i, (token, pos) in enumerate(self.pos_tags) if pos == "NOUN"]
        return [self.lemmas[i] for i in noun_indices]
```

---

### T2: Intent Classifier ML

**Archivo**: `app/nlp/intent_classifier.py` (refactorizar)

```python
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer

class MLIntentClassifier:
    def __init__(self, model_path: str = "models/intent_classifier.joblib"):
        self.model = None
        self.model_path = model_path
        self._load_model()
    
    def _load_model(self):
        if Path(self.model_path).exists():
            import joblib
            self.model = joblib.load(self.model_path)
    
    def classify(self, text: str) -> Tuple[Optional[str], float]:
        if self.model is None:
            return None, 0.0
        
        probs = self.model.predict_proba([text])[0]
        max_idx = np.argmax(probs)
        intent = self.model.classes_[max_idx]
        confidence = float(probs[max_idx])
        
        return intent, confidence

class IntentClassifierEnsemble:
    """Combina regex + ML + LLM con pesos"""
    
    def __init__(self):
        self.regex_clf = IntentClassifier()  # Original
        self.ml_clf = MLIntentClassifier()
        self.weights = {'regex': 0.3, 'ml': 0.7}
    
    def classify(self, text: str) -> Tuple[Optional[str], float]:
        regex_intent, regex_conf = self.regex_clf.classify(text)
        ml_intent, ml_conf = self.ml_clf.classify(text)
        
        # Ensemble
        if regex_intent == ml_intent:
            confidence = (
                self.weights['regex'] * regex_conf +
                self.weights['ml'] * ml_conf
            )
            return regex_intent, confidence
        
        # Favor ML when there's disagreement
        if ml_conf > 0.7:
            return ml_intent, ml_conf
        elif regex_conf > 0.6:
            return regex_intent, regex_conf
        
        return None, 0.0
```

---

### T3-4: Speech Support

**Archivo**: `app/audio/transcriber.py` (NUEVO)

```python
import asyncio
from typing import Optional

class WhisperTranscriber:
    """Integración con OpenAI Whisper API"""
    
    def __init__(self, api_key: str):
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(api_key=api_key)
        self.cache = {}  # Redis en producción
    
    async def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        timeout: int = 30
    ) -> str:
        # Check cache
        cache_key = hash_file(audio_path)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            with open(audio_path, "rb") as f:
                transcript = await asyncio.wait_for(
                    self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=f,
                        language=language,
                    ),
                    timeout=timeout
                )
            
            result = transcript.text
            self.cache[cache_key] = result
            return result
        except asyncio.TimeoutError:
            raise ValueError("Transcription timeout")
        except Exception as e:
            raise ValueError(f"Transcription failed: {e}")
```

---

### T5: Conversation Memory

**Archivo**: `app/agent/memory.py` (mejorada)

```python
from dataclasses import dataclass, field
from typing import Dict, List, Any
from datetime import datetime

@dataclass
class ConversationEvent:
    timestamp: datetime
    user_msg: str
    bot_response: str
    intent: Optional[str] = None
    entities: List[Dict] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class ConversationMemory:
    """Mantiene contexto conversacional de sesión"""
    
    def __init__(self, max_messages: int = 10, llm_enabled: bool = False):
        self.history: List[ConversationEvent] = []
        self.max_messages = max_messages
        self.extracted_facts: Dict[str, Any] = {}
        self.timeline: List[ConversationEvent] = []
        self.entity_refs: Dict[str, str] = {}  # pronoun → entity mapping
        self.llm_enabled = llm_enabled
    
    def add_exchange(
        self,
        user_msg: str,
        bot_response: str,
        intent: Optional[str] = None,
        entities: Optional[List[Dict]] = None
    ):
        event = ConversationEvent(
            timestamp=datetime.utcnow(),
            user_msg=user_msg,
            bot_response=bot_response,
            intent=intent,
            entities=entities or []
        )
        
        # Sliding window
        if len(self.history) >= self.max_messages:
            self.history.pop(0)
        
        self.history.append(event)
        self.timeline.append(event)
        
        # Extract facts
        self._extract_facts(user_msg)
        
        # Resolve pronouns
        self._resolve_pronouns(user_msg)
    
    def _extract_facts(self, text: str):
        """Extrae datos relevantes del texto"""
        # Usar NER + reglas para extraer
        from app.nlp import EntityExtractor
        extractor = EntityExtractor()
        entities = extractor.extract(text)
        
        for ent in entities:
            key = f"{ent.label.lower()}_{len(self.extracted_facts)}"
            self.extracted_facts[key] = {
                'value': ent.value,
                'type': ent.label,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _resolve_pronouns(self, text: str):
        """Resuelve pronombres a entidades conocidas"""
        pronouns = {
            'él': 'he',
            'ella': 'she',
            'ellos': 'they',
            'ellas': 'they',
            'esto': 'this',
            'eso': 'that'
        }
        
        text_lower = text.lower()
        for pronoun in pronouns:
            if pronoun in text_lower:
                # Buscar entidad más reciente del tipo correcto
                if self.extracted_facts:
                    latest = sorted(
                        self.extracted_facts.items(),
                        key=lambda x: x[1]['timestamp'],
                        reverse=True
                    )[0]
                    self.entity_refs[pronoun] = latest[1]['value']
    
    def get_context(self, for_llm: bool = False) -> Dict[str, Any]:
        """Retorna contexto para siguiente request"""
        if for_llm:
            return self._render_context_for_llm()
        return {
            'recent_history': self.history[-5:],
            'facts': self.extracted_facts,
            'entity_refs': self.entity_refs,
            'timeline_len': len(self.timeline)
        }
    
    def _render_context_for_llm(self) -> str:
        """Renderiza contexto legible para LLM"""
        lines = ["## Conversation Context\n"]
        
        # Recent messages
        lines.append("### Recent Messages:")
        for event in self.history[-3:]:
            lines.append(f"- User: {event.user_msg}")
            lines.append(f"- Bot: {event.bot_response}\n")
        
        # Facts
        if self.extracted_facts:
            lines.append("### Known Facts:")
            for fact, value in self.extracted_facts.items():
                lines.append(f"- {fact}: {value['value']}")
        
        return "\n".join(lines)
```

---

## Plan de Rollout

```
SEMANA 1-2: Phase 1 → Merge to develop
  ✓ Tokenización mejorada
  ✓ Tests pasando 85%+
  
SEMANA 3: Phase 2 → Beta channel
  ✓ ML classifier entrenado
  ✓ A/B test vs regex
  
SEMANA 4: Phase 2-3 → Producción gradual
  ✓ Ensemble deployment (10% → 50% → 100%)
  ✓ Monitor accuracy
  
SEMANA 5-6: Phase 4-5 → Feature branches
  ✓ Audio + Memory en desarrollo
  ✓ Testing en staging
  
SEMANA 7-8: Phase 6-7 → Staging
  ✓ ReAct + Tools
  ✓ Load testing
  
SEMANA 9-10: Fase 8 → Canary deployment
  ✓ Fine-tuned models (5% → 25%)
  
SEMANA 11-12: Fase 9 → Full monitoring
  ✓ Analytics dashboard live
  ✓ Health checks automáticos
```

---

## Criterios de Aceptación

### Global
- ✓ 0 breaking changes a producción
- ✓ Backward compatibility mantenida
- ✓ Tests coverage >= 85%
- ✓ Documentation actualizada
- ✓ Performance no degradado

### Por Fase
- **Fase 1**: Intent accuracy >= 75%
- **Fase 2**: ML classifier F1 >= 0.75
- **Fase 3**: Ensemble accuracy >= 82%
- **Fase 4**: Speech WER < 10%
- **Fase 5**: Context retrieval accuracy >= 90%
- **Fase 6**: Multi-step tasks completados >= 80%
- **Fase 7**: Tools execution success >= 95%
- **Fase 8**: Fine-tuned F1 >= 0.88
- **Fase 9**: Monitoring coverage >= 100%

---

## Riesgos & Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|--------|-----------|
| Dataset sesgado | Media | Alto | Data augmentation + validación cruzada |
| Degradación de accuracy | Alta | Crítico | Fallback a regex + A/B testing |
| Costo LLM/Whisper | Baja | Medio | Rate limiting + caching + fallbacks |
| Regresiones | Media | Medio | Tests + CI/CD + staging |
| Adoption bajo | Baja | Bajo | Comunicación + training |

---

## Conclusión

Este plan sienta las bases para evolucionar el sistema NLP de **50% a 90% de accuracy** en 12 semanas. La arquitectura final será **robusta, escalable y agnóstica a LLM**, con fallbacks en cada capa.

**Próximos pasos:**
1. Aprobar plan y asignar recursos
2. Comenzar Phase 1 (Tokenización) esta semana
3. Curar dataset para Phase 2
4. Setup CI/CD y monitoring
5. Comunicar a stakeholders
