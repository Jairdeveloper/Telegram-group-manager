Fecha: 2026-03-18
version: v1.0
referencia: implementacion_refactor_menu_moderacion.md

Resumen de la migracion:
- Se elimino el boton "Moderacion" del menu principal.
- Se expusieron en el menu principal los accesos directos de moderacion (Anti-Flood, Anti-Canal, Anti-Enlaces, Moderacion Media, Palabras Bloqueadas, Modo Nocturno).
- Se ajusto la navegacion de submenus de moderacion para volver a "main".
- Se mantuvo compatibilidad con callbacks existentes (mod:*).
 - Se corrigio el regreso de los submenus (Media/Anti-Enlaces/Modo Nocturno) que aun apuntaban a "mod".

Arquitectura final:
- Menu principal (menu_id: main)
  - Antispam, Filtros, Bienvenida, Despedida, Captcha, Reportes, Informacion.
  - Accesos directos de moderacion en el menu principal:
    - Anti-Flood (toggle directo via mod:antiflood:toggle)
    - Anti-Canal (abre mod:antichannel)
    - Anti-Enlaces (abre mod:antilink)
    - Moderacion Media (abre mod:media)
    - Palabras Bloqueadas (abre mod:words)
    - Modo Nocturno (abre mod:nightmode)
- Submenus de moderacion mantienen menu_id mod:* pero con back a main.

Tabla de tareas:
| Fase | Objetivo fase | Implementacion fase |
| --- | --- | --- |
| 1 | Reubicar accesos de moderacion al menu principal | main_menu actualizado, agregando botones de moderacion y quitando mod:show. |
| 2 | Ajustar navegacion de submenus | moderation_menu actualizado y menus dedicados (media/antilink/nightmode) ahora vuelven a main. |
| 3 | Compatibilidad y validacion | Se mantuvieron callbacks mod:* y menu mod registrado. Se actualizo el render de menu principal para usar config en runtime. |

Fase: 1
OBjetivo fase: Reubicar accesos de moderacion al menu principal.
Implementacion fase:
- app/manager_bot/_menus/main_menu.py
  - Se elimino el boton "mod:show".
  - Se agregaron acciones para: Anti-Flood, Anti-Canal, Anti-Enlaces, Moderacion Media, Palabras Bloqueadas, Modo Nocturno.
  - Se reorganizaron filas para mantener 2 botones por fila.

Fase: 2
OBjetivo fase: Ajustar navegacion de submenus de moderacion.
Implementacion fase:
- app/manager_bot/_menus/moderation_menu.py
  - mod:antichannel, mod:antilink, mod:media, mod:words, mod:nightmode ahora vuelven a main.
  - parent_menu actualizado a "main" y back a "nav:back:main".
- app/manager_bot/_menus/antilink_menu.py
  - back actualizado a "nav:back:main".
- app/manager_bot/_menus/nightmode_menu.py
  - back actualizado a "nav:back:main".
- app/manager_bot/_menus/media_menu.py
  - back actualizado a "nav:back:main".

Fase: 3
OBjetivo fase: Compatibilidad y validacion.
Implementacion fase:
- app/manager_bot/_transport/telegram/menu_engine.py
  - Se ajusto el render del menu principal para que se construya con config en runtime (evita perdida de estado de Anti-Flood y contador de palabras bloqueadas).
- Se mantuvo registro de mod y callbacks existentes para compatibilidad con mensajes antiguos.

Notas:
- No se ejecutaron tests en esta ronda.
