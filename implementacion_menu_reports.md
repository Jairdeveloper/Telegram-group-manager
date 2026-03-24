# Plan de Implementación: Menú de Reportes

Fecha: 2026-03-23
version: 1.0
referencia: `app/manager_bot/_features/reports/__init__.py`, `app/manager_bot/_menus/reports_menu.py`

## Resumen de la implementación

El sistema de reportes permite a los administradores de grupos gestionar informes de usuarios sobre comportamientos inapropiados. Actualmente existe una base funcional con estructuras de datos y menús UI básicos, pero faltan components críticos como persistencia, comandos de usuario, y callbacks funcionales.

---

## Arquitectura final

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
│                     Persistence Layer                            │
│  ConfigStorage + ReportRepository (SQLite/JSON)                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        UI Layer                                  │
│  reports_menu.py: create_reports_menu()                        │
│  - Reportes abiertos / resueltos / estadísticas                │
└─────────────────────────────────────────────────────────────────┘
```

---

## Tabla de tareas

| # | Tarea | Prioridad | Estado |
|---|-------|-----------|--------|
| 1 | Implementar persistencia de reportes (SQLite) | Alta | Completado |
| 2 | Crear comando /report para reportar usuarios | Alta | Completado |
| 3 | Crear comando /reports para listar reportes | Alta | Completado |
| 4 | Completar handlers de callbacks (list, resolve, stats) | Media | Completado |
| 5 | Agregar paginación para lista de reportes | Media | Completado |
| 6 | Implementar acciones automáticas (ban, kick, warn) | Media | Completado |
| 7 | Agregar notificación al usuario reportado | Baja | Completado (en acciones) |
| 8 | Mejorar UI del menú con estadísticas en tiempo real | Baja | Completado |
| 9 | Exportación a CSV/JSON | Baja | Completado |
| 10 | Auto-limpieza de reportes antiguos | Baja | Completado |

---

## Fase 1: Núcleo y Persistencia
**Objetivo fase:** обеспечить хранение данных и базовую функциональidad

### Implementacion fase 1

1. **Crear `ReportRepository`** - Capa de persistencia ✅
   - Ubicación: `app/manager_bot/_features/reports/repository.py`
   - Métodos: `save()`, `get_by_chat()`, `get_by_id()`, `update_status()`, `delete()`

2. **Modificar `ReportsFeature`** para usar repositorio ✅
   - Inyectar `ReportRepository` en constructor
   - Reemplazar `self._reports` (dict en memoria) por llamadas al repositorio
   - Actualizar métodos: `create_report()`, `get_reports()`, `resolve_report()`, `get_stats()`

3. **Añadir métodos adicionales** ✅
   - `dismiss_report(report_id, dismissed_by)` - Descartar reporte
   - `get_report_by_id(report_id)` - Obtener reporte específico
   - `delete_report(report_id)` - Eliminar reporte

---

## Fase 2: Comandos de Usuario
**Objetivo fase:** Permitir a usuarios y administradores interacturar con el sistema

### Implementacion fase 2

1. **Crear comando `/report`**
   - Sintaxis: `/report <usuario> <razón>` o respuesta a mensaje + `/report <razón>`
   - Validaciones: usuario válido, razón proporcionada, no auto-reportarse
   - Acción: Crear reporte y notificar a administradores

2. **Crear comando `/reports`**
   - Sintaxis: `/reports` - Muestra menú de reportes
   - Opciones: `/reports abiertos`, `/reports resueltos`, `/reports stats`
   - Formato: Lista paginada con botones de acción

3. **Registrar comandos en bot**
   - Agregar a `command_registry` o similar
   - Descripciones en español

---

## Fase 3: Callbacks y UI
**Objetivo fase:** Completar la interfaz interactiva

### Implementacion fase 3

1. **Completar handlers de callbacks** (`reports/__init__.py`)
   - `handle_show_list`: Mostrar lista de reportes filtrada
   - `handle_stats`: Mostrar estadísticas detalladas
   - `handle_resolve`: Procesar resolución con acción (ban/warn/kick/ignore)
   - `handle_dismiss`: Descartar reporte sin acción

2. **Mejorar menú `reports_menu.py`**
   - Agregar contador de reportes en cada opción
   - Incluir información de configuración activa

3. **Agregar paginación**
   - Limitar a 10-20 reportes por página
   - Botones Anterior/Siguiente

---

## Fase 4: Acciones Automáticas
**Objetivo fase:** Ejecutar acciones sobre usuarios reportados

### Implementacion fase 4

1. **Integrar con módulos de moderación**
   - `ban_user()` - Banear usuario
   - `kick_user()` - Expulsar usuario
   - `warn_user()` - Advertir usuario

2. **Lógica de acciones**
   - Por acción manual de administrador
   - Por configuración auto-ban/warn

3. **Notificaciones**
   - Notificar a reportado sobre la acción
   - Notificar a reportero sobre resolución

---

## Fase 5: Mejoras y Optimización
**Objetivo fase:** Pulir y optimizar

### Implementacion fase 5

1. **Estadísticas avanzadas**
   - Top usuarios reportados
   - Reportes por razón
   - Historial temporal

2. **Exportación**
   - Exportar reportes a CSV/JSON

3. **Limpieza**
   - Auto-eliminar reportes resueltos después de X días
   - Mantener solo últimos N reportes por chat

---

## Dependencias identificadas

- `FeatureModule` (base class)
- `ConfigStorage` - Configuración de grupos
- `GroupConfig` - Modelo de configuración
- `CallbackRouter` - Sistema de callbacks
- Módulos de moderación: `AntifloodFeature`, `ModerationFeature` (para acciones)
