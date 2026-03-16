# 01_IMPLEMENTACION_ROBOT
Fecha: 2026-03-10

## Objetivo
Implementar el bot EnterpriseRobot (especificado en `GLOBAL/EntrepriseBot.md`) sobre el estado actual del proyecto, manteniendo el runtime canonico y evitando acoplamiento a `python-telegram-bot` v13.

## Estado actual (resumen corto)
- Arquitectura modular con entrypoints canonicos API y webhook.
- Componentes enterprise ya existentes: policy engine, guardrails, auth, billing, audit, monitoring, admin, API multi-tenant.
- Persistencia PostgreSQL + Alembic y Redis disponibles.

## Especificacion base del bot (resumen)
EnterpriseRobot incluye modulos de administracion, anti-spam, warnings, notas, federaciones, utilidades, entretenimiento, y soporte de idiomas, con jerarquia de permisos (owner/dev/sudo/support/whitelist/special).

## Estrategia de integracion
- Reimplementar modulos como casos de uso internos (application/domain) y exponerlos via webhook canonico.
- Mantener desacoplo de Telegram: handlers solo traducen mensajes a casos de uso.
- Usar Postgres + Alembic para persistencia; Redis para cache, rate limit y colas.
- Reutilizar policy/guardrails/audit/billing existentes para control operacional y seguridad.

## Arquitectura objetivo para EnterpriseRobot

```
Telegram -> app.webhook.entrypoint
              -> dispatcher enterprise
              -> application use cases
              -> domain policies
              -> infrastructure (db/cache/external)
              -> response
```

### Estructura propuesta
```
app/
  enterprise/
    transport/
      dispatcher.py
      handlers.py
    application/
      commands/
      services/
    domain/
      entities/
      policies/
      value_objects/
    infrastructure/
      db/
        models.py
        repositories.py
      cache/
      external/
        spamwatch.py
        sibyl.py
```

## Mapa de modulos (EntrepriseBot -> EnterpriseRobot)

Administracion y moderacion:
- admin, bans, muting, purge, locks, antiflood

Bienvenida y reglas:
- welcome, rules

Notas y filtros:
- notes, cust_filters

Federaciones:
- feds

Anti-spam:
- antispam, blacklist, sticker_blacklist, blacklistusers, antichannel, antilinkedchannel

Warnings:
- warns

Utilidades:
- paste, currency, gettime, speed_test, wallpaper

Entretenimiento:
- fun, weebify, reactions, anilist

Usuarios:
- userinfo, users, afk

Backup y auditoria:
- backups, reporting, log_channel, cleaner, disable

Especiales:
- modules, language, connection, announce, debug, eval, shell

## Modelo de permisos
Jerarquia soportada:
- OWNER -> DEV -> SUDO -> SUPPORT -> WHITELIST -> USER
- SARDEGNA como override (inmunidad parcial)

Implementacion recomendada:
- Mapear a roles existentes del sistema (`admin`, `manager`, `user`, `api_user`) y extender con niveles internos.
- Configurar lista de IDs privilegiados por tenant en base de datos.
- Aplicar policy engine antes de ejecutar comandos sensibles.

## Persistencia (SQLAlchemy + Alembic)
Tablas recomendadas (minimo):
- users
- warns
- rules
- notes
- feds
- blacklist
- locks
- welcome
- afk
- antispam
- logs

## Integraciones externas
- SpamWatch API (baneo global)
- SibylSystem (bans distribuidos)
- APIs varias para utilidades (currency, time, wallpapers)

Estrategia:
- Crear adaptadores en `app/enterprise/infrastructure/external/`
- Configurar timeouts, retries y circuit breaker.

## Plan de implementacion por fases

### Fase 0 - Congelacion y baseline
Tareas:
- Confirmar contratos actuales de webhook/API.
- Crear estructura `app/enterprise`.
- Definir scope de modulos para MVP.
Entregables: estructura base y plan de modulos MVP.
Criterio de salida: tests base en verde.

### Fase 1 - Core de permisos y usuarios
Tareas:
- Modelo de roles y permisos por tenant.
- CRUD basico de usuarios y bans.
- Integracion con policy/guardrails existentes.
Entregables: permisos operativos y auditoria.
Criterio de salida: comandos admin basicos funcionando.

### Fase 2 - Moderacion esencial
Tareas:
- bans, muting, warns, locks, antiflood.
- tablas y repositorios.
- comandos y respuestas estables.
Entregables: suite de moderacion base.
Criterio de salida: tests unitarios y de contrato.

### Fase 3 - Contenido y mensajes
Tareas:
- welcome, rules, notes, cust_filters.
- soporte de media y persistencia.
Entregables: mensajes configurables por chat.
Criterio de salida: flujo completo en webhook.

### Fase 4 - Anti-spam avanzado
Tareas:
- antispam, blacklist, sticker_blacklist, antichannel.
- integracion SpamWatch/Sibyl.
Entregables: proteccion avanzada.
Criterio de salida: metricas + auditoria.

### Fase 5 - Utilidades y entretenimiento
Tareas:
- fun, reactions, anilist, wallpaper, gettime.
Entregables: comandos no criticos.
Criterio de salida: feature flags por modulo.

### Fase 6 - Hardening y rollout
Tareas:
- documentacion operativa y runbooks.
- e2e tests con Telegram.
- feature flags y rollback.
Entregables: release checklist y despliegue controlado.
Criterio de salida: sin regresiones y rollback listo.

## Testing recomendado
- Unit tests por caso de uso.
- Contract tests para comandos principales.
- E2E para flujo webhook -> response.
- Tests de regresion para permisos y bans.

## Riesgos y mitigaciones
- Riesgo: acoplamiento legacy PTB.
Mitigacion: usar webhook canonico y casos de uso internos.
- Riesgo: explosion de complejidad por modulos.
Mitigacion: rollout por fases y feature flags.
- Riesgo: seguridad multi-tenant.
Mitigacion: enforcement de tenant_id en repositorios y policies.
