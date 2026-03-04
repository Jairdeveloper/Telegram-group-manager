# 00_implementacion_modelo_lenguaje - Blueprint tecnico PR-9

## Alcance de PR-9
Implementar la primera capa seria de NLU sin romper contratos existentes.

Incluye en PR-9:
- Contratos NLU (`interfaces` + `DTOs`).
- Pipeline NLU minimo.
- Integracion no intrusiva con flujo actual (`fallback` al motor de patrones).
- Pruebas unitarias + smoke funcional.

No incluye en PR-9:
- Dialog manager completo.
- Response planner completo.
- NLG avanzado.

---

## 1) Estructura de carpetas (exacta)

```text
app/
  nlu/
    __init__.py
    contracts.py
    dtos.py
    pipeline.py
    steps/
      __init__.py
      normalization.py
      intent.py
      entities.py
  orchestrator/
    __init__.py
    chat_orchestrator.py
tests/
  test_nlu_pipeline_unit.py
  test_chat_orchestrator_unit.py
```

---

## 2) DTOs y contratos

### 2.1 `app/nlu/dtos.py`

```python
from dataclasses import dataclass, field
from typing import Any

@dataclass
class MessageContext:
    session_id: str
    raw_text: str
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class NLUResult:
    intent: str
    confidence: float
    entities: dict[str, Any] = field(default_factory=dict)
    tokens: list[str] = field(default_factory=list)
    normalized_text: str = ""
    source: str = "nlu"
```

### 2.2 `app/nlu/contracts.py`

```python
from typing import Protocol
from .dtos import MessageContext, NLUResult

class NLUStep(Protocol):
    def run(self, ctx: MessageContext, state: dict) -> None: ...

class NLUPipeline(Protocol):
    def analyze(self, ctx: MessageContext) -> NLUResult: ...
```

---

## 3) Clases concretas PR-9

### 3.1 `NormalizeStep` (`steps/normalization.py`)
Responsabilidad:
- lower-case
- trim
- colapsar espacios
- tokenizacion simple por espacio

Salida en `state`:
- `normalized_text`
- `tokens`

### 3.2 `RuleBasedIntentStep` (`steps/intent.py`)
Responsabilidad:
- detectar intent por reglas basicas (saludo, despedida, ayuda, desconocido)
- asignar `confidence`

Salida en `state`:
- `intent`
- `confidence`

### 3.3 `SimpleEntityStep` (`steps/entities.py`)
Responsabilidad:
- extraer entidades basicas por reglas/regex (ej. numeros, fechas simples)

Salida en `state`:
- `entities`

### 3.4 `DefaultNLUPipeline` (`pipeline.py`)
Responsabilidad:
- ejecutar steps en orden
- construir `NLUResult`

Firma:
```python
class DefaultNLUPipeline:
    def __init__(self, steps: list[NLUStep]): ...
    def analyze(self, ctx: MessageContext) -> NLUResult: ...
```

---

## 4) Integracion con el chatbot actual

## 4.1 `app/orchestrator/chat_orchestrator.py`

Crear orquestador minimo que combine NLU + motor actual.

```python
class ChatOrchestrator:
    def __init__(self, nlu_pipeline, pattern_agent, min_confidence: float = 0.70): ...

    def process(self, message: str, session_id: str):
        # 1) NLU
        # 2) Si confidence >= min_confidence -> respuesta por intent map
        # 3) Si confidence < min_confidence -> fallback pattern_agent.process(message)
        # 4) devolver objeto compatible con respuesta actual
```

Regla de compatibilidad:
- No tocar payload de `/api/v1/chat`.
- Seguir retornando: `response`, `confidence`, `source`, `pattern_matched`.

## 4.2 Mapa inicial `intent -> response`
- `greeting` -> saludo amigable
- `goodbye` -> despedida
- `help` -> mensaje de ayuda
- `unknown` -> fallback a patrones

---

## 5) Flujo exacto PR-9

```text
POST /api/v1/chat
  -> ChatOrchestrator.process(message, session_id)
      -> DefaultNLUPipeline.analyze(ctx)
          -> NormalizeStep
          -> RuleBasedIntentStep
          -> SimpleEntityStep
      -> if confidence >= threshold:
            response from intent map
         else:
            fallback to existing pattern agent
  -> persist history
  -> return same API contract
```

---

## 6) Criterios de implementacion (Definition of Done)

1. Se crean modulos `app/nlu/*` y `app/orchestrator/*` con codigo ejecutable.
2. Se integra el orquestador sin romper rutas existentes.
3. No se rompe contrato de `POST /api/v1/chat`.
4. Fallback al motor actual funcionando.
5. Tests verdes.

---

## 7) Plan de pruebas PR-9

### 7.1 Unit tests NLU (`tests/test_nlu_pipeline_unit.py`)
- normalizacion correcta
- intent greeting detectado
- intent unknown cuando no hay regla
- entities basicas extraidas

### 7.2 Unit tests orquestador (`tests/test_chat_orchestrator_unit.py`)
- alto confidence usa respuesta por intent
- bajo confidence usa fallback pattern agent
- respuesta conserva forma esperada

### 7.3 Regresion API
- `tests/test_api_contract.py` sigue en verde

### 7.4 Comandos
```bash
pytest -q tests/test_nlu_pipeline_unit.py tests/test_chat_orchestrator_unit.py tests/test_api_contract.py
pytest -q
```

---

## 8) Riesgos y mitigaciones (PR-9)

Riesgo:
- respuestas menos naturales en intents nuevos.
Mitigacion:
- mantener fallback agresivo al motor de patrones.

Riesgo:
- degradacion de contrato API.
Mitigacion:
- no tocar schema de salida y validar contrato en CI.

Riesgo:
- acoplar NLU con transporte.
Mitigacion:
- NLU solo en `app/nlu`, orquestacion en `app/orchestrator`.

---

## 9) Checklist de merge PR-9

- [ ] Nuevos modulos creados con tests.
- [ ] `pytest -q` verde.
- [ ] `/api/v1/chat` sin cambios de payload/status.
- [ ] Fallback a patrones verificado.
- [ ] Documentacion minima de NLU agregada.
