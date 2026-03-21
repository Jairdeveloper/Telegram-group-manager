Fecha: 20/03/2026
Version: 1.0
Referencia: filtro.md

Resumen de la migracion:
 Migrar la feature de filtros de seguridad desde un sistema de comandos individuales hacia una arquitectura modular basada en menus dinamicos con submenus de configuracion. La feature permitira configurar obligaciones y bloqueos de usuarios con diferentes acciones (kick, ban, silenciar, off, warn, aviso) para cada tipo de filtro.

Arquitectura final:

app/manager_bot/
├── _config/
│   └── group_config.py          # Agregar campos: filtros, filter_on_entry, delete_filtered_messages
├── _menus/
│   ├── __init__.py               # Registrar menus de filtro
│   └── filtro_menu.py            # Menus dinamicos para filtros
└── _features/
    └── filtro/
        ├── __init__.py           # FiltroFeature con callbacks
        └── _handlers.py          # Handlers de acciones (opcional)

Tabla de tareas:

| # | Tarea                                        | Tipo      | Prioridad |
|---|----------------------------------------------|-----------|-----------|
| 1 | Definir modelos de datos en GroupConfig       | Modelo    | Alta      |
| 2 | Crear estructura de directorios de filtro    | Estructura| Alta      |
| 3 | Implementar FiltroFeature con callbacks      | Feature   | Alta      |
| 4 | Crear menus dinamicos de obligaciones        | Menu      | Alta      |
| 5 | Crear menus dinamicos de bloqueos           | Menu      | Alta      |
| 6 | Crear menu de filtro al ingreso              | Menu      | Media     |
| 7 | Crear menu de borrar mensajes               | Menu      | Media     |
| 8 | Registrar menus en __init__.py              | Registro  | Alta      |
| 9 | Integrar con sistema de moderation           | Integracion| Media    |
|10 | Documentar implementacion                    | Docs      | Baja      |

Fase 1:
Objetivo fase: Definir modelos de datos y estructura base
Implementacion fase:
  - Agregar modelos FilterObligation y FilterBlock en _config/group_config.py
  - Agregar campos filter_on_entry y delete_filtered_messages
  - Crear directorio _features/filtro/
  - Crear archivo __init__.py base para FiltroFeature

Fase 2:
Objetivo fase: Implementar menus de obligaciones
Implementacion fase:
  - Crear menu principal de obligaciones con 4 items
  - Crear submenus para cada obligacion (username, foto perfil, union canal, aniadir usuarios)
  - Submenus con acciones: kick, ban, silenciar, off, warn, aviso
  - Titulos dinamicos mostrando estado actual

Fase 3:
Objetivo fase: Implementar menus de bloqueos
Implementacion fase:
  - Crear menu principal de bloqueos con 4 items
  - Crear submenus para cada bloqueo (nombre arabe, chino, ruso, spam)
  - Submenus con acciones: kick, ban, silenciar, off, warn, aviso
  - Titulos dinamicos mostrando estado actual

Fase 4:
Objetivo fase: Implementar menus de configuracion general
Implementacion fase:
  - Menu de filtro al ingreso (toggle activo/inactivo)
  - Menu de borrar mensajes (toggle activo/inactivo)
  - Registrar todos los menus en __init__.py

Fase 5:
Objetivo fase: Implementar handlers de callbacks
Implementacion fase:
  - Crear FiltroFeature con handleObligationAction
  - Crear handleBlockAction para cada tipo de bloqueo
  - Crear handleFilterEntry y handleDeleteMessages
  - Integrar callbacks con acciones reales (kick, ban, warn, etc.)
