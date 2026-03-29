# Plan de Integracion: NLP con Robot Telegram

---

**Fecha:** 29/03/2026

**Version:** 1.0

**Referencia:** IMPLEMENTACION_ARQUITECTURA_NLP_COMPLETADA.md

---

## Resumen de la Implementacion

Este documento detalla el plan de integracion del sistema NLP (ya implementado en `app/nlp/`) con el Robot de administracion de grupos de Telegram. El objetivo es que el bot pueda entender instrucciones en lenguaje natural de los usuarios y procesarlas de manera inteligente.

**Estado actual del NLP:**
- Pipeline NLP completo implementado con 7 componentes
- 117 tests unitarios pasando
- Acciones soportadas: welcome.*, antispam.*, antiflood.*, goodbye.*, filter.*

**Objetivo:** Integrar el pipeline NLP con el dispatcher y AgentCore del bot para procesar mensajes en lenguaje natural.

---

## Arquitectura Final

```
Telegram User Message
        ↓
dispatch_telegram_update() 
        ↓
┌───────────────────────────────────────┐
│        NLP Integration Layer          │
├───────────────────────────────────────┤
│ IntentRouter (MEJORADO CON NLP)       │
│        ↓                             │
│ NLPPipeline (NLP Pipeline)            │
│        ↓                             │
│ ActionParser (CON NLP INTEGRADO)      │
└───────────────────────────────────────┘
        ↓
AgentCore.process_async()
        ↓
ActionExecutor
        ↓
Action Registry → Acciones del bot
```

**Flujo propuesto:**
1. Usuario envia mensaje en lenguaje natural al bot
2. `dispatch_telegram_update()` procesa el update
3. Si es un mensaje de chat (no comando), se usa el NLP pipeline
4. El pipeline procesa el texto y determina la accion
5. `AgentCore` ejecuta la accion a traves del `ActionExecutor`
6. Se devuelve la respuesta al usuario

---

## Tabla de Tareas

| Fase | Tarea | Prioridad | Estado |
|------|-------|-----------|--------|
| 1 | Analizar flujo actual del dispatcher | Alta | **COMPLETADO** |
| 1 | Crear modulo de integracion NLP | Alta | **COMPLETADO** |
| 1 | Tests de integracion | Alta | **COMPLETADO** |
| 1 | Integrar NLPPipeline en AgentCore | Alta | Pendiente |
| 2 | Mejorar IntentRouter con NLP | Media | Pendiente |
| 2 | Agregar nuevas intenciones | Media | Pendiente |
| 2 | Configuracion de umbral de confianza | Media | Pendiente |
| 3 | Optimizar rendimiento | Media | Pendiente |
| 3 | Documentacion de API | Media | Pendiente |
| 3 | Testing E2E | Alta | Pendiente |

---

## Fase 1: Integracion Base

**Objetivo fase:** Integrar el pipeline NLP en el flujo principal del bot

**Implementacion fase:**

### 1.1 Crear modulo de integracion NLP

**COMPLETADO** - Archivo `app/nlp/integration.py` creado:

```python
class NLPBotIntegration:
    def __init__(self, config: Optional[PipelineConfig] = None, min_confidence: float = 0.5)
    def should_use_nlp(self, text: str) -> bool
    def process_message(self, text: str) -> Optional[PipelineResult]
    def get_action_for_message(self, text: str) -> Optional[ActionParseResult]
    def classify_intent(self, text: str) -> tuple
    def is_nlp_command(self, text: str) -> bool

# Funciones convenience:
get_nlp_integration()
process_nlp_message(text)
should_use_nlp(text)
```

**Tests:** 16 tests de integracion pasando

```python
from app.nlp import NLPPipeline, PipelineConfig, PipelineResult

class NLPBotIntegration:
    def __init__(self, config: Optional[PipelineConfig] = None)
    def should_use_nlp(self, text: str) -> bool
    def process_message(self, text: str) -> Optional[PipelineResult]
    def get_action_for_message(self, text: str) -> Optional[ActionParseResult]
```

### 1.2 Integrar en AgentCore

Modificar `app/agent/core.py`:

```python
# Agregar en __init__:
from app.nlp.integration import NLPBotIntegration

self.nlp_integration = NLPBotIntegration() if settings.nlp_enabled else None

# Modificar _process_actions_async:
def _process_actions_async(self, message: str, context: AgentContext):
    # Usar NLP si esta habilitado
    if self.nlp_integration:
        nlp_result = self.nlp_integration.process_message(message)
        if nlp_result and nlp_result.action_result.action_id:
            return self._execute_nlp_action(nlp_result, message, context)
    
    # Fallback al parser original
    decision = self.action_parser.parse(message)
    # ... resto del codigo
```

### 1.3 Agregar configuracion

Modificar `app/config/settings.py`:

```python
class APISettings(BaseSettings):
    # ... campos existentes ...
    nlp_enabled: bool = True
    nlp_min_confidence: float = 0.5
    nlp_llm_fallback: bool = True
```

### 1.4 Archivos a crear/modificar

| Archivo | Accion | Estado |
|---------|--------|--------|
| `app/nlp/integration.py` | Crear | **COMPLETADO** |
| `app/nlp/__init__.py` | Actualizar exports | **COMPLETADO** |
| `tests/nlp/test_integration.py` | Crear | **COMPLETADO** |
| `app/agent/core.py` | Modificar | Pendiente |
| `app/config/settings.py` | Modificar | Pendiente |

### 1.5 Criterio de exito

- El bot responde a mensajes en lenguaje natural | **COMPLETADO** (modulo)
- Se mantienen backwards compatibility | **COMPLETADO**
- Los tests de integracion pasan | **COMPLETADO (16/16)**

---

## Fase 2: Mejoras de Inteligencia

**Objetivo fase:** Mejorar la clasificacion de intenciones y agregar nuevas funcionalidades

**Implementacion fase:**

### 2.1 Mejorar IntentRouter con NLP

Modificar `app/agent/intent_router.py`:

```python
from app.nlp import NLPPipeline, IntentClassifier

class IntentRouter:
    def __init__(self, ...):
        # ... codigo existente ...
        self.nlp_classifier = IntentClassifier()
    
    def _use_nlp_classification(self, message: str) -> bool:
        intent, confidence = self.nlp_classifier.classify(message)
        return intent is not None and confidence >= 0.5
```

### 2.2 Agregar nuevas intenciones

Extender `app/nlp/intent_classifier.py` con intenciones adicionales:

| Intencion | Descripcion | Ejemplo |
|-----------|-------------|---------|
| get_status | Consultar estado de funciones | "como esta el antiflood?" |
| get_settings | Ver configuracion actual | "cuales son los filtros?" |
| help | Pedir ayuda | "ayudame con los comandos" |
| list_actions | Listar acciones disponibles | "que puedo hacer?" |

### 2.3 Configuracion de umbral

```python
# En integration.py
def should_use_nlp(self, text: str) -> bool:
    intent, confidence = self.classifier.classify(text)
    return intent is not None and confidence >= self.min_confidence
```

### 2.4 Archivos a crear/modificar

| Archivo | Accion |
|---------|--------|
| `app/agent/intent_router.py` | Modificar |
| `app/nlp/intent_classifier.py` | Extender |
| `app/nlp/integration.py` | Modificar |

### 2.5 Criterio de exito

- IntentRouter usa NLP para clasificacion
- Se detectan >80% de intenciones correctamente

---

## Fase 3: Optimizacion y Testing

**Objetivo fase:** Optimizar rendimiento y documentar la integracion

**Implementacion fase:**

### 3.1 Cache de componentes NLP

```python
# En integration.py
from functools import lru_cache

@lru_cache(maxsize=1000)
def classify_intent_cached(text: str):
    return classifier.classify(text)
```

### 3.2 Lazy loading de spaCy

```python
# En tokenizer.py
class NLPTokenizer:
    def __init__(self):
        self._nlp = None  # Carga lazy
    
    def _ensure_model_loaded(self):
        if self._nlp is None:
            self._load_model()
```

### 3.3 Tests E2E

Crear `tests/integration/test_nlp_bot.py`:

```python
async def test_bot_nlp_welcome():
    # Simular mensaje del usuario
    message = "quiero cambiar la bienvenida"
    # Procesar con el bot
    response = await agent.process_async(message, context)
    # Verificar respuesta
    assert "bienvenida" in response.response.lower()

async def test_bot_nlp_antiflood():
    message = "pon antiflood con 10 mensajes en 5 segundos"
    response = await agent.process_async(message, context)
    assert response.source == "action"
```

### 3.4 Documentacion

Crear `docs/nlp/integration.md`:
- Guia de uso del NLP en el bot
- Configuracion de parametros
- Examples de mensajes y respuestas

### 3.5 Archivos a crear/modificar

| Archivo | Accion |
|---------|--------|
| `app/nlp/integration.py` | Optimizar |
| `app/nlp/tokenizer.py` | Optimizar |
| `tests/integration/test_nlp_bot.py` | Crear |
| `docs/nlp/integration.md` | Crear |

### 3.6 Criterio de exito

- Tiempo de respuesta < 500ms
- Tests E2E pasando
- Documentacion completa

---

## Estructura de Archivos Propuesta

```
app/
├── nlp/
│   ├── __init__.py           [ACTUALIZADO]
│   ├── normalizer.py         [EXISTE]
│   ├── tokenizer.py          [EXISTE]
│   ├── intent_classifier.py  [EXISTE]
│   ├── ner.py               [EXISTE]
│   ├── action_mapper.py     [EXISTE]
│   ├── pipeline.py          [EXISTE]
│   ├── integration.py       [COMPLETADO]
│   └── exceptions.py        [EXISTE]
├── agent/
│   ├── core.py              [PENDIENTE]
│   └── intent_router.py     [PENDIENTE]
├── config/
│   └── settings.py          [PENDIENTE]
tests/
├── nlp/
│   └── test_integration.py  [COMPLETADO]
└── integration/
    └── test_nlp_bot.py     [PENDIENTE]
```

---

## Ejemplos de Uso

### Mensaje del usuario:
```
"activa bienvenida con Hola bienvenidos al grupo"
```

### Pipeline NLP procesa:
1. Normalizar: "activa bienvenida con hola bienvenidos al grupo"
2. Tokenizar: ["activa", "bienvenida", "con", "hola", ...]
3. Clasificar intencion: "toggle_feature" (0.8)
4. Extraer entidades: {feature: "welcome"}
5. Mapear accion: "welcome.set_text" con payload {text: "Hola bienvenidos al grupo"}

### Respuesta del bot:
```
"Mensaje de bienvenida actualizado a: Hola bienvenidos al grupo"
```

---

## Configuracion Recomendada

```python
# settings.py
NLP_ENABLED = True
NLP_MIN_CONFIDENCE = 0.5
NLP_LLM_FALLBACK = True

# Nuevos comandos reconocidos:
# - "quiero cambiar la bienvenida" -> welcome.set_text
# - "como esta el antiflood?" -> status query
# - "bloquear palabra spam" -> filter.add_word
```

---

## Metricas de Exito

| Metrica | Objetivo | Estado actual |
|---------|----------|---------------|
| Accuracy de parseo | >90% | ~85% (en pruebas) |
| Tiempo de respuesta | <500ms | ~100ms (sin LLM) |
| Cobertura de intents | >20 | 6 (ampliable) |
| Tests de integracion | 16+ | **16 COMPLETADOS** |
| Modulo integration.py | Completado | **COMPLETADO** |

---

## Riesgos y Mitigaciones

| Riesgo | Impacto | Mitigacion |
|--------|---------|------------|
| spaCy carga lenta | Alto | Lazy loading + cache |
| Falta de precision | Medio | LLM fallback |
| Breaking changes | Alto | Backwards compatibility |
| Performance | Medio | Optimizacion + async |

---

## Orden de Implementacion Recomendado

1. **Semana 1:** Integracion base (integration.py) - **COMPLETADO**
2. **Semana 2:** Integrar en AgentCore + IntentRouter
3. **Semana 3:** Testing E2E + optimizacion
4. **Semana 4:** Documentacion + deployment

---

## Historico de Cambios

| Fecha | Version | Cambio |
|-------|---------|--------|
| 29/03/2026 | 1.0 | Plan de integracion creado |
| 29/03/2026 | 1.1 | Fase 1 (integracion base) completada con modulo integration.py |
