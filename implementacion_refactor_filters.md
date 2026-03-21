Fecha: 21/03/2026
Version: 1.0
Referencia: refactorizacion_filtro.md

Resumen de la implementacion:
Separar las funciones de filtrado en dos menus distintos accesibles desde el menu principal /config. Actualmente solo se muestra el filtro de contenido (palabras bloqueadas, stickers, patrones), y se requiere agregar el filtro de seguridad (obligaciones y bloqueos de nombres) para que ambos sean accesibles desde el menu principal.

Arquitectura final:

app/manager_bot/_menus/
├── filtro_seguridad_menu.py    # Renombrado de filtro_menu.py (obligaciones y bloqueos de nombres)
├── filtro_contenido_menu.py    # Renombrado de filters_menu.py (palabras, stickers, patrones)
└── main_menu.py                # Menu principal actualizado con ambos filtros

Tabla de tareas:

| # | Tarea                                        | Tipo      | Prioridad |
|---|----------------------------------------------|-----------|-----------|
| 1 | Renombrar filtro_menu.py a filtro_seguridad_menu.py | Refactor | Alta      |
| 2 | Renombrar filters_menu.py a filtro_contenido_menu.py | Refactor | Alta      |
| 3 | Actualizar imports y funciones en filtro_seguridad_menu.py | Refactor | Alta      |
| 4 | Actualizar imports y funciones en filtro_contenido_menu.py | Refactor | Alta      |
| 5 | Actualizar __init__.py de menus con nuevos nombres | Registro  | Alta      |
| 6 | Actualizar imports en FiltroFeature | Registro  | Alta      |
| 7 | Actualizar main_menu.py para agregar ambos filtros | UI        | Alta      |
| 8 | Actualizar referencias en archivos que usen filtros_menu | Refactor  | Media     |

Fase 1:
Objetivo fase: Renombrar archivos y mantener logica existente
Implementacion fase:
  - Renombrar filtro_menu.py a filtro_seguridad_menu.py
  - Renombrar filters_menu.py a filtro_contenido_menu.py
  - Actualizar docstrings en ambos archivos para reflejar los nuevos nombres
  - Mantener toda la logica y estructura de funciones intacta

Fase 2:
Objetivo fase: Actualizar funciones con prefijos consistentes
Implementacion fase:
  - En filtro_contenido_menu.py, renombrar funciones con prefijo filtro_contenido_:
    - create_filters_menu -> create_filtro_contenido_menu
    - create_filters_list_menu -> create_filtro_contenido_list_menu
    - create_blocked_words_menu -> create_filtro_contenido_words_menu
    - create_sticker_blacklist_menu -> create_filtro_contenido_sticker_menu
  - En filtro_seguridad_menu.py, renombrar funciones con prefijo filtro_seguridad_:
    - create_filtro_menu -> create_filtro_seguridad_menu
    - Mantener nombres de submenus existentes
  - Actualizar referencias a menu_id en todas las funciones

Fase 3:
Objetivo fase: Actualizar registros e imports
Implementacion fase:
  - Actualizar imports en __init__.py de menus
  - Actualizar imports en FiltroFeature
  - Registrar menus con nuevos nombres de funcion
  - Actualizar todas las referencias a menu_id

Fase 4:
Objetivo fase: Agregar ambos filtros al menu principal
Implementacion fase:
  - En main_menu.py, agregar opcion "Filtros de Seguridad" -> "filtro_seguridad:show"
  - En main_menu.py, agregar opcion "Filtros de Contenido" -> "filtro_contenido:show"
  - Crear submenu intermedio "Filtros" con dos opciones si se desea anidacion
  - Actualizar titulos y labels para claridad
  - Registrar nuevos handlers de navegacion si se crea submenu
