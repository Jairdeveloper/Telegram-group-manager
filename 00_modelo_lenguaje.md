# 00_modelo_lenguaje - Propuesta de evolucion del chatbot

## Objetivo
Evolucionar el chatbot actual (basado en `pattern -> response`) hacia una arquitectura de funcionamiento mas cercana a sistemas modernos de lenguaje, sin romper produccion y con migracion incremental.

## Estado actual resumido
- Flujo principal actual: `pattern -> response`.
- Base tecnica ya madura para evolucion:
  - settings centralizados
  - webhook/api modulares
  - puertos/adaptadores
  - bootstrap y pruebas de regresion

## Vision objetivo (pipeline)

```text
input
  ↓
morphological analysis
  ↓
syntactic parsing
  ↓
semantic role labeling
  ↓
intent detection
  ↓
dialog state update
  ↓
response planning
  ↓
surface realization
```

## Enfoque recomendado
No hacer una sustitucion total de una vez. Implementar por fases, manteniendo fallback al motor actual para estabilidad operativa.

---

## Fase 1 - Base NLU minima (MVP serio)

### Tareas
1. Crear paquete `app/nlu/` con contratos y pipeline inicial.
2. Implementar `IntentDetector` + `EntityExtractor` (version inicial).
3. Definir salida estructurada `NLUResult`:
- `intent`
- `entities`
- `confidence`
- `tokens`
4. Integrar el pipeline en el orquestador sin reemplazar aun `PatternEngine`.
5. Mantener fallback:
- si `confidence` baja, usar `pattern -> response`.

### Criterio de salida
- NLU entrega resultados consistentes para intents principales.
- Fallback funciona sin regresiones.

---

## Fase 2 - Dialog Manager (estado conversacional)

### Tareas
1. Crear paquete `app/dialog/`.
2. Definir `DialogState` por `session_id/chat_id`.
3. Implementar `state update`:
- slot filling
- contexto de turno
- historial util
4. Definir politicas basicas de dialogo:
- preguntar datos faltantes
- confirmar acciones
- fallback por ambiguedad

### Criterio de salida
- El bot mantiene contexto multi-turno estable.
- Disminuyen respuestas fuera de contexto.

---

## Fase 3 - Response Planning

### Tareas
1. Crear paquete `app/planning/`.
2. Definir `ActionPlan` (intencion de respuesta):
- informar
- pedir aclaracion
- confirmar
- ejecutar accion
3. Mapear `intent + state` -> `ActionPlan`.
4. Agregar manejo de errores semanticos (ambiguedad, datos incompletos).

### Criterio de salida
- Decisiones de respuesta explicables y testeables.
- Menos respuestas "aleatorias".

---

## Fase 4 - Surface Realization (NLG)

### Tareas
1. Crear paquete `app/nlg/`.
2. Implementar realizacion de texto por plantilla/estrategia.
3. Agregar variacion controlada de respuestas (sin perder consistencia).
4. Definir tono y estilo por canal (Telegram primero).

### Criterio de salida
- Respuestas mas naturales y consistentes.
- Trazabilidad entre `ActionPlan` y respuesta final.

---

## Fase 5 - Analisis linguistico avanzado (opcional, fase de madurez)

### Tareas
1. Agregar `morphological analysis` y `syntactic parsing` donde aporten valor real.
2. Agregar `semantic role labeling` para intents complejos.
3. Medir impacto real en precision y UX.

### Criterio de salida
- Mejora medible vs costo computacional.
- No introducir complejidad sin beneficio operativo.

---

## Recomendaciones tecnicas

1. Priorizar utilidad de negocio antes que complejidad linguistica.
- Primero: intent + dialog state + planning.
- Despues: parsing/SRL si hay casos que lo justifican.

2. Diseñar todo por interfaces.
- NLU, Dialog, Planner y NLG deben tener puertos claros para pruebas.

3. Mantener compatibilidad operativa.
- `PatternEngine` queda como fallback durante la migracion.

4. Medir todo.
- precision de intent
- tasa de fallback
- errores por ambiguedad
- tiempo de respuesta

5. No romper contratos existentes.
- `POST /api/v1/chat`
- `POST /webhook/{token}`

6. Despliegue incremental.
- habilitar nuevas capacidades por feature flags.
- rollout por porcentaje/canal antes de activacion total.

---

## Arquitectura sugerida de paquetes

```text
app/
  nlu/
    contracts.py
    pipeline.py
    intent_detector.py
    entity_extractor.py
  dialog/
    state.py
    manager.py
    policy.py
  planning/
    planner.py
    actions.py
  nlg/
    realizer.py
    templates.py
  orchestrator/
    chat_orchestrator.py
```

## Plan de PR recomendado

- PR-9: contratos NLU + pipeline minimo + tests unitarios.
- PR-10: dialog state manager + integracion basica.
- PR-11: response planner + cobertura de casos ambiguos.
- PR-12: NLG surface realization + ajuste de estilo.
- PR-13: metricas y evaluacion (precision/fallback/latencia).

## Validacion minima por PR

```bash
pytest -q
```

Y smoke obligatorio:
- `POST /api/v1/chat`
- `POST /webhook/{token}`
- mensaje real por Telegram en entorno de desarrollo.
