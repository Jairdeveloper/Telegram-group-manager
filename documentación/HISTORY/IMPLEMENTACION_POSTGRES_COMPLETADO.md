# Implementación PostgreSQL - Fases 1 y 2 Completadas

## Fecha de Completion: 2026-03-08

## Resumen

Se han implementado las Fases 1 y 2 de la migracion de almacenamiento JSON a PostgreSQL, manteniendo compatibilidad hacia atras con fallback a JSON.

---

## Tareas Completadas

### Fase 1: Setup y Repositorios

#### 1. Dependencias (`requirements.txt`)
- ✅ `asyncpg` - Cliente async para PostgreSQL
- ✅ `alembic` - Migraciones de base de datos

#### 2. Configuracion (`app/config/settings.py`)
- ✅ `database_url` ahora es `Optional[str] = None`
- ✅ Metodo `is_postgres_enabled()` - Verifica si PostgreSQL esta configurado
- ✅ Metodo `is_storage_disabled()` - Verifica si el storage esta deshabilitado (modo JSON)

#### 3. Modelos SQLAlchemy (`app/database/models.py`)
- ✅ `Base` - Declarative base
- ✅ `Conversation` - Tabla de conversaciones con tenant_id
- ✅ `Tenant` - Tabla de tenants
- ✅ `ApiKey` - Tabla de API keys
- ✅ `User` - Tabla de usuarios

#### 4. Repositorios (`app/database/repositories/`)
- ✅ Interfaz `ConversationRepository` - Abstract base class
- ✅ `PostgresConversationRepository` - Implementacion PostgreSQL
- ✅ `JsonConversationRepository` - Fallback JSON (para desarrollo local)
- ✅ `Factory` - `create_conversation_repository()` selecciona segun configuracion

#### 5. Adapter de Compatibilidad (`app/database/adapters.py`)
- ✅ `StorageAdapter` - Wrapper que hace compatible el nuevo repositorio con la interfaz legacy de `SimpleConversationStorage`

#### 6. Integracion con API (`app/api/bootstrap.py`)
- ✅ `build_api_runtime()` ahora usa `create_conversation_repository()` y `StorageAdapter`
- ✅ La API funciona igual que antes sin cambios en los endpoints

#### 7. Tests
- ✅ 57 tests pasando
- ✅ Test de contrato de API pasando
- ✅ Test de bootstrap actualizado para el nuevo StorageAdapter

### Fase 2: Alembic Migrations

#### 8. Configuracion de Alembic
- ✅ `alembic.ini` - Archivo de configuracion principal
- ✅ `migrations/env.py` - Configuracion del entorno de migraciones
- ✅ `migrations/script.py.mako` - Template para nuevas migraciones

#### 9. Migracion Inicial
- ✅ `migrations/versions/001_initial.py` - Crea todas las tablas:
  - `tenants`
  - `conversations`
  - `api_keys`
  - `users`

---

## Arquitectura Implementada

```
┌─────────────────────────────────────────────┐
│              API (FastAPI)                  │
│         app/api/routes.py                   │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│         bootstrap.py                        │
│    build_api_runtime()                      │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│      StorageAdapter                         │
│   (Legacy interface wrapper)               │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│    ConversationRepository (Abstract)        │
└────────┬────────────────────────────────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼────────┐
│PostgreSQL│ │   JSON    │
│  Repo   │ │  Fallback │
└─────────┘ └───────────┘
```

---

## Uso

### Configuracion PostgreSQL (Produccion)

En `.env`:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/chatbot
```

### Comandos de Migracion

```bash
# Aplicar migraciones
alembic upgrade head

# Crear nueva migracion despues de cambios en modelos
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head

# Rollback de la ultima migracion
alembic downgrade -1

# Ver historia de migraciones
alembic history --verbose
```

### Configuracion JSON (Desarrollo Local)

En `.env`:
```env
# Opcion 1: No definir DATABASE_URL
# Opcion 2: Definir como "no-db"
DATABASE_URL=no-db
```

---

## Endpoints API (sin cambios)

| Metodo | Path | Descripcion |
|--------|------|-------------|
| POST | `/api/v1/chat` | Procesar mensaje |
| GET | `/api/v1/history/{session_id}` | Historial de sesion |
| GET | `/api/v1/stats` | Estadisticas |

---

## Archivos Creados/Modificados

| Archivo | Accion |
|---------|--------|
| `requirements.txt` | Modificado - añadidas dependencias |
| `app/config/settings.py` | Modificado - database_url opcional |
| `app/database/__init__.py` | Creado |
| `app/database/models.py` | Creado |
| `app/database/adapters.py` | Creado |
| `app/database/repositories/__init__.py` | Creado |
| `app/database/repositories/conversation_repository.py` | Creado |
| `app/database/repositories/postgres_conversation_repository.py` | Creado |
| `app/database/repositories/json_conversation_repository.py` | Creado |
| `app/database/repositories/factory.py` | Creado |
| `app/api/bootstrap.py` | Modificado - usa nuevo repositorio |
| `tests/test_bootstrap_unit.py` | Modificado - actualizado para StorageAdapter |
| `alembic.ini` | Creado |
| `migrations/__init__.py` | Creado |
| `migrations/env.py` | Creado |
| `migrations/script.py.mako` | Creado |
| `migrations/versions/001_initial.py` | Creado |

---

## Rollback Strategy

Si PostgreSQL falla:
1. Configurar `DATABASE_URL=no-db` o eliminar la variable
2. El sistema usara `JsonConversationRepository` automaticamente
3. No hay downtime, solo fallback a archivo JSON

Para hacer rollback de migraciones:
```bash
alembic downgrade -1  # Rollback de la ultima migracion
alembic downgrade base  # Rollback de todas las migraciones
```

---

## Notas

- El sistema automaticamente selecciona el repositorio segun la configuracion
- Si `DATABASE_URL` no esta definida o es `no-db`, usa JSON fallback
- Si `DATABASE_URL` empieza con `postgresql://`, usa PostgreSQL
- No hay downtime - el cambio es transparente para la API
- Las migraciones pueden ejecutarse con `alembic upgrade head` una vez configurada la base de datos
