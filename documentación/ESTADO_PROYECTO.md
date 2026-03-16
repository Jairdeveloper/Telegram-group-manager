# ESTADO_PROYECTO
Fecha: 2026-03-10

## Estado canonico
Este es el unico documento canonico de estado del proyecto.
Todos los demas documentos de evaluacion/planificacion deben tratarse como referencia historica o legacy si no coinciden con este estado.

## Fuentes revisadas (BASE_DE_CONOCIMIENTO_ROBOT)
- GLOBAL/EVALUACION_ALCANCE_PROYECTO.md
- GLOBAL/00_cambio_ejecutados.md
- GLOBAL/00_CONCLUSION.md
- GLOBAL/design/advantages.md
- GLOBAL/design/roadmap.md
- GLOBAL/design/architecture.md
- GLOBAL/design/01_arquitecture.md
- GLOBAL/design/stack.md
- GLOBAL/design/risks.md
- GLOBAL/design/cost_and_scalability.md
- GLOBAL/design/contratos.md
- GLOBAL/FASE_0/CHAT_MANAGER_README.md
- ARCHITECTURE/FASE_2/00_ARQUITECTURA_OBJETIVO.md
- FEATURE/IMPLEMENTACION_POLICY_COMPLETADO.md
- FEATURE/IMPLEMENTACION_MULTITENANT_COMPLETADA.md
- FEATURE/IMPLEMENTACION_POSTGRES_COMPLETADO.md
- FEATURE/01_IMPLEMENTACION_SEMANA_9_12_MULTITENANT.md
- PROJECT/01_ARQUITECTURA_OBJETIVO.md
- PROJECT/PROPUESTA_EVOLUCION_AGENTE.md
- PROJECT/CHATBOT_MONOLITH_README.md
- PROJECT/01ENTERPRIME_ROBOT.md
- PROJECT/analisis_propuesta_arquitectura.md
- PROJECT/migracion-chatbot-arquitectura.md
- PROJECT/PLAN_EJECUCION_MIGRACION_PRESUPUESTO_CERO.md
- REVIEWS/ANALISIS_POLICY_PLANNER.md
- REVIEWS/MIGRACION.md
- REVIEWS/TELEGRAM_E2E_LOG_APP.md

## Resumen ejecutivo
El codigo actual esta mas avanzado en gobierno y operacion que la proyeccion original. Ya existen componentes enterprise (policy engine, guardrails, planner, tool routing, multi-tenant, billing, audit, monitoring, admin y API publica) y una arquitectura modular con entrypoints canonicos. La proyeccion futura se concentra en LLM real, memory, RAG y herramientas reales, que aun aparecen como placeholders o no integradas de forma consistente en el flujo principal.

## Ventajas competitivas del codigo actual vs proyeccion
- Gobernanza enterprise ya implementada (policy, quotas, budgets, guardrails, auth, billing, audit, monitoring, admin, API multi-tenant), lo que adelanta fases 6-12 y reduce riesgo de costos y cumplimiento.
- Arquitectura modular con entrypoints canonicos y dispatcher Telegram unificado, lo que elimina intermitencia y habilita escalado sin migracion inmediata a microservicios.
- Persistencia en Postgres con Alembic y fallback JSON, lo que permite transicion segura sin romper contratos ni operacion.
- Suite de tests de contrato y unitarios ya instalada (78-85 tests segun documentos), lo que acelera iteracion y reduce regresiones.
- Observabilidad y health checks en el runtime actual, lo que soporta operacion diaria y SLOs basicos sin esperar fases avanzadas.
- Base de costos controlables preparada (policies y billing), lo que hace viable integrar LLMs reales sin perder control financiero.

## Brechas frente a la proyeccion (lo que falta para cumplir el target)
- LLM real integrado en el flujo principal (el handler LLM y tools reales siguen descritos como placeholders).
- Memory de conversacion y RAG con pgvector para conocimiento interno.
- Tools reales (search, weather, http, db) y ejecucion agentica multi-step con razonamiento.
- Analytics funcional con pipeline de eventos y dashboards mas alla de metricas basicas.
- Consolidacion definitiva de un solo runtime canonico y retiro total de wrappers legacy.

## Inconsistencias tecnicas detectadas
- Policy/Planner/Guardrails: REVIEWS/ANALISIS_POLICY_PLANNER.md indica no implementado, mientras FEATURE/IMPLEMENTACION_POLICY_COMPLETADO.md y GLOBAL/EVALUACION_ALCANCE_PROYECTO.md lo dan por completado con tests.
- Multi-tenant: FEATURE/01_IMPLEMENTACION_SEMANA_9_12_MULTITENANT.md describe ausencia de auth y multi-tenant, pero FEATURE/IMPLEMENTACION_MULTITENANT_COMPLETADA.md declara 7 fases completadas y tests pasando.
- Persistencia: GLOBAL/EVALUACION_ALCANCE_PROYECTO.md dice "persistencia no implementada", pero FEATURE/IMPLEMENTACION_POSTGRES_COMPLETADO.md reporta migracion y repositorios Postgres con fallback.
- Legacy runtimes: GLOBAL/FASE_0/CHAT_MANAGER_README.md y GLOBAL/design/roadmap.md aun promueven telegram_adapter.py, mientras ARCHITECTURE/FASE_2/00_ARQUITECTURA_OBJETIVO.md y REVIEWS/TELEGRAM_E2E_LOG_APP.md lo marcan deprecated y no operativo.
- Stack y proyeccion: PROJECT/migracion-chatbot-arquitectura.md y PLAN_EJECUCION_MIGRACION_PRESUPUESTO_CERO.md proponen microservicios Node.js, mientras PROJECT/analisis_propuesta_arquitectura.md y GLOBAL/design/stack.md confirman Python/FastAPI monolito modular.
- Monolith vs modular: PROJECT/CHATBOT_MONOLITH_README.md describe un archivo unico production-ready con LLM fallback, pero la arquitectura actual prioriza runtimes modulares y depreca el monolito.
- Conteo de tests y estado "production-ready": 78 tests (GLOBAL/EVALUACION_ALCANCE_PROYECTO.md) vs 85 tests (FEATURE/IMPLEMENTACION_MULTITENANT_COMPLETADA.md) y issues de seguridad aun listados en GLOBAL/00_CONCLUSION.md.

## Recomendaciones de alineacion (para resolver inconsistencias)
- Definir un unico documento canonico de estado (features completadas, tests totales, runtime canonico) y marcar los demas como "legacy" o "archivado".
- Unificar la proyeccion: elegir entre "monolito modular con LLM/RAG" o "microservicios Node.js" y retirar el plan alterno.
- Actualizar ROADMAP para reflejar que policy, planner y multi-tenant ya estan implementados y mover foco a LLM, memory, RAG y tools reales.
- Aclarar en docs el rol del monolito (wrapper de compatibilidad) y el runtime recomendado para produccion.

## Documentos marcados como legacy (no canonicos)
- BASE_DE_CONOCIMIENTO_ROBOT/LEGACY/GLOBAL/EVALUACION_ALCANCE_PROYECTO.md
- BASE_DE_CONOCIMIENTO_ROBOT/LEGACY/GLOBAL/01_EVALUACION_ALCANSE_PROYECTO.md
- BASE_DE_CONOCIMIENTO_ROBOT/LEGACY/GLOBAL/00_CONCLUSION.md
- BASE_DE_CONOCIMIENTO_ROBOT/LEGACY/GLOBAL/design/roadmap.md
- BASE_DE_CONOCIMIENTO_ROBOT/LEGACY/PROJECT/migracion-chatbot-arquitectura.md
- BASE_DE_CONOCIMIENTO_ROBOT/LEGACY/PROJECT/PLAN_EJECUCION_MIGRACION_PRESUPUESTO_CERO.md
- BASE_DE_CONOCIMIENTO_ROBOT/LEGACY/REVIEWS/ANALISIS_POLICY_PLANNER.md
- BASE_DE_CONOCIMIENTO_ROBOT/LEGACY/FEATURE/01_IMPLEMENTACION_SEMANA_9_12_MULTITENANT.md
- BASE_DE_CONOCIMIENTO_ROBOT/LEGACY/PROJECT/CHATBOT_MONOLITH_README.md
- BASE_DE_CONOCIMIENTO_ROBOT/LEGACY/GLOBAL/FASE_0/CHAT_MANAGER_README.md

## Documentos de referencia (no canonicos, pero vigentes)
- BASE_DE_CONOCIMIENTO_ROBOT/FEATURE/IMPLEMENTACION_POLICY_COMPLETADO.md
- BASE_DE_CONOCIMIENTO_ROBOT/FEATURE/IMPLEMENTACION_MULTITENANT_COMPLETADA.md
- BASE_DE_CONOCIMIENTO_ROBOT/FEATURE/IMPLEMENTACION_POSTGRES_COMPLETADO.md
- BASE_DE_CONOCIMIENTO_ROBOT/ARCHITECTURE/FASE_2/00_ARQUITECTURA_OBJETIVO.md
- BASE_DE_CONOCIMIENTO_ROBOT/PROJECT/01_ARQUITECTURA_OBJETIVO.md
- BASE_DE_CONOCIMIENTO_ROBOT/PROJECT/PROPUESTA_EVOLUCION_AGENTE.md
