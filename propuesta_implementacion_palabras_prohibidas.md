Fecha: 21/03/2026
Version: 1.0
Referencia: palabras_bloqueadas.md

Resumen de la implementacion:
Implementar menu de palabras prohibidas que permite establecer palabras o patrones que no estan permitidos en el grupo. Para cada palabra se puede configurar una accion de castigo (kick, ban, warn, silenciar, aviso, off) y si se eliminan automaticamente los mensajes que contengan dichas palabras.

Arquitectura final:

app/manager_bot/_menus/
├── palabras_prohibidas_menu.py    # Menu de palabras prohibidas
└── moderation_menu.py             # Menu de moderation (referencia)

app/manager_bot/_config/
└── group_config.py               # Campos: blocked_words_enabled, blocked_words_action, blocked_words_delete

app/manager_bot/_features/
├── blocked_words/
│   └── __init__.py               # BlockedWordsFeature con handlers
└── moderation/
    └── __init__.py               # ModerationFeature (referencia)

Estructura del menu:

Menu Principal - Palabras Prohibidas:
| Campo | Valor |
|-------|-------|
| Titulo | 🔤 Palabras Prohibidas\n\nCastigo: {accion}\nEliminacion: {Si/No} |
| Menu ID | palabras_prohibidas |
| Parent | main |

Opciones del menu:
| Fila | Columna 1 | Columna 2 |
|------|-----------|-----------|
| 1 | Accion: {Kick} | Ver Palabras |
| 2 | Eliminacion: {Si} | Agregar Palabra |
| 3 | Eliminar Todas | - |
| 4 | Volver | - |

Acciones disponibles: Kick, Ban, Silenciar, Warn, Aviso, Off

Tabla de tareas:

| # | Tarea                                        | Tipo      | Prioridad |
|---|----------------------------------------------|-----------|-----------|
| 1 | Agregar campos en GroupConfig                  | Modelo    | Alta      |
| 2 | Crear menu principal de palabras prohibidas    | Menu      | Alta      |
| 3 | Crear menu de accion de castigo               | Menu      | Alta      |
| 4 | Crear menu de agregar palabras                | Menu      | Alta      |
| 5 | Crear menu de lista de palabras               | Menu      | Media     |
| 6 | Crear BlockedWordsFeature con handlers         | Feature   | Alta      |
| 7 | Registrar menus y feature                      | Registro  | Alta      |
| 8 | Integrar con sistema de moderation            | Integracion| Media    |

Fase 1:
Objetivo fase: Preparar estructura y modelos de datos
Implementacion fase:
  - Agregar campos en GroupConfig si no existen:
    - blocked_words_enabled: bool = True
    - blocked_words_action: str = "off" (kick, ban, silenciar, warn, aviso, off)
    - blocked_words_delete: bool = False
    - blocked_words: List[str] (ya existe)
  - Crear directorio _features/blocked_words/

Fase 2:
Objetivo fase: Crear menu principal de palabras prohibidas
Implementacion fase:
  - create_palabras_prohibidas_menu(config) -> MenuDefinition
  - Menu ID: palabras_prohibidas
  - Parent: main
  - Titulo dinamico con:
    - Estado actual (Activo/Apagado)
    - Accion de castigo actual
    - Estado de eliminacion (Si/No)
  - Opciones:
    - Accion de castigo (ver/editar)
    - Eliminacion (ver/editar)
    - Ver lista de palabras
    - Agregar palabra
    - Eliminar todas
    - Volver

Fase 3:
Objetivo fase: Crear menus de configuracion
Implementacion fase:
  - create_palabras_prohibidas_action_menu:
    - Submenu para seleccionar accion de castigo
    - Opciones: Kick, Ban, Silenciar, Warn, Aviso, Off
    - Mostrar accion actual marcada
  - create_palabras_prohibidas_delete_menu:
    - Toggle para activar/desactivar eliminacion de mensajes
    - Opcion: Si / No

Fase 4:
Objetivo fase: Crear menus de gestion de palabras
Implementacion fase:
  - create_palabras_prohibidas_add_menu:
    - Instrucciones para agregar palabra
    - Prompt para enviar la palabra
  - create_palabras_prohibidas_list_menu:
    - Lista de palabras agregadas (max 10)
    - Opcion para eliminar cada palabra
    - Paginacion si hay mas de 10

Fase 5:
Objetivo fase: Crear BlockedWordsFeature con handlers
Implementacion fase:
  - Clase BlockedWordsFeature(FeatureModule)
  - Implementar handlers:
    - handle_show_menu: Muestra menu principal
    - handle_action_set: Establece accion de castigo
    - handle_delete_toggle: Toggle eliminacion de mensajes
    - handle_add_word: Agregar palabra a la lista
    - handle_del_word: Eliminar palabra de la lista
    - handle_clear_all: Eliminar todas las palabras
    - handle_list: Mostrar lista de palabras
  - Registrar callbacks con prefijo palabras_prohibidas:

Fase 6:
Objetivo fase: Registrar e integrar con sistema
Implementacion fase:
  - Registrar menus en __init__.py de menus
  - Registrar BlockedWordsFeature en _menu_service.py
  - Integrar con menu principal de configuracion
  - Actualizar menu_engine.py con handler

Fase 7:
Objetivo fase: Documentar implementacion
Implementacion fase:
  - Documentar cambios en archivo de implementacion completada
  - Verificar consistencia con otras features de moderation
