# EnterpriseRobot - Analisis de arquitectura e implementacion

## 1) Estructura del proyecto (arquitectura y diseno actual)

### Vision general
`EnterpriseRobot` es un bot de Telegram en Python con arquitectura **modular por funcionalidades** y arranque centrado en `python-telegram-bot` (v13.x). El proyecto sigue un enfoque de monolito modular: todo vive en un mismo servicio, pero separado por modulos funcionales.

### Estructura principal
- `tg_bot/__init__.py`
: Punto de inicializacion global. Carga configuracion (`config.ini`), crea `Updater/Dispatcher`, inicializa Redis, logging y variables compartidas.
- `tg_bot/__main__.py`
: Entry point real de ejecucion. Importa dinamicamente todos los modulos y arranca en modo polling o webhook.
- `tg_bot/modules/*.py`
: Modulos de negocio (admins, warns, antiflood, notes, rules, etc.). Cada modulo registra sus handlers de Telegram.
- `tg_bot/modules/sql/*.py`
: Persistencia por feature con SQLAlchemy (tablas/modelos + funciones CRUD por dominio).
- `tg_bot/modules/helper_funcs/*.py`
: Utilidades transversales (decoradores, filtros, extraccion de texto/usuarios, permisos, etc.).
- `tg_bot/langs/*.yaml` + `tg_bot/langs/language.py`
: Internacionalizacion basada en archivos YAML.
- `requirements.txt`
: Dependencias Python del runtime.
- `Dockerfile`
: Contenerizacion basica para despliegue.
- `sample_config.ini`
: Plantilla de configuracion para bootstrap.

### Diseno y patrones observados
- **Carga dinamica de modulos**
: `tg_bot/modules/__init__.py` genera `ALL_MODULES` escaneando archivos `.py`; permite `LOAD` y `NO_LOAD` desde config.
- **Plugin-like por convencion**
: Los modulos exponen convenciones opcionales como `__mod_name__`, `get_help`, `__stats__`, `__migrate__`, `__chat_settings__`, etc. `__main__.py` detecta estas capacidades y arma registries globales.
- **Capa de transporte acoplada al dominio**
: La logica de negocio esta mezclada con handlers de Telegram en varios modulos (patron comun en bots legacy PTB v13).
- **Persistencia por modulo**
: Cada feature mantiene su propio archivo SQL (`*_sql.py`) con modelos y operaciones.
- **Estado global compartido**
: Config, dispatcher, usuarios privilegiados y conexiones viven como globals importables.
- **Concurrencia**
: PTB usa workers + handlers async-style de v13; algunas operaciones SQL usan locks (`threading.RLock`) para evitar condiciones de carrera.

### Fortalezas actuales
- Modularidad funcional alta (facil activar/desactivar modulos).
- Curva de extension rapida para nuevas features.
- Separacion razonable entre helper functions y features.
- Soporte tanto polling como webhook.

### Limitaciones tecnicas
- Acoplamiento alto entre handlers, estado global y logica de dominio.
- Arquitectura orientada a PTB v13 (stack legacy frente a versiones actuales asincronas).
- Ausencia de capa de servicio clara (use-cases) entre handler y repositorio.
- Inicializacion de infraestructura en import-time (menos testeable).
- Esquema SQL disperso por modulo y migraciones no centralizadas con Alembic.

---

## 2) Como implementarlo actualmente (stack tecnico recomendado)

Si hoy se implementa una version equivalente de este bot en produccion, el stack sugerido seria:

### Runtime y framework bot
- **Python 3.12+**
- **python-telegram-bot v21+ (async nativo)**
- Event loop `asyncio` con handlers async y jobs async.

### Persistencia y cache
- **PostgreSQL 16+** como base principal.
- **SQLAlchemy 2.x** (estilo moderno) + **Alembic** para migraciones.
- **Redis 7+** para rate-limiting, cache, locks distribuidos y colas ligeras.

### Configuracion y validacion
- **Pydantic Settings (v2)** para tipado fuerte de settings.
- Variables de entorno (`.env`) en vez de `config.ini` como fuente principal.

### API externas y tareas
- `httpx` async para integraciones externas.
- `apscheduler` o `JobQueue` de PTB para tareas programadas.

### Observabilidad
- Logging estructurado (`structlog` o `logging` JSON).
- Metrics (`prometheus-client`) + healthchecks.
- Sentry para captura de excepciones.

### Calidad y CI/CD
- `pytest` + `pytest-asyncio` + `coverage`.
- `ruff` + `black` + `mypy`.
- GitHub Actions (lint, test, build docker, release).

### Despliegue
- Docker multi-stage, imagen slim/no-root.
- Orquestacion en Fly.io/Render/Railway/Kubernetes segun escala.
- Secret manager (GitHub/Cloud provider) para tokens y credenciales.

---

## 3) Como implementarlo from scratch (blueprint propuesto)

### Objetivo
Construir un bot modular, escalable y testeable, manteniendo el enfoque por features de EnterpriseRobot pero con arquitectura moderna async.

### Arquitectura objetivo
- **Capa 1 - Interface/Transport (Telegram)**
: Handlers, callbacks, middlewares, rate limits de entrada.
- **Capa 2 - Application (Use Cases/Services)**
: Casos de uso puros (warn user, set rules, antiflood action, etc.).
- **Capa 3 - Domain**
: Entidades, reglas de negocio y politicas (sin dependencia de Telegram/DB).
- **Capa 4 - Infrastructure**
: Repositorios SQLAlchemy, Redis adapters, clientes HTTP externos.

### Estructura de carpetas sugerida
```text
bot/
  app/
    main.py
    settings.py
    bootstrap.py
  transport/
    telegram/
      handlers/
      routers/
      middlewares/
  application/
    services/
    use_cases/
  domain/
    entities/
    policies/
    value_objects/
  infrastructure/
    db/
      models/
      repositories/
      migrations/
    cache/
    external/
  modules/
    moderation/
    federation/
    filters/
    notes/
    users/
  tests/
    unit/
    integration/
    e2e/
```

### Plan de implementacion incremental
1. **Bootstrap tecnico**
- Crear repo, `pyproject.toml`, linters, testing, docker base y CI minima.

2. **Core de plataforma**
- Implementar `settings`, logger estructurado, DI simple y ciclo de vida de app.

3. **Infra basica**
- Conectar PostgreSQL + Alembic.
- Conectar Redis (rate limits y cache).

4. **Primer modulo vertical (ej. Warnings)**
- Domain: reglas de warning/ban.
- Application: casos de uso (`warn_user`, `reset_warns`, `set_warn_limit`).
- Infrastructure: repositorios SQL.
- Transport: comandos/callbacks Telegram.

5. **Sistema de modulos cargables**
- Registro de modulos via manifest (`module.py` + metadata) en vez de import global ad-hoc.

6. **Observabilidad y resiliencia**
- Tracing/log correlacionado por `chat_id/user_id`.
- Manejo de errores centralizado y retries en integraciones externas.

7. **Migracion de features restantes**
- Portar modulo por modulo (notes, rules, antiflood, antispam, etc.) con tests por feature.

8. **Hardening de produccion**
- Health/readiness checks, alertas, backups DB, politicas de secretos y rotacion de tokens.

### Decisiones clave para mantener compatibilidad funcional
- Conservar nombres de comandos y comportamiento visible para usuarios/admins.
- Separar comandos legacy y nuevos tras un flag de rollout.
- Introducir versionado de respuestas/mensajes cuando cambie formato.

### Riesgos y mitigacion
- **Riesgo:** regresion funcional por volumen de modulos.
: **Mitigacion:** migracion por vertical slices + tests de regresion por comando.
- **Riesgo:** lock-in a estado global heredado.
: **Mitigacion:** DI explicita y eliminar globals progresivamente.
- **Riesgo:** cambios en APIs externas.
: **Mitigacion:** adapters con contratos estables y retries/circuit breaker.

---

## 4) Resumen ejecutivo
- EnterpriseRobot ya tiene una base modular potente para un bot de moderacion multiproposito.
- Su principal deuda tecnica es el acoplamiento a PTB v13 + globals + falta de capas de aplicacion.
- La ruta recomendada es una reimplementacion incremental async (PTB v21+, SQLAlchemy 2, Alembic, Redis) preservando comandos actuales y migrando modulo por modulo.
