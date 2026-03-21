Fecha: 21/03/2026
Version: 1.0

Resumen de la refactorizacion:
Separar las funciones de filtrado en dos menus distintos accesibles desde el menu principal /config. Actualmente solo se muestra el filtro de contenido (palabras bloqueadas, stickers, patrones), y se requiere agregar el filtro de seguridad (obligaciones y bloqueos de nombres).

Arquitectura objetivo:

app/manager_bot/_menus/
├── filtro_seguridad_menu.py    # Renombrado de filtro_menu.py (obligaciones y bloqueos de nombres)
├── filtro_contenido_menu.py    # Renombrado de filters_menu.py (palabras, stickers, patrones)

Cambios requeridos:

1. Renombrar filtro_menu.py -> filtro_seguridad_menu.py
   - Actualizar docstrings y comentarios
   - Mantener toda la logica existente

2. Renombrar filters_menu.py -> filtro_contenido_menu.py
   - Actualizar docstrings y comentarios
   - Renombrar funciones con prefijo filtro_contenido_

3. Actualizar __init__.py de menus:
   - Importar desde los nuevos nombres de archivo
   - Registrar menus con nombres consistentes

4. Actualizar referencias en FiltroFeature:
   - Actualizar imports para usar filtro_seguridad_menu

5. Agregar ambos menus al menu principal:
   - En main_menu.py, agregar opcion "Filtros de Seguridad"
   - En main_menu.py, agregar opcion "Filtros de Contenido"
   - O usar submenu "Filtros" con dos opciones

Pasos de implementacion:

| # | Tarea | Tipo | Prioridad |
|---|-------|------|-----------|
| 1 | Renombrar filtro_menu.py | Refactor | Alta |
| 2 | Renombrar filters_menu.py | Refactor | Alta |
| 3 | Actualizar imports en __init__.py | Registro | Alta |
| 4 | Actualizar imports en FiltroFeature | Registro | Alta |
| 5 | Agregar menus al menu principal | UI | Alta |
