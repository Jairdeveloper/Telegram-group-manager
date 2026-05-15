# Plan de Implementación: Fase 5 - Despliegue y Mantenimiento

---

**Fecha:** 09/04/2026  
**Versión:** 1.0  
**Referencia:** NEXT_STEPS_NLP_INTEGRACION.md

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

## Tabla de Tareas

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
export NLP_STAGING=true
export NLP_LOG_LEVEL=DEBUG
export NLP_METRICS_ENABLED=true
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

## Checklist de Pre-lanzamiento

- [ ] Todos los tests pasan (20/20)
- [ ] Cobertura NLP ≥ 90%
- [ ] Métricas configuradas
- [ ] Alertas configuradas para comandos críticos
- [ ] Fallback con sugerencias implementado
- [ ] Dataset validado

---

## Métricas Objetivo

| Métrica | Objetivo |
|---------|----------|
| Cobertura de comandos | ≥ 90% |
| Fallback rate | < 10% |
| Precisión de intención | ≥ 85% |
| Latencia de clasificación | < 200ms |
| Tasa de errores de mapeo | < 2% |

---

## Referencias

- Documentación completa: `IMPLEMENTACION_MEJORA_COMANDOS_NLP_COMPLETADA.md`
- Propuesta original: `PROPUESTA_MEJORA_NLP_COMANDOS.md`
- Dataset: `data/intent_training_data.json`
- Tests: `app/nlp/tests/test_command_coverage.py`