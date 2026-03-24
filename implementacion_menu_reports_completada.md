# Implementación Menú de Reportes - Completada

Fecha: 2026-03-23
Versión: 1.0
Referencia: 
- `app/manager_bot/_features/reports/__init__.py`
- `app/manager_bot/_features/reports/repository.py`
- `app/manager_bot/_menus/reports_menu.py`
- `app/enterprise/transport/handlers.py`

---

## Resumen de la implementación

Se ha implementado el sistema completo de reportes para el bot de Telegram, permitiendo a usuarios reportar comportamientos inapropiados y a administradores gestionar dichos reportes.

**Fases completadas:**
- Fase 1: Núcleo y Persistencia ✅
- Fase 2: Comandos de Usuario ✅

---

## Arquitectura Final

```
┌─────────────────────────────────────────────────────────────────┐
│                        Commands Layer                           │
│  /report <usuario> <razón>    /reports [abiertos|resueltos]    │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Callback Handlers                          │
│  reports:list:* / reports:stats / reports:resolve:*            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ReportsFeature Module                        │
│  create_report() / get_reports() / resolve_report()            │
│  get_stats() / dismiss_report()                                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Persistence Layer                           │
│  ConfigStorage + ReportRepository (PostgreSQL/SQLite)          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        UI Layer                                  │
│  reports_menu.py: create_reports_menu()                         │
│  - Reportes abiertos / resueltos / estadísticas                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Cambios Implementados

### Fase 1: Núcleo y Persistencia

#### 1.1 ReportRepository (`app/manager_bot/_features/reports/repository.py`)

Capa de persistencia para reportes usando SQLAlchemy.

**Características:**
- Soporte para PostgreSQL y SQLite
- Tabla `reports` con índices optimizados
- Métodos completos CRUD

**Tabla: reports**
```sql
CREATE TABLE reports (
    report_id VARCHAR(36) PRIMARY KEY,
    chat_id BIGINT NOT NULL,
    reporter_id BIGINT NOT NULL,
    reported_id BIGINT NOT NULL,
    reason TEXT NOT NULL,
    message_id BIGINT,
    status VARCHAR(20) NOT NULL DEFAULT 'open',
    action VARCHAR(20),
    resolved_by BIGINT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMP
)
```

**Métodos implementados:**
- `save(report)` - Guardar reporte
- `get_by_chat(chat_id, status)` - Obtener reportes por chat
- `get_by_id(report_id)` - Obtener reporte por ID
- `update_status(report_id, status, action, resolved_by)` - Actualizar estado
- `delete(report_id)` - Eliminar reporte
- `get_stats(chat_id)` - Obtener estadísticas

#### 1.2 ReportsFeature Actualizado

Modificaciones en `app/manager_bot/_features/reports/__init__.py`:

- Constructor acepta `ReportRepository` opcional
- Fallback a memoria si no hay repositorio
- Métodos actualizados para usar repositorio cuando esté disponible

**Nuevos métodos:**
- `get_report_by_id(report_id)` - Obtener reporte específico
- `dismiss_report(report_id, dismissed_by)` - Descartar reporte
- `delete_report(report_id)` - Eliminar reporte

---

### Fase 2: Comandos de Usuario

#### 2.1 Comando `/report`

Implementado en `app/enterprise/transport/handlers.py`:

**Sintaxis:**
- `/report <user_id> <razón>` - Reportar por ID
- `/report <razón>` (respondiendo a mensaje) - Reportar mensaje

**Funcionalidades:**
- Validación: usuario válido, razón proporcionada
- No auto-reportarse
- Soporte para respuesta a mensajes
- Crear reporte y almacenar en BD

**Respuestas:**
- Éxito: "Reporte creado ID: [short_id]..."
- Error: "Uso: /report <user_id> <razón>..."

#### 2.2 Comando `/reports`

**Sintaxis:**
- `/reports` - Mostrar menú de configuración
- `/reports abiertos` - Listar reportes abiertos
- `/reports resueltos` - Listar reportes resueltos
- `/reports stats` - Mostrar estadísticas

**Salida de ejemplo (stats):**
```
📊 Estadísticas de Reportes:
• Total: 5
• Abiertos: 2
• Resueltos: 3
• Descartados: 0
```

---

## Integración con el Sistema

### Flujo de comandos

1. Update llega al webhook
2. `dispatch_telegram_update()` determina tipo de update
3. Si es `enterprise_command`, se llama a `handle_enterprise_command()`
4. En `handle_enterprise_command()`:
   - Si comando es `/report`, llama a `_handle_report_command()`
   - Si comando es `/reports`, llama a `_handle_reports_command()`

### Inicialización

El `ReportsFeature` se inicializa en `_menu_service.py`:
```python
ReportsFeature(config_storage)
```

El repositorio se crea dinámicamente si hay `database_url` configurado:
```python
if settings.database_url:
    repository = ReportRepository(settings.database_url)
reports_feature = ReportsFeature(config_storage, repository)
```

---

### Fase 3: Callbacks y UI

#### 3.1 Callbacks Implementados

Modificaciones en `app/manager_bot/_features/reports/__init__.py`:

**Handlers registrados:**
- `reports:list` - Muestra lista de reportes con paginación
- `reports:stats` - Muestra estadísticas detalladas
- `reports:resolve` - Resuelve reporte con acción (ban/warn/kick/ignore)
- `reports:dismiss` - Descarta reporte sin acción

**Características:**
- Paginación (10 reportes por página)
- Navegación Anterior/Siguiente
- Botones de acción en cada reporte
- Validación de datos

#### 3.2 Menú Mejorado

Modificaciones en `app/manager_bot/_menus/reports_menu.py`:

**Nueva función `create_reports_menu(config, stats)`:**
- Muestra contadores de reportes abiertos/resueltos
- Información de configuración activa

**Nueva función `build_reports_list_keyboard(...)`:**
- Keyboard interactivo con paginación
- Botones de Resolver/Descartar por reporte
- Navegación entre páginas

#### 3.3 Paginación

- Límite de 10 reportes por página
- Botones Anterior/Siguiente
- Indicador de página actual

---

### Fase 4: Acciones Automáticas

#### 4.1 Integración con módulos de moderación

Modificaciones en `app/manager_bot/_features/reports/__init__.py`:

**Handler `handle_resolve` mejorado:**
- `ban` - Llama a `user_service.ban_user()` del módulo Enterprise
- `kick` - Expulsa usuario via `bot.unban_chat_member()` + `ban_chat_member()`
- `warn` - Marca como advertid@
- `ignore` - Resuelve sin acción

#### 4.2 Menú de acciones

Modificaciones en `app/manager_bot/_menus/reports_menu.py`:

**Keyboard ahora incluye 4 acciones:**
- 🚫 Ban - Banear usuario
- ⚠️ Warn - Advertir usuario
- 👢 Kick - Expulsar usuario
- ✅ Ignorar - Resolver sin acción
- ❌ Descartar - Descartar reporte

#### 4.3 Lógica de acciones

- Validación de permisos via EnterpriseUserService
- Manejo de errores gracefully
- Feedback al administrador
- Registro de acción tomada en el reporte

---

### Fase 5: Mejoras y Optimización

#### 5.1 Estadísticas Avanzadas

Nuevos métodos en `app/manager_bot/_features/reports/repository.py`:

- `get_top_reported_users(chat_id, limit)` - Top usuarios más reportados
- `get_reports_by_reason(chat_id, limit)` - Razones más comunes

**Nuevo subcomando `/reports top`:**
```
👤 Usuarios más reportados:
• User ID: 123456 - 5 reportes
• User ID: 789012 - 3 reportes
```

#### 5.2 Exportación

**Nuevos métodos en Repository:**
- `export_to_json(chat_id)` - Exporta a JSON
- `export_to_csv(chat_id)` - Exporta a CSV

**Nuevo subcomando `/reports export [json|csv]`:**
- Retorna archivo para descargar
- Estados: `"status": "file"` con contenido

#### 5.3 Limpieza Automática

**Nuevo método en Repository:**
- `cleanup_old_reports(days, keep_count)` - Autoelimina reportes antiguos
  - Borra reportes resueltos/descartados mayores a X días
  - Mantiene al menos N reportes por chat

#### 5.4 Comandos Completos

**`/reports` ahora soporta:**
- `/reports` - Menú interactivo
- `/reports abiertos` - Lista abiertos
- `/reports resueltos` - Lista resueltos
- `/reports stats` - Estadísticas
- `/reports top` - Top usuarios
- `/reports export json` - Exportar JSON
- `/reports export csv` - Exportar CSV

---

## Implementación Completa ✅

**Todas las fases completadas:**

| Fase | Descripción | Estado |
|------|-------------|--------|
| 1 | Núcleo y Persistencia | ✅ Completado |
| 2 | Comandos de Usuario | ✅ Completado |
| 3 | Callbacks y UI | ✅ Completado |
| 4 | Acciones Automáticas | ✅ Completado |
| 5 | Mejoras y Optimización | ✅ Completado |

---

## Resumen de Archivos Modificados

1. `app/manager_bot/_features/reports/__init__.py` - Feature module
2. `app/manager_bot/_features/reports/repository.py` - Persistencia
3. `app/manager_bot/_menus/reports_menu.py` - UI menus
4. `app/enterprise/transport/handlers.py` - Command handlers

---

## Dependencias

- `sqlalchemy>=2.0.0` - Ya en dependencies
- `python-telegram-bot>=22.6` - Ya en dependencies
- `FeatureModule` (base class)
- `ConfigStorage` - Almacenamiento de configuración
- `GroupConfig` - Modelo de configuración
- `CallbackRouter` - Sistema de callbacks
