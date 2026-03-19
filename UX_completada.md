Fecha: 2026-03-19
version: v1.0-fase1
referencia: migracion_estructura_UI/UX.md

Resumen de la solucion (Fase 1 ejecutada):
- Se creo infraestructura comun para el renderizado de estados en menus (formatters y rendering).
- Se agrego un helper en FeatureModule para actualizar configuracion y refrescar el menu sin mostrar modales.

Cambios realizados:
1) Helpers de formato reutilizables
   - Archivo: app/manager_bot/_menus/formatters.py
   - Funciones: yes_no, on_off, duration_label, action_label
   - Objetivo: estandarizar estados (Si/No, Off/Warn/Kick, duraciones).

2) Helpers de renderizado
   - Archivo: app/manager_bot/_menus/rendering.py
   - Funciones: build_section, build_title
   - Objetivo: construir descripciones de menu consistentes y reutilizables.

3) Helper comun para refrescar menus (sin modal)
   - Archivo: app/manager_bot/_features/base.py
   - Metodo: update_config_and_refresh(...)
   - Objetivo: aplicar cambios, persistir config y refrescar el menu con show_menu_by_callback.
   - Nota UX: por defecto no se muestra modal; solo se usa show_alert cuando se indique explicitamente o hay error.

Efecto esperado:
- Los features podran migrar sus handlers a update_config_and_refresh para reflejar los cambios directamente en el texto del menu.
- La UI quedara consistente y mas reutilizable en todos los menus.

Pendiente para Fase 2:
- Migrar antispam/antiflood a los helpers nuevos.
- Eliminar callback.answer(..., show_alert=True) en exitos.
- Ajustar titulos de menus para mostrar estados con los nuevos formatters.
