# Módulos de la Aplicación

Este documento describe la funcionalidad y finalidad de cada módulo en el directorio `app/`.

---

## admin

**Ubicación:** `app/admin/`

**Funcionalidad:** Proporciona rutas administrativas para la gestión multi-tenant del portal empresarial.

**Finalidad:**
- Listar, crear y obtener detalles de tenants
- Gestionar usuarios por tenant
- Ver uso de tenant (solicitudes, tokens, costos)
- Suspender/activar tenants
- Gestión de suscripciones y planes de facturación
- Consultar logs de auditoría por tenant
- Verificar salud del sistema

---

## api

**Ubicación:** `app/api/`

**Funcionalidad:** Punto de entrada legacy de la API REST.

**Finalidad:**
- **DEPRECATED** desde 2026-03-13
- La funcionalidad fue migrada a `app.webhook.entrypoint:app`
- Mantenido para compatibilidad durante la migración
- Incluye rutas empresariales en `enterprise_routes.py`

---

## audit

**Ubicación:** `app/audit/`

**Funcionalidad:** Servicio de auditoría para entornos multi-tenant.

**Finalidad:**
- Registro de eventos de auditoría (login, logout, mensajes, violaciones de políticas)
- Consulta de eventos con filtros (por tenant, tipo, actor, recurso)
- Métodos especializados: `log_login`, `log_logout`, `log_chat_message`, `log_policy_violation`
- Repositorio en memoria (`InMemoryAuditRepository`)

---

## auth

**Ubicación:** `app/auth/`

**Funcionalidad:** Sistema de autenticación y autorización.

**Finalidad:**
- Autenticación de usuarios con username/password
- Gestión de sesiones (crear, verificar, refrescar, revocar)
- API keys para acceso programático
- Rate limiting de intentos de login
- Middleware para protección de rutas
- Modelos: `User`, `UserRole`, `ApiKey`, `AuthSession`

---

## billing

**Ubicación:** `app/billing/`

**Funcionalidad:** Servicio de facturación y seguimiento de cuotas.

**Finalidad:**
- Gestión de planes (Free, Starter, Professional, Enterprise)
- Seguimiento de uso (solicitudes, tokens, costos)
- Control de límites (requests, tokens, sesiones, usuarios)
- Creación y cancelación de suscripciones
- Cálculo de costos por excedente

---

## config

**Ubicación:** `app/config/`

**Funcionalidad:** Configuración centralizada de la aplicación.

**Finalidad:**
- `ApiSettings`: Configuración para runtime API/monolith
- `WebhookSettings`: Configuración para runtime de webhook de Telegram
- `WorkerSettings`: Configuración para runtime de workers RQ
- `EnterpriseSettings`: Configuración específica de Enterprise
- Carga de variables de entorno con validación Pydantic

---

## database

**Ubicación:** `app/database/`

**Funcionalidad:** Modelos SQLAlchemy y repositorios para persistencia.

**Finalidad:**
- Modelos: `Tenant`, `Conversation`, `ApiKey`, `User`, `EnterpriseUser`, `EnterpriseBan`, `EnterpriseRule`, `EnterpriseWelcome`, `EnterpriseNote`, `EnterpriseFilter`, `EnterpriseAntiSpam`, `EnterpriseBlacklist`, `EnterpriseStickerBlacklist`, `EnterpriseAntiChannel`
- Repositorios para acceso a datos
- Adapters para abstracción de almacenamiento

---

## enterprise

**Ubicación:** `app/enterprise/`

**Funcionalidad:** Módulos de bot empresarial integrados en el runtime de webhook.

**Finalidad:**
- Gestión de permisos de usuarios
- Control de usuarios y bans
- Handlers para comandos empresariales (`handle_enterprise_command`, `handle_enterprise_moderation`)
- Modelos relacionados con moderación y reglas de chat

---

## guardrails

**Ubicación:** `app/guardrails/`

**Funcionalidad:** Sistema de filtros de contenido.

**Finalidad:**
- Bloqueo de patrones regex específicos
- Filtrado de palabras clave
- Patrones permitidos (allowlist)
- Máscarización de contenido bloqueado
- Estadísticas de patrones bloqueados

---

## manager_bot

**Ubicación:** `app/manager_bot/`

**Funcionalidad:** Gestor unificado de bots con registro de módulos.

**Finalidad:**
- Arquitectura de módulos con contratos (`ModuleContract`)
- Registro dinámico de módulos
- Feature flags para habilitación de módulos
- Módulos core: `OpsModule`, `EnterpriseModule`, `AgentModule`
- Router de Telegram integrado
- Health checks por módulo

---

## monitoring

**Ubicación:** `app/monitoring/`

**Funcionalidad:** Verificación de salud del sistema.

**Finalidad:**
- Health checks de componentes (database, redis, APIs externas)
- Estados: healthy, degraded, unhealthy
- Métricas de latencia
- Readiness y Liveness checks para Kubernetes

---

## ops

**Ubicación:** `app/ops/`

**Funcionalidad:** Servicios operacionales y comandos del sistema.

**Finalidad:**
- Manejo de mensajes de chat
- Comandos OPS: `/start`, `/health`, `/e2e`, `/webhookinfo`, `/logs`
- Verificación de salud de API y webhook
- Chequeos E2E
- Sistema de eventos para logging
- Políticas de rate limiting y acceso

---

## planner

**Ubicación:** `app/planner/`

**Funcionalidad:** Planificador de tareas multi-paso.

**Finalidad:**
- Creación de planes a partir de objetivos de usuario
- Descomposición de objetivos en pasos (`PlanStep`)
- Ejecución síncrona y asíncrona de planes
- Gestión de dependencias entre pasos
- Estados: pending, running, completed, failed
- Integración con `ToolRouter` para ejecución de herramientas

---

## policies

**Ubicación:** `app/policies/`

**Funcionalidad:** Motor de políticas para control de acceso y cuotas.

**Finalidad:**
- Tipos de políticas: RateLimit, Quota, ContentFilter, Budget, AccessControl
- Evaluación de políticas por tenant
- Registro y listado de políticas
- Stats de rate limits y cuotas
- Tipos de acciones: ALLOW, DENY, WARN

---

## telegram

**Ubicación:** `app/telegram/`

**Funcionalidad:** Transporte Telegram para comunicación con el bot.

**Finalidad:**
- Modelos para actualización de Telegram
- Servicios de extracción de payloads
- Dispatcher para clasificación de actualizaciones
- Comandos OPS predefinidos

---

## telegram_ops

**Ubicación:** `app/telegram_ops/`

**Funcionalidad:** Bot OPS de Telegram independiente (polling).

**Finalidad:**
- **DEPRECATED** desde 2026-03-13
- Migrado a `app.webhook.entrypoint:app`
- Comandos: `/start`, `/health`, `/e2e`, `/webhookinfo`, `/logs`
- Previene instancias múltiples con lock de PID

---

## tools

**Ubicación:** `app/tools/`

**Funcionalidad:** Sistema de herramientas ejecutables y router.

**Finalidad:**
- Registro de herramientas (`ToolRegistry`)
- Herramientas integradas:
  - `calculator`: Expresiones matemáticas
  - `search`: Búsqueda web
  - `weather`: Información meteorológica
  - `convert`: Conversión de unidades
  - `date`: Fechas (now, today, tomorrow, yesterday)
  - `llm`: Procesamiento con LLM
- Router que selecciona herramientas basadas en mensaje
- Integración con PolicyEngine para control de acceso

---

## webhook

**Ubicación:** `app/webhook/`

**Funcionalidad:** Punto de entrada canónico de webhook de Telegram.

**Finalidad:**
- Endpoint `/webhook/{token}` para recibir updates de Telegram
- Deduplicación de updates
- Procesamiento síncrono y asíncrono
- Integración con ManagerBot (FASE 0)
- Métricas Prometheus
- Health check en `/health`
- Montaje de rutas de ManagerBot en `/manager`

---

## Resumen de Arquitectura

```
                    ┌─────────────────────┐
                    │   Telegram API       │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Webhook Entrypoint │ (app.webhook.entrypoint)
                    │  /webhook/{token}   │
                    └──────────┬──────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
┌─────────▼─────────┐ ┌───────▼───────┐ ┌────────▼────────┐
│   ManagerBot     │ │  Chat Ops     │ │  Enterprise    │
│   (Módulos)      │ │  Commands     │ │  Handlers      │
└──────────────────┘ └───────────────┘ └─────────────────┘
          │                    │                    │
          └────────────────────┼────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Domain Services   │
                    │  - Auth Provider    │
                    │  - Billing Service  │
                    │  - Audit Service    │
                    │  - Policy Engine    │
                    └─────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │    Database/       │
                    │    Storage          │
                    └─────────────────────┘
```
