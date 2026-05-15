# Próximos Pasos: Integración y Entrenamiento del Sistema NLP Mejorado

---

**Fecha:** 05/04/2026  
**Versión:** 1.0  
**Referencia:** IMPLEMENTACION_MEJORA_COMANDOS_NLP_COMPLETADA.md, PROPUESTA_MEJORA_NLP_COMANDOS.md

---

## Resumen de la Migración

El sistema NLP del bot ha sido mejorado para comprender y procesar todos los comandos de administración de grupo de Telegram. Las fases 1-4 han sido completadas, alcanzando una cobertura del 95% de los comandos administrativos.

### Estado Actual

| Métrica | Valor Anterior | Valor Actual |
|---------|----------------|---------------|
| Intenciones cubiertas | 10 | 17 |
| Action mappings | 6 | 17 |
| Features detectables | 5 | 12 |
| Ejemplos en dataset | 460 | 540+ |
| Cobertura NLP | 40% | 95% |
| Tests unitarios | 0 | 20+ |

### Componentes Implementados

- **IntentClassifier**: 17 intenciones con keywords en español e inglés
- **ActionMapper**: 17 mapeos intencion→acción
- **EntityExtractor**: Extracción de límites, acciones, IDs de reporte, horarios
- **NLPMetricsCollector**: Métricas de producción
- **NLPFeedbackManager**: Feedback para admins

---

## Arquitectura Final

```
┌─────────────────────────────────────────────────────────────────────┐
│                  Mensaje Telegram / Comando de usuario              │
└─────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│  1. INPUT CAPTURE                                                    │
│  - Comandos / texto libre                                             │
│  - Mensajes de administradores                                       │
└─────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│  2. NORMALIZACIÓN y TOKENIZACIÓN                                      │
│  - text cleaning                                                     │
│  - normalización lingüística                                         │
│  - token hinting de intención                                        │
└─────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│  3. INTENT CLASSIFICATION (17 intents)                              │
│  - Regex + keyword matching                                          │
│  - Cobertura: 95% comandos administrativos                          │
└─────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│  4. ACTION MAPPING (17 action_ids)                                   │
│  - Mapear intención a acción bot concreta                             │
│  - Extraer parámetros / entidades                                     │
└─────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│  5. VALIDACIÓN DE COMANDO                                              │
│  - Verificar que el action_id existe en el registry                  │
│  - Fallback con sugerencias si no se entiende                        │
└─────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│  6. EJECUCIÓN / RESPUESTA                                             │
│  - Ejecutar configuración o comando                                   │
│  - Confirmar al usuario con el comando reconocido                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Tabla de Tareas: Fase 5 - Despliegue y Mantenimiento

| # | Tarea | Estado | Prioridad |
|---|-------|--------|-----------|
| 1 | Ejecutar tests de regresión | ⏳ PENDIENTE | P1 |
| 2 | Validar dataset con ejemplos de producción | ⏳ PENDIENTE | P1 |
| 3 | Configurar environment de staging | ⏳ PENDIENTE | P1 |
| 4 | Desplegar en modo canary (10% tráfico) | ⏳ PENDIENTE | P2 |
| 5 | Monitorear métricas de clasificación | ⏳ PENDIENTE | P2 |
| 6 | Ajustar umbrales de confianza | ⏳ PENDIENTE | P2 |
| 7 | Desplegar a producción (100%) | ⏳ PENDIENTE | P3 |
| 8 | Configurar alertas de Fallback | ⏳ PENDIENTE | P3 |
| 9 | Documentar comandos soportados | ⏳ PENDIENTE | P3 |
| 10 | Configurar pipeline de actualización | ⏳ PENDIENTE | P3 |

---

## Fase 5: Despliegue gradual y mantenimiento

**Objetivo fase:** Introducir mejoras de NLP de forma controlada y mantener la cobertura completa de comandos en el tiempo.

### Implementacion fase

#### 1. Prerrequisitos para Despliegue

```bash
# Instalar dependencias actualizadas
pip install -r requirements.txt

# Verificar que los tests pasan
pytest app/nlp/tests/test_command_coverage.py -v

# Verificar integridad del dataset
python -c "import json; d=json.load(open('data/intent_training_data.json')); print(f'Ejemplos: {len(d[\"training_data\"])}')"
```

#### 2. Environment de Staging

```bash
# Configurar variables de entorno para staging
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{"message": {"chat": {"id": 123}, "text": "activar bienvenida", "from": {"id": 456}}}'
```

#### 3. Despliegue Canary

```python
# En app/nlp/__init__.py o configuración
USE_NLP_CANARY = os.getenv("NLP_CANARY_PERCENT", "10")  # 10% initially
```

#### 4. Monitoreo

```python
# Usar el metrics collector
from app.nlp.metrics import get_metrics_collector

collector = get_metrics_collector()
coverage = collector.get_coverage_report()
alerts = collector.get_critical_commands_alerts()

# Integrar con监控系统
# - Prometheus: metrics
# - Grafana: dashboards
# - PagerDuty: alerts
```

#### 5. Fallback y Feedback

```python
# Configurar feedback
from app.nlp.feedback import get_feedback_manager, record_fallback

# En tu webhook/processor:
if not intent:
    record_fallback(text, "no_intent", user_id, chat_id)
    reply = get_suggestion(text)
```

---

## Guía de Integración

### Paso 1: Preparación

1. **Verificar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Ejecutar tests:**
   ```bash
   pytest app/nlp/tests/test_command_coverage.py -v
   ```

3. **Validar configuración:**
   ```bash
   python -c "from app.nlp import get_classifier, get_mapper; print('NLP OK')"
   ```

### Paso 2: Integración en Webhook

El NLP ya está integrado en `app/webhook/processors/chat_message.py`. Verifica que funciona:

```bash
# Probar con un mensaje de test
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{"message": {"chat": {"id": 123}, "text": "activar bienvenida", "from": {"id": 456}}}'
```

### Paso 3: Verificación de Cobertura

```python
from app.nlp.intent_classifier import get_classifier
from app.nlp.action_mapper import get_mapper

classifier = get_classifier()
mapper = get_mapper()

# Probar comandos clave
test_commands = [
    "activar bienvenida",
    "cambiar mensaje de bienvenida",
    "desactivar antiflood",
    "bloquear palabra spam",
    "ver estado del bot",
    "ver configuracion",
]

for cmd in test_commands:
    intent, conf = classifier.classify(cmd)
    result = mapper.map(cmd, intent)
    print(f"{cmd}: {intent} -> {result.action_id} (conf: {conf:.2f})")
```

### Paso 4: Configuración de Métricas

```python
# En tu aplicación principal
from app.nlp.metrics import track_intent_classification, track_command_execution
import time

# Track classification
start = time.time()
intent, conf = classifier.classify(text)
track_intent_classification(intent, conf, success=True)

# Track execution
start_exec = time.time()
# ... execute action ...
track_command_execution(action_id, (time.time() - start_exec) * 1000, success)
```

### Paso 5: Feedback Loop

```python
# Configurar feedback endpoint (opcional)
from app.nlp.feedback import get_feedback_manager

manager = get_feedback_manager()

# Obtener fallbacks no resueltos
unresolved = manager.get_unresolved_fallbacks()

# Obtener patrones comunes
patterns = manager.get_common_patterns()
```

---

## Verificación de Producción

### Checklist de Pre-lanzamiento

- [ ] Todos los tests pasan (20/20)
- [ ] Cobertura NLP ≥ 90%
- [ ] Métricas configuradas
- [ ] Alertas configuradas para comandos críticos
- [ ] Fallback con sugerencias implementado
- [ ] Dataset validado

### Métricas Objetivo

| Métrica | Objetivo |
|---------|----------|
| Cobertura de comandos | ≥ 90% |
| Fallback rate | < 10% |
| Precisión de intención | ≥ 85% |
| Latencia de clasificación | < 200ms |
| Tasa de errores de mapeo | < 2% |

---

## Mantenimiento Continuo

### Revisión Semanal

1. Revisar métricas de fallback
2. Analizar patrones de comandos no entendidos
3. Ajustar keywords si es necesario

### Revisión Mensual

1. Actualizar dataset con nuevos ejemplos
2. Re-entrenar modelo si se usa ML
3. Actualizar tests si hay nuevos comandos
4. Documentar nuevos comandos agregados

### Actualización de Comandos

Cuando se agregue un nuevo comando:

1. Añadir al `INTENTS` en `intent_classifier.py`
2. Añadir al `ACTION_MAPPINGS` en `action_mapper.py`
3. Añadir al `FEATURE_KEYWORDS` si es una feature
4. Añadir ejemplos al dataset
5. Añadir tests
6. Desplegar con el pipeline

---

## Notas

- **Dependencias**: Las dependencias de NLP ya están en requirements.txt
- **Fallback**: El sistema incluye fallback automático con sugerencias
- **Tests**: 20+ tests unitarios disponibles en `app/nlp/tests/`
- **Métricas**: Sistema de métricas listo para Prometheus/Grafana
- **Feedback**: Mecanismo de feedback para admins implementado

---

## Referencias

- Documentación completa: `IMPLEMENTACION_MEJORA_COMANDOS_NLP_COMPLETADA.md`
- Propuesta original: `PROPUESTA_MEJORA_NLP_COMANDOS.md`
- Dataset: `data/intent_training_data.json`
- Tests: `app/nlp/tests/test_command_coverage.py`
