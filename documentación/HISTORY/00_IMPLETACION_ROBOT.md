# IMPLETACION_ALROBOT
Fecha: 2026-03-10

## Objetivo
Implementar el BOT EnterpriseRobot alineado al estado actual del codigo, dejando el proyecto actual congelado como punto de interrupcion para futuras investigaciones y decisiones.

## Estrategia para dejar el estado actual como punto de interrupcion
- Crear un tag y rama de congelacion con fecha, por ejemplo `state-2026-03-10`.
- Generar un snapshot de dependencias y runtime (versiones de Python, FastAPI, Redis, Postgres).
- Respaldar configuracion operativa sin secretos (plantillas `.env.example`, settings, runbooks).
- Respaldar el esquema de base de datos y migraciones (alembic head).
- Registrar el resultado de tests base y cobertura en un reporte simple.
- Mantener `BASE_DE_CONOCIMIENTO_ROBOT/ESTADO_PROYECTO.md` como unica fuente canonica.
- Aislar documentacion legacy en `BASE_DE_CONOCIMIENTO_ROBOT/LEGACY/` para no contaminar decisiones futuras.

## Evaluacion de integracion con el proyecto actual
Compatibilidades claras:
- El proyecto actual ya es modular y tiene entrypoints canonicos API y webhook.
- Existen componentes enterprise listos para gobernanza: policy, guardrails, auth, billing, audit y monitoring.
- Postgres y Redis ya estan previstos como base de datos y cache/colas.

Gaps de integracion:
- EnterpriseRobot descrito usa `python-telegram-bot` v13 y arquitectura legacy por handlers.
- El proyecto actual opera con webhook canonico y separacion por servicios internos.
- Falta un layer de application/servicios para mapear modulos de EnterpriseRobot sin acoplarse a Telegram.

Conclusion de integracion:
- Es viable integrar EnterpriseRobot en el proyecto actual si se reimplementan sus modulos como casos de uso internos, evitando depender de PTB v13.
- La integracion directa "tal cual" del bot legacy no es recomendable por incompatibilidad de stack y deuda tecnica.

## Recomendacion tecnica
- Mantener el runtime actual (FastAPI + webhook canonico) y crear un paquete `app/enterprise/` con modulos equivalentes a EnterpriseRobot.
- Implementar un router de comandos que traduzca mensajes Telegram a casos de uso del dominio.
- Reutilizar policy engine, guardrails y billing para control operativo y costos.
- Usar Postgres como fuente de verdad con migraciones Alembic.
- Definir un token de bot separado si se desea aislar el bot enterprise del bot conversacional.

## Plan de implementacion (estructurado)

### Fase 0 - Preparacion y contratos
Tareas:
- Definir alcance de modulos EnterpriseRobot a implementar primero.
- Congelar contratos actuales `/api/v1/chat` y `/webhook/{token}`.
- Crear estructura `app/enterprise` y `app/enterprise/transport`.
Entregables: esqueleto de modulos y contrato de entrada de comandos.
Criterio de salida: estructura creada y tests base pasando.

### Fase 1 - Capa Application y Domain
Tareas:
- Definir casos de uso por modulo (warn, antiflood, notes, rules).
- Crear entidades y politicas de dominio sin dependencias de Telegram.
- Inyectar repositorios con interfaces claras.
Entregables: casos de uso unitarios y modelos base en dominio.
Criterio de salida: tests unitarios de casos de uso en verde.

### Fase 2 - Persistencia y migraciones
Tareas:
- Modelar tablas necesarias en SQLAlchemy.
- Crear migraciones Alembic para modulos enterprise.
- Definir repositorios por modulo con aislamiento por tenant.
Entregables: migraciones y repositorios listos.
Criterio de salida: migraciones aplican y tests de repositorios pasan.

### Fase 3 - Integracion Telegram (router de comandos)
Tareas:
- Implementar un dispatcher de comandos enterprise en el webhook canonico.
- Mapear comandos a casos de uso sin logica de negocio en handlers.
- Definir respuestas consistentes y versionables.
Entregables: comandos base funcionando en webhook.
Criterio de salida: pruebas de contrato y e2e con comandos enterprise.

### Fase 4 - Observabilidad y seguridad
Tareas:
- Integrar audit logging para acciones de administracion.
- Registrar metricas por modulo y por tenant.
- Aplicar policy engine y guardrails a comandos sensibles.
Entregables: eventos audit y metricas visibles.
Criterio de salida: panel operativo con eventos y metricas claves.

### Fase 5 - Hardening y rollout
Tareas:
- Feature flags por modulo.
- Documentacion operativa y runbook de despliegue.
- Pruebas de regresion completas.
Entregables: checklist de release y rollout controlado.
Criterio de salida: despliegue sin regresiones y rollback definido.

## Mapa de integracion propuesto
- Ingress Telegram: `app.webhook.entrypoint:app`
- Dispatcher enterprise: `app/enterprise/transport/dispatcher.py`
- Casos de uso: `app/enterprise/application/*`
- Dominio: `app/enterprise/domain/*`
- Repositorios: `app/enterprise/infrastructure/*`
- Observabilidad: `app/audit`, `app/monitoring`

## Riesgos y mitigaciones
- Riesgo: mezclar logica legacy PTB con webhook actual.
Mitigacion: reimplementar modulos en application layer y mantener contratos.
- Riesgo: crecimiento de complejidad por modulos enterprise.
Mitigacion: rollout por modulos con feature flags y tests dedicados.
- Riesgo: acoplamiento de datos y seguridad multi-tenant.
Mitigacion: enforcement de tenant_id en repositorios y policies.
