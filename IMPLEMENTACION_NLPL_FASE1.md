# IMPLEMENTACIÓN NLP - FASE 1: TOKENIZACIÓN & NORMALIZACIÓN MEJORADA

Fecha: 2026-03-30
Versión: 1.0
Referencia: `02_PLAN_IMPLEMENTACION_NLPL.md` - Sección "FASE 1: Tokenización & Normalización Mejorada"

---

## Resumen de la Migración

La **Fase 1** constituye la base fundamental para mejorar la calidad del procesamiento del lenguaje natural. Se enfoca en **fortalecer los componentes de entrada** que actualmente son débiles (tokenización simple, normalización básica).

### Cambio Principal
```
Actual: texto → split() simple → tokens sin estructura
        ↓
Esperado: texto → Normalización profunda → Tokenización lingüística → 
          POS tagging → Lemmatización → Dependency parsing
```

### Impacto Esperado
- **Intent Classification Accuracy**: 50% → 75% (con ML classifier en Fase 2)
- **Entity Recognition Precision**: +20% (mejor tokens → mejor NER)
- **Latencia**: +15ms (aceptable para mejor calidad)
- **Mantenibilidad**: ↑↑ (código estructurado y testeable)

### Duración
- **Estimación**: 2 semanas (10 días laborales)
- **Recursos**: 1 ingeniero senior + 1 junior para tests
- **Riesgo**: Bajo (cambios localizados, backward compatible)

---

## Arquitectura Final (Fase 1)

```
┌──────────────────────────────────────────────────────────┐
│                  TEXT INPUT                              │
│          "Cambiar mensaje de bienvenida"                 │
└────────────────────┬─────────────────────────────────────┘
                     ▼
         ┌──────────────────────────────┐
         │ NORMALIZATION LAYER (NUEVO)  │
         ├──────────────────────────────┤
         │ ✓ Remove diacríticos         │
         │ ✓ Handle contractions        │
         │ ✓ Expand abbreviations       │
         │ ✓ Lowercase (contextual)     │
         │ ✓ Remove extra whitespace    │
         └────────────┬──────────────────┘
                      ▼
       "cambiar mensaje de bienvenida"
                      ▼
         ┌──────────────────────────────┐
         │ TOKENIZATION LAYER           │
         ├──────────────────────────────┤
         │ spaCy-based tokenization     │
         │ (linguistic boundaries)      │
         └────────────┬──────────────────┘
                      ▼
    ["cambiar", "mensaje", "de", "bienvenida"]
                      ▼
         ┌──────────────────────────────┐
         │ POS TAGGING (NUEVO)          │
         ├──────────────────────────────┤
         │ VERB, NOUN, ADP, NOUN        │
         └────────────┬──────────────────┘
                      ▼
    [("cambiar", "VERB"), ("mensaje", "NOUN"),
     ("de", "ADP"), ("bienvenida", "NOUN")]
                      ▼
         ┌──────────────────────────────┐
         │ LEMMATIZATION (NUEVO)        │
         ├──────────────────────────────┤
         │ cambiar→cambiar              │
         │ mensaje→mensaje              │
         │ de→de                        │
         │ bienvenida→bienvenido        │
         └────────────┬──────────────────┘
                      ▼
    ["cambiar", "mensaje", "de", "bienvenido"]
                      ▼
         ┌──────────────────────────────┐
         │ DEPENDENCY PARSING (NUEVO)   │
         ├──────────────────────────────┤
         │ Identifica: ROOT, OBJ, CASE  │
         │ Estructura: cambiar → objeto │
         │            mensaje ← preposición
         │            bienvenida ← tipo │
         └────────────┬──────────────────┘
                      ▼
         ┌──────────────────────────────┐
         │ TokenizationResult (OUTPUT)  │
         ├──────────────────────────────┤
         │ tokens: [...]                │
         │ pos_tags: [...]              │
         │ lemmas: [...]                │
         │ deps: ['ROOT', 'OBJ', ...]   │
         │ intent_hint: 'set_*'         │
         └────────────────────────────────┘
```

### Componentes Modificados

```
app/nlp/
│
├── normalizer.py (REFACTORIZADO)
│   ├── TextNormalizer
│   │   ├── remove_diacritics()     [NUEVO]
│   │   ├── expand_contractions()   [NUEVO]
│   │   ├── normalize_whitespace()  [MEJORADO]
│   │   └── normalize_case()        [MEJORADO]
│   │
│   └── Normalization Rules
│       ├── Spanish contractions    [NUEVO]
│       ├── Common typos           [NUEVO]
│       └── Entity-aware rules     [NUEVO]
│
├── tokenizer.py (REFACTORIZADO)
│   ├── NLPTokenizer
│   │   ├── tokenize()             [MEJORADO]
│   │   ├── lazy loading           [MANTENIDA]
│   │   └── spaCy integration      [MEJORADA]
│   │
│   └── TokenizationResult        [EXPANDIDA]
│       ├── tokens               [EXISTENTE]
│       ├── pos_tags             [NUEVO]
│       ├── lemmas               [NUEVO]
│       ├── deps                 [NUEVO]
│       ├── intent_hint          [NUEVO]
│       ├── get_nouns()          [EXISTENTE]
│       ├── get_verbs()          [EXISTENTE]
│       ├── get_adjectives()     [NUEVO]
│       ├── get_lemmas_for_nouns() [NUEVO]
│       └── get_dependencies()   [NUEVO]
│
└── tests/
    ├── test_normalizer.py       [NUEVO]
    ├── test_tokenizer_enhanced.py [NUEVO]
    └── test_integration.py      [NUEVO]
```

---

## Tabla de Tareas

### Desglose Detallado de Tareas Fase 1

| ID | Tarea | Descripción | Prioridad | Estimación | Dependencias | Status |
|---|---|---|---|---|---|---|
| **T1.1** | Mejorar normalización: diacríticos, contracciones | Agregar reglas para normalizar caracteres acentuados, contracciones españolas (p.ej., "p'al" → "para el") | Alta | 2d | Ninguna | TODO |
| **T1.2** | Implementar lemmatización con spaCy | Usar `token.lemma_` de spaCy para obtener forma base de palabras (running → run, bienvenida → bienvenido) | Alta | 2d | T1.5 | TODO |
| **T1.3** | Agregar POS tagging a TokenizationResult | Expandir TokenizationResult para incluir `pos_tags: List[Tuple[str, str]]` (token, POS) | Alta | 1d | T1.5 | TODO |
| **T1.4** | Implementar dependency parsing | Agregar análisis de dependencias syntácticas (subject, object, modifiers) para mejor comprensión sintáctica | Media | 2d | T1.5 | TODO |
| **T1.5** | Crear cache de modelos spaCy | Implementar caching eager (no lazy) de modelos spaCy para evitar cargas repetidas en cada request | Media | 1d | Ninguna | TODO |
| **T1.6** | Tests unitarios para tokenización | Escribir suite completa: test_normalize, test_tokenize, test_lemma, test_deps, test_intent_hint con 85%+ coverage | Alta | 2d | T1.1-T1.4 | TODO |
| **T1.7** | Benchmark de performance | Medir latencia, memory, throughput antes/después; documentar en `/reports/phase1_benchmark.md` | Media | 1d | T1.6 | TODO |

---

### Timeline Gantt (Semanas 1-2)

```
SEMANA 1
┌─────────────────────────────────────────────────────┐
│ Lun │ Mar │ Mié │ Jue │ Vie │
├─────────────────────────────────────────────────────┤
│ T1.5: Cache     T1.1: Norm         T1.2: Lemma      │
│ ┌────┐       ┌──────────────┐    ┌──────────────┐  │
│ │███ │       │████████████  │    │████████████  │  │
│ └────┘       └──────────────┘    └──────────────┘  │
│              T1.3: POS        T1.4: Deps           │
│              ┌──────┐         ┌──────────────┐     │
│              │████  │         │████████████  │     │
│              └──────┘         └──────────────┘     │
└─────────────────────────────────────────────────────┘

SEMANA 2
┌─────────────────────────────────────────────────────┐
│ Lun │ Mar │ Mié │ Jue │ Vie │
├─────────────────────────────────────────────────────┤
│              T1.6: Tests                T1.7: Bench │
│              ┌──────────────────────┐  ┌──────┐    │
│              │████████████████████  │  │████  │    │
│              └──────────────────────┘  └──────┘    │
│                                                     │
│              ✓ Code Review & Merge                 │
│              ✓ Integration Tests                   │
│              ✓ Deploy to Staging                  │
└─────────────────────────────────────────────────────┘
```

---

## Fase: Tokenización & Normalización Mejorada

### Objetivo Fase

**Objetivo Principal:**
Fortalecer el **pipeline de preprocesamiento de texto** para que el sistema comprenda mejor la estructura lingüística, mejorando la precisión de componentes downstream (intent classification, NER, similarity matching).

**Objetivos Secundarios:**
1. Implementar normalization rules robustas (diacríticos, contracciones)
2. Agregar analysis lingüístico (POS, dependencies, lemmas)
3. Mantener backward compatibility con código existente
4. Establecer baseline de performance para mejoras futuras

**Métricas de Éxito:**
- ✓ TokenizationResult contiene: tokens, pos_tags, lemmas, deps
- ✓ Intent hint detection accuracy >= 85%
- ✓ Tests coverage >= 85%
- ✓ Latencia <= +20ms vs baseline
- ✓ 0 breaking changes en código cliente

---

### Implementación Fase

#### T1.1: MEJORAR NORMALIZACIÓN (Días 2-3)

**Descripción:**
Expandir `TextNormalizer` con reglas avanzadas para español.

**Cambios en `app/nlp/normalizer.py`:**

```python
import unicodedata
import re
from typing import Dict, List

class EnhancedTextNormalizer:
    """Normalización mejorada para texto español"""
    
    # Spanish contractions mapping
    CONTRACTIONS = {
        "p'al": "para el",
        "p'al": "para al",
        "d'elas": "de elas",
        "n'est": "no est",
        "tá": "está",
        "q'el": "que el",
        "acá": "aquí",  # Regional variants
    }
    
    # Typo corrections
    TYPOS = {
        "que quieres": "qué quieres",  # Acento
        "eston": "esto en",  # Spacing
        "porfa": "por favor",  # Slang
    }
    
    # Whitespace normalization
    WHITESPACE_PATTERN = re.compile(r'\s+')
    
    # Diacritical marks
    DIACRITICS_MAP = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'ñ': 'n', 'ü': 'u',
    }
    
    def __init__(self, keep_diacritics: bool = True):
        """
        Args:
            keep_diacritics: Si False, remueve acentos (útil para búsqueda)
        """
        self.keep_diacritics = keep_diacritics
    
    def normalize(self, text: str) -> str:
        """Pipeline completo de normalización"""
        if not text:
            return text
        
        # 1. Expandir contracciones
        text = self._expand_contractions(text)
        
        # 2. Corregir typos comunes
        text = self._fix_typos(text)
        
        # 3. Remover diacríticos (opcional)
        if not self.keep_diacritics:
            text = self._remove_diacritics(text)
        
        # 4. Normalizar whitespace
        text = self._normalize_whitespace(text)
        
        # 5. Normalizar mayúsculas (contextual)
        text = self._normalize_case(text)
        
        return text.strip()
    
    def _expand_contractions(self, text: str) -> str:
        """Expande contracciones españolas"""
        for contraction, expansion in self.CONTRACTIONS.items():
            text = re.sub(rf'\b{re.escape(contraction)}\b', expansion, text, flags=re.IGNORECASE)
        return text
    
    def _fix_typos(self, text: str) -> str:
        """Corrige typos y variaciones comunes"""
        for typo, correct in self.TYPOS.items():
            text = re.sub(rf'\b{re.escape(typo)}\b', correct, text, flags=re.IGNORECASE)
        return text
    
    def _remove_diacritics(self, text: str) -> str:
        """Remueve acentos y diacríticos"""
        # Método Unicode (preserva ñ como opción)
        nfd_form = unicodedata.normalize('NFD', text)
        return ''.join(c for c in nfd_form if unicodedata.category(c) != 'Mn')
    
    def _normalize_whitespace(self, text: str) -> str:
        """Normaliza espacios múltiples"""
        text = self.WHITESPACE_PATTERN.sub(' ', text)  # Multiple spaces → single
        text = re.sub(r'\n+', ' ', text)  # Newlines → space
        return text
    
    def _normalize_case(self, text: str) -> str:
        """Normaliza mayúsculas de forma inteligente"""
        # Convertir a minúsculas PERO preservar:
        # - Acrónimos (todas caps)
        # - Nombres propios (detectar por patrones)
        
        words = text.split()
        result = []
        
        for word in words:
            # Si es todo mayúsculas y > 2 caracteres, probablemente sea acrónimo
            if word.isupper() and len(word) > 2:
                result.append(word)  # Mantener
            else:
                result.append(word.lower())
        
        return ' '.join(result)
```

**Tests:**
```python
def test_expand_contractions():
    normalizer = EnhancedTextNormalizer()
    
    assert normalizer.normalize("Dame p'al kitchen") == "dame para el kitchen"
    assert normalizer.normalize("N'est aquí") == "no est aqui"

def test_remove_diacritics():
    normalizer = EnhancedTextNormalizer(keep_diacritics=False)
    
    assert normalizer.normalize("Hola, ¿cómo estás?") == "hola como estas"
    assert normalizer.normalize("Niño") == "nino"

def test_normalize_whitespace():
    normalizer = EnhancedTextNormalizer()
    
    text = "Hola   mundo\n\ntest"
    expected = "hola mundo test"
    assert normalizer.normalize(text) == expected

def test_typo_correction():
    normalizer = EnhancedTextNormalizer()
    
    assert normalizer.normalize("porfa ayuda") == "por favor ayuda"
```

**Deliverable:**
- ✓ EnhancedTextNormalizer implementado
- ✓ Manejo de contracciones
- ✓ Opción de remover diacríticos
- ✓ Tests >= 90% coverage

---

#### T1.2: IMPLEMENTAR LEMMATIZACIÓN (Días 3-4)

**Descripción:**
Expandir TokenizationResult con lemmas usando spaCy.

**Cambios en `app/nlp/tokenizer.py`:**

```python
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

@dataclass
class TokenizationResult:
    tokens: List[str]
    pos_tags: List[Tuple[str, str]] = field(default_factory=list)
    lemmas: List[str] = field(default_factory=list)  # NUEVO
    deps: List[Tuple[str, str]] = field(default_factory=list)  # NUEVO
    text: str = ""
    intent_hint: Optional[str] = None  # NUEVO
    
    def get_nouns(self) -> List[str]:
        """Retorna sustantivos"""
        return [token for token, pos in self.pos_tags if pos == "NOUN"]
    
    def get_verbs(self) -> List[str]:
        """Retorna verbos"""
        return [token for token, pos in self.pos_tags if pos == "VERB"]
    
    def get_adjectives(self) -> List[str]:  # NUEVO
        """Retorna adjetivos"""
        return [token for token, pos in self.pos_tags if pos == "ADJ"]
    
    def get_lemmas_for_nouns(self) -> List[str]:  # NUEVO
        """Retorna lemmas solo de sustantivos"""
        noun_indices = [i for i, (_, pos) in enumerate(self.pos_tags) if pos == "NOUN"]
        return [self.lemmas[i] for i in noun_indices]
    
    def get_dependencies(self) -> List[str]:  # NUEVO
        """Retorna lista de dependencias sintácticas"""
        return [dep for _, dep in self.deps]
    
    def has_word(self, word: str) -> bool:
        """Chequea si palabra está en tokens (case-insensitive)"""
        return word.lower() in [t.lower() for t in self.tokens]
    
    def has_lemma(self, lemma: str) -> bool:  # NUEVO
        """Chequea si lemma está en lemmas (case-insensitive)"""
        return lemma.lower() in [l.lower() for l in self.lemmas]

class NLPTokenizer:
    def tokenize(self, text: str) -> TokenizationResult:
        """Tokeniza texto con análisis lingüístico completo"""
        if not text or not text.strip():
            return TokenizationResult(tokens=[], text=text)
        
        self._ensure_model_loaded()
        doc = self._nlp(text)
        
        # Extraer información
        tokens = [token.text for token in doc]
        pos_tags = [(token.text, token.pos_) for token in doc]
        lemmas = [token.lemma_ for token in doc]
        deps = [
            (token.text, token.dep_) for token in doc
        ]
        
        # Detectar intent hint
        intent_hint = self._detect_intent_hint(lemmas)
        
        return TokenizationResult(
            tokens=tokens,
            pos_tags=pos_tags,
            lemmas=lemmas,
            deps=deps,
            text=text,
            intent_hint=intent_hint
        )
    
    def _detect_intent_hint(self, lemmas: List[str]) -> Optional[str]:
        """Detecta intent hints tempranos basado en lemmas"""
        hint_keywords = {
            "set_welcome": ["cambiar", "configurar", "establecer", "definir", "bienvenida"],
            "set_goodbye": ["despedida", "adiós", "salida", "cambiar"],
            "toggle_feature": ["activar", "desactivar", "encender", "apagar", "on", "off"],
            "add_filter": ["bloquear", "filtrar", "agregar", "añadir"],
            "remove_filter": ["eliminar", "quitar", "desbloquear", "remover"],
        }
        
        lemmas_lower = [l.lower() for l in lemmas]
        
        for intent, keywords in hint_keywords.items():
            if any(kw in lemmas_lower for kw in keywords):
                return intent
        
        return None
```

**Tests:**
```python
def test_lemmatization():
    tokenizer = NLPTokenizer()
    result = tokenizer.tokenize("Los niños están corriendo")
    
    assert result.lemmas == ["el", "niño", "estar", "correr"]
    assert result.get_lemmas_for_nouns() == ["el", "niño"]

def test_intent_hint_detection():
    tokenizer = NLPTokenizer()
    
    result = tokenizer.tokenize("Cambiar mensaje de bienvenida")
    assert result.intent_hint == "set_welcome"
    
    result = tokenizer.tokenize("Bloquear palabra malas")
    assert result.intent_hint == "add_filter"

def test_pos_tags():
    tokenizer = NLPTokenizer()
    result = tokenizer.tokenize("El gato corre")
    
    assert result.get_nouns() == ["gato"]
    assert result.get_verbs() == ["corre"]
```

**Deliverable:**
- ✓ Lemmas en TokenizationResult
- ✓ Intent hint detection
- ✓ Helper methods para acceso
- ✓ Tests exhaustivos

---

#### T1.3: AGREGAR POS TAGGING (Día 5)

Ya incluido en T1.2. El `pos_tags` está en TokenizationResult como `List[Tuple[str, str]]`.

**Validación:**
```python
def test_pos_tagging():
    tokenizer = NLPTokenizer()
    result = tokenizer.tokenize("Cambiar la bienvenida")
    
    pos_dict = dict(result.pos_tags)
    assert pos_dict["Cambiar"] == "VERB"
    assert pos_dict["bienvenida"] == "NOUN"
    assert pos_dict["la"] == "DET"
```

---

#### T1.4: IMPLEMENTAR DEPENDENCY PARSING (Días 5-6)

**Descripción:**
Agregar análisis de dependencias sintácticas.

**En `app/nlp/tokenizer.py` (ya incluido en tokenize()):**

```python
def tokenize(self, text: str) -> TokenizationResult:
    """..."""
    doc = self._nlp(text)
    
    # Dependencias sintácticas
    deps = [(token.text, token.dep_) for token in doc]
    
    # Opcional: crear estructura más compleja
    dependencies_graph = {
        "heads": [token.head.text for token in doc],
        "deps": [token.dep_ for token in doc],
        "tree": self._build_dependency_tree(doc)
    }
    
    # ...resto del código

def _build_dependency_tree(self, doc) -> Dict[str, Any]:
    """Construye árbol de dependencias para visualización"""
    tree = {}
    for token in doc:
        if token.dep_ == "ROOT":
            tree["root"] = token.text
        else:
            head_text = token.head.text
            if head_text not in tree:
                tree[head_text] = []
            tree[head_text].append({
                "text": token.text,
                "dep": token.dep_
            })
    return tree
```

**Ejemplo de output:**
```
Input: "Cambiar el mensaje de bienvenida"

deps:
  [("Cambiar", "ROOT"),
   ("el", "DET"),
   ("mensaje", "OBJ"),
   ("de", "CASE"),
   ("bienvenida", "NMOD")]

tree:
  {
    "root": "Cambiar",
    "Cambiar": [
      {"text": "mensaje", "dep": "OBJ"}
    ],
    "mensaje": [
      {"text": "el", "dep": "DET"},
      {"text": "bienvenida", "dep": "NMOD"}
    ]
  }
```

**Test:**
```python
def test_dependency_parsing():
    tokenizer = NLPTokenizer()
    result = tokenizer.tokenize("Cambiar el mensaje")
    
    deps_dict = dict(result.deps)
    assert deps_dict["Cambiar"] == "ROOT"
    assert "OBJ" in deps_dict.values()
```

#### T1.5: CREAR CACHE DE MODELOS SPACY (Día 1)

**Descripción:**
Actualmente spaCy se carga lazy en cada request. Convertir a eager loading con cache para mejor performance.

**Cambios en `app/nlp/tokenizer.py`:**

```python
# ANTES (Lazy Loading)
class NLPTokenizer:
    def __init__(self, model_name: str = "es_core_news_sm", lazy_load: bool = True):
        self.model_name = model_name
        self._nlp = None
        self._lazy_load = lazy_load
        if not lazy_load:
            self._load_model()

# DESPUÉS (Eager + Cache)
import threading

_SPACY_MODELS_CACHE = {}
_CACHE_LOCK = threading.Lock()

class NLPTokenizer:
    def __init__(self, model_name: str = "es_core_news_sm", use_cache: bool = True):
        self.model_name = model_name
        self._nlp = None
        self.use_cache = use_cache
        self._ensure_model_loaded()  # Eager load
    
    def _ensure_model_loaded(self) -> None:
        if self.use_cache:
            with _CACHE_LOCK:
                if self.model_name not in _SPACY_MODELS_CACHE:
                    self._load_model()
                    _SPACY_MODELS_CACHE[self.model_name] = self._nlp
                else:
                    self._nlp = _SPACY_MODELS_CACHE[self.model_name]
        else:
            self._load_model()
    
    def _load_model(self) -> None:
        try:
            import spacy
            self._nlp = spacy.load(self.model_name)
            logger.info(f"Loaded spaCy model: {self.model_name}")
        except (ImportError, OSError) as e:
            logger.error(f"Failed to load spaCy model: {e}")
            raise RuntimeError(f"Cannot load spaCy model: {self.model_name}")
```

**Testing:**
```python
def test_spacy_cache():
    """Verifica que el modelo se carga una sola vez"""
    import time
    
    # Clear cache
    _SPACY_MODELS_CACHE.clear()
    
    # Primera instancia (carga el modelo)
    start = time.time()
    tokenizer1 = NLPTokenizer()
    time1 = time.time() - start
    
    # Segunda instancia (usa cache)
    start = time.time()
    tokenizer2 = NLPTokenizer()
    time2 = time.time() - start
    
    # La segunda debe ser mucho más rápida
    assert time2 < time1 / 5, f"Cache no funcionó: {time1}ms vs {time2}ms"
    
    # Deben apuntar al mismo modelo
    assert tokenizer1._nlp is tokenizer2._nlp
```

**Deliverable:**
- ✓ Cache implementado
- ✓ Thread-safe con locks
- ✓ Tests de validación
- ✓ Backward compatible

---

---

#### T1.6: TESTS UNITARIOS (Días 7-8)

**Suite de Tests Completa:**

```python
# tests/test_phase1_integration.py

import pytest
from app.nlp.normalizer import EnhancedTextNormalizer
from app.nlp.tokenizer import NLPTokenizer, TokenizationResult

class TestNormalization:
    def test_contractions(self):
        norm = EnhancedTextNormalizer()
        assert norm.normalize("p'al kitchen") == "para el kitchen"
    
    def test_whitespace(self):
        norm = EnhancedTextNormalizer()
        assert norm.normalize("Hola   mundo") == "hola mundo"
    
    def test_diacritics(self):
        norm = EnhancedTextNormalizer(keep_diacritics=False)
        assert norm.normalize("Hola, ¿cómo estás?") == "hola como estas"

class TestTokenization:
    @pytest.fixture
    def tokenizer(self):
        return NLPTokenizer()
    
    def test_basic_tokenization(self, tokenizer):
        result = tokenizer.tokenize("Hola mundo")
        assert result.tokens == ["Hola", "mundo"]
    
    def test_pos_tagging(self, tokenizer):
        result = tokenizer.tokenize("El gato duerme")
        assert dict(result.pos_tags)["gato"] == "NOUN"
        assert dict(result.pos_tags)["duerme"] == "VERB"
    
    def test_lemmatization(self, tokenizer):
        result = tokenizer.tokenize("corriendo")
        assert "correr" in result.lemmas
    
    def test_intent_hint(self, tokenizer):
        result = tokenizer.tokenize("Cambiar bienvenida")
        assert result.intent_hint == "set_welcome"
    
    def test_get_nouns(self, tokenizer):
        result = tokenizer.tokenize("El perro y el gato")
        nouns = result.get_nouns()
        assert "perro" in nouns
        assert "gato" in nouns
    
    def test_get_lemmas_for_nouns(self, tokenizer):
        result = tokenizer.tokenize("Los perros corren")
        lemmas = result.get_lemmas_for_nouns()
        assert "perro" in lemmas

class TestBackwardCompatibility:
    def test_old_tokenize_still_works(self):
        """Verifica que código viejo siga funcionando"""
        tokenizer = NLPTokenizer()
        result = tokenizer.tokenize("Hola")
        
        # Propiedades antiguas
        assert result.tokens
        assert result.text
```

**Coverage Target:** >= 85%

**Deliverable:**
- ✓ 25+ tests
- ✓ Coverage report
- ✓ CI/CD integration

---

#### T1.7: BENCHMARK DE PERFORMANCE (Día 9)

**Script de Benchmark:**

```python
# scripts/benchmark_phase1.py

import time
import json
from pathlib import Path
from app.nlp.tokenizer import NLPTokenizer
from app.nlp.normalizer import EnhancedTextNormalizer

def benchmark():
    """Evalúa performance antes/después"""
    
    test_texts = [
        "Cambiar mensaje de bienvenida",
        "Bloquear palabra malas",
        "¿Cuál es el estado del antiflood?",
        "p'al sistema de mensajería",
    ]
    
    normalizer = EnhancedTextNormalizer()
    tokenizer = NLPTokenizer()
    
    results = {}
    
    # Benchmark normalización
    times_norm = []
    for text in test_texts * 100:  # 400 iterations
        start = time.perf_counter()
        normalizer.normalize(text)
        times_norm.append(time.perf_counter() - start)
    
    results['normalization'] = {
        'avg_ms': (sum(times_norm) / len(times_norm)) * 1000,
        'min_ms': min(times_norm) * 1000,
        'max_ms': max(times_norm) * 1000,
    }
    
    # Benchmark tokenización
    times_tok = []
    for text in test_texts * 100:
        start = time.perf_counter()
        tokenizer.tokenize(text)
        times_tok.append(time.perf_counter() - start)
    
    results['tokenization'] = {
        'avg_ms': (sum(times_tok) / len(times_tok)) * 1000,
        'min_ms': min(times_tok) * 1000,
        'max_ms': max(times_tok) * 1000,
    }
    
    # Pipeline completo
    times_pipeline = []
    for text in test_texts * 100:
        start = time.perf_counter()
        normalized = normalizer.normalize(text)
        result = tokenizer.tokenize(normalized)
        times_pipeline.append(time.perf_counter() - start)
    
    results['pipeline'] = {
        'avg_ms': (sum(times_pipeline) / len(times_pipeline)) * 1000,
        'min_ms': min(times_pipeline) * 1000,
        'max_ms': max(times_pipeline) * 1000,
    }
    
    # Guardar report
    report_path = Path("reports/phase1_benchmark.md")
    report_path.parent.mkdir(exist_ok=True)
    
    with open(report_path, 'w') as f:
        f.write("# Phase 1 Performance Benchmark\n\n")
        f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Results\n\n")
        for component, metrics in results.items():
            f.write(f"### {component.title()}\n")
            f.write(f"- Average: {metrics['avg_ms']:.2f}ms\n")
            f.write(f"- Min: {metrics['min_ms']:.2f}ms\n")
            f.write(f"- Max: {metrics['max_ms']:.2f}ms\n\n")
        
        f.write("## Targets\n")
        f.write("- Normalization: < 5ms (✓ if avg < 5)\n")
        f.write("- Tokenization: < 30ms (✓ if avg < 30)\n")
        f.write("- Pipeline: < 35ms (✓ if avg < 35)\n")
    
    print(f"Benchmark report: {report_path}")
    return results

if __name__ == "__main__":
    benchmark()
```

**Expected Results:**
```
┌──────────────────┬─────────┬────────┬────────┐
│ Component        │ Avg(ms) │ Min(ms)│ Max(ms)│
├──────────────────┼─────────┼────────┼────────┤
│ Normalization    │  2.5    │  1.2   │  8.3   │
│ Tokenization     │ 22.1    │ 18.5   │ 35.2   │
│ Pipeline Total   │ 24.6    │ 20.1   │ 42.3   │
└──────────────────┴─────────┴────────┴────────┘

Status: ✓ PASS (pipeline < 35ms)
```

**Deliverable:**
- ✓ Benchmark script
- ✓ Performance report
- ✓ Comparativa baseline

---

## Checklist de Completado

Una vez que se completen todas las tareas, verificar:

- [ ] T1.1: `EnhancedTextNormalizer` implementado
- [ ] T1.2: Lemmatización funcional en `TokenizationResult`
- [ ] T1.3: POS tagging en `TokenizationResult`
- [ ] T1.4: Dependency parsing en `TokenizationResult`
- [ ] T1.5: Caching eagerde spaCy modelos
- [ ] T1.6: Tests suite (25+ tests, 85%+ coverage)
- [ ] T1.7: Benchmark report en `reports/phase1_benchmark.md`
- [ ] Todos los tests pasan en CI/CD
- [ ] Backward compatibility verificada
- [ ] Documentación actualizada (docstrings)
- [ ] Code review aprobado
- [ ] Merge a rama `develop`
- [ ] Deploy a staging

---

## Criterios de Aceptación

### Funcionalidad
- ✓ `TokenizationResult` contiene: tokens, pos_tags, lemmas, deps, intent_hint
- ✓ Normalización maneja: diacríticos, contracciones, whitespace, typos
- ✓ Lemmatización usa spaCy correctamente
- ✓ Intent hints detectan >= 80% de intents

### Tests
- ✓ Coverage >= 85%
- ✓ Todos los tests pasan
- ✓ Tests de regresión verifican backward compatibility

### Performance
- ✓ Normalización: <= 5ms
- ✓ Tokenización: <= 30ms
- ✓ Pipeline total: <= 35ms
- ✓ Memory overhead: <= 50MB

### Code Quality
- ✓ No breaking changes
- ✓ Docstrings completos
- ✓ Type hints en todas las funciones
- ✓ Logging apropiado
- ✓ Error handling robusto

---

## Próximos Pasos (Post-Fase 1)

Una vez completada la Fase 1, proceder inmediatamente a:

1. **Fase 2** (Semanas 3-4): Machine Learning Intent Classifier
   - Curar dataset de 50+ ejemplos
   - Entrenar Logistic Regression
   - A/B testing: Regex vs ML vs Ensemble

2. **Integraciones**: Usar TokenizationResult mejorado en:
   - `IntentClassifier` (usar lemmas + intent_hint)
   - `EntityExtractor` (mejor NER con POS context)
   - `ActionMapper` (usar dependencias sintácticas)

---

## Referencias & Documentación

- spaCy Spanish Model: https://spacy.io/models/es
- POS Tags Reference: https://spacy.io/api/annotation/#pos-tagging
- Dependency Labels: https://spacy.io/api/annotation/#dependency-parsing
- Plan General: `02_PLAN_IMPLEMENTACION_NLPL.md`
- Estado Proyecto: `01_ESTADO_PROYECTO.md`

---

**Documento creado:** 2026-03-30
**Versión:** 1.0
**Estado:** LISTO PARA IMPLEMENTACIÓN
