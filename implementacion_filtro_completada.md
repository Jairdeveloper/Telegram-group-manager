Fecha: 20/03/2026
Version: 1.0
Referencia: filtro.md, propuesta_implementacion_filtro.md

Resumen de la migracion:
 Migrar la feature de filtros de seguridad desde un sistema de comandos individuales hacia una arquitectura modular basada en menus dinamicos con submenus de configuracion. La feature permitira configurar obligaciones y bloqueos de usuarios con diferentes acciones (kick, ban, silenciar, off, warn, aviso) para cada tipo de filtro.

Arquitectura final:

app/manager_bot/
├── _config/
│   └── group_config.py          # Agregados campos de filtros
├── _menus/
│   ├── __init__.py               # Registrar menus de filtro
│   └── filtro_menu.py            # Menus dinamicos para filtros (pendiente)
└── _features/
    └── filtro/
        ├── __init__.py           # FiltroFeature con callbacks
        └── _handlers.py          # Handlers de acciones (opcional)

============================================================
FASE 1 COMPLETADA
============================================================

Objetivo fase: Definir modelos de datos y estructura base

Implementacion fase:

1. Modelos de datos en GroupConfig (group_config.py:96-112)

   Agregados los siguientes campos:

   Configuracion general:
   - filtro_on_entry: bool = True          (verificar al ingreso vs al mensaje)
   - filtro_delete_messages: bool = False (borrar mensajes filtrados)

   Obligaciones:
   - filtro_obligation_username_action: str = "off"
   - filtro_obligation_photo_action: str = "off"
   - filtro_obligation_channel_action: str = "off"
   - filtro_obligation_add_users_action: str = "off"

   Bloqueos:
   - filtro_block_arabic_action: str = "off"
   - filtro_block_chinese_action: str = "off"
   - filtro_block_russian_action: str = "off"
   - filtro_block_spam_action: str = "off"

   Acciones disponibles: kick, ban, silenciar, off, warn, aviso

2. Estructura de directorios

   Creado: app/manager_bot/_features/filtro/__init__.py

3. FiltroFeature base (_features/filtro/__init__.py)

   Clase FiltroFeature con los siguientes metodos:

   - handle_callback(): Entry point para callbacks filtro:*
   - _handle_show_menu(): Muestra submenus (obligation, block, config)
   - _handle_obligation_action(): Maneja acciones de obligaciones
   - _handle_block_action(): Maneja acciones de bloqueos
   - _handle_config_action(): Maneja toggles de configuracion general

   Callbacks soportados:
   - filtro:obligation:{type}:{action}  (type: username|photo|channel|add_users)
   - filtro:block:{type}:{action}      (type: arabic|chinese|russian|spam)
   - filtro:config:{action}            (action: on_entry|delete)

Estado: FASE 1 COMPLETADA

Proximos pasos: Fases 2-4 (crear menus dinamicos)

============================================================
FASE 2 COMPLETADA
============================================================

Objetivo fase: Implementar menus de obligaciones

Implementacion fase:

1. Archivo creado: app/manager_bot/_menus/filtro_menu.py

   Menu principal (create_filtro_menu):
   - menu_id: "filtro"
   - Titulo dinamico con estado de todas las obligaciones
   - Items: Obligaciones, Bloquear, Configuracion

   Menu de Obligaciones (create_obligation_menu):
   - menu_id: "filtro:obligation"
   - Muestra las 4 obligaciones con su accion actual
   - Items para cada tipo de obligacion

   Menus de accion por obligacion (create_obligation_action_menu):
   - menu_id: "filtro:obligation:{type}"
   - Submenus con acciones: kick, ban, silenciar, off, warn, aviso
   - Marcar la opcion actual con corchetes []

   Constantes definidas:
   - FILTRO_OBLIGATIONS: ["username", "photo", "channel", "add_users"]
   - FILTRO_OBLIGATION_LABELS: etiquetas en espanol
   - FILTRO_ACTIONS: ["kick", "ban", "silenciar", "off", "warn", "aviso"]
   - FILTRO_ACTION_LABELS: etiquetas en espanol

2. Registro de menus en __init__.py

   registry.register(create_filtro_menu)
   registry.register(create_obligation_menu)
   for obligation in ("username", "photo", "channel", "add_users"):
       registry.register(lambda config, o=obligation: create_obligation_action_menu(o, config))

3. Callbacks de obligaciones

   Formato: filtro:obligation:{action}:{type}
   Ejemplos:
   - filtro:obligation:show -> muestra menu de obligaciones
   - filtro:obligation:kick:username -> configura kick para username
   - filtro:obligation:warn:channel -> configura warn para canal

Estado: FASE 2 COMPLETADA

Proximos pasos: Fase 3 (menus de bloqueos)

============================================================
FASE 3 COMPLETADA
============================================================

Objetivo fase: Implementar menus de bloqueos

Implementacion fase:

1. Constantes agregadas en filtro_menu.py

   FILTRO_BLOCKS = ["arabic", "chinese", "russian", "spam"]
   FILTRO_BLOCK_LABELS: {
       "arabic": "Nombre Arabe",
       "chinese": "Nombre Chino",
       "russian": "Nombre Ruso",
       "spam": "Nombre Spam",
   }

2. Funciones helper agregadas

   _get_block_field(block_type) -> str
   _get_action_for_block(config, block_type) -> str

3. Menus de bloqueos agregados

   Menu de Bloquear (create_block_menu):
   - menu_id: "filtro:block"
   - Muestra los 4 tipos de bloqueo con su accion actual
   - Items para cada tipo de bloqueo

   Menu de accion por bloqueo (create_block_action_menu):
   - menu_id: "filtro:block:{type}"
   - Submenus con acciones: kick, ban, silenciar, off, warn, aviso
   - Marcar la opcion actual con corchetes []

4. Registro de menus en __init__.py

   registry.register(create_block_menu)
   for block in ("arabic", "chinese", "russian", "spam"):
       registry.register(lambda config, b=block: create_block_action_menu(b, config))

5. Callbacks de bloqueos

   Formato: filtro:block:{action}:{type}
   Ejemplos:
   - filtro:block:show -> muestra menu de bloqueos
   - filtro:block:kick:arabic -> configura kick para nombre arabe
   - filtro:block:warn:chinese -> configura warn para nombre chino

6. FiltroFeature actualizado

   _handle_show_menu() ahora maneja bloques:
   - filtro:block:show -> "filtro:block"
   - filtro:block:{type}:show -> "filtro:block:{type}"

Estado: FASE 3 COMPLETADA

Proximos pasos: Fase 4 (menus de configuracion general)

============================================================
FASE 4 COMPLETADA
============================================================

Objetivo fase: Implementar menus de configuracion general

Implementacion fase:

1. Menu de configuracion (create_config_menu)

   - menu_id: "filtro:config"
   - Titulo con descripcion de cada opcion
   - Estado actual de cada opcion en el titulo

   Opciones:
   - Filtrar al ingreso: Toggle on/off
     Si esta activo, el bot verificara Obligaciones/Bloqueos cuando el usuario se una al grupo.
     En cambio si no, solo lohara cuando el usuario envie un mensaje.

   - Borrar los Mensajes: Toggle on/off
     Si esta activo, el bot eliminara todos los mensajes enviados por usuarios
     que no cumplan con las Obligaciones/Bloqueos.

2. Registro de menu en __init__.py

   registry.register(create_config_menu)

3. Callbacks de configuracion

   Formato: filtro:config:{action}:{value}
   Ejemplos:
   - filtro:config:show -> muestra menu de configuracion
   - filtro:config:on_entry:on -> activa filtro al ingreso
   - filtro:config:on_entry:off -> desactiva filtro al ingreso
   - filtro:config:delete:on -> activa borrar mensajes
   - filtro:config:delete:off -> desactiva borrar mensajes

4. FiltroFeature actualizado

   _handle_config_action() ahora parsea el valor:
   - Accepta on/off para on_entry y delete
   - Actualiza config y retorna "filtro:config"

   _handle_show_menu() ahora maneja config:
   - filtro:config:show -> "filtro:config"

============================================================
RESUMEN DE MENUS IMPLEMENTADOS
============================================================

Menu principal:
- filtro:show -> Menu principal con estado de todas las opciones

Submenus:
- filtro:obligation -> Lista de obligaciones
- filtro:obligation:{type} -> Acciones para obligacion especifica

- filtro:block -> Lista de bloqueos
- filtro:block:{type} -> Acciones para bloqueo especifico

- filtro:config -> Configuracion general (filtro al ingreso, borrar mensajes)

Total de menus: 1 principal + 1 obligacion + 4 accion obligacion + 1 bloqueos + 4 accion bloqueo + 1 config = 12 menus

============================================================
TODAS LAS FASES COMPLETADAS
============================================================

Fase 1: Modelos de datos y estructura base
Fase 2: Menus de obligaciones
Fase 3: Menus de bloqueos
Fase 4: Menus de configuracion general

============================================================
FASE 5 COMPLETADA
============================================================

Objetivo fase: Implementar handlers de callbacks e integracion

Implementacion fase:

1. Refactorizacion de FiltroFeature

   - Ahora hereda de FeatureModule (base class)
   - Implementa register_callbacks() para el CallbackRouter
   - Soporta patron de callback del sistema existente

2. Registro de callbacks en CallbackRouter

   Menu principal:
   - filtro:show -> handle_show_menu

   Obligaciones:
   - filtro:obligation:show -> handle_obligation_show
   - filtro:obligation:{type}:show -> handle_obligation_type_show
   - filtro:obligation -> handle_obligation_action

   Bloqueos:
   - filtro:block:show -> handle_block_show
   - filtro:block:{type}:show -> handle_block_type_show
   - filtro:block -> handle_block_action

   Configuracion:
   - filtro:config:show -> handle_config_show
   - filtro:config -> handle_config_toggle

3. Metodos de verificacion de filtros

   Obligaciones:
   - check_username_filter(config, username) -> Optional[str]
   - check_photo_filter(config, has_photo) -> Optional[str]
   - check_channel_filter(config, is_channel_member) -> Optional[str]
   - check_add_users_filter(config, can_add_users) -> Optional[str]

   Bloqueos:
   - check_arabic_filter(config, name) -> Optional[str]
   - check_chinese_filter(config, name) -> Optional[str]
   - check_russian_filter(config, name) -> Optional[str]
   - check_spam_filter(config, name) -> Optional[str]

   Retorna la accion a tomar si se activa el filtro, None si no aplica.

4. Patrones de deteccion

   - ARABIC_PATTERN: re para caracteres arabes
   - CHINESE_PATTERN: re para caracteres chinos
   - RUSSIAN_PATTERN: re para caracteres cirilicos

   Filtro de spam detecta:
   - Caracteres repetidos (5+ veces)
   - Nombres muy largos sin espaciado
   - URLs
   - Palabras clave: buy, sell, offer, discount

5. Funciones de inicializacion

   - get_filtro_feature() -> Optional[FiltroFeature]
   - init_filtro_feature(config_storage) -> FiltroFeature

============================================================
INTEGRACION FUTURA
============================================================

Para integrar con el sistema de moderation:

1. En el handler de new_chat_members:
   - Obtener config del grupo
   - Para cada nuevo usuario:
     - Verificar filtros de obligacion (username, foto, canal)
     - Verificar filtros de bloqueo (nombre arabe, chino, ruso, spam)
   - Si se activa un filtro, aplicar la accion correspondiente

2. En el handler de mensajes:
   - Si filtro_on_entry es False, verificar filtros
   - Verificar filtros de nombre para usuarios activos

3. Acciones disponibles:
   - kick: Expulsar al usuario
   - ban: Banear al usuario
   - silenciar: Silenciar al usuario
   - warn: Advertir al usuario
   - aviso: Enviar aviso
   - off: No hacer nada

============================================================
IMPLEMENTACION COMPLETADA
============================================================

Todas las fases completadas:
- Fase 1: Modelos de datos y estructura base
- Fase 2: Menus de obligaciones
- Fase 3: Menus de bloqueos
- Fase 4: Menus de configuracion general
- Fase 5: Handlers de callbacks e integracion
