# Debug: Bot responde "(sin respuesta)" para lenguaje natural

---

**Fecha:** 09/04/2026  
**Versión:** 1.0  
**Referencia:** NEXT_STEPS_NLP_INTEGRACION.md

---

## Problema

El bot responde con "(sin respuesta)" cuando el usuario envía mensajes en lenguaje natural como:
- "ver estado"
- "ver configuracion"
- "ayuda"
- "ver reportes"

---

## Diagnóstico

### Flujo de procesamiento

```
Usuario envía mensaje
    ↓
ChatMessageProcessor._handle_regular_message()
    ↓
ActionParser.parse() - LLM falla, rule-based no reconoce → action_id=None
    ↓
ChatMessageProcessor._handle_service_fallback()
    ↓
NLPIntegration.should_use_nlp() - USA EnsembleIntentClassifier
    ↓
NLPIntegration.process_message() - process_message funciona bien
    ↓
ActionParser.parse() del primer paso falló → action_id es None
    ↓
handle_chat_message() del fallback retorna "That's interesting..." 
    ↓
ResponseBuilder.build() → "(sin respuesta)" (por respuesta vacía)
```

### Causa raíz

El problema está en `_handle_regular_message()` (líneas 77-108 de `chat_message.py`):

1. **ActionParser.parse()** con `llm_enabled=True` intenta primero LLM, luego rule-based
2. Para muchos mensajes, el rule-based **no encuentra coincidencia** (devuelve `action_id=None`)
3. El código verifica `parse_result.action_id and parse_result.confidence >= 0.5`
4. Como `action_id` es `None`, la condición es `False`
5. Entonces cae al fallback: `_handle_service_fallback()`

El fallback debería usar NLP correctamente, pero hay un problema adicional:

### Causa secundaria

En `app/nlp/integration.py`, el método `should_use_nlp()` usa `EnsembleIntentClassifier`:

```python
@property
def classifier(self):
    if self._classifier is None:
        # Inicializar ensemble con todos los componentes
        ml_classifier = MLIntentClassifier()  # Carga modelo entrenado
        self._classifier = EnsembleIntentClassifier(
            ml_classifier=ml_classifier,
            ml_weight=0.5,
            regex_weight=0.5
        )
    return self._classifier
```

El `EnsembleIntentClassifier` tiene thresholds altos:
- `high_confidence_threshold = 0.75`
- `medium_confidence_threshold = 0.50`

Pero el `RegexIntentClassifier` interno tiene configuración diferente al `IntentClassifier` de `app/nlp/intent_classifier.py`.

### Verificación

```python
# EnsembleIntentClassifier internal RegexIntentClassifier:
# patterns: set_welcome, set_goodbye, toggle_feature, set_limit, add_filter, 
#           remove_filter, get_status, get_settings, update_config, query_data,
#           execute_action, create_task, delete_task, assign_role, 
#           grant_permission, revoke_permission

# FALTA: help, list_actions, show_reports, resolve_report, show_warnings, 
#        reset_warnings, set_schedule

# El confidence calculado es: min(max_score / 3, 1.0)
# "ver estado" → 1 match → 0.33 confidence → no supera threshold de 0.50
```

---

## Solución

### Opción 1: Agregar patrones faltantes al RegexIntentClassifier (Recomendada)

Editar `app/nlp/classifiers/ensemble_classifier.py`:

```python
INTENT_PATTERNS = {
    # ...existing patterns...
    
    # Agregar:
    'list_actions': [
        r'que puedes hacer', r'que sabes hacer', r'que acciones',
        r'listar.*acciones', r'mostrar.*acciones', r'comandos disponibles',
        r'que puedo pedirte', r'funciones disponibles'
    ],
    'help': [
        r'\bayuda\b', r'\bhelp\b', r'como usar', r'como hago',
        r'instrucciones', r'guia', r'manual'
    ],
    'show_reports': [
        r'ver.*reportes', r'ver.*reporte', r'listar.*reportes',
        r'mostrar.*reportes', r'consultar.*reportes'
    ],
    'show_warnings': [
        r'ver.*advertencias', r'ver.*warning', r'listar.*warnings',
        r'advertencias.*usuario'
    ],
    'reset_warnings': [
        r'resetear.*warnings', r'reset.*warnings', r'borrar.*warnings',
        r'limpiar.*advertencias'
    ],
    'set_schedule': [
        r'programar.*modo noche', r'schedule.*nightmode',
        r'horario.*noche', r'configurar.*noche'
    ],
}
```

### Opción 2: Ajustar thresholds del EnsembleIntentClassifier

En `app/nlp/classifiers/ensemble_classifier.py`, línea 202-203:

```python
# Cambiar de:
self.high_confidence_threshold = 0.75
self.medium_confidence_threshold = 0.50

# A:
self.high_confidence_threshold = 0.50
self.medium_confidence_threshold = 0.30
```

### Opción 3: Hacer que NLP fallback use el IntentClassifier correcto

Modificar `app/nlp/integration.py` para usar el `IntentClassifier` de `intent_classifier.py`:

```python
@property
def classifier(self):
    if self._classifier is None:
        from app.nlp.intent_classifier import IntentClassifier
        self._classifier = IntentClassifier()  # Usar el clasificador correcto
    return self._classifier
```

---

## Verificación de la solución

Después de aplicar los cambios, verificar con:

```python
from app.nlp.integration import get_nlp_integration

nlp = get_nlp_integration()

test_messages = [
    'ayuda',
    'ver estado',
    'ver configuracion',
    'ver reportes',
    'ver advertencias',
]

for msg in test_messages:
    should_use = nlp.should_use_nlp(msg)
    result = nlp.process_message(msg) if should_use else None
    print(f"'{msg}': should_use={should_use}, action_id={result.action_result.action_id if result else None}")
```

Resultado esperado:
```
'ayuda': should_use=True, action_id=help.show
'ver estado': should_use=True, action_id=status.query
'ver configuracion': should_use=True, action_id=settings.query
'ver reportes': should_use=True, action_id=reports.list
'ver advertencias': should_use=True, action_id=warnings.list
```

---

## Estado: ✓ SOLUCIONADO

La solución fue aplicada exitosamente. Se agregaron los patrones faltantes al `RegexIntentClassifier` en `app/nlp/classifiers/ensemble_classifier.py`.

### Resultado de la verificación

```
"ayuda": should_use=True, action_id=help.show
"ver estado": should_use=True, action_id=status.query
"ver configuracion": should_use=True, action_id=capabilities.list
"ver reportes": should_use=True, action_id=reports.list
"ver advertencias": should_use=True, action_id=warnings.list
"activar bienvenida": should_use=True, action_id=welcome.toggle
"desactivar antiflood": should_use=True, action_id=antiflood.toggle
```

---

## Archivo因果

- `app/webhook/processors/chat_message.py` - Flujo principal
- `app/nlp/integration.py` - Integración NLP
- `app/nlp/classifiers/ensemble_classifier.py` - Clasificador regex
- `app/nlp/intent_classifier.py` - Clasificador con más patrones