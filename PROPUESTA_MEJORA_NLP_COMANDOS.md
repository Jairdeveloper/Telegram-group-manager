# Propuesta de Implementación: Mejorar el entendimiento NLP para todos los comandos disponibles

---

**Fecha:** 05/04/2026  
**version:** 1.0  
**referencia:** app/nlp/, app/telegram/services.py, app/nlp/action_mapper.py, data/intent_training_data.json

---

## Resumen de la migracion

La migración busca ampliar la cobertura del sistema NLP para que comprenda todos los comandos existentes del bot administrador de Telegram. Actualmente el NLP está entrenado en un subconjunto de intenciones y el `ActionMapper` solo transforma unas pocas intenciones en acciones ejecutables. El objetivo es alinear el inventario de comandos del bot con las intenciones del NLP, cubrir expresiones naturales de todos los comandos administrativos y reducir los casos en los que el bot no entiende o no mapea una intención válida.

---

## Arquitectura final

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
│  3. INTENT CLASSIFICATION                                             │
│  - Ensemble regex + ML + LLM                                          │
│  - Cobertura de todos los comandos disponibles                        │
└─────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│  4. ACTION MAPPING                                                    │
│  - Mapear intención a acción bot concreta                             │
│  - Extraer parámetros / entidades                                     │
│  - Manejo de toggle, set, status, permisos, filtros, configuración    │
└─────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│  5. VALIDACIÓN DE COMANDO                                              │
│  - Verificar que el action_id existe en el registry del bot           │
│  - Fallback instructivo si no se entiende                            │
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

## Tabla de tareas

| Fase | Objetivo fase | Implementacion fase | Estado |
|------|---------------|---------------------|--------|
| 1 | Inventario y mapeo completo de comandos | Documentar todos los comandos / intenciones actuales y su cobertura NLP | - |
| 2 | Enriquecer el dataset de comandos | Expandir el dataset con ejemplos reales y variaciones para cada comando | - |
| 3 | Alinear intentiones con el bot | Ampliar intent classifier y ActionMapper para todos los comandos | - |
| 4 | Validaciones y feedback | Crear pruebas, métricas y feedback en tiempo real | - |
| 5 | Despliegue gradual y mantenimiento | Desplegar versiones iterativas de NLP y monitorizar uso real | - |

---

## Fase 1: Inventario y mapeo completo de comandos

**OBjetivo fase:** Identificar todos los comandos administrativos que el bot puede ejecutar y mapearlos con precisión a intenciones NLP.

**Implementacion fase:**

| # | Tarea | Estado |
|---|-------|--------|
| 1 | Extraer la lista de comandos explícitos de `app/telegram/services.py` y de menús del bot | - |
| 2 | Identificar acciones bot del `ActionMapper` y del catálogo de `app/agent/core.py` | - |
| 3 | Crear tabla de intenciones faltantes versus comandos actuales | - |
| 4 | Marcar comandos no cubiertos por `app/nlp/intent_classifier.py` y `app/nlp/action_mapper.py` | - |
| 5 | Priorizar comandos críticos de administración de grupo y configuración | - |
| 6 | Definir gramáticas de comandos en texto libre para cada acción | - |
| 7 | Generar lista de sinónimos / frases comunes por comando | - |
| 8 | Documentar ejemplos de uso real por comando | - |
| 9 | Alinear nomenclatura de comandos con nombres de intenciones | - |
| 10 | Validar que todos los comandos nuevos tienen un intent asociado | - |

---

## Fase 2: Enriquecer el dataset de comandos

**OBjetivo fase:** Construir un dataset robusto que cubra todas las variantes del lenguaje natural usadas para invocar cada comando.

**Implementacion fase:**

| # | Tarea | Estado |
|---|-------|--------|
| 1 | Revisar `data/intent_training_data.json` y añadir ejemplos faltantes por comando | - |
| 2 | Crear ejemplos específicos para comandos administrativos y de moderación | - |
| 3 | Incluir variaciones en español e inglés, regionalismos y abreviaturas | - |
| 4 | Añadir ejemplos de patrones indirectos y preguntas de estado | - |
| 5 | Registrar ejemplos negativos y comandos no válidos para reducir falsos positivos | - |
| 6 | Usar logs reales para generar ejemplos concretos de comandos fallidos | - |
| 7 | Añadir metadatos de fuente y prioridad por comando | - |
| 8 | Implementar un balance de ejemplos entre intenciones frecuentes y raras | - |
| 9 | Crear un dataset de evaluación específico de comandos | - |
| 10 | Validar el dataset con una revisión manual de admins | - |

---

## Fase 3: Alinear intenciones con el bot

**OBjetivo fase:** Ampliar el clasificador e `ActionMapper` para que todas las intenciones de comandos existentes se traduzcan en acciones ejecutables.

**Implementacion fase:**

| # | Tarea | Estado |
|---|-------|--------|
| 1 | Ampliar `MLIntentClassifier.INTENT_CLASSES` con comandos no cubiertos | - |
| 2 | Extender `IntentClassifier.INTENTS` con keywords de todos los comandos | - |
| 3 | Añadir patrones missing en `RegexIntentClassifier.INTENT_PATTERNS` | - |
| 4 | Crear mapeos en `ActionMapper.ACTION_MAPPINGS` para nuevos intents | - |
| 5 | Implementar lógica adicional en `_execute_mapping` para nuevos comandos | - |
| 6 | Mejorar `detect_feature()` y `EntityExtractor` para reconocer argumentos de comando | - |
| 7 | Agregar soporte para comandos compuestos y multi-intención | - |
| 8 | Verificar que cada `action_id` mapeado existe en el runtime del bot | - |
| 9 | Ajustar umbrales de confianza para cobertura completa de comandos | - |
| 10 | Registrar `fallback_reason` específico para cada comando no entendido | - |

---

## Fase 4: Validaciones y feedback

**OBjetivo fase:** Asegurar que el NLP entienda el conjunto completo de comandos con pruebas, métricas y retroalimentación activa.

**Implementacion fase:**

| # | Tarea | Estado |
|---|-------|--------|
| 1 | Crear tests unitarios para cada comando/intención nueva | - |
| 2 | Añadir tests de integración en `app/nlp/tests/` con ejemplos de comando reales | - |
| 3 | Implementar métricas de cobertura de comandos en producción | - |
| 4 | Medir intent_confidence y tasa de fallback por comando | - |
| 5 | Crear alertas para comandos críticos mal clasificados | - |
| 6 | Añadir logging de intent / action_id en `app/webhook/processors/chat_message.py` | - |
| 7 | Implementar mecanismo de feedback para admins cuando el bot no entiende | - |
| 8 | Evaluar regularmente la matriz de confusión por comando | - |
| 9 | Ajustar dataset y patrones con base en errores detectados | - |
| 10 | Asegurar tests de regresión antes de cada despliegue | - |

---

## Fase 5: Despliegue gradual y mantenimiento

**OBjetivo fase:** Introducir mejoras de NLP de forma controlada y mantener la cobertura completa de comandos en el tiempo.

**Implementacion fase:**

| # | Tarea | Estado |
|---|-------|--------|
| 1 | Desplegar iteraciones de NLP con canary / validación progresiva | - |
| 2 | Mantener versionamiento de modelos y mapeos de intenciones | - |
| 3 | Implementar rollback rápido si comandos cruciales fallan | - |
| 4 | Añadir monitoreo continuo de uso de comandos | - |
| 5 | Actualizar dataset de comandos cada vez que se agregue uno nuevo | - |
| 6 | Crear documentación interna de comandos y ejemplos de lenguaje | - |
| 7 | Mantener un catálogo vivo de comandos soportados y su cobertura NLP | - |
| 8 | Incorporar nuevos comandos con pipeline de validación automática | - |
| 9 | Revisar cada 2 semanas los casos de comando no entendido | - |
| 10 | Conservar fallback instructivo que sugiera al usuario el comando correcto | - |

---

## Recomendaciones clave

- Priorizar la cobertura de comandos antes de ampliar capacidades generales de NLP.
- Asegurar que cada comando del bot tenga una intención única y una ruta de mapeo clara.
- Evitar que keywords genéricas como "activar" o "configurar" causen false positives en comandos no relacionados.
- Usar logs reales de comandos fallidos para alimentar el entrenamiento y los patrones regex.
- Definir un mecanismo de retroalimentación explícito para admins cuando el bot no entienda un comando.
- Mantener el `ActionMapper` sincronizado con el catálogo de acciones del bot y con los nombres de `action_id`.
- Establecer pruebas de regresión por comando para prevenir roturas cuando se agregue un nuevo comando.
- Si el proyecto evoluciona, considerar un modelo específico por dominio de comando (configuración, moderación, estado, permisos).

---

## Riesgos y mitigaciones

- **Riesgo:** Cobertura parcial de comandos provoca intentos de interpretación incorrecta.
  - **Mitigación:** Implementar fallback claro que indique qué comandos el bot entiende.

- **Riesgo:** El vocabulario de comando crece y las reglas regex se vuelven difíciles de mantener.
  - **Mitigación:** Potenciar el ML/Transformer con dataset balanceado y mantener reglas solo como safety net.

- **Riesgo:** Nuevos comandos no se reflejan en el `ActionMapper` y se clasifican sin ejecutar acción.
  - **Mitigación:** Agregar tests automatizados de mapeo comando→acción para cada nuevo comando.

- **Riesgo:** Cambios en el nombre de `action_id` desalinean el runtime del bot.
  - **Mitigación:** Validar automáticamente `action_id` contra el registro de acciones en tiempo de inicialización.

---

## Métricas de éxito

- Cobertura de comandos NLP = 100% para comandos documentados.
- Reducción de fallbacks en comandos administrativos > 80%.
- Precisión de intención para comandos críticos > 90%.
- Latencia de clasificación < 200ms.
- Tasa de errores de mapeo comando→acción < 2%.