# Plan de Implementación: Arquitectura NLP para el Robot

---

**Fecha:** 29/03/2026

**Version:** 1.0

**Referencia:** MIGRACION_ARQUITECTURA.md

---

## Resumen de la Implementacion

Este documento detalla el plan de implementación para la migración de la arquitectura actual del Robot hacia un pipeline robusto de Procesamiento de Lenguaje Natural (PLN). La implementación se realizará en 5 fases incrementales, manteniendo compatibilidad con el sistema actual y utilizando spaCy como herramienta principal de procesamiento.

**Objetivo General:** Transformar el parser basado en reglas regex frágil en un pipeline NLP escalable y mantenible con múltiples capas de análisis.

---

## Arquitectura Final

```
Usuario → Normalizer → Tokenizer → POS Tagger → NER → Intent Classifier → Entity Extractor → Action Mapper → ActionExecutor
                                                           ↓
                                                      LLM (fallback)
```

**Componentes del pipeline:**

| Componente | Archivo | Funcion |
|------------|---------|---------|
| TextNormalizer | `app/nlp/normalizer.py` | Limpiar y estandarizar texto de entrada |
| NLPTokenizer | `app/nlp/tokenizer.py` | Tokenizar y etiquetar partes gramaticales |
| POS Tagger | Integrado en tokenizer | Analizar estructura gramatical |
| EntityExtractor | `app/nlp/ner.py` | Detectar entidades relevantes |
| IntentClassifier | `app/nlp/intent_classifier.py` | Clasificar intención del usuario |
| ActionMapper | `app/nlp/action_mapper.py` | Mapear intención a accion específica |
| NLPPipeline | `app/nlp/pipeline.py` | Orquestador del pipeline completo |

---

## Tabla de Tareas

| Fase | Duracion | Tarea | Prioridad | Estado |
|------|----------|-------|-----------|--------|
| 1 | Semana 1 | Crear TextNormalizer | Alta | Pendiente |
| 1 | Semana 1 | Integrar en ActionParser | Alta | Pendiente |
| 1 | Semana 1 | Tests unitarios normalizer | Alta | Pendiente |
| 2 | Semana 2 | Crear NLPTokenizer con spaCy | Alta | Pendiente |
| 2 | Semana 2 | Agregar analisis POS al parser | Media | Pendiente |
| 2 | Semana 2 | Tests de integracion tokenizer | Media | Pendiente |
| 3 | Semana 3 | Crear IntentClassifier | Alta | Pendiente |
| 3 | Semana 3 | Crear EntityExtractor (NER) | Alta | Pendiente |
| 3 | Semana 3 | Definir intents principales | Alta | Pendiente |
| 4 | Semana 4 | Crear ActionMapper | Alta | Pendiente |
| 4 | Semana 4 | Migrar reglas existentes | Alta | Pendiente |
| 4 | Semana 4 | Tests end-to-end | Alta | Pendiente |
| 5 | Semana 5 | Crear NLPPipeline (orchestrator) | Alta | Pendiente |
| 5 | Semana 5 | Reemplazar ActionParser gradualmente | Alta | Pendiente |
| 5 | Semana 5 | Documentacion final | Media | Pendiente |

---

## Fase 1: Normalizacion de Texto

**Objetivo fase:** Limpiar y estandarizar el texto de entrada del usuario

**Implementacion fase:**

1. Crear archivo `app/nlp/normalizer.py`
2. Implementar clase `TextNormalizer` con los siguientes metodos:
   - Convertir a minusculas
   - Remover numeros
   - Remover puntuacion
   - Remover espacios extra
3. Crear tests unitarios en `tests/nlp/test_normalizer.py`
4. Integrar normalizer en `ActionParser.parse()` existente
5. Agregar logging para debugging

**Archivos a crear/modificar:**
- `app/nlp/normalizer.py` (crear)
- `app/nlp/__init__.py` (actualizar)
- `app/agent/actions/parser.py` (integrar)
- `tests/nlp/test_normalizer.py` (crear)

**Criterio de exito:** Normalizer procesa texto sin errores y reduce ruido en input

---

## Fase 2: Tokenizacion y Analisis POS

**Objetivo fase:** Analizar la estructura gramatical del texto para mejorar la comprensión

**Implementacion fase:**

1. Crear archivo `app/nlp/tokenizer.py`
2. Implementar clase `NLPTokenizer`:
   - Cargar modelo spaCy `es_core_news_sm`
   - Metodo `tokenize()` que devuelve tokens, POS tags y lemmas
3. Crear tests de integracion
4. Integrar analisis POS en el flujo del parser

**Archivos a crear/modificar:**
- `app/nlp/tokenizer.py` (crear)
- `app/nlp/__init__.py` (actualizar)
- `tests/nlp/test_tokenizer.py` (crear)

**Criterio de exito:** Tokenizer devuelve estructura gramatical correcta para oraciones en español

**Dependencias:**
```
spacy>=3.7.0
python -m spacy download es_core_news_sm
```

---

## Fase 3: NER y Clasificacion de Intencion

**Objetivo fase:** Identificar entidades relevantes y clasificar la intención del usuario

**Implementacion fase:**

1. Crear archivo `app/nlp/intent_classifier.py`
   - Definir constantes de intents (set_welcome, toggle_feature, set_limit, add_filter, remove_filter)
   - Implementar metodo `classify()` con clasificacion basada en embeddings o regex
2. Crear archivo `app/nlp/ner.py`
   - Implementar clase `EntityExtractor`
   - Detectar entidades: ACTION_TYPE, SETTING_VALUE, MODIFIER
3. Definir intents principales:

| Intencion | Descripcion | Ejemplo |
|-----------|-------------|---------|
| set_welcome | Establecer mensaje de bienvenida | "quiero cambiar la bienvenida" |
| toggle_feature | Activar/desactivar funcion | "activa antiflood" |
| set_limit | Configurar limites | "pon limite de 5 mensajes" |
| add_filter | Agregar filtro | "bloquea la palabra spam" |
| remove_filter | Quitar filtro | "desbloquea spam" |

4. Crear tests para ambos componentes

**Archivos a crear/modificar:**
- `app/nlp/intent_classifier.py` (crear)
- `app/nlp/ner.py` (crear)
- `app/nlp/__init__.py` (actualizar)
- `tests/nlp/test_intent_classifier.py` (crear)
- `tests/nlp/test_ner.py` (crear)

**Criterio de exito:** Classifier alcanza >80% accuracy en intents definidos

---

## Fase 4: Action Mapper

**Objetivo fase:** Mapear la intención identificada a una acción específica del sistema

**Implementacion fase:**

1. Crear archivo `app/nlp/action_mapper.py`
2. Implementar clase `ActionMapper`:
   - Metodo `map()` que recibe intent, entities y original_text
   - Casos para cada intent definido
   - Retornar `ActionParseResult` con action_id, payload y confidence
3. Migrar reglas existentes del `ActionParser` actual
4. Mantener backwards compatibility con sistema existente
5. Crear tests end-to-end

**Ejemplo de implementacion:**
```python
def map(self, intent: str, entities: dict, original_text: str) -> ActionParseResult:
    if intent == "set_welcome":
        text = entities.get("welcome_text") or self._extract_welcome_text(original_text)
        return ActionParseResult(
            action_id="welcome.set_text",
            payload={"text": text},
            confidence=0.85,
        )
```

**Archivos a crear/modificar:**
- `app/nlp/action_mapper.py` (crear)
- `app/nlp/__init__.py` (actualizar)
- `tests/nlp/test_action_mapper.py` (crear)

**Criterio de exito:** ActionMapper mapea correctamente >90% de los casos de uso definidos

---

## Fase 5: Pipeline Integrado

**Objetivo fase:** Orquestar todos los componentes en un pipeline unificado y reemplazar gradualmente el ActionParser

**Implementacion fase:**

1. Crear archivo `app/nlp/pipeline.py`
2. Implementar clase `NLPPipeline`:
   - Inicializar todos los componentes del pipeline
   - Metodo `process()` que ejecuta el flujo completo
   - Manejo de errores y fallback a LLM cuando sea necesario
3. Crear archivo `app/nlp/exceptions.py` para excepciones personalizadas
4. Actualizar `ActionParser` para usar el nuevo pipeline como opcion primaria
5. Mantener parser actual como fallback
6. Agregar configuracion para habilitar/deshabilitar NLP pipeline
7. Documentar API y casos de uso

**Archivos a crear/modificar:**
- `app/nlp/pipeline.py` (crear)
- `app/nlp/exceptions.py` (crear)
- `app/nlp/__init__.py` (actualizar exportacion)
- `app/agent/actions/parser.py` (integrar pipeline)
- `docs/nlp/pipeline.md` (documentacion)

**Criterio de exito:** Pipeline integrado funciona correctamente con todos los componentes y mantiene backwards compatibility

---

## Estructura Final de Archivos

```
app/
├── nlp/
│   ├── __init__.py
│   ├── normalizer.py
│   ├── tokenizer.py
│   ├── ner.py
│   ├── intent_classifier.py
│   ├── action_mapper.py
│   ├── pipeline.py
│   └── exceptions.py
├── agent/
│   └── actions/
│       └── parser.py
tests/
├── nlp/
│   ├── test_normalizer.py
│   ├── test_tokenizer.py
│   ├── test_intent_classifier.py
│   ├── test_ner.py
│   ├── test_action_mapper.py
│   └── test_pipeline.py
```

---

## Dependencias a Instalar

```bash
pip install spacy>=3.7.0
python -m spacy download es_core_news_sm
pip install nltk>=3.8.0
pip install scikit-learn>=1.3.0
pip install numpy>=1.24.0
```

---

## Metricas de Exito

| Metrica | Actual | Objetivo |
|---------|--------|----------|
| Accuracy de parseo | ~60% | >90% |
| Tiempo de respuesta | ~500ms | <300ms |
| Fallback a LLM | 100% cuando falla | <30% |
| Cobertura de intents | 5 | 20+ |

---

## Notas de Implementacion

1. **Backwards Compatibility:** El ActionParser actual debe funcionar como fallback
2. **Logging:** Agregar logging en cada fase del pipeline para facilitar debugging
3. **Enhancement Progresivo:** Empezar con regex simple, agregar NLP gradualmente
4. **Fallback a LLM:** Usar LLM solo cuando el pipeline NLP no pueda determinar la accion
5. **Testing:** Cada fase debe incluir tests unitarios y de integracion

---

## Orden de Implementacion Recomendado

1. Normalizer (base para todo)
2. Tokenizer (dependencia para NER)
3. Intent Classifier y NER (analisis semantico)
4. Action Mapper (mapeo a acciones)
5. Pipeline Orchestrator (integracion final)
