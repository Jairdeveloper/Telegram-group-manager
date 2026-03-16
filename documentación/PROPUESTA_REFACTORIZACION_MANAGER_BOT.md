# PROPUESTA_REFACTORIZACION_MANAGER_BOT.md
Fecha: 2026-03-11

**Contexto**
Actualmente conviven dos apps/funcionalidades en el mismo bot y el diseno es confuso en codigo y uso:
- OPS / E2E Log App (runbook en `BASE_DE_CONOCIMIENTO_ROBOT/REVIEWS/TELEGRAM_E2E_LOG_APP.md`).
- Bot funcional tipo EnterpriseRobot (ver `BASE_DE_CONOCIMIENTO_ROBOT/01_IMPLEMENTACION_ROBOT.md`).
- Proyeccion futura de agente autonomo (ver `BASE_DE_CONOCIMIENTO_ROBOT/PROJECT/PROPUESTA_EVOLUCION_AGENTE.md`).

El problema principal es la falta de una entidad unica que gobierne rutas, permisos, dependencias y dispatching. Esto genera entrypoints duplicados, handlers mezclados y confusiones operativas (tokens, comandos, runtime).

**Objetivos**
- Unificar el bot bajo una sola entidad en codigo: `ManagerBot`.
- Mantener un solo runtime por token y un solo ingress canonico: `app.webhook.entrypoint:app`.
- Separar claramente capas: transport, application, domain, infrastructure.
- Encapsular OPS y Enterprise como modulos internos con contratos claros.
- Aislar la proyeccion del agente autonomo para evitar acoplamientos.

**No objetivos**
- No implementar LLM ni capabilities nuevas del agente.
- No reescribir toda la base Enterprise en esta fase.
- No cambiar comandos visibles para usuarios sin necesidad.

**Principios de diseno**
- Single entrypoint, single dispatcher.
- Modules con contratos explicitos y registro centralizado.
- Policies y guardrails antes de ejecutar casos de uso.
- Observabilidad comun (eventos y logs).
- Feature flags para activar/desactivar capacidades.

**Arquitectura propuesta (high level)**
```
Telegram -> app.webhook.entrypoint
              -> ManagerBot
                  -> Router (ops / enterprise / agent)
                  -> Application use cases
                  -> Domain policies
                  -> Infrastructure adapters
                  -> Response
```

**Estructura propuesta (target)**
```
app/
  manager_bot/
    core.py
    settings.py
    registry.py
    transport/
      telegram/
        router.py
        handlers.py
    application/
      ops/
        commands.py
        services.py
      enterprise/
        commands.py
        services.py
    domain/
      ops/
      enterprise/
    infrastructure/
      storage/
      external/
  webhook/
    entrypoint.py
  shared/
    policies/
    guardrails/
    telemetry/
```

**Entidad unica: `ManagerBot`**
- Responsable de bootstrapping (config, deps, registry).
- Expone un router unico para Telegram.
- Registra modulos `ops` y `enterprise` con permisos y rutas.
- Unifica observabilidad y manejo de errores.

**Contrato de modulo (sugerido)**
- `name`, `version`, `routes`, `permissions`, `handlers`.
- `health_checks()` opcional.
- `feature_flag` obligatorio para activacion controlada.

**Separacion de la proyeccion de agente autonomo**
Opcion recomendada:
- Servicio separado con token propio y despliegue independiente.
- Se integra con el resto solo via APIs internas si es necesario.

Opcion transitoria (si debe convivir):
- Mantener `AgentGateway` desacoplado en `app/manager_bot/application/agent_gateway.py`.
- Activar solo con `MANAGER_ENABLE_AGENT=true`.
- Sin mezclar dominio de agente con dominio OPS/Enterprise.

**Plan de migracion por fases**
Fase 0 - Baseline:
- Crear `app/manager_bot/` con `core.py`, `registry.py`, `transport/telegram/router.py`.
- Hacer que `app.webhook.entrypoint:app` delegue a `ManagerBot`.
- Prohibir runtimes paralelos para el mismo token.

Fase 1 - OPS unificado:
- Mover comandos `/health`, `/e2e`, `/webhookinfo`, `/logs` a `application/ops`.
- Implementar `ops` como modulo registrado.
- Consolidar logging y eventos en `shared/telemetry`.

Fase 2 - Enterprise unificado:
- Envolver handlers actuales como casos de uso en `application/enterprise`.
- Mantener compatibilidad de comandos y permisos.
- Centralizar policy checks antes de ejecutar comandos.

Fase 3 - Aislamiento del agente:
- Extraer `chat_service` a servicio aparte o mantener solo gateway.
- Eliminar dependencias directas del bot hacia el core del agente.

Fase 4 - Limpieza:
- Deprecar `telegram_adapter.py` y cualquier entrypoint legacy.
- Documentar runbook unico para operacion.

**Definition of Done**
- Un solo ingress operativo: `app.webhook.entrypoint:app`.
- `ManagerBot` es el unico dispatcher.
- OPS y Enterprise funcionan con el mismo token sin conflictos.
- El agente autonomo queda aislado o desactivado por default.
- Runbook unico y consistente para despliegue.

**Riesgos y mitigaciones**
- Riesgo: regresiones en comandos existentes.
Mitigacion: tests de contrato por comando y feature flags.
- Riesgo: dependencia legacy mezclada con nuevas capas.
Mitigacion: wrappers temporales y refactor incremental.
- Riesgo: confusion operativa durante la migracion.
Mitigacion: documentar un runbook unico y bloquear runtimes paralelos.

**Siguientes pasos concretos**
1. Crear esqueleto `app/manager_bot/` y router unico.
2. Migrar los comandos OPS al modulo `application/ops`.
3. Definir registro de modulos y feature flags.
4. Hacer inventory de comandos Enterprise a migrar por lotes.
