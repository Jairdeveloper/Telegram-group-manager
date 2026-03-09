# Análisis del Proyecto: Implementación Policy Engine + Planner

## Resumen Ejecutivo

El documento `01_IMPLEMENTACION_SEMANA_6_8_POLICY_PLANNER.md` describe la planificación para implementar un sistema avanzado de políticas, planificación y control de herramientas en las semanas 6-8 del proyecto. **A la fecha del análisis, esta implementación NO está desarrollada en el código base.**

---

## Estado Actual del Proyecto

### Sistema Existente

| Componente | Estado | Ubicación |
|------------|--------|-----------|
| Pattern Engine | ✅ Implementado | `chat_service/pattern_engine.py` |
| Chat Service | ✅ Implementado | `chat_service/agent.py`, `chat_service/brain.py` |
| Telegram Adapter | ✅ Implementado | `app/telegram/` |
| Webhook Handler | ✅ Implementado | `app/webhook/` |
| Database Repositories | ✅ Implementado | `app/database/repositories/` |
| Policy Engine | ❌ No implementado | - |
| Tool Routing | ❌ No implementado | - |
| Planner | ❌ No implementado | - |
| Guardrails | ❌ No implementado | - |

### Motor Actual

El proyecto actualmente utiliza:
- **Pattern Engine**: Sistema basado en reglas y palabras clave (`chat_service/pattern_engine.py`)
- **Orquestación LLM**: OpenAI/Ollama como único orquestador
- **Sin**: Policy engine, tool routing, planner, budgets, guardrails

---

## Análisis de la Implementación Propuesta

### 1. Policy Engine (Semana 6)

#### Estructura Propuesta

```
Policy → Rules → Actions
  ↓
RateLimit, Quota, AccessControl, ContentFilter, Budget
```

#### Componentes a Crear

| Archivo | Descripción |
|---------|-------------|
| `app/policies/models.py` | Modelos: Policy, PolicyRule, Action, PolicyType |
| `app/policies/types.py` | Configuraciones: RateLimitConfig, QuotaConfig, BudgetConfig, ContentFilterConfig, AccessControlConfig |
| `app/policies/engine.py` | PolicyEngine con evaluación de reglas |

#### Funcionalidades

- **Rate Limiting**: Control de requests por minuto/hora
- **Quota**: Límites mensuales de requests y tokens
- **Access Control**: Control de acceso por tenant/chat
- **Content Filter**: Filtrado de palabras clave
- **Budget**: Control de costos LLM por mes

#### Evaluación
La arquitectura propuesta es sólida y escalable. El uso de Pydantic para modelos y la estructura de evaluación basada en prioridades es apropiada para el caso de uso multi-tenant.

---

### 2. Tool Routing (Semana 7)

#### Estructura Propuesta

| Archivo | Descripción |
|---------|-------------|
| `app/tools/registry.py` | Registro de herramientas con ToolRegistry |
| `app/tools/router.py` | Enrutamiento de herramientas basado en mensajes |
| `app/tools/builtins.py` | Herramientas integradas (calculator, search) |

#### Tipos de Herramientas

- SEARCH
- CALCULATOR
- WEATHER
- DATABASE
- HTTP
- CUSTOM

#### Evaluación
El sistema de registry y router es simple pero funcional. La extracción de parámetros es básica (solo raw_input) - se menciona que puede mejorarse con LLM.

---

### 3. Planner (Semana 7-8)

#### Estructura Propuesta

```
app/planner/planner.py
```

#### Componentes

- **PlanStep**: Paso individual con tool, parámetros, dependencias
- **Plan**: Colección de pasos con estado
- **Planner**: Crea y ejecuta planes multi-paso

#### Características

- Descomposición de goals en steps
- Soporte para dependencias entre steps
- Ejecución secuencial con manejo de errores
- Estados: PENDING, RUNNING, COMPLETED, FAILED

#### Evaluación
El planner es básico pero funcional para tareas simples. No usa LLM para planificación - solo enrutamiento de herramientas.

---

### 4. Guardrails (Semana 8)

#### Estructura Propuesta

| Archivo | Descripción |
|---------|-------------|
| `app/guardrails/guardrail.py` | Sistema de filtrado con patrones |
| `app/guardrails/middleware.py` | Integración con guardrails por defecto |

#### Patrones Bloqueados por Defecto

- SSN (`\d{3}-\d{2}-\d{4}`)
- Tarjetas de crédito (`\d{16}`)
- Emails (`[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}`)

#### Funcionalidades

- Bloqueo de patrones regex
- Filtrado con mask de caracteres
- Check de allow patterns

#### Evaluación
Los guardrails implementan PII detection básica. Es un buen punto de partida pero podría beneficiarse de más patrones (números de teléfono, direcciones IP, etc.).

---

## Flujo de Integración Propuesto

```
User Message
    ↓
Guardrails (PII filter)
    ↓
Policy Engine (rate limit, quota, access)
    ↓
Planner (create plan)
    ↓
Tool Router (find tools)
    ↓
Execute Tools
    ↓
LLM (generate response)
    ↓
Guardrails (output filter)
    ↓
Response
```

---

## Gap Analysis

| Requisito | Estado Actual | Estado Requerido | Prioridad |
|-----------|---------------|------------------|-----------|
| Rate Limiting | ❌ No existe | Implementar | Alta |
| Quota Tracking | ❌ No existe | Implementar | Alta |
| Content Filter | ❌ No existe | Implementar | Alta |
| Budget Control | ❌ No existe | Implementar | Media |
| Tool Registry | ❌ No existe | Implementar | Alta |
| Tool Router | ❌ No existe | Implementar | Alta |
| Planner Multi-step | ❌ No existe | Implementar | Alta |
| Guardrails PII | ❌ No existe | Implementar | Alta |
| Integración Chat | ❌ No existe | Implementar | Alta |

---

## Recomendaciones

### 1. Prioridad de Implementación

1. **Policy Engine** (Semana 6)
   - Implementar modelos base
   - Rate limiting y quota son críticos para producción

2. **Tool Routing** (Semana 7)
   - Tool registry y router
   - Integrar con sistema existente

3. **Guardrails** (Semana 8)
   - PII filtering antes dePolicy engine
   - Filtrar tanto input como output

### 2. Consideraciones Técnicas

- **Persistencia**: Los stores en memoria (`_rate_limit_store`, `_quota_store`) deben persistirse o usar Redis
- **Thread Safety**: El PolicyEngine actual no es thread-safe
- **Testing**: Incluir tests de integración con la infraestructura existente
- **Configuración**: Los límites deben ser configurables por tenant

### 3. Mejoras Futuras

- Integrar LLM para planificación más inteligente
- Analytics de uso de políticas
- Dashboard de administración
- Alertas de budget threshold

---

## Conclusión

El documento de implementación describe una arquitectura robusta y bien estructurada para agregar capacidades de políticas, routing y planificación al proyecto. El sistema actual (pattern-based) se complementaría con estas nuevas capacidades para crear un chatbot más inteligente y controlable.

**Estado de la implementación: Planificada (no iniciada)**

---
*Documento generado automáticamente tras análisis del código base y documento de implementación.*
