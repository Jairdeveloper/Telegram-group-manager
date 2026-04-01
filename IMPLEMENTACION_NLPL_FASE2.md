# IMPLEMENTACIÓN FASE 2: MACHINE LEARNING INTENT CLASSIFIER

## Metadatos

**Fecha:** 2026-03-30  
**Versión:** 2.0  
**Referencia:** `02_PLAN_IMPLEMENTACION_NLPL.md`, `IMPLEMENTACION_NLPL_FASE1.md`

---

## Resumen de la Migración

### Estado Actual (Después de FASE 1)
Después de completar FASE 1, tenemos:
- ✅ Tokenización avanzada con lemmatización y POS tagging
- ✅ Normalización mejorada (diacríticos, contracciones)
- ✅ Dependency parsing sintáctico
- ✅ Intent hints tempranos (keyword-based, 50% accuracy)
- ✅ Base sólida para siguiente nivel de inteligencia

### Objetivo de FASE 2
Evolucionar de **detección de intents basada en reglas/keywords** a **clasificación mediante Machine Learning**, mejorando:

| Aspecto | FASE 1 | FASE 2 (meta) | Mejora |
|---------|--------|---------------|--------|
| **Intent Accuracy** | 50% | 78%+ | ↑ 28pp |
| **Method** | Regex + Keywords | ML Classifier (LR) | Escalable |
| **Data-driven** | No | Sí | ↑ Inteligencia |
| **Confianza calibrada** | No | Sí (probabilities) | ↑ Fiabilidad |
| **Fallback automático** | No | Sí (ensemble) | ↑ Robustez |
| **Tiempo inference** | 10ms | 25ms | ↓ (aceptable) |

### Migración Arquitectónica

```
┌─────────────────────────────────────────┐
│      FASE 1: Tokenización              │
├─────────────────────────────────────────┤
│          TokenizationResult              │
│  (tokens, lemmas, deps, pos_tags)      │
└────────────────┬────────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────┐
    │  FASE 2: ML Intent Classifier   │
    ├────────────────────────────────┤
    │ 1. Feature Engineering          │
    │    └─ TF-IDF embeddings         │
    │    └─ Lemma combinations        │
    │    └─ Dependency features       │
    │                                 │
    │ 2. ML Pipeline                  │
    │    └─ LogisticRegression        │
    │    └─ Confidence scores         │
    │    └─ Probability calibration   │
    │                                 │
    │ 3. Ensemble + Fallback          │
    │    └─ Regex baseline (0.5x)     │
    │    └─ ML classifier (0.5x)      │
    │    └─ LLM fallback (<0.5 conf)  │
    └────────────────┬────────────────┘
                     │
                     ▼
        ┌──────────────────────────┐
        │   IntentClassifierResult  │
        │  (intent, confidence,     │
        │   method, alternatives)   │
        └──────────────────────────┘
```

---

## Arquitectura Final (FASE 2)

### Pipeline Completo: Tokenización → Clasificación ML

```
Input Text: "Cambiar mensaje de bienvenida"
    │
    ▼
┌───────────────────────────────────┐
│   FASE 1: Preprocessing           │
├───────────────────────────────────┤
│ Tokenize → Normalize → Lemmatize  │
│                                   │
│ TokenizationResult:               │
│  tokens: ['cambiar', 'mensaje',   │
│           'de', 'bienvenida']     │
│  lemmas: ['cambiar', 'mensaje',   │
│           'de', 'bienvenido']     │
│  deps: [('cambiar', 'ROOT'),      │
│         ('mensaje', 'OBJ'), ...]  │
│  intent_hint: 'set_welcome' (50%) │
└───────────────┬───────────────────┘
                │
                ▼
┌───────────────────────────────────┐
│   FASE 2: Feature Engineering     │
├───────────────────────────────────┤
│                                   │
│ 1. TF-IDF Vectorization           │
│    - Bag of words lemmas          │
│    - Sparse matrix (10000 dims)   │
│                                   │
│ 2. Contextual Features            │
│    - Lemma combinations (bigrams) │
│    - POS tag patterns             │
│    - Dependency structures        │
│    - Keyword presence             │
│                                   │
│ Feature Vector (500+ features)    │
│ [0.23, 0.15, ..., 0.42]           │
└───────────────┬───────────────────┘
                │
                ▼
┌───────────────────────────────────┐
│  FASE 2: ML Classification        │
├───────────────────────────────────┤
│                                   │
│ Model: LogisticRegression         │
│ Classes: 15 intents               │
│                                   │
│ Prediction:                       │
│ ┌─────────────────────────────┐  │
│ │ set_welcome: 0.82           │  │
│ │ toggle_feature: 0.10        │  │
│ │ add_filter: 0.05            │  │
│ │ ...                         │  │
│ └─────────────────────────────┘  │
│                                   │
│ Confidence: 0.82 (HIGH) ✅       │
└───────────────┬───────────────────┘
                │
                ▼
┌───────────────────────────────────┐
│  FASE 2: Ensemble & Fallback      │
├───────────────────────────────────┤
│                                   │
│ Confidence >= 0.75:               │
│   └─ Return ML prediction ✅      │
│                                   │
│ Confidence 0.5-0.75:              │
│   └─ Ensemble (Regex + ML)        │
│   └─ Return if agreement, else... │
│   └─ Try LLM fallback             │
│                                   │
│ Confidence < 0.5:                 │
│   └─ LLM Fallback (timeout 2s)    │
│   └─ Return human review queue    │
│                                   │
└───────────────┬───────────────────┘
                │
                ▼
        IntentClassifierResult:
        {
          intent: "set_welcome",
          confidence: 0.82,
          method: "ml_classifier",
          probability_distribution: {...},
          explanation: "82% confidence en set_welcome..."
        }
```

### Componentes Principales

#### 1. Feature Extractor (`app/nlp/features.py`)
```python
class FeatureExtractor:
    """Extrae features de TokenizationResult para ML"""
    
    def extract(self, tokenization_result: TokenizationResult) -> np.ndarray:
        """
        Retorna vector de features (500+ dimensiones)
        
        Componentes:
        - TF-IDF de lemmas (300 dims)
        - Bigram lemmas (100 dims)
        - POS tag patterns (50 dims)
        - Dependency patterns (30 dims)
        - Keyword presence (20 dims)
        """
        pass
    
    def fit(self, training_data: List[TokenizationResult], labels: List[str]):
        """Fitear extractor con datos de entrenamiento"""
        pass
```

#### 2. ML Classifier (`app/nlp/classifiers/ml_classifier.py`)
```python
class MLIntentClassifier:
    """Logistic Regression para clasificación de intents"""
    
    def __init__(self, model_path: str = "models/intent_classifier.joblib"):
        self.model = load(model_path)
        self.classes = 15  # Intents soportados
        self.feature_extractor = FeatureExtractor()
    
    def predict(self, tokenization_result: TokenizationResult) -> IntentPrediction:
        """
        Predice intent con probabilidades calibradas
        
        Returns:
            IntentPrediction(
                intent: str,
                confidence: float (0.0-1.0),
                probabilities: Dict[str, float],
                explanation: str
            )
        """
        pass
    
    def predict_proba(self, tokenization_result: TokenizationResult) -> Dict[str, float]:
        """Retorna probabilidades para todos los intents"""
        pass
```

#### 3. Ensemble Classifier (`app/nlp/classifiers/ensemble_classifier.py`)
```python
class EnsembleIntentClassifier:
    """Combina predicciones de múltiples métodos"""
    
    def __init__(self):
        self.regex_classifier = RegexIntentClassifier()      # Baseline (0.5x)
        self.ml_classifier = MLIntentClassifier()            # Principal (0.5x)
        self.llm_classifier = LLMIntentClassifier()          # Fallback
    
    def predict(self, text: str, tokenization_result: TokenizationResult) \
            -> IntentClassificationResult:
        """
        Pipeline de clasificación con fallback:
        
        1. ML predict + confidence
        2. If confidence >= 0.75: return ML
        3. If 0.5 <= confidence < 0.75: try ensemble
        4. If confidence < 0.5: try LLM (timeout 2s)
        5. Else: human review queue
        """
        pass
```

#### 4. Confidence Calibration (`app/nlp/calibration.py`)
```python
class ConfidenceCalibrator:
    """Calibra probabilidades del modelo (Platt scaling)"""
    
    def __init__(self):
        self.scaler = None  # LogisticRegression para calibración
    
    def fit(self, probabilities: np.ndarray, true_labels: np.ndarray):
        """Fitear calibrador en validation set"""
        pass
    
    def calibrate(self, raw_probabilities: np.ndarray) -> np.ndarray:
        """Aplicar calibración a probabilidades del modelo"""
        pass
```

---

## Tabla de Tareas

### FASE 2: Machine Learning Intent Classifier (Semanas 2-3)

#### Block 1: Data Curation & Preparation

| ID | Tarea | Prioridad | Estimación | Riesgo | DependsOn | Status |
|---|---|---|---|---|---|---|
| **T2.1a** | Diseñar schema de dataset | Alta | 0.5d | Bajo | - | TODO |
| **T2.1b** | Curar 50+ ejemplos por intent (15 intents) | Alta | 3d | Media | T2.1a | TODO |
| **T2.1c** | Validar dataset quality (duplicados, inconsistencias) | Media | 1d | Bajo | T2.1b | TODO |
| **T2.1d** | Guardar dataset en `data/intent_training_data.json` | Media | 0.5d | Bajo | T2.1c | TODO |

**Deliverable:** `data/intent_training_data.json` con 750+ ejemplos curados

```json
{
  "training_data": [
    {
      "text": "Cambiar mensaje de bienvenida",
      "intent": "set_welcome",
      "metadata": {
        "source": "requirements_doc",
        "confidence": "high",
        "priority": "P1"
      }
    },
    ...
  ]
}
```

---

#### Block 2: Feature Engineering & Preprocessing

| ID | Tarea | Prioridad | Estimación | Riesgo | DependsOn | Status |
|---|---|---|---|---|---|---|
| **T2.2a** | Implementar TF-IDF vectorization (`features.py`) | Alta | 2d | Bajo | T2.1d | TODO |
| **T2.2b** | Agregar contextual features (bigrams, POS patterns) | Media | 1.5d | Media | T2.2a | TODO |
| **T2.2c** | Crear feature normalization pipeline | Media | 1d | Bajo | T2.2b | TODO |
| **T2.2d** | Tests de feature extraction (coverage 80%+) | Alta | 1d | Bajo | T2.2c | TODO |

**Deliverable:** `app/nlp/features.py` - Feature extractor completamente testeado

```python
# Ejemplo de output
feature_vector = feature_extractor.extract(tokenization_result)
# Shape: (500,) - 500 features TF-IDF + contextual
```

---

#### Block 3: Model Training & Validation

| ID | Tarea | Prioridad | Estimación | Riesgo | DependsOn | Status |
|---|---|---|---|---|---|---|
| **T2.3a** | Setup train/test split (80/20) con stratification | Alta | 0.5d | Bajo | T2.2d | TODO |
| **T2.3b** | Train LogisticRegression baseline | Alta | 1d | Bajo | T2.3a | TODO |
| **T2.3c** | Implement cross-validation (5-fold) | Media | 1d | Bajo | T2.3b | TODO |
| **T2.3d** | Hyperparameter tuning (C, solver) | Media | 1.5d | Media | T2.3c | TODO |
| **T2.3e** | Evaluate: Accuracy, Precision, Recall, F1 | Alta | 1d | Bajo | T2.3d | TODO |
| **T2.3f** | Generate classification report per intent | Media | 0.5d | Bajo | T2.3e | TODO |

**Métricas de Éxito:**
```
Overall Accuracy:     >= 75%
Macro-avg Precision:  >= 0.78
Macro-avg Recall:     >= 0.72
Macro-avg F1:         >= 0.75
```

---

#### Block 4: Confidence Calibration

| ID | Tarea | Prioridad | Estimación | Riesgo | DependsOn | Status |
|---|---|---|---|---|---|---|
| **T2.4a** | Implement Platt scaling (logistic calibration) | Media | 1.5d | Media | T2.3f | TODO |
| **T2.4b** | Fit calibrator on validation set | Media | 0.5d | Bajo | T2.4a | TODO |
| **T2.4c** | Validate calibration (ECE - Expected Calibration Error < 0.10) | Media | 1d | Bajo | T2.4b | TODO |
| **T2.4d** | Tests de calibración | Media | 0.5d | Bajo | T2.4c | TODO |

**Deliverable:** Calibration report in `reports/confidence_calibration.md`

---

#### Block 5: Model Serialization

| ID | Tarea | Prioridad | Estimación | Riesgo | DependsOn | Status |
|---|---|---|---|---|---|---|
| **T2.5a** | Serializar modelo en joblib | Media | 0.5d | Bajo | T2.3f | TODO |
| **T2.5b** | Guardar feature extractor (fitted vectorizer) | Media | 0.5d | Bajo | T2.4d | TODO |
| **T2.5c** | Guardar confidence calibrator | Media | 0.5d | Bajo | T2.4d | TODO |
| **T2.5d** | Implement model versioning & checksums | Media | 0.5d | Bajo | T2.5a-c | TODO |

**Deliverables:**
- `models/intent_classifier.joblib` - Modelo entrenado
- `models/feature_extractor.joblib` - Vectorizer fitted
- `models/confidence_calibrator.joblib` - Calibrador
- `models/metadata.json` - Versioning info

---

#### Block 6: Ensemble & Fallback Integration

| ID | Tarea | Prioridad | Estimación | Riesgo | DependsOn | Status |
|---|---|---|---|---|---|---|
| **T2.6a** | Implementar EnsembleIntentClassifier | Alta | 1.5d | Media | T2.5d | TODO |
| **T2.6b** | Integrar avec RegexIntentClassifier (baseline) | Alta | 1d | Bajo | T2.6a | TODO |
| **T2.6c** | Implementar weighted combination (0.5 ML + 0.5 Regex) | Media | 1d | Bajo | T2.6b | TODO |
| **T2.6d** | LLM fallback con timeout (2s max) | Media | 1.5d | Alta | T2.6c | TODO |
| **T2.6e** | Tests de ensemble (robustness) | Alta | 1.5d | Bajo | T2.6d | TODO |

---

#### Block 7: A/B Testing & Evaluation

| ID | Tarea | Prioridad | Estimación | Riesgo | DependsOn | Status |
|---|---|---|---|---|---|---|
| **T2.7a** | Setup A/B test framework | Media | 1d | Media | T2.6b | TODO |
| **T2.7b** | Comparativa: Regex vs ML vs Ensemble | Media | 2d | Media | T2.6e | TODO |
| **T2.7c** | Analizar confidence distribution | Media | 1d | Bajo | T2.7b | TODO |
| **T2.7d** | Rapport A/B testing con métricas | Media | 0.5d | Bajo | T2.7c | TODO |

**Deliverable:** `reports/intent_classifier_ab_testing.md`

```
┌──────────────────┬──────────┬───────────┬────────┬──────────┐
│ Método           │ Accuracy │ Precision │ Recall │ Latency  │
├──────────────────┼──────────┼───────────┼────────┼──────────┤
│ Regex (baseline) │ 50%      │ 0.65      │ 0.45   │ 10ms     │
│ ML Classifier    │ 78%      │ 0.82      │ 0.75   │ 25ms     │
│ Ensemble         │ 81%      │ 0.84      │ 0.78   │ 40ms     │
└──────────────────┴──────────┴───────────┴────────┴──────────┘
```

---

#### Block 8: Documentation & Tests

| ID | Tarea | Prioridad | Estimación | Riesgo | DependsOn | Status |
|---|---|---|---|---|---|---|
| **T2.8a** | Crear `tests/test_ml_intent_classifier.py` | Alta | 1.5d | Bajo | T2.6e | TODO |
| **T2.8b** | Tests de features extraction (80%+ coverage) | Alta | 1d | Bajo | T2.2d | TODO |
| **T2.8c** | Tests de ensemble (edge cases) | Alta | 1d | Bajo | T2.6e | TODO |
| **T2.8d** | Documentation: README.md de FASE 2 | Media | 1d | Bajo | T2.8a-c | TODO |

---

## Fase

**FASE 2: Machine Learning Intent Classifier**

**Duración:** 2 semanas (Weeks 2-3 del plan general)

**Timeline:**
```
Semana 2:
├─ Lunes-Viernes: Data Curation (T2.1) + Features (T2.2)
└─ Viernes-Sábado: Model Training (T2.3)

Semana 3:
├─ Lunes-Miércoles: Calibration (T2.4) + Serialization (T2.5)
├─ Miércoles-Viernes: Ensemble (T2.6) + A/B Testing (T2.7)
└─ Viernes: Tests & Documentation (T2.8)
```

---

## Objetivo Fase

### Objetivo General
Implementar un **Machine Learning Intent Classifier** que mejore la detección de intents de **50% accuracy a 78%+** mediante:

1. **Curación de dataset** - 750+ ejemplos de entrenamiento
2. **Feature engineering** - TF-IDF + contextual features
3. **Modelo de ML** - LogisticRegression con validación cruzada
4. **Confianza calibrada** - Platt scaling para probabilidades confiables
5. **Ensemble robusto** - Combinación de Regex + ML + LLM fallback
6. **Evaluación completa** - A/B testing y benchmarks

### Objetivos Específicos

#### O2.1: Dataset de Entrenamiento Curado
**Meta:** 750+ ejemplos etiquetados, 50 por intent (15 intents)
- Cobertura: 95%+ de variaciones de lenguaje natural
- Calidad: 0 duplicados, 0 errores de etiqueta
- Formato: JSON con metadata

#### O2.2: Feature Engineering Robusto
**Meta:** 500+ features por texto
- TF-IDF: 300 dimensiones (bag of lemmas)
- Contextual: 200 dimensiones (bigrams, POS, deps)
- Normalización: StandardScaler para estabilidad

#### O2.3: Modelo ML Entrenado y Validado
**Meta:** >= 75% accuracy en test set
- Architecture: LogisticRegression (lineal, interpretable)
- Classes: 15 intents
- Validation: 5-fold cross-validation
- Hyperparameters: Tuned via GridSearch

#### O2.4: Confianza Calibrada
**Meta:** Probabilidades confiables (ECE < 0.10)
- Método: Platt scaling en validation set
- Beneficio: Sabemos cuándo confiar en predicción

#### O2.5: Ensemble Inteligente
**Meta:** Decisión robusta con fallback automático
- Threshold >= 0.75: Return ML prediction
- Threshold 0.5-0.75: Try ensemble
- Threshold < 0.5: LLM fallback (2s timeout)

#### O2.6: Evaluación Completa
**Meta:** A/B testing vs Regex baseline
- Métrica: Accuracy, Precision, Recall, F1
- Comparativa: 3 métodos en 3 escenarios
- Reporte: Insights y recomendaciones

---

## Implementación Fase

### 1. Estructura de Archivos

```
manufacturing/robot/
├── data/
│   └── intent_training_data.json          # Dataset curado 750+ ejemplos
│
├── models/
│   ├── intent_classifier.joblib           # Modelo entrenado
│   ├── feature_extractor.joblib           # Vectorizer fitted
│   ├── confidence_calibrator.joblib       # Calibrador
│   └── metadata.json                      # Version info
│
├── app/nlp/
│   ├── features.py                        # Feature extraction
│   ├── classifiers/
│   │   ├── __init__.py
│   │   ├── ml_classifier.py               # LogisticRegression
│   │   ├── regex_classifier.py            # Baseline (FASE 1)
│   │   ├── ensemble_classifier.py         # Ensemble + fallback
│   │   └── llm_classifier.py              # LLM fallback
│   └── calibration.py                     # Confidence calibration
│
├── tests/
│   ├── test_ml_intent_classifier.py       # Tests del modelo
│   ├── test_features.py                   # Tests de features
│   └── test_ensemble_classifier.py        # Tests ensemble
│
└── reports/
    ├── intent_classifier_eval.md          # Evaluación completa
    ├── confidence_calibration.md          # Calibración report
    ├── intent_classifier_ab_testing.md    # A/B test results
    └── feature_importance.md              # Feature analysis
```

---

### 2. Implementación Detallada por Componente

#### 2.1 Feature Extractor (`app/nlp/features.py`)

```python
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List, Dict
from app.nlp.tokenizer import TokenizationResult

class FeatureExtractor:
    """Extrae features para ML classifier"""
    
    def __init__(self, max_features: int = 300):
        self.max_features = max_features
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=(1, 2),         # Unigrams + Bigrams
            min_df=2,                    # Appear in at least 2 documents
            max_df=0.8,                  # Not in >80% of documents
            sublinear_tf=True            # Sublinear TF scaling
        )
        self.is_fitted = False
    
    def fit(self, textual_inputs: List[str], labels: List[str] = None):
        """Fit TF-IDF en los datos de entrenamiento"""
        self.tfidf_vectorizer.fit(textual_inputs)
        self.is_fitted = True
        return self
    
    def extract(self, tokenization_result: TokenizationResult) -> np.ndarray:
        """
        Extrae features de TokenizationResult
        
        Componentes:
        1. TF-IDF de lemmas (300 dims)
        2. Lemma bigrams (50 dims)
        3. POS tag patterns (20 dims)
        4. Dependency relations (10 dims)
        5. Keyword presence (20 dims)
        
        Total: 400 dimensions
        """
        if not self.is_fitted:
            raise ValueError("Fit extractor first!")
        
        # TF-IDF de lemmas
        lemma_text = " ".join(tokenization_result.lemmas)
        tfidf_features = self.tfidf_vectorizer.transform([lemma_text]).toarray()[0]
        
        # POS patterns (simple encoding)
        pos_patterns = self._extract_pos_patterns(tokenization_result)
        
        # Dependency features
        dep_features = self._extract_dependency_features(tokenization_result)
        
        # Keyword presence
        keyword_features = self._extract_keyword_features(tokenization_result)
        
        # Concatenate all features
        features = np.concatenate([
            tfidf_features,          # 300
            pos_patterns,            # 20
            dep_features,            # 10
            keyword_features         # 20
        ])
        
        return features
    
    def _extract_pos_patterns(self, result: TokenizationResult) -> np.ndarray:
        """Extrae patrones de POS tags"""
        pos_counts = {}
        for _, pos in result.pos_tags:
            pos_counts[pos] = pos_counts.get(pos, 0) + 1
        
        # Normalizar
        total = len(result.tokens) if result.tokens else 1
        features = np.array([
            pos_counts.get('VERB', 0) / total,
            pos_counts.get('NOUN', 0) / total,
            pos_counts.get('ADJ', 0) / total,
            pos_counts.get('ADV', 0) / total,
            # ... más POS
        ])
        return features
    
    def _extract_dependency_features(self, result: TokenizationResult) -> np.ndarray:
        """Extrae features de dependencias"""
        dep_counts = {}
        for _, dep in result.deps:
            dep_counts[dep] = dep_counts.get(dep, 0) + 1
        
        return np.array([
            dep_counts.get('ROOT', 0),
            dep_counts.get('OBJ', 0),
            dep_counts.get('NMOD', 0),
            # ... más dependencias
        ])
    
    def _extract_keyword_features(self, result: TokenizationResult) -> np.ndarray:
        """Extrae presencia de keywords importantes"""
        action_keywords = {
            'set_welcome': ['cambiar', 'configurar', 'bienvenida'],
            'add_filter': ['bloquear', 'filtrar', 'agregar'],
            # ...
        }
        
        features = []
        for intent, keywords in action_keywords.items():
            has_keyword = any(
                kw in [l.lower() for l in result.lemmas]
                for kw in keywords
            )
            features.append(float(has_keyword))
        
        return np.array(features)
```

---

#### 2.2 ML Classifier (`app/nlp/classifiers/ml_classifier.py`)

```python
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_validate, GridSearchCV
import joblib
import numpy as np
from typing import Dict, List

class MLIntentClassifier:
    """Logistic Regression para intent classification"""
    
    # Intent classes (15 total)
    INTENT_CLASSES = [
        'set_welcome', 'set_goodbye', 'toggle_feature',
        'add_filter', 'remove_filter', 'get_status',
        'get_settings', 'update_config', 'query_data',
        'execute_action', 'create_task', 'delete_task',
        'assign_role', 'grant_permission', 'revoke_permission'
    ]
    
    def __init__(self, model_path: str = "models/intent_classifier.joblib"):
        self.model = None
        self.model_path = model_path
        self.feature_extractor = None
        self.classes = self.INTENT_CLASSES
        self.load_model()
    
    def load_model(self):
        """Cargar modelo preentrenado"""
        try:
            self.model = joblib.load(self.model_path)
            logger.info(f"Model loaded from {self.model_path}")
        except FileNotFoundError:
            logger.warning(f"Model not found at {self.model_path}, initialize empty")
            self.model = None
    
    def train(self, X_train: np.ndarray, y_train: List[str], 
              feature_extractor = None):
        """
        Entrenar modelo con datos de entrenamiento
        
        Args:
            X_train: Feature matrix (n_samples, n_features)
            y_train: Intent labels
            feature_extractor: Fitted feature extractor
        """
        self.feature_extractor = feature_extractor
        
        # Hyperparameter tuning
        param_grid = {
            'C': [0.1, 1, 10, 100],
            'solver': ['newton-cg', 'lbfgs', 'liblinear'],
            'max_iter': [1000, 2000]
        }
        
        lr = LogisticRegression(multi_class='multinomial', random_state=42)
        grid_search = GridSearchCV(lr, param_grid, cv=5, scoring='accuracy', n_jobs=-1)
        grid_search.fit(X_train, y_train)
        
        self.model = grid_search.best_estimator_
        logger.info(f"Best params: {grid_search.best_params_}")
        logger.info(f"Best CV score: {grid_search.best_score_:.4f}")
        
        # Save model
        joblib.dump(self.model, self.model_path)
    
    def predict(self, feature_vector: np.ndarray) -> Dict[str, any]:
        """
        Predecir intent con confianza
        
        Returns:
            {
                'intent': str,
                'confidence': float (0.0-1.0),
                'probabilities': Dict[str, float],
                'method': 'ml_classifier'
            }
        """
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        # Ensure 2D input
        if feature_vector.ndim == 1:
            feature_vector = feature_vector.reshape(1, -1)
        
        # Predict
        prediction = self.model.predict(feature_vector)[0]
        probabilities = self.model.predict_proba(feature_vector)[0]
        confidence = float(np.max(probabilities))
        
        # Create probability dict
        prob_dict = {
            intent: float(prob)
            for intent, prob in zip(self.classes, probabilities)
        }
        
        return {
            'intent': prediction,
            'confidence': confidence,
            'probabilities': prob_dict,
            'method': 'ml_classifier'
        }
    
    def evaluate(self, X_test: np.ndarray, y_test: List[str]):
        """Evaluar modelo en test set"""
        from sklearn.metrics import accuracy_score, precision_recall_fscore_support
        
        y_pred = self.model.predict(X_test)
        
        accuracy = accuracy_score(y_test, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_test, y_pred, average='macro'
        )
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1
        }
```

---

#### 2.3 Ensemble Classifier (`app/nlp/classifiers/ensemble_classifier.py`)

```python
from typing import Optional, Dict
import asyncio

class EnsembleIntentClassifier:
    """Ensemble de múltiples clasificadores con fallback"""
    
    def __init__(self, 
                 ml_classifier,
                 regex_classifier,
                 llm_classifier,
                 timeout_llm: float = 2.0):
        self.ml_classifier = ml_classifier
        self.regex_classifier = regex_classifier
        self.llm_classifier = llm_classifier
        self.timeout_llm = timeout_llm
    
    def predict(self, text: str, tokenization_result) -> Dict:
        """
        Pipeline de predicción con fallback inteligente
        
        1. ML predict
        2. If confidence >= 0.75: Return
        3. Elif 0.5 <= confidence < 0.75: Try ensemble
        4. Else (< 0.5): Try LLM fallback
        5. Else: Human review queue
        """
        
        # Step 1: ML Classifier
        features = self.ml_classifier.feature_extractor.extract(tokenization_result)
        ml_result = self.ml_classifier.predict(features)
        ml_confidence = ml_result['confidence']
        
        logger.debug(f"ML confidence: {ml_confidence:.2f}")
        
        # Step 2: High confidence - use ML
        if ml_confidence >= 0.75:
            return {
                **ml_result,
                'confidence_level': 'high',
                'used_ensemble': False
            }
        
        # Step 3: Medium confidence - try ensemble
        elif ml_confidence >= 0.5:
            regex_result = self.regex_classifier.predict(text)
            
            # If both agree, return with higher confidence
            if ml_result['intent'] == regex_result['intent']:
                return {
                    'intent': ml_result['intent'],
                    'confidence': (ml_confidence + regex_result['confidence']) / 2,
                    'probabilities': ml_result['probabilities'],
                    'method': 'ensemble',
                    'confidence_level': 'medium'
                }
        
        # Step 4: Low confidence - try LLM fallback
        logger.warning(f"Low confidence ({ml_confidence:.2f}), attempting LLM fallback")
        
        try:
            llm_result = asyncio.run_coroutine_threadsafe(
                self.llm_classifier.predict(text),
                timeout=self.timeout_llm
            )
            return {
                **llm_result,
                'confidence_level': 'low_llm_fallback'
            }
        except asyncio.TimeoutError:
            logger.error("LLM fallback timeout, sending to human review")
            return {
                'intent': None,
                'confidence': 0.0,
                'method': 'human_review_queue',
                'confidence_level': 'failed'
            }
```

---

#### 2.4 Confidence Calibration (`app/nlp/calibration.py`)

```python
from sklearn.linear_model import LogisticRegression
import numpy as np

class ConfidenceCalibrator:
    """Calibra probabilidades usando Platt scaling"""
    
    def __init__(self):
        self.calibrator = LogisticRegression(C=1.0)
        self.is_fitted = False
    
    def fit(self, probabilities: np.ndarray, true_labels: np.ndarray):
        """
        Fitear calibrador en validation set
        
        Args:
            probabilities: Predicted probabilities (n_samples, n_classes)
            true_labels: True binary labels for max probability class
        """
        # Get max probability for each sample
        max_probs = np.max(probabilities, axis=1)
        
        # Create binary labels: 1 if prediction was correct
        labels = (np.argmax(probabilities, axis=1) == true_labels).astype(int)
        
        # Fit logistic regression on (max_probs, labels)
        self.calibrator.fit(max_probs.reshape(-1, 1), labels)
        self.is_fitted = True
    
    def calibrate(self, probabilities: np.ndarray) -> np.ndarray:
        """Aplicar calibración a nuevas probabilidades"""
        if not self.is_fitted:
            raise ValueError("Fit calibrator first!")
        
        max_probs = np.max(probabilities, axis=1)
        calibrated = self.calibrator.predict_proba(
            max_probs.reshape(-1, 1)
        )[:, 1]
        
        return calibrated
    
    def expected_calibration_error(self, 
                                    predictions: np.ndarray,
                                    true_labels: np.ndarray,
                                    n_bins: int = 10) -> float:
        """Calcular ECE (Expected Calibration Error)"""
        confidences = np.max(predictions, axis=1)
        
        bins = np.linspace(0, 1, n_bins + 1)
        accs = []
        confs = []
        
        for i in range(len(bins) - 1):
            mask = (confidences >= bins[i]) & (confidences < bins[i + 1])
            if np.sum(mask) > 0:
                acc = np.mean(np.argmax(predictions[mask], axis=1) == true_labels[mask])
                conf = np.mean(confidences[mask])
                accs.append(acc)
                confs.append(conf)
        
        ece = np.mean(np.abs(np.array(accs) - np.array(confs)))
        return ece
```

---

### 3. Dataset Schema (`data/intent_training_data.json`)

```json
{
  "metadata": {
    "version": "2.0",
    "date_created": "2026-03-30",
    "total_examples": 750,
    "languages": ["es", "en"],
    "intents_count": 15,
    "examples_per_intent": 50
  },
  "training_data": [
    {
      "id": "001",
      "text": "Cambiar mensaje de bienvenida",
      "intent": "set_welcome",
      "language": "es",
      "metadata": {
        "source": "requirements_doc",
        "confidence": "high",
        "priority": "P1",
        "context": "user_onboarding"
      }
    },
    {
      "id": "002",
      "text": "Change welcome message",
      "intent": "set_welcome",
      "language": "en",
      "metadata": {
        "source": "requirements_doc",
        "confidence": "high",
        "priority": "P1"
      }
    },
    {
      "id": "003",
      "text": "Nuevo mensaje de bienvenida por favor",
      "intent": "set_welcome",
      "language": "es",
      "metadata": {
        "source": "chat_logs",
        "confidence": "medium",
        "priority": "P2",
        "variations": true
      }
    },
    // ... más 747 ejemplos (50 por intent)
  ],
  "statistics": {
    "set_welcome": 50,
    "set_goodbye": 50,
    "toggle_feature": 50,
    "add_filter": 50,
    "remove_filter": 50,
    "get_status": 50,
    "get_settings": 50,
    "update_config": 50,
    "query_data": 50,
    "execute_action": 50,
    "create_task": 50,
    "delete_task": 50,
    "assign_role": 50,
    "grant_permission": 50,
    "revoke_permission": 50
  }
}
```

---

### 4. Testing Strategy

#### Test Categories

1. **Feature Extraction Tests** (`tests/test_features.py`)
```python
def test_feature_extraction_shape():
    """Features debe tener shape correcto"""
    result = tokenization_result_fixture()
    features = feature_extractor.extract(result)
    assert features.shape == (400,)  # 400 features totales

def test_tfidf_normalization():
    """TF-IDF features deben estar normalizadas"""
    # L2 norm should be close to 1
    assert np.allclose(np.linalg.norm(features[:300]), 1.0, atol=0.1)
```

2. **Model Training Tests** (`tests/test_ml_intent_classifier.py`)
```python
def test_model_training():
    """Modelo debe entrenar sin errores"""
    X_train = feature_extractor.fit_transform(training_texts)
    y_train = training_labels
    
    classifier.train(X_train, y_train)
    
    assert classifier.model is not None
    assert os.path.exists("models/intent_classifier.joblib")

def test_prediction_shape():
    """Prediction debe tener estructura correcta"""
    result = classifier.predict(features)
    
    assert 'intent' in result
    assert 'confidence' in result
    assert 'probabilities' in result
    assert 0.0 <= result['confidence'] <= 1.0
```

3. **Ensemble Tests** (`tests/test_ensemble_classifier.py`)
```python
def test_ensemble_high_confidence_ml():
    """Si ML confidence >= 0.75, usar ML"""
    # Mock ML result with high confidence
    ensemble_result = ensemble.predict(text, tokenization_result)
    
    assert ensemble_result['method'] == 'ml_classifier'
    assert ensemble_result['confidence_level'] == 'high'

def test_ensemble_low_confidence_fallback():
    """Si ML confidence < 0.5, intentar LLM fallback"""
    # Mock ML result with low confidence
    ensemble_result = ensemble.predict(text, tokenization_result)
    
    # Should try fallback (either LLM or human review)
    assert ensemble_result['confidence_level'] in [
        'low_llm_fallback', 'failed'
    ]
```

4. **A/B Testing** (`tests/test_ab_testing.py`)
```python
def test_ab_comparison_accuracy():
    """Comparar accuracy de Regex vs ML vs Ensemble"""
    
    regex_accuracy = evaluate_regex_classifier(test_set)
    ml_accuracy = evaluate_ml_classifier(test_set)
    ensemble_accuracy = evaluate_ensemble_classifier(test_set)
    
    # ML should be significantly better than Regex
    assert ml_accuracy >= 0.75
    assert ensemble_accuracy >= ml_accuracy * 0.90
```

---

### 5. Performance Targets

| Métrica | Target | Acceptance |
|---------|--------|------------|
| **Intent Accuracy** | 78% | >= 75% |
| **Macro Precision** | 0.80 | >= 0.78 |
| **Macro Recall** | 0.75 | >= 0.72 |
| **Macro F1** | 0.77 | >= 0.75 |
| **Inference Latency** | 25ms | < 50ms |
| **Calibration (ECE)** | < 0.05 | < 0.10 |
| **Test Coverage** | 85% | >= 80% |
| **Confidence Correctness** | 90% | >= 85% |

---

### 6. Deliverables Checklist

- [ ] `data/intent_training_data.json` - 750+ ejemplos curados
- [ ] `app/nlp/features.py` - Feature extractor completamente implementado
- [ ] `app/nlp/classifiers/ml_classifier.py` - LogisticRegression classifier
- [ ] `app/nlp/classifiers/ensemble_classifier.py` - Ensemble + fallback
- [ ] `app/nlp/calibration.py` - Confidence calibration
- [ ] `models/intent_classifier.joblib` - Modelo entrenado
- [ ] `models/feature_extractor.joblib` - Vectorizer fitted
- [ ] `models/confidence_calibrator.joblib` - Calibrador
- [ ] `models/metadata.json` - Versioning info
- [ ] `tests/test_ml_intent_classifier.py` - 25+ test cases
- [ ] `tests/test_features.py` - Feature extraction tests
- [ ] `tests/test_ensemble_classifier.py` - Ensemble tests
- [ ] `reports/intent_classifier_eval.md` - Evaluación completa
- [ ] `reports/confidence_calibration.md` - Calibration report
- [ ] `reports/intent_classifier_ab_testing.md` - A/B test results
- [ ] `reports/feature_importance.md` - Feature analysis

---

## Resumen de Dependencias

### Dependencias de FASE 1
- ✅ `TokenizationResult` con lemmas, POS tags, deps
- ✅ `NLPTokenizer` funcionando correctamente
- ✅ normalizer.py completo

### Nuevas Dependencias para FASE 2
```
scikit-learn >= 1.0.0
  - LogisticRegression
  - TfidfVectorizer
  - GridSearchCV
  - cross_validate

numpy >= 1.20.0
joblib >= 1.0.0
pandas >= 1.2.0  (para análisis)
```

---

## Riesgos y Mitigación

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--|---|---|
| Dataset insufficient | Media | Alta | Curar 750+ ejemplos de múltiples fuentes |
| Overfitting | Media | Media | 5-fold cross-validation + regularization |
| LLM timeout | Baja | Media | Fallback a human review con timeout 2s |
| Feature drift | Baja | Media | Monitoring de feature distribution |
| Model serialization | Muy Baja | Media | Test serialization/deserialization |

---

## Referencias

- FASE 1: `IMPLEMENTACION_NLPL_FASE1.md`
- Plan General: `02_PLAN_IMPLEMENTACION_NLPL.md`
- Estado Inicial: `01_ESTADO_PROYECTO.md`

---

**Versión:** 2.0  
**Última actualización:** 2026-03-30  
**Estado:** SPECIFICATION COMPLETE - READY FOR IMPLEMENTATION
