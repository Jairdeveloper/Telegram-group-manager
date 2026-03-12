# Plan de Implementación - Manager Bot

## Resumen del Proyecto

Implementación de un sistema de menús interactivos mediante Inline Keyboards para el Manager Bot, permitiendo una administración completa de grupos de Telegram sin necesidad de usar comandos de texto.

**Duración estimada**: 5 semanas

---

## FASE 1: Core de Menús (Semana 1)

### Objetivo
Establecer la infraestructura base del sistema de menús.

### Tareas

#### 1.1 Crear estructura de carpetas
```bash
app/manager_bot/
├── menus/
│   ├── __init__.py
│   ├── base.py
│   ├── registry.py
│   ├── main_menu.py
│   ├── moderation_menu.py
│   └── navigation.py
├── transport/telegram/
│   ├── menu_engine.py
│   ├── callback_router.py
│   └── keyboard_builder.py
├── config/
│   ├── __init__.py
│   ├── storage.py
│   └── group_config.py
└── features/
    ├── __init__.py
    └── base.py
```

**Archivos a crear:**
- [ ] `app/manager_bot/menus/__init__.py`
- [ ] `app/manager_bot/menus/base.py` - MenuDefinition, MenuAction, MenuRow
- [ ] `app/manager_bot/menus/registry.py` - MenuRegistry
- [ ] `app/manager_bot/menus/navigation.py` - NavigationManager, NavigationContext
- [ ] `app/manager_bot/transport/telegram/keyboard_builder.py` - KeyboardBuilder
- [ ] `app/manager_bot/transport/telegram/callback_router.py` - CallbackRouter, CallbackPattern
- [ ] `app/manager_bot/transport/telegram/menu_engine.py` - MenuEngine
- [ ] `app/manager_bot/config/__init__.py`
- [ ] `app/manager_bot/config/group_config.py` - GroupConfig dataclass
- [ ] `app/manager_bot/config/storage.py` - ConfigStorage abstract, PostgresConfigStorage, RedisConfigStorage
- [ ] `app/manager_bot/features/__init__.py`
- [ ] `app/manager_bot/features/base.py` - FeatureModule base class

#### 1.2 Implementar MenuDefinition y MenuRegistry
**Archivo:** `app/manager_bot/menus/base.py`
- Crear dataclass `MenuAction` con callback_data, label, emoji
- Crear dataclass `MenuRow` con lista de acciones y método add_action()
- Crear dataclass `MenuDefinition` con:
  - menu_id (str)
  - title (str)
  - rows (list[MenuRow])
  - back_button (Optional[str])
  - parent_menu (Optional[str])
  - método to_keyboard(context) -> InlineKeyboardMarkup

**Archivo:** `app/manager_bot/menus/registry.py`
- Crear clase `MenuRegistry` con:
  - register(menu: MenuDefinition)
  - get(menu_id: str) -> Optional[MenuDefinition]
  - list_menus() -> list[str]

#### 1.3 Implementar KeyboardBuilder
**Archivo:** `app/manager_bot/transport/telegram/keyboard_builder.py`
- Clase KeyboardBuilder con métodos fluidos:
  - create() -> KeyboardBuilder
  - add_button(text, callback_data, emoji) -> KeyboardBuilder
  - add_toggle(label, current_value, callback_prefix) -> KeyboardBuilder
  - add_row(*buttons) -> KeyboardBuilder
  - add_back(menu_id, label) -> KeyboardBuilder
  - add_home(label) -> KeyboardBuilder
  - build() -> InlineKeyboardMarkup
  - build_pagination(items, page, per_page, callback_prefix) -> KeyboardBuilder

#### 1.4 Implementar CallbackRouter
**Archivo:** `app/manager_bot/transport/telegram/callback_router.py`
- Definir estructura de callback_data: `{module}:{action}:{subaction}:{value}`
- Crear clase CallbackRouter con:
  - register(pattern, handler, description)
  - register_prefix(prefix, handler)
  - set_fallback(handler)
  - async handle(callback, bot) -> Any
  - _answer_callback(callback, text)

#### 1.5 Implementar NavigationManager
**Archivo:** `app/manager_bot/menus/navigation.py`
- Crear dataclass NavigationContext:
  - user_id, chat_id, current_menu
  - menu_stack (list[str])
  - metadata (dict)
  - last_update (datetime)
- Crear clase NavigationManager:
  - push_menu(user_id, menu_id, chat_id)
  - pop_menu(user_id) -> Optional[str]
  - go_home(user_id) -> str
  - get_current(user_id) -> Optional[str]

#### 1.6 Implementar GroupConfig
**Archivo:** `app/manager_bot/config/group_config.py`
- Crear dataclass GroupConfig con todos los campos:
  - chat_id, tenant_id
  - Moderación: antiflood_enabled, antiflood_limit, antichannel_enabled, antilink_enabled
  - Antispam: antispam_enabled, spamwatch_enabled, sibyl_enabled
  - Captcha: captcha_enabled, captcha_timeout
  - Welcome/Goodbye: welcome_enabled, welcome_text, welcome_media, goodbye_enabled, goodbye_text
  - Bloqueos: blocked_words, filters
  - Modo nocturno: nightmode_enabled, nightmode_start, nightmode_end
  - Advertencias: max_warnings, auto_ban_on_max
- Métodos: to_dict(), from_dict()

#### 1.7 Implementar ConfigStorage
**Archivo:** `app/manager_bot/config/storage.py`
- Interfaz abstracta ConfigStorage:
  - async get(chat_id) -> Optional[GroupConfig]
  - async set(config: GroupConfig)
  - async delete(chat_id)
  - async list_groups() -> list[int]
- PostgresConfigStorage: implementación con SQLAlchemy
- RedisConfigStorage: implementación con Redis para caché
- Factory: get_config_storage() -> ConfigStorage

#### 1.8 Implementar MenuEngine
**Archivo:** `app/manager_bot/transport/telegram/menu_engine.py`
- Clase MenuEngine:
  - __init__(menu_registry, callback_router, navigation_manager, config_storage)
  - async show_menu(update, context, menu_id, edit=True)
  - async handle_callback(update, context)
  - async _handle_navigation(callback, context, data)
  - async show_menu_by_callback(callback, context, menu_id)

#### 1.9 Implementar FeatureModule Base
**Archivo:** `app/manager_bot/features/base.py`
- Clase abstracta FeatureModule:
  - MENU_ID: str
  - abstract methods: register_callbacks(router), get_config(chat_id)

### Entregables Fase 1
- [ ] Infraestructura base de menús funcionando
- [ ] Unit tests para cada componente
- [ ] Documentación de API interna

---

## FASE 2: Menús Base (Semana 2)

### Objetivo
Crear los menús principales y realizar la integración básica.

### Tareas

#### 2.1 Crear menú principal /config
**Archivo:** `app/manager_bot/menus/main_menu.py`
- Función create_main_menu() -> MenuDefinition
- Estructura:
  ```
  ⚙️ Configuración del Grupo
  ├── 🛡️ Moderación
  ├── 🚫 Antispam | 🔤 Filtros
  ├── 👋 Bienvenida | 👋 Despedida
  ├── 🔐 Captcha | 📊 Reportes
  └── ℹ️ Información
  ```
- Registrar en MenuRegistry

#### 2.2 Crear menú de moderación
**Archivo:** `app/manager_bot/menus/moderation_menu.py`
- Función create_moderation_menu() -> MenuDefinition
- Estructura:
  ```
  🛡️ Configuración de Moderación
  ├── 🌊 Anti-Flood
  ├── 📢 Anti-Canal | 🔗 Anti-Enlaces
  ├── 📸 Moderación Media
  ├── 🔇 Palabras Bloqueadas
  └── 🌙 Modo Nocturno
  ```

#### 2.3 Crear menú de antispam
**Archivo:** `app/manager_bot/menus/antispam_menu.py`
- Función create_antispam_menu() -> MenuDefinition
- Estructura:
  ```
  🚫 Configuración Antispam
  ├── ✅ Antispam General (toggle)
  ├── 🔍 SpamWatch (toggle)
  ├── 🛡️ Sibyl (toggle)
  └── 📊 Sensibilidad: Medium/High/Low
  ```

#### 2.4 Crear menú de filtros
**Archivo:** `app/manager_bot/menus/filters_menu.py`
- Función create_filters_menu() -> MenuDefinition
- Estructura:
  ```
  🔤 Gestión de Filtros
  ├── ➕ Agregar Filtro
  ├── 📋 Lista de Filtros
  ├── 🔇 Palabras Bloqueadas
  └── 🖼️ Sticker Blacklist
  ```

#### 2.5 Crear menú de bienvenida
**Archivo:** `app/manager_bot/menus/welcome_menu.py`
- Función create_welcome_menu() -> MenuDefinition
- Estructura:
  ```
  👋 Configuración de Bienvenida
  ├── ✅ Bienvenida (toggle)
  ├── 📝 Texto de Bienvenida
  ├── 🖼️ Media (Foto/Video)
  └── 👋 Despedida (toggle)
  ```

#### 2.6 Integrar comando /config
**Modificar:** `app/manager_bot/application/enterprise/__init__.py`
- Agregar handler para /config
- Integrar MenuEngine en EnterpriseModule
- Conectar con callback handlers existentes

#### 2.7 Actualizar webhook handlers
**Modificar:** `app/webhook/handlers.py`
- Agregar handling de callback_query
- Integrar MenuEngine.handle_callback()

#### 2.8 Crear módulo de registration
**Archivo:** `app/manager_bot/menus/__init__.py`
- Función register_all_menus(registry)
- Importar y registrar todos los menús

### Entregables Fase 2
- [ ] Menú /config funcional con navegación
- [ ] Todos los submenús visibles
- [ ] Integración con EnterpriseModule
- [ ] Pruebas end-to-end del flujo completo

---

## FASE 3: Features Iniciales (Semana 3)

### Objetivo
Implementar la lógica de negocio para las features principales con sus menús.

### Tareas

#### 3.1 Antispam con menús
**Carpeta:** `app/manager_bot/features/antispam/`
- [ ] `__init__.py` - Exportar AntispamFeature
- [ ] `service.py`:
  - Dataclass AntispamConfig
  - Clase AntispamFeature con:
    - toggle(chat_id, enabled, actor_id)
    - toggle_spamwatch(chat_id, enabled, actor_id)
    - toggle_sibyl(chat_id, enabled, actor_id)
    - set_sensitivity(chat_id, level)
    - register_callbacks(router)
- [ ] `menu.py`:
  - create_antispam_menu(config) -> MenuDefinition
  - Integrar estados actuales en el menú

**Callbacks a implementar:**
- `antispam:toggle:on|off`
- `antispam:spamwatch:toggle:on|off`
- `antispam:sibyl:toggle:on|off`
- `antispam:sensitivity:low|medium|high`

#### 3.2 Filtros con menús
**Carpeta:** `app/manager_bot/features/filters/`
- [ ] `__init__.py` - Exportar FiltersFeature
- [ ] `service.py`:
  - Clase FiltersFeature con:
    - add_filter(chat_id, pattern, response)
    - remove_filter(chat_id, pattern)
    - list_filters(chat_id) -> list
    - add_blocked_word(chat_id, word)
    - remove_blocked_word(chat_id, word)
    - add_sticker(chat_id, file_id)
    - remove_sticker(chat_id, file_id)
    - register_callbacks(router)
- [ ] `menu.py`:
  - create_filters_menu(config) -> MenuDefinition

**Callbacks a implementar:**
- `filters:add:pattern`
- `filters:del:pattern`
- `filters:list`
- `filters:words:add`
- `filters:words:del`
- `filters:sticker:add`
- `filters:sticker:del`

#### 3.3 Bienvenida con menús
**Carpeta:** `app/manager_bot/features/welcome/`
- [ ] `__init__.py` - Exportar WelcomeFeature
- [ ] `service.py`:
  - Clase WelcomeFeature con:
    - toggle_welcome(chat_id, enabled)
    - set_welcome_text(chat_id, text)
    - set_welcome_media(chat_id, file_id, type)
    - toggle_goodbye(chat_id, enabled)
    - set_goodbye_text(chat_id, text)
    - get_welcome(chat_id) -> WelcomeConfig
    - register_callbacks(router)
- [ ] `menu.py`:
  - create_welcome_menu(config) -> MenuDefinition
  - create_goodbye_menu(config) -> MenuDefinition

**Callbacks a implementar:**
- `welcome:toggle:on|off`
- `welcome:edit:text`
- `welcome:edit:media`
- `goodbye:toggle:on|off`
- `goodbye:edit:text`

#### 3.4 Anti-Flood con menús
**Carpeta:** `app/manager_bot/features/antiflood/`
- [ ] `__init__.py`
- [ ] `service.py`:
  - Clase AntiFloodFeature con:
    - toggle(chat_id, enabled)
    - set_limit(chat_id, limit)
    - set_interval(chat_id, seconds)
    - register_callbacks(router)
- [ ] `menu.py`:
  - create_antiflood_menu(config) -> MenuDefinition

**Callbacks a implementar:**
- `antiflood:toggle:on|off`
- `antiflood:limit:5|10|15|20`
- `antiflood:interval:3|5|10`

#### 3.5 Anti-Canal con menús
**Carpeta:** `app/manager_bot/features/antichannel/`
- [ ] `__init__.py`
- [ ] `service.py`:
  - Clase AntiChannelFeature con:
    - toggle(chat_id, enabled)
    - register_callbacks(router)
- [ ] `menu.py`:
  - create_antichannel_menu(config) -> MenuDefinition

**Callbacks a implementar:**
- `antichannel:toggle:on|off`

### Entregables Fase 3
- [ ] Menú de antispam completamente funcional
- [ ] Menú de filtros con CRUD completo
- [ ] Menú de bienvenida/despedida
- [ ] Anti-flood y anti-canal operativos
- [ ] Persistencia de configuración en DB

---

## FASE 4: Features Avanzados (Semana 4)

### Objetivo
Implementar funcionalidades avanzadas de moderación.

### Tareas

#### 4.1 Captcha
**Carpeta:** `app/manager_bot/features/captcha/`
- [ ] `__init__.py`
- [ ] `service.py`:
  - Tipos de captcha: button, math, emoji
  - Clase CaptchaFeature:
    - toggle(chat_id, enabled)
    - set_type(chat_id, type)
    - set_timeout(chat_id, seconds)
    - generate_captcha() -> CaptchaChallenge
    - verify_captcha(user_id, answer) -> bool
    - register_callbacks(router)
- [ ] `menu.py`:
  - create_captcha_menu(config) -> MenuDefinition

**Callbacks a implementar:**
- `captcha:toggle:on|off`
- `captcha:type:button|math|emoji`
- `captcha:timeout:60|120|300|600`
- `captcha:verify:{challenge_id}:{answer}`

#### 4.2 Sistema de Advertencias
**Carpeta:** `app/manager_bot/features/warnings/`
- [ ] `__init__.py`
- [ ] `service.py`:
  - Clase WarningsFeature:
    - add_warning(chat_id, user_id, reason, actor_id)
    - remove_warning(chat_id, user_id, warning_id)
    - list_warnings(chat_id, user_id) -> list
    - get_warn_count(chat_id, user_id) -> int
    - set_max_warnings(chat_id, max)
    - set_auto_ban(chat_id, enabled)
    - register_callbacks(router)
- [ ] `menu.py`:
  - create_warnings_menu(config) -> MenuDefinition

**Callbacks a implementar:**
- `warnings:add:{user_id}`
- `warnings:remove:{user_id}:{warning_id}`
- `warnings:list:{user_id}`
- `warnings:max:1|2|3|4|5`
- `warnings:autoban:on|off`

#### 4.3 Sistema de Reportes
**Carpeta:** `app/manager_bot/features/reports/`
- [ ] `__init__.py`
- [ ] `service.py`:
  - Clase ReportsFeature:
    - create_report(chat_id, reporter_id, reported_id, reason, message_id)
    - get_reports(chat_id, status) -> list
    - resolve_report(report_id, action)
    - get_stats(chat_id) -> ReportStats
    - register_callbacks(router)
- [ ] `menu.py`:
  - create_reports_menu(config) -> MenuDefinition
  - create_report_detail_menu(report_id) -> MenuDefinition

**Callbacks a implementar:**
- `reports:list:open|resolved|all`
- `reports:view:{report_id}`
- `reports:resolve:{report_id}:ban|warn|ignore`
- `reports:stats`

#### 4.4 Modo Nocturno
**Carpeta:** `app/manager_bot/features/nightmode/`
- [ ] `__init__.py`
- [ ] `service.py`:
  - Clase NightModeFeature:
    - toggle(chat_id, enabled)
    - set_schedule(chat_id, start_time, end_time)
    - set_actions(chat_id, actions) # mute, hide, etc.
    - is_active(chat_id) -> bool
    - apply_nightmode(chat_id)
    - remove_nightmode(chat_id)
    - register_callbacks(router)
- [ ] `menu.py`:
  - create_nightmode_menu(config) -> MenuDefinition

**Callbacks a implementar:**
- `nightmode:toggle:on|off`
- `nightmode:start:{time}`
- `nightmode:end:{time}`
- `nightmode:action:mute|hide|kick`

#### 4.5 Anti-Enlaces
**Carpeta:** `app/manager_bot/features/antilink/`
- [ ] `__init__.py`
- [ ] `service.py`:
  - Clase AntiLinkFeature:
    - toggle(chat_id, enabled)
    - set_whitelist(chat_id, domains)
    - register_callbacks(router)
- [ ] `menu.py`:
  - create_antilink_menu(config) -> MenuDefinition

**Callbacks a implementar:**
- `antilink:toggle:on|off`
- `antilink:whitelist:add:{domain}`
- `antilink:whitelist:remove:{domain}`

#### 4.6 Moderación de Multimedia
**Carpeta:** `app/manager_bot/features/media/`
- [ ] `__init__.py`
- [ ] `service.py`:
  - Clase MediaFeature:
    - toggle(chat_id, media_type, enabled)
    - allowed_types: photo, video, document, sticker
    - register_callbacks(router)
- [ ] `menu.py`:
  - create_media_menu(config) -> MenuDefinition

**Callbacks a implementar:**
- `media:photo:on|off`
- `media:video:on|off`
- `media:document:on|off`
- `media:sticker:on|off`

### Entregables Fase 4
- [ ] Sistema de captcha operativo
- [ ] Gestión completa de advertencias
- [ ] Sistema de reportes funcionales
- [ ] Modo nocturno con programación
- [ ] Control de enlaces y multimedia

---

## FASE 5: Optimización (Semana 5)

### Objetivo
Mejorar rendimiento, UX y estabilidad del sistema.

### Tareas

#### 5.1 Caché con Redis
**Objetivo:** Reducir latencia en lecturas frecuentes
- [ ] Implementar RedisConfigStorage completo
- [ ] Agregar caché para:
  - GroupConfig (TTL: 1 hora)
  - Menú definitions (TTL: 24 horas)
  - User permissions (TTL: 5 minutos)
- [ ] Implementar cache invalidation en updates
- [ ] Agregar métricas de cache hit rate

#### 5.2 Paginación
**Objetivo:** Manejar grandes listas de elementos
- [ ] Implementar paginación en:
  - Lista de filtros (10 por página)
  - Lista de advertencias (10 por página)
  - Lista de reportes (10 por página)
  - Lista de usuarios (20 por página)
- [ ] Agregar controles de navegación:
  - ◀️ ▶️ para páginas
  - Indicador "Página X de Y"
  - Botones de acceso directo (1-5)

#### 5.3 Tests de Integración
**Objetivo:** Garantizar estabilidad
- [ ] Crear tests end-to-end:
  - [ ] Flujo completo /config → navegación → toggle → guardado
  - [ ] Flujo de filtros: agregar → listar → eliminar
  - [ ] Flujo de advertencias: warn → listar → remove
  - [ ] Flujo de reportes: crear → resolver
  - [ ] Paginación en todas las listas
- [ ] Tests de carga:
  - [ ] 100 grupos simulados
  - [ ] 50 usuarios concurrentes
  - [ ] 1000 callbacks/hora

#### 5.4 Manejo de Errores
**Objetivo:** Robustez ante fallos
- [ ] Agregar try-catch en todos los handlers
- [ ] Mensajes de error amigables
- [ ] Logging estructurado
- [ ] Retry logic para DB/Redis

#### 5.5 UX Improvements
**Objetivo:** Mejorar experiencia de usuario
- [ ] Estados de carga (⏳ Processing...)
- [ ] Confirmaciones visuales (✅ Guardado)
- [ ] Animaciones de transición entre menús
- [ ] Tooltips en botones largos

#### 5.6 Seguridad
**Objetivo:** Proteger el sistema
- [ ] Rate limiting en callbacks
- [ ] Validación de permisos antes de acciones
- [ ] Sanitización de inputs
- [ ] Protección contra callback injection

### Entregables Fase 5
- [ ] Sistema con caché funcionando
- [ ] Paginación en todas las listas
- [ ] Suite de tests completa
- [ ] Documentación técnica
- [ ] Guía de usuario

---

## Checklist Final de Implementación

### Core (Fase 1)
- [ ] MenuDefinition y MenuRegistry
- [ ] KeyboardBuilder
- [ ] CallbackRouter
- [ ] NavigationManager
- [ ] GroupConfig
- [ ] ConfigStorage
- [ ] MenuEngine

### Menús Base (Fase 2)
- [ ] Menú principal /config
- [ ] Menú moderación
- [ ] Menú antispam
- [ ] Menú filtros
- [ ] Menú bienvenida
- [ ] Integración webhook

### Features (Fase 3-4)
- [ ] Antispam
- [ ] Filtros
- [ ] Bienvenida/Despedida
- [ ] Anti-Flood
- [ ] Anti-Canal
- [ ] Captcha
- [ ] Advertencias
- [ ] Reportes
- [ ] Modo Nocturno
- [ ] Anti-Enlaces
- [ ] Moderación Media

### Optimización (Fase 5)
- [ ] Redis caché
- [ ] Paginación
- [ ] Tests
- [ ] Manejo errores
- [ ] Seguridad

---

## Dependencias Externas

```
python-telegram-bot==22.6
redis==7.2.1
SQLAlchemy==2.0.47
pydantic==2.12.5
```

---

## Métricas de Éxito

| Métrica | Objetivo |
|---------|----------|
| Latencia menu render | < 100ms |
| Cache hit rate | > 90% |
| Uptime | 99.9% |
| Tests coverage | > 80% |
| Tiempo respuesta callback | < 200ms |

---

## Riesgos y Mitigaciones

| Riesgo | Impacto | Mitigación |
|--------|---------|-------------|
| Complejidad excesiva | Alto | Dividir en fases pequenas |
| Migración de datos | Medio | Scripts de migración automatizados |
| Breaking changes | Alto | Versionado de API interna |
| Performance con muchos grupos | Medio | Caché aggressive + Redis |
| Callback storms | Alto | Rate limiting + debounce |

---

*Documento generado para implementación del Plan de Migración Manager Bot*
*Versión: 1.0*
*Fecha: 2026-03-12*