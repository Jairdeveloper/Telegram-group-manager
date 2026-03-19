Fecha: 2026-03-18
version: v1.0
referencia: implementacion_funcionalidad_menu_service.md, app/manager_bot/_menus/*, app/manager_bot/_transport/telegram/menu_engine.py

Resumen de la migracion:
- Eliminar el boton "Moderacion" del menu principal.
- Exponer en el menu principal los accesos directos a: Anti-Flood, Anti-Canal, Anti-Enlaces, Moderacion Media, Palabras Bloqueadas y Modo Nocturno.
- Ajustar navegacion para que los submenus de moderacion regresen a "main".
- Mantener compatibilidad con callbacks existentes (mod:*), evitando romper mensajes antiguos.

Arquitectura final:
- Menu principal (menu_id: main)
  - Antispam, Filtros, Bienvenida, Despedida, Captcha, Reportes, Informacion.
  - Accesos directos de moderacion:
    - Anti-Flood (toggle directo, sin submenu)
    - Anti-Canal (abre submenu mod:antichannel)
    - Anti-Enlaces (abre submenu mod:antilink)
    - Moderacion Media (abre submenu mod:media)
    - Palabras Bloqueadas (abre submenu mod:words)
    - Modo Nocturno (abre submenu mod:nightmode)
- Submenus de moderacion mantienen menu_id actual (mod:*), pero con parent_menu="main" y back="nav:back:main".
- Menu "mod" se deja oculto (sin boton) o se marca como deprecado para compatibilidad.

Tabla de tareas:
| Fase | Objetivo fase | Implementacion fase |
| --- | --- | --- |
| 1 | Reubicar accesos de moderacion al menu principal | Actualizar main_menu.py para quitar "mod:show" y agregar acciones para antiflood, antichannel, antilink, media, words, nightmode. Reorganizar filas para no sobrecargar el menu. |
| 2 | Ajustar navegacion de submenus | Cambiar parent_menu y botones "Volver" en moderation_menu.py (mod:antichannel, mod:antilink, mod:media, mod:words, mod:nightmode) para que regresen a main. |
| 3 | Compatibilidad y validacion | Mantener registro de callbacks mod:*; opcionalmente mantener mod menu en registry para mensajes antiguos. Actualizar tests de menu si existen snapshots o expectativas. |

Fase: 1
OBjetivo fase: Reubicar accesos de moderacion al menu principal.
Implementacion fase: Modificar app/manager_bot/_menus/main_menu.py. Eliminar el boton "Moderacion" (mod:show) y agregar botones directos para antiflood (toggle), antichannel (mod:antichannel:show), antilink (mod:antilink:show), media (mod:media:show), palabras bloqueadas (mod:words:show), nightmode (mod:nightmode:show). Reordenar filas para mantener una grilla de 2 botones por fila.

Fase: 2
OBjetivo fase: Ajustar navegacion de submenus de moderacion para que vuelvan a main.
Implementacion fase: Actualizar app/manager_bot/_menus/moderation_menu.py en los menus mod:antichannel, mod:antilink, mod:media, mod:words y mod:nightmode para usar parent_menu="main" y nav:back:main. Mantener menu_id actual para no romper callbacks existentes.

Fase: 3
OBjetivo fase: Compatibilidad y validacion.
Implementacion fase: Mantener registrado el handler de mod:show y el menu mod (opcional) para soportar botones antiguos ya enviados; marcarlo como deprecado en comentarios. Revisar tests de menus si existen, y ajustar expectativas del menu principal. Ejecutar pruebas focalizadas de navegacion/menu.
