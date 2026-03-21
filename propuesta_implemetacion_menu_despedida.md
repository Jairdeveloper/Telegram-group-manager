Fecha: 21/03/2026
Version: 1.0
Referencia: despedida.md

Resumen de la implementacion:
Implementar menu de despedida que permite establecer un mensaje de despedida personalizado que se enviara cuando un usuario abandone el grupo. El menu incluira opciones para activar/desactivar, personalizar texto, multimedia y teclado inline, ademas de una vista previa completa.

Arquitectura final:

app/manager_bot/_menus/
├── goodbye_menu.py              # Menu principal de despedida (actualizar)
└── welcome_menu.py              # Menu de bienvenida (referencia)

app/manager_bot/_features/
├── goodbye/
│   └── __init__.py              # GoodbyeFeature con handlers de callbacks
└── welcome/
    └── __init__.py              # WelcomeFeature (referencia)

Estructura del menu:

Menu Principal - Despedida:
| Campo | Valor |
|-------|-------|
| Titulo | 👋🏻 Despedida\n\nEstado: {Activo/Apagado} |

Opciones:
| # | Opcion | Submenu |
|---|--------|---------|
| 1 | Texto | create_goodbye_text_menu + Vista |
| 2 | Multimedia | create_goodbye_media_menu + Vista |
| 3 | Personalizar Mensaje | Submenu |
| 4 | Vista Previa Completa | Vista previa |

Submenu Personalizar:
| # | Opcion | Descripcion |
|---|--------|-------------|
| 1 | Encabezado | Establecer encabezado personalizado |
| 2 | Pie de pagina | Establecer pie de pagina personalizado |
| 3 | Teclado Inline | Configurar botones inline |

Tabla de tareas:

| # | Tarea                                        | Tipo      | Prioridad |
|---|----------------------------------------------|-----------|-----------|
| 1 | Actualizar estructura de GroupConfig          | Modelo    | Alta      |
| 2 | Renombrar goodbye_menu.py a despedida_menu.py | Refactor  | Alta      |
| 3 | Actualizar funciones del menu de despedida    | Menu      | Alta      |
| 4 | Crear submenus de personalizacion            | Menu      | Alta      |
| 5 | Crear menu de vista previa                   | Menu      | Media     |
| 6 | Crear GoodbyeFeature con handlers             | Feature   | Alta      |
| 7 | Registrar menus en __init__.py               | Registro  | Alta      |
| 8 | Integrar con sistema de moderation           | Integracion| Media    |

Fase 1:
Objetivo fase: Preparar estructura y modelos de datos
Implementacion fase:
  - Verificar campos goodbye_enabled, goodbye_text en GroupConfig
  - Agregar campos si no existen: goodbye_media, goodbye_inline_keyboard
  - Agregar campos: goodbye_header, goodbye_footer
  - Crear directorio _features/goodbye/ si no existe

Fase 2:
Objetivo fase: Renombrar y estructurar menu de despedida
Implementacion fase:
  - Renombrar goodbye_menu.py a despedida_menu.py (o mantener nombre existente)
  - Crear funcion create_despedida_menu para menu principal
  - Estructura de opciones:
    - Fila 1: "Texto" | "Ver Texto"
    - Fila 2: "Multimedia" | "Ver Multimedia"
    - Fila 3: "Personalizar Mensaje"
    - Fila 4: "Vista Previa Completa"
  - Mostrar estado actual (Activo/Apagado) en titulo

Fase 3:
Objetivo fase: Crear submenus de personalizacion
Implementacion fase:
  - create_despedida_text_menu: Menu de texto
    - Opcion "Ver" para ver texto actual
    - Opcion para establecer nuevo texto (envia prompt)
  - create_despedida_media_menu: Menu de multimedia
    - Opcion "Ver" para ver multimedia actual
    - Opcion para establecer multimedia
  - create_despedida_customize_menu: Menu de personalizacion
    - Encabezado: crear/edit/ver
    - Pie de pagina: crear/edit/ver
    - Teclado inline: crear/edit/ver

Fase 4:
Objetivo fase: Crear menu de vista previa
Implementacion fase:
  - create_despedida_preview_menu: Vista previa completa
  - Renderizar mensaje completo con:
    - Encabezado (si existe)
    - Texto de despedida
    - Multimedia (si existe)
    - Teclado inline (si existe)
    - Pie de pagina (si existe)
  - Mostrar preview formateado con labels de cada componente

Fase 5:
Objetivo fase: Crear GoodbyeFeature con handlers
Implementacion fase:
  - Renombrar WelcomeFeature a GoodbyeFeature o crear nueva clase
  - Implementar handlers:
    - handle_show_menu: Muestra menu principal
    - handle_toggle: Activar/Desactivar despedida
    - handle_text_show: Mostrar texto actual
    - handle_text_set: Establecer nuevo texto
    - handle_media_show: Mostrar multimedia actual
    - handle_media_set: Establecer multimedia
    - handle_customize: Mostrar menu de personalizacion
    - handle_header_*: Ver/Establecer encabezado
    - handle_footer_*: Ver/Establecer pie de pagina
    - handle_inline_*: Ver/Establecer teclado inline
    - handle_preview: Mostrar vista previa completa
  - Registrar callbacks con prefijo despedida:

Fase 6:
Objetivo fase: Registrar e integrar con sistema
Implementacion fase:
  - Registrar menus en __init__.py de menus
  - Registrar GoodbyeFeature en _menu_service.py
  - Integrar con menu principal de configuracion
  - Verificar navegacion entre menus

Fase 7:
Objetivo fase: Documentar implementacion
Implementacion fase:
  - Documentar cambios en archivo de implementacion completada
  - Verificar consistencia con bienvenida
