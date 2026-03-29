# Integracion NLP con Robot Telegram

---

**Fecha:** 29/03/2026

**Version:** 1.0

---

## Resumen

Este documento describe la integracion del sistema NLP con el Robot de administracion de grupos de Telegram. El bot ahora puede entender instrucciones en lenguaje natural y procesarlas de manera inteligente.

---

## Arquitectura

```
Telegram User Message
        ↓
dispatch_telegram_update() 
        ↓
AgentCore.process_async()
        ↓
┌───────────────────────────────────────┐
│     NLP Integration Layer             │
├───────────────────────────────────────┤
│ IntentRouter (MEJORADO CON NLP)       │
│        ↓                             │
│ NLPPipeline                          │
│        ↓                             │
│ ActionParser                         │
└───────────────────────────────────────┘
        ↓
ActionExecutor → Action Registry
```

---

## Componentes NLP

### 1. Normalizer (`app/nlp/normalizer.py`)

Limpia y estandariza texto de entrada.

```python
from app.nlp import TextNormalizer, normalize_text

normalizer = TextNormalizer()
normalized = normalizer.normalize("HOLA MUNDO!!!")  # "hola mundo"
```

### 2. Tokenizer (`app/nlp/tokenizer.py`)

Tokenizacion y analisis POS con spaCy.

```python
from app.nlp import NLPTokenizer

tokenizer = NLPTokenizer()
result = tokenizer.tokenize("Activa bienvenida")
print(result.tokens)  # ["Activa", "bienvenida"]
print(result.lemmas)  # ["Activa", "bienvenido"]
```

### 3. Intent Classifier (`app/nlp/intent_classifier.py`)

Clasifica intenciones del usuario.

```python
from app.nlp import IntentClassifier, classify_intent

classifier = IntentClassifier()
intent, confidence = classifier.classify("activa bienvenida")
print(intent)  # "toggle_feature"
print(confidence)  # 0.8
```

### 4. Entity Extractor (`app/nlp/ner.py`)

Extrae entidades del texto.

```python
from app.nlp import EntityExtractor

extractor = EntityExtractor()
limits = extractor.extract_limits("pon limite de 10 mensajes en 5 segundos")
print(limits)  # {"limit": 10, "interval": 5}
```

### 5. Action Mapper (`app/nlp/action_mapper.py`)

Mapea intenciones a acciones del sistema.

```python
from app.nlp import ActionMapper, map_to_action

mapper = ActionMapper()
result = mapper.map("bienvenida: Hola mundo")
print(result.action_id)  # "welcome.set_text"
print(result.payload)  # {"text": "Hola mundo"}
```

### 6. Pipeline (`app/nlp/pipeline.py`)

Orquestador del pipeline completo.

```python
from app.nlp import NLPPipeline, PipelineConfig

config = PipelineConfig(min_confidence_threshold=0.5)
pipeline = NLPPipeline(config)
result = pipeline.process("activa bienvenida")
print(result.action_result.action_id)  # "welcome.toggle"
```

### 7. Integration (`app/nlp/integration.py`)

Modulo de integracion con el bot.

```python
from app.nlp import NLPBotIntegration, should_use_nlp, process_nlp_message

integration = NLPBotIntegration()

# Verificar si es un comando NLP
if should_use_nlp("activa bienvenida"):
    result = process_nlp_message("activa bienvenida")
    print(result.action_id)  # "welcome.toggle"
```

---

## Intenciones Soportadas

### Acciones de Bot

| Intencion | Descripcion | Ejemplo |
|-----------|-------------|---------|
| set_welcome | Establecer mensaje de bienvenida | "bienvenida: Hola" |
| toggle_feature | Activar/desactivar funcion | "activa antiflood" |
| set_limit | Configurar limites | "pon limite de 5 mensajes" |
| add_filter | Agregar filtro | "bloquear palabra spam" |
| remove_filter | Quitar filtro | "desbloquea spam" |
| set_goodbye | Establecer mensaje de despedida | "despedida: Adios" |

### Consultas

| Intencion | Descripcion | Ejemplo |
|-----------|-------------|---------|
| get_status | Consultar estado | "como esta el antiflood?" |
| get_settings | Ver configuracion | "cuales son los filtros?" |
| help | Pedir ayuda | "ayudame con los comandos" |
| list_actions | Listar acciones | "que puedes hacer?" |

---

## Configuracion

### Variables de Entorno

```bash
# .env
NLP_ENABLED=True
NLP_MIN_CONFIDENCE=0.5
NLP_LLM_FALLBACK=True
```

### Configuracion Programatica

```python
from app.nlp import NLPPipeline, PipelineConfig

config = PipelineConfig(
    use_normalizer=True,
    use_tokenizer=True,
    use_intent_classifier=True,
    use_entity_extractor=True,
    use_action_mapper=True,
    enable_llm_fallback=True,
    min_confidence_threshold=0.5
)

pipeline = NLPPipeline(config)
```

---

## Uso con AgentCore

```python
from app.agent.core import AgentCore, AgentContext

# El agente usa NLP automaticamente si esta habilitado
agent = AgentCore()

context = AgentContext(
    chat_id=123456789,
    tenant_id="default",
    user_id="user123"
)

# Procesar mensaje en lenguaje natural
response = agent.process_async("activa bienvenida", context)
print(response.response)  # Respuesta del bot
```

---

## Uso con IntentRouter

```python
from app.agent.intent_router import IntentRouter, IntentKind

router = IntentRouter(nlp_enabled=True)

decision = router.route("activa bienvenida")
print(f"Tipo: {decision.kind}")  # bot_action
print(f"Intencion: {decision.nlp_intent}")  # toggle_feature
print(f"Confianza: {decision.confidence}")  # 0.8
```

---

## Ejemplos de Comandos

### Bienvenida

```python
"bienvenida: Hola bienvenido"  # -> welcome.set_text
"activa bienvenida"            # -> welcome.toggle
"desactiva bienvenida"          # -> welcome.toggle (enabled=False)
```

### Antiflood

```python
"pon limite de 10 mensajes en 5 segundos"  # -> antiflood.set_limits
"desactiva antiflood"                        # -> antiflood.toggle
"antiflood con mute"                        # -> antiflood.set_action
```

### Filtros

```python
"bloquear palabra spam"    # -> filter.add_word
"desbloquea spam"         # -> filter.remove_word
```

### Despedida

```python
"despedida: Hasta luego"  # -> goodbye.set_text
"activa despedida"         # -> goodbye.toggle
```

---

## Rendimiento

| Operacion | Tiempo estimado |
|----------|----------------|
| Normalizacion | ~1ms |
| Tokenizacion | ~10-50ms (spaCy) |
| Clasificacion | ~1ms |
| Extraccion de entidades | ~1ms |
| Mapeo de accion | ~1ms |
| **Total** | **~15-60ms** |

### Optimizaciones

1. **Lazy Loading:** El modelo spaCy se carga solo cuando se necesita
2. **Caching:** Resultados de clasificacion se cachean
3. **Singleton:** Componentes NLP son singletons

---

## Testing

```bash
# Tests de integracion NLP
pytest tests/integration/test_nlp_bot.py -v

# Todos los tests NLP
pytest tests/nlp/ -v

# Tests de IntentRouter
pytest tests/agent/test_intent_router.py -v
```

---

## Errores Comunes

### spaCy no instalado

```bash
pip install spacy>=3.7.0
python -m spacy download es_core_news_sm
```

### Modelo no encontrado

```bash
python -m spacy download es_core_news_sm
```

### Configuracion incorrecta

Verificar que `NLP_ENABLED=True` en el archivo `.env`.

---

## API Reference

### Funciones Exportadas

```python
# Normalizer
from app.nlp import TextNormalizer, normalize_text, normalize_text_keep_numbers

# Tokenizer
from app.nlp import NLPTokenizer, tokenize_text

# Intent Classifier
from app.nlp import IntentClassifier, classify_intent

# Entity Extractor
from app.nlp import EntityExtractor, extract_entities

# Action Mapper
from app.nlp import ActionMapper, map_to_action

# Pipeline
from app.nlp import NLPPipeline, process_text

# Integration
from app.nlp import NLPBotIntegration, should_use_nlp, process_nlp_message
```

---

## Historial de Cambios

| Fecha | Version | Cambio |
|-------|---------|--------|
| 29/03/2026 | 1.0 | Documentacion inicial |
