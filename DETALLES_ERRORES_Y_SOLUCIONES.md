# 🔧 DETALLES TÉCNICOS - ERRORES Y SOLUCIONES

## PROBLEMA #1: integration.py - ERROR FATAL DE INDENTACIÓN

### 🔍 Código ACTUAL (ROTO)

```python
# Línea 16-30: Dentro de la clase ✓
class NLPBotIntegration:
    def __init__(self, ...):
        ...

    @property      # Línea 25 - dentro de clase ✓
    def pipeline(self):
        if self._pipeline is None:
            from app.nlp.pipeline import NLPPipeline
            self._pipeline = NLPPipeline(self.config)
        return self._pipeline  # Línea 30

@property          # Línea 31 - ❌ FUERA DE CLASE (sin indentación)
def classifier(self):  # Línea 32 - ❌ FUERA DE CLASE
    if self._classifier is None:
        from app.nlp.classifiers.ensemble_classifier import EnsembleIntentClassifier
        from app.nlp.classifiers.ml_classifier import MLIntentClassifier
        
        ml_classifier = MLIntentClassifier()
        
        self._classifier = EnsembleIntentClassifier(
            ml_classifier=ml_classifier,
            ml_weight=0.5,
            regex_weight=0.5
        )
    return self._classifier  # Línea 46

    def should_use_nlp(self, text: str) -> bool:  # Línea 48 - ❌ Parcialmente indentado
        if not text or not text.strip():
            return False
        intent, confidence = self.classifier.classify(text)
        return intent is not None and confidence >= self.min_confidence

    def process_message(self, text: str):  # ❌ Parcialmente indentado
        ...

    def get_action_for_message(self, text: str):  # ❌ Parcialmente indentado
        ...

    def classify_intent(self, text: str) -> tuple:  # ❌ Parcialmente indentado
        ...

    def is_nlp_command(self, text: str) -> bool:  # ❌ Parcialmente indentado
        ...


_integration_instance: Optional[NLPBotIntegration] = None  # Línea 85 - Fuera de clase ✓

def get_nlp_integration(...):  # Línea 88 - Función módulo ✓
    ...
```

### ✅ Código CORRECTO (debe ser)

```python
class NLPBotIntegration:
    def __init__(self, config: Optional[Any] = None, min_confidence: float = 0.5):
        from app.nlp.pipeline import PipelineConfig
        self.config = config or PipelineConfig()
        self.min_confidence = min_confidence
        self._pipeline = None
        self._classifier = None
        logger.info("NLPBotIntegration initialized")

    @property  # ← Indentado dentro de la clase
    def pipeline(self):
        if self._pipeline is None:
            from app.nlp.pipeline import NLPPipeline
            self._pipeline = NLPPipeline(self.config)
        return self._pipeline

    @property  # ← Indentado dentro de la clase
    def classifier(self):  # ← Indentado dentro de la clase
        if self._classifier is None:
            from app.nlp.classifiers.ensemble_classifier import EnsembleIntentClassifier
            from app.nlp.classifiers.ml_classifier import MLIntentClassifier
            
            ml_classifier = MLIntentClassifier()
            
            self._classifier = EnsembleIntentClassifier(
                ml_classifier=ml_classifier,
                ml_weight=0.5,
                regex_weight=0.5
            )
        return self._classifier

    def should_use_nlp(self, text: str) -> bool:  # ← Indentado dentro de la clase
        if not text or not text.strip():
            return False
        intent, confidence = self.classifier.classify(text)
        return intent is not None and confidence >= self.min_confidence

    def process_message(self, text: str):  # ← Indentado dentro de la clase
        if not text or not text.strip():
            return None
        try:
            logger.debug(f"Processing message with NLP: {text}")
            result = self.pipeline.process(text)
            logger.info(f"NLP result: action={result.action_result.action_id}, confidence={result.action_result.confidence}")
            return result
        except Exception as e:
            logger.error(f"NLP processing failed: {e}")
            return None

    def get_action_for_message(self, text: str):  # ← Indentado dentro de la clase
        result = self.process_message(text)
        if result and result.action_result.action_id:
            if result.action_result.confidence >= self.min_confidence:
                return result.action_result
        return None

    def classify_intent(self, text: str) -> tuple:  # ← Indentado dentro de la clase
        if not text or not text.strip():
            return None, 0.0
        return self.classifier.classify(text)

    def is_nlp_command(self, text: str) -> bool:  # ← Indentado dentro de la clase
        intent, confidence = self.classify_intent(text)
        return intent is not None and confidence >= self.min_confidence


# ← Fuera de la clase (correcto)
_integration_instance: Optional[NLPBotIntegration] = None


def get_nlp_integration(config: Optional[Any] = None, min_confidence: float = 0.5) -> NLPBotIntegration:
    global _integration_instance
    if _integration_instance is None:
        _integration_instance = NLPBotIntegration(config, min_confidence)
    return _integration_instance


def process_nlp_message(text: str):
    return get_nlp_integration().get_action_for_message(text)


def should_use_nlp(text: str) -> bool:
    return get_nlp_integration().should_use_nlp(text)
```

### 🔴 Por qué esto es crítico:

```
Python Parser: "Espera, ¿@property al nivel raíz? ¿self fuera de una clase?"
       ↓
Syntax Error: `def classifier(self)` con `self` no tiene sentido fuera de clase
       ↓
ImportError cuando alguien intenta: from app.nlp.integration import get_nlp_integration
       ↓
El webhook handler que intenta importar NLP → FALLA
       ↓
Todo el bot se quiebra
```

---

## PROBLEMA #2: ner.py - Dependencia Faltante

### 📍 Ubicación: `app/nlp/ner.py` línea 36

```python
def _load_spacy(self) -> None:
    try:
        import spacy  # ← ImportError: No module named 'spacy'
        self._nlp = spacy.load("es_core_news_sm")
        logger.info("spaCy NER loaded")
    except (ImportError, OSError) as e:
        logger.warning(f"spaCy not available: {e}")
        self._nlp = None  # ← Fallback: EntityExtractor funciona sin spaCy
```

### ✅ Estado Actual:
- `try/except` previene crash
- Fallback a regex patterns
- EntityExtractor usará patrones menos precisos pero funcionales

### ⚠️ Impacto:
- NER menos preciso pero tolerable
- No es tan crítico como integration.py

---

## PROBLEMA #3: NLP No Integrado en el Flujo de Webhook

### 📍 Ubicación: `app/ops/services.py:22`

```python
def handle_chat_message(chat_id: int, text: str, *, agent=None, storage=None) -> Dict[str, Any]:
    """Process a chat message using the chatbot domain service."""
    runtime = None
    if agent is None or storage is None:
        runtime = _get_default_api_runtime()
    agent = agent or runtime.agent
    storage = storage or runtime.storage

    session_id = str(chat_id)
    response = agent.process(text)  # ← ❌ SIEMPRE usa agent, NUNCA usa NLP
    storage.save(session_id, text, response.text)

    return {
        "chat_id": chat_id,
        "session_id": session_id,
        "message": text,
        "response": response.text,
        "confidence": response.confidence,
        "source": response.source,
        "pattern_matched": response.pattern_matched,
    }
```

### ⚠️ Por qué falla el bot:

```
Usuario: "cambiar mensaje de bienvenida hola usuario"
    ↓
webhook recibe → dispatch_telegram_update("cambiar...")
    ↓
dispatch clasifica como "chat_message" ✓
    ↓
process_update_impl() llama a handle_chat_message("cambiar...") ✓
    ↓
handle_chat_message() llama a agent.process("cambiar...")
    ↓
agent espera patrones como:
    - "/setwelcome hola usuario"  (comando)
    - "bienvenida: hola usuario"  (dos puntos)
    ↓
"cambiar..." NO coincide con ningún patrón
    ↓
agent intenta pattern matching genérico → falla
    ↓
respuesta genérica de chat (no la acción esperada)
    ↓
Usuario: "¿Por qué el bot no responde a comandos?"
```

### ✅ Solución (arquitectura):

Debería ser:

```python
async def process_update_impl(update, ...):
    dispatch = dispatch_telegram_update(update)
    
    if dispatch.kind == "chat_message":
        text = dispatch.text
        
        # 1. INTENTAR NLP PRIMERO
        nlp_result = get_nlp_integration().get_action_for_message(text)
        if nlp_result and nlp_result.action_id:
            # → Procesar acción NLP
            await execute_action(nlp_result.action_id, nlp_result.payload)
        else:
            # 2. FALLBACK al agent de chat
            result = handle_chat_message(chat_id, text)
            # → Devolver respuesta de chat
```

---

## 📋 RESUMEN DE QSFIX

| Problema | Archivo | Líneas | Severidad | Fix |
|----------|---------|--------|-----------|-----|
| Indentación @property | `integration.py` | 31-78 | 🔴 CRÍTICA | Indentar 4 espacios |
| Métodos fuera de clase | `integration.py` | 48-78 | 🔴 CRÍTICA | Indentar 4 espacios |
| spaCy no instalado | `ner.py` | 36 | 🟡 MEDIA | Instalar o mejorar fallback |
| NLP no integrado | `handlers.py` | ~170-300 | 🔴 CRÍTICA | Llamar get_nlp_integration() |
| NLP no en flujo | `services.py` | 22-40 | 🔴 CRÍTICA | Añadir lógica NLP antes agent |

