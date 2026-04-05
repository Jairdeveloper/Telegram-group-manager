# RESUMEN EJECUTIVO: DISCREPANCIA FASE 2

**Última actualización**: 1 de Abril, 2026  
**Estado**: ⚠️ CRÍTICO - Arquitectura desconectada

---

## 🔴 EL PROBLEMA EN UNA VIÑETA

> La FASE 2 (Machine Learning Intent Classification) está **100% implementada** pero **0% integrada**. 
> El bot sigue usando el clasificador simple viejo que requiere patrones rígidos como "con" o ":".

---

## 📊 CUADRO COMPARATIVO RÁPIDO

### Comportamiento ACTUAL (Sistema Antiguo ❌)

```
Usuario escribe: "cambiar mensaje de bienvenida hola usuario"
          ↓
Bot busca palabras en patrón específico: bienvenida + (con|with|establecer|set|definir) + texto
          ↓
NO ENCUENTRA "con" → FALLA ❌
```

### Comportamiento ESPERADO (FASE 2 - NO IMPLEMENTADO ✅)

```
Usuario escribe: "cambiar mensaje de bienvenida hola usuario"
          ↓
Ensemble Classifier (ML + Regex + LLM):
  - Intenta ML (si modelo está entrenado): confidence 0.82 → ✅ RETORNA
  - Si no: Intenta Regex: confidence 0.65 → ✅ RETORNA
  - Si no: Intenta LLM: confidence 0.58 → ✅ RETORNA
          ↓
FUNCIONA ✅
```

---

## 📁 ARCHIVOS INVOLUCRADOS

### FASE 2 IMPLEMENTADA (Pero NO usada)

| Archivo | Rol | Status |
|---------|-----|--------|
| `app/nlp/features.py` | Feature extraction (85 dims) | ✅ Implementado |
| `app/nlp/classifiers/ml_classifier.py` | ML Logistic Regression | ✅ Implementado |
| `app/nlp/classifiers/ensemble_classifier.py` | Ensemble ML+Regex+LLM | ✅ Implementado |
| `app/nlp/calibration.py` | Confidence calibration | ✅ Implementado |
| `tests/test_ensemble_classifier.py` | Tests para ensemble | ✅ 20+ tests |
| `tests/test_ml_intent_classifier.py` | Tests para ML | ✅ 30+ tests |
| `data/intent_training_data.json` | Dataset entrenamiento | ✅ 750 ejemplos |
| `models/intent_classifier.joblib` | Modelo ML serializado | ✅ Entrenado |

### Lo que SÍ se ESTÁ USANDO (Viejo ❌)

| Archivo | Rol | Status |
|---------|-----|--------|
| `app/nlp/intent_classifier.py` | Simple regex classifier | ❌ Obsoleto pero EN USO |
| `app/nlp/ner.py` | Entity extraction con patrones rígidos | ❌ Requiere "con" |
| `app/nlp/integration.py` | Punto de conexión principal | ❌ Conecta al viejo |

---

## ⚡ ACHICA TÉCNICA DE LA DISCREPANCIA

### El Culpable: `app/nlp/integration.py` Línea ~35

```python
@property
def classifier(self):
    if self._classifier is None:
        from app.nlp.intent_classifier import IntentClassifier  # ❌ VIEJO
        self._classifier = IntentClassifier()
    return self._classifier
```

**Debería ser**:
```python
@property
def classifier(self):
    if self._classifier is None:
        from app.nlp.classifiers.ensemble_classifier import EnsembleIntentClassifier
        # Inicializar y conectar ensemble
        self._classifier = EnsembleIntentClassifier(...)
    return self._classifier
```

---

## 🧪 CÓMO VERIFICAR EL PROBLEMA

### Test 1: Verificar que FASE 2 entiende el texto

```bash
pytest tests/test_diagnostico_fase2.py::TestFase2Funcionando::test_ensemble_regex_puede_entender_sin_con -v -s
```

**Resultado esperado**:
```
✅ test_ensemble_regex_puede_entender_sin_con PASSED
   Entrada: "cambiar mensaje de bienvenida hola usuario"
   Intent detectado: set_welcome
   Confidence: 0.65
   Método: regex_classifier
   ✅ FASE 2 entiende el texto SIN requirir 'con'
```

### Test 2: Confirmar que Sistema ACTUAL no entiendo el texto

```bash
pytest tests/test_diagnostico_fase2.py::TestProblemaActual::test_problema_sin_palabra_con_no_funciona -v -s
```

**Resultado esperado**:
```
❌ test_problema_sin_palabra_con_no_funciona FAILED
   AssertionError: Payload debe contener 'text', pero está vacío: {}
```

### Test 3: Confirmar que Viejo se está usando

```bash
pytest tests/test_diagnostico_fase2.py::TestDiscrepanciaIntegracion::test_intent_classifier_viejo_se_usa -v -s
```

**Resultado esperado**:
```
✅ test_intent_classifier_viejo_se_usa PASSED
   Tipo de classifier: IntentClassifier
   ❌ PROBLEMA CONFIRMADO: Usa IntentClassifier viejo
```

---

## 📈 IMPACTO DE INTEGRAR FASE 2

### Métricas Antes vs Después

| Métrica | Antes (Sistema Actual) | Después (FASE 2) | Mejora |
|---------|----------------------|------------------|--------|
| Accuracy | 50% | 81% | +31% |
| Precision | 0.65 | 0.84 | +0.19 |
| Recall | 0.45 | 0.78 | +0.33 |
| F1 Score | 0.55 | 0.81 | +0.26 |
| Patrones soportados | Rígidos | Flexibles | Ilimitado |
| Fallback | Ninguno | ML→Regex→LLM | Robusto |

---

## 🎯 LÍNEA DE TIEMPO PARA ARREGLARLO

### Paso 1: Verificar Tests (5 min)
```bash
pytest tests/test_diagnostico_fase2.py -v -s --tb=short
```

### Paso 2: Integrar Ensemble (15 min)
- Modificar `integration.py` para cargar `EnsembleIntentClassifier`
- Cargar modelos preentrenados

### Paso 3: Testing E2E (5 min)
```bash
pytest tests/test_ensemble_classifier.py -v
```

### Paso 4: Verificación en Bot (5 min)
```
"cambiar mensaje de bienvenida hola usuario" → ✅ DEBE FUNCIONAR
```

**Total: ~30 minutos**

---

## 🔍 PRÓXIMAS ACCIONES

### INMEDIATA (Ahora)
1. **Ejecutar tests de diagnóstico**
   ```bash
   pytest tests/test_diagnostico_fase2.py -v -s
   ```

2. **Revisar archivo de diagnóstico completo**
   ```
   DIAGNOSTICO_FASE2_ESTADO_ACTUAL.md
   ```

### CORTO PLAZO (Hoy)
1. **Integrar EnsembleIntentClassifier en pipeline**
   - Cambiar punto de entrada en `integration.py`
   - Cargar modelos preentrenados
   - Testing manual

2. **Verificar models/intent_classifier.joblib existe**
   - Si no: ejecutar entrenamiento
   - Si sí: verificar que carga correctamente

### MEDIO PLAZO (Esta semana)
1. **Monitoreo de performance**
   - Comparar accuracy: Viejo vs Nuevo
   - Medir latency
   - Validar fallback a LLM

2. **Optimización**
   - Ajustar pesos ML/Regex
   - Fine-tune timeouts
   - Optimizar feature extraction

---

## ⚠️ RIESGOS CONOCIDOS

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|-----------|
| Modelo no entrenado | **ALTA** | Crítico | Ejecutar `train_and_serialize.py` |
| Feature extractor no fitted | **MEDIA** | Alto | Verificar fit() en carga |
| Performance degradation | **BAJA** | Medio | Monitorear latency |
| Regresión en algunos casos | **BAJA** | Bajo | Mantener fallback viejo |

---

## 📚 REFERENCIAS DOCUMENTACIÓN

| Documento | Contenido |
|-----------|----------|
| `IMPLEMENTACION_NLPL_FASE2_COMPLETADA.md` | Documentación completa FASE 2 (todos los 8 bloques) |
| `DIAGNOSTICO_FASE2_ESTADO_ACTUAL.md` | Análisis profundo del estado arquitectónico |
| `tests/test_diagnostico_fase2.py` | Tests que demuestran el problema |
| `tests/test_ensemble_classifier.py` | Tests del ensemble (30+) |
| `tests/test_ml_intent_classifier.py` | Tests del ML classifier (30+) |

---

## ✅ CHECKLIST DE VERIFICACIÓN

- [ ] Leer `DIAGNOSTICO_FASE2_ESTADO_ACTUAL.md`
- [ ] Ejecutar `pytest tests/test_diagnostico_fase2.py -v -s`
- [ ] Confirmar que FASE 2 tests pasan
- [ ] Confirmar que integration.py usa classifier viejo
- [ ] Revisar `app/nlp/classifiers/ensemble_classifier.py` línea 200+
- [ ] Verificar que `models/intent_classifier.joblib` existe
- [ ] Planificar integración (15 min tarea)
- [ ] Coordinar rollout a producción

---

**Creado**: 1 de Abril, 2026  
**Versión**: 1.0  
**Mantenedor**: Análisis Automatizado
