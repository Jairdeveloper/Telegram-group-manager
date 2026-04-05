# Módulo NLP - Procesamiento de Lenguaje Natural

## Propósito

El módulo NLP permite que el robot de Telegram procese mensajes en lenguaje natural, entendiendo la **intención del usuario** y ejecutando **acciones** apropiadas sin necesidad de comandos explícitos.

### Problema que resuelve

Los comandos tradicionales de Telegram (`/setwelcome`, `/antiflood`, etc.) requieren que el usuario recuerde sintaxis específica. El NLP permite:

- **Entrada natural**: "cambia el mensaje de bienvenida" → ejecuta `welcome.set_creative_text`
- **Sin sintaxis estricta**: "pon antiflood con 5 mensajes en 3 segundos" → ejecuta `antiflood.set_limits`

---

## Arquitectura del Módulo

```
┌─────────────────────────────────────────────────────────────────┐
│                        Mensaje del usuario                      │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  NLPBotIntegration (app/nlp/integration.py)                   │
│  - Punto de entrada para el resto del sistema                 │
│  - Decide si usar NLP según confianza                          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  NLPPipeline (app/nlp/pipeline.py)                             │
│  -_orquestador del flujo de procesamiento                      │
└─────────────────────────────────────────────────────────────────┘
        │           │           │           │           │
        ▼           ▼           ▼           ▼           ▼
   Normalizer   Tokenizer   Intent       NER       Action
                                             Mapper
```

---

## Flujo de Datos

### 1. Normalización (`normalizer.py`)

Convierte el texto a un formato estándar:

- Minusculas
- Elimina acentos (opcional)
- Normaliza puntuación
- **Ejemplo**: "CAMBIAR Mensaje de BIENVENIDA" → "cambiar mensaje de bienvenida"

### 2. Tokenización (`tokenizer.py`)

Divide el texto en tokens (palabras significativas):

- **Ejemplo**: "cambiar mensaje de bienvenida" → `["cambiar", "mensaje", "bienvenida"]`

### 3. Clasificación de Intención (`intent_classifier.py` + `classifiers/`)

Determina qué quiere hacer el usuario:

| Mensaje | Intención detectada |
|---------|---------------------|
| "cambiar bienvenida" | `set_welcome` |
| "activa antiflood" | `antiflood.toggle` |
| "bloquear palabra spam" | `filter.add_word` |

Usa un **ensemble** de:
- Clasificador ML (modelo entrenado)
- Clasificador regex (reglas)
- Pesos configurables (50% cada uno)

### 4. Extracción de Entidades (`ner.py`)

Identifica información específica en el texto:

- Números: "5 mensajes" → `{"limit": 5}`
- Palabras clave: "spam" → `{"word": "spam"}`

### 5. Mapeo de Acción (`action_mapper.py`)

Convierte la intención en una **acción ejecutable**:

- `set_welcome` → `welcome.set_creative_text` o `welcome.set_text`
- `antiflood.toggle` → `antiflood.toggle` con payload
- `add_filter` → `filter.add_word`

### 6. Fallback con LLM (`parser.py`)

Si la confianza es baja, usa un modelo de lenguaje para interpretar:

- Prompt con ejemplos de acciones disponibles
- El LLM retorna JSON con `action_id` y `payload`

---

## Integración con el Robot Telegram

### Punto de entrada: `handlers.py`

El webhook recibe mensajes y los procesa así:

```python
# En app/webhook/handlers.py
if dispatch.kind in ("chat_message", "agent_task"):
    text = dispatch.text
    
    # Intentar ActionParser primero (reglas + LLM)
    parser = ActionParser(llm_enabled=True)
    parse_result = parser.parse(text)
    
    if parse_result.action_id and parse_result.confidence >= 0.5:
        # Ejecutar acción
        executor = ActionExecutor(registry)
        action_result = await executor.execute(...)
        reply = action_result.message
```

### Fallback: NLP Pipeline

Si ActionParser no reconoce el mensaje:

```python
# Intentar NLP
nlp_integration = get_nlp_integration()
if nlp_integration.should_use_nlp(text):
    nlp_result = nlp_integration.process_message(text)
    if nlp_result.action_result.action_id:
        reply = f"✓ Acción: {nlp_result.action_result.action_id}"
```

### Flujo completo en el handler

```
Mensaje Telegram
       │
       ▼
dispatch_telegram_update()
       │
       ▼
Router.route_update() → determina tipo de mensaje
       │
       ▼
process_update_impl()
       │
       ├─→ callback_query → MenuEngine
       │
       ├─→ ops_command → handle_ops_command()
       │
       ├─→ enterprise_command → handle_enterprise_command()
       │
       └─→ chat_message → ActionParser (prioridad)
                              │
                              ├─→ LLM parse
                              ├─→ Rule-based
                              └─→ NLP Pipeline (fallback)
```

---

## Componentes del Módulo

| Archivo | Función |
|---------|---------|
| `integration.py` | Punto de entrada, decide cuándo usar NLP |
| `pipeline.py` | Orquesta los componentes del pipeline |
| `normalizer.py` | Normaliza texto (minúsculas, acentos) |
| `tokenizer.py` | Tokeniza texto en palabras |
| `intent_classifier.py` | Clasifica intención del mensaje |
| `classifiers/*.py` | Implementaciones de clasificadores (ML, ensemble) |
| `ner.py` | Extrae entidades (números, palabras clave) |
| `action_mapper.py` | Mapea intención a acción ejecutable |
| `features.py` | Palabras clave para clasificación |
| `serialization.py` | Carga/guarda modelos entrenados |

---

## Actions Soportadas

El NLP mapea intents a actions del sistema:

- **Welcome**: `welcome.toggle`, `welcome.set_text`, `welcome.set_creative_text`
- **Antispam**: `antispam.toggle`
- **Antiflood**: `antiflood.toggle`, `antiflood.set_limits`, `antiflood.set_action`
- **Goodbye**: `goodbye.toggle`, `goodbye.set_text`
- **Filters**: `filter.add_word`, `filter.remove_word`

---

## Configuración

```python
PipelineConfig(
    use_normalizer=True,       # Normalizar texto
    use_tokenizer=True,        # Tokenizar
    use_intent_classifier=True, # Clasificar intención
    use_entity_extractor=True, # Extraer entidades
    use_action_mapper=True,    # Mapear acción
    enable_llm_fallback=True,  # Usar LLM si confianza baja
    min_confidence_threshold=0.5  # Umbral mínimo
)
```

---

## Resumen

El módulo NLP permite que el robot entienda lenguaje natural mediante:

1. **Normalización y tokenización** del texto
2. **Clasificación de intención** con ensemble ML+regex
3. **Extracción de entidades** para parámetros
4. **Mapeo a acciones** ejecutables por el sistema
5. **Fallback con LLM** para casos complejos

Se integra en `handlers.py` como fallback después de ActionParser, permitiendo que el robot responda tanto a comandos explícitos (`/setwelcome`) como a mensajes naturales ("cambia el mensaje de bienvenida").