# Propuesta de Migración: Arquitectura NLP para el Robot

## Resumen Ejecutivo

Este documento propone una migración de arquitectura para integrar técnicas de Procesamiento del Lenguaje Natural (PLN) en el proyecto del Robot. La implementación se basa en las 5 fases del PLN descritas en el documento `NLP/nlp.md`.

---

## Estado Actual

### Arquitectura Actual

```
Usuario → Webhook → handlers.py → ActionParser (rule-based) → LLM (fallback) → Acción
```

**Componentes actuales:**
- `ActionParser`: Parser basado en reglas regex
- `_llm_parse`: Fallback usando LLM (OpenAI/Ollama)
- `ActionExecutor`: Ejecutor de acciones registradas

**Limitaciones:**
1. Regex rule-based limitado y frágil
2. No hay análisis léxico/morfológico
3. No hay comprensión semántica
4. No hay detección de intención robusta
5. LLM falla frecuentemente por rate limits

---

## Propuesta de Arquitectura NLP

### Fase 1: Pipeline NLP Propuesto

```
Usuario → normalizer → tokenizer → pos_tagger → ner → intent_classifier → entity_extractor → action_mapper → ActionExecutor
```

### Fase 2: Componentes por Capa

| Capa NLP | Función | Herramienta Propuesta |
|----------|---------|----------------------|
| Normalización | Limpiar texto (case, puntuación) | Custom + Regex |
| Tokenización | Segmentar en tokens | spaCy o NLTK |
| POS Tagging | Etiquetar partes gramaticales | spaCy |
| Análisis Morfológico | Stemming/Lematización | spaCy |
| NER | Detectar entidades | spaCy |
| Clasificación de Intención | Entender qué quiere el usuario | Hugging Face / Rule-based |
| Extracción de Entidades | Extraer parámetros de la acción | Custom |

---

## Plan de Implementación

### Fase 1: Normalización de Texto

**Objetivo:** Limpiar y estandarizar el texto de entrada

```python
# pipeline/normalizer.py
class TextNormalizer:
    def normalize(self, text: str) -> str:
        # 1. Lowercase
        text = text.lower()
        # 2. Remove numbers
        text = re.sub(r'\d+', '', text)
        # 3. Remove punctuation
        text = re.sub(r'[^\w\s]', '', text)
        # 4. Remove extra whitespace
        text = text.strip()
        return text
```

**Archivos a crear:**
- `app/nlp/normalizer.py`

### Fase 2: Tokenización y POS Tagging

**Objetivo:** Analizar estructura gramatical

```python
# pipeline/tokenizer.py
class NLPTokenizer:
    def __init__(self):
        import spacy
        self.nlp = spacy.load("es_core_news_sm")
    
    def tokenize(self, text: str):
        doc = self.nlp(text)
        return {
            "tokens": [token.text for token in doc],
            "pos_tags": [(token.text, token.pos_) for token in doc],
            "lemmas": [token.lemma_ for token in doc],
        }
```

**Archivos a crear:**
- `app/nlp/tokenizer.py`

### Fase 3: Análisis Semántico (NER)

**Objetivo:** Identificar entidades relevantes

```python
# pipeline/ner.py
class EntityExtractor:
    def __init__(self):
        import spacy
        self.nlp = spacy.load("es_core_news_sm")
    
    def extract(self, text: str):
        doc = self.nlp(text)
        return [(ent.text, ent.label_) for ent in doc.ents]
```

**Entidades a detectar:**
- `ACTION_TYPE`: bienvenido, antiflood, antispam, etc.
- `SETTING_VALUE`: on/off, números, texto
- `MODIFIER`: cambiar, activar, desactivar

### Fase 4: Clasificación de Intención

**Objetivo:** Entender qué quiere hacer el usuario

```python
# pipeline/intent_classifier.py
class IntentClassifier:
    INTENTS = {
        "set_welcome": ["bienvenida", "welcome"],
        "toggle_feature": ["activar", "desactivar", "encender", "apagar"],
        "set_limit": ["limite", "limitar", "mensajes", "segundos"],
        "add_filter": ["bloquear", "filtrar"],
        "remove_filter": ["desbloquear", "eliminar"],
    }
    
    def classify(self, text: str) -> tuple[str, float]:
        # Usar embeddings o regex para clasificar
        ...
```

**Intenciones a soportar:**
| Intención | Descripción | Ejemplo |
|-----------|-------------|---------|
| set_welcome | Establecer mensaje de bienvenida | "quiero cambiar la bienvenida" |
| toggle_feature | Activar/desactivar función | "activa antiflood" |
| set_limit | Configurar límites | "pon limite de 5 mensajes" |
| add_filter | Agregar filtro | "bloquea la palabra spam" |
| remove_filter | Quitar filtro | "desbloquea spam" |

### Fase 5: Extracción de Entidades/Acción

**Objetivo:** Mapear intención a acción específica

```python
# pipeline/action_mapper.py
class ActionMapper:
    def map(self, intent: str, entities: dict, original_text: str) -> ActionParseResult:
        if intent == "set_welcome":
            text = entities.get("welcome_text") or self._extract_welcome_text(original_text)
            return ActionParseResult(
                action_id="welcome.set_text",
                payload={"text": text},
                confidence=0.85,
            )
        # ...
```

---

## Estructura de Archivos Propuesta

```
app/
├── nlp/
│   ├── __init__.py
│   ├── normalizer.py      # Normalización de texto
│   ├── tokenizer.py       # Tokenización y POS
│   ├── ner.py            # Named Entity Recognition
│   ├── intent_classifier.py  # Clasificación de intención
│   ├── action_mapper.py  # Mapeo a acciones
│   └── pipeline.py       # Orchestrator del pipeline
├── agent/
│   └── actions/
│       └── parser.py     # Actual - mantener compatibilidad
```

---

## Comparación: Actual vs Propuesto

| Aspecto | Actual | Propuesto |
|---------|--------|-----------|
| Tokenización | Regex simple | spaCy/NLTK |
| Lemmatización | No | spaCy |
| POS Tagging | No | spaCy |
| NER | No | spaCy |
| Intención | Regex + LLM | Clasificador dedicado |
| Fallback LLM | Siempre | Solo cuando sea necesario |
| Manejo de errores | Limitado | Robusto con múltiples capas |

---

## Casos de Uso Mejorados

### Caso 1: Mensaje Ambiguo

**Input:** "Quiero cambiar el mensaje de bienvenida"

| Paso | Actual | Propuesto |
|------|--------|-----------|
| Normalización | No | "quiero cambiar el mensaje de bienvenida" |
| Tokenización | N/A | ["quiero", "cambiar", "mensaje", "bienvenida"] |
| POS | N/A | [VERB, VERB, NOUN, NOUN] |
| Intención | Regex → toggle | Classifier → "set_welcome" |
| Entidades | Ninguna | {intent: "set_welcome"} |
| Acción | welcome.toggle | Preguntar por texto O usar LLM |

### Caso 2: Mensaje con Entidades

**Input:** "Pon antiflood con 10 mensajes en 5 segundos"

| Paso | Actual | Propuesto |
|------|--------|-----------|
| NER | Regex manual | {limit: 10, interval: 5} |
| Acción | antiflood.set_limits | antiflood.set_limits |

---

## Implementación por Fases

### Fase 1: Normalizador (Semana 1)
- [ ] Crear `app/nlp/normalizer.py`
- [ ] Integrar en `ActionParser.parse()`
- [ ] Tests unitarios

### Fase 2: Tokenizador (Semana 2)
- [ ] Crear `app/nlp/tokenizer.py` con spaCy
- [ ] Agregar análisis POS al parser
- [ ] Tests de integración

### Fase 3: NER y Clasificación (Semana 3)
- [ ] Crear `app/nlp/intent_classifier.py`
- [ ] Crear `app/nlp/ner.py`
- [ ] Definir intents principales

### Fase 4: Action Mapper (Semana 4)
- [ ] Crear `app/nlp/action_mapper.py`
- [ ] Migrar reglas existentes
- [ ] Tests end-to-end

### Fase 5: Pipeline Integrado (Semana 5)
- [ ] Crear `app/nlp/pipeline.py`
- [ ] Reemplazar `ActionParser` gradualmente
- [ ] Documentación

---

## Dependencias Requeridas

```python
# requirements.txt
spacy>=3.7.0
# python -m spacy download es_core_news_sm
nltk>=3.8.0
# nltk.download('punkt')
# nltk.download('stopwords')
# nltk.download('wordnet')
scikit-learn>=1.3.0  # Para clasificadores
numpy>=1.24.0
```

---

## Recomendaciones

1. **Mantener backwards compatibility**: El `ActionParser` actual debe seguir funcionando como fallback
2. **Agregar logging en cada fase**: Facilita debugging
3. **Progressive enhancement**: Empezar con regex, agregar NLP gradualmente
4. **Fallback a LLM**: Usar LLM solo cuando el pipeline NLP no pueda determinar la acción

---

## Métricas de Éxito

| Métrica | Actual | Objetivo |
|---------|--------|----------|
| Accuracy de parseo | ~60% | >90% |
| Tiempo de respuesta | ~500ms | <300ms |
| Fallback a LLM | 100% cuando falla | <30% |
| Cobertura de intents | 5 | 20+ |

---

## Conclusión

Esta migración transforma el parser actual basado en reglas frágiles en un pipeline robusto de NLP con múltiples capas de análisis. La implementación gradual permite validar cada componente antes de reemplazar completamente el sistema actual.
