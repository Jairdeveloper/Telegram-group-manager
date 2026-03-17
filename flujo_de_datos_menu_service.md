# Flujo de Datos del Sistema de Menús (/config)

## Resumen Ejecutivo

Este documento describe el flujo de datos desde que el usuario ejecuta el comando `/config` hasta que el bot responde con el menú interactivo.

---

## Flujo Principal: Comando `/config` → Menú

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. USUARIO ENVÍA /config                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. WEBHOOK RECIBE UPDATE                                                   │
│    app/webhook/handlers.py:handle_update()                                 │
│    - Extrae: update_id, chat_id, user_id, text                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 3. TELEGRAM ROUTER CLASIFICA EL UPDATE                                      │
│    app/manager_bot/_transport/telegram/router.py:TelegramRouter           │
│    - route_update() → RouterDispatchResult                                 │
│    - Clasifica como: kind="enterprise_command"                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 4. ENTERPRISE MODULE PROCESA EL COMANDO                                    │
│    app/manager_bot/_application/enterprise/__init__.py                    │
│    - EnterpriseModule._config_handler()                                    │
│    - Retorna: {"status": "menu", "menu_id": "main"}                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 5. WEBHOOK VERIFICA STATUS="menu"                                          │
│    app/webhook/handlers.py:204-219                                        │
│    - if result.get("status") == "menu":                                    │
│    - Obtiene menu_engine via get_menu_engine()                            │
│    - Llama menu_engine.send_menu_message()                                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 6. MENU ENGINE OBTIENE EL MENÚ                                            │
│    app/manager_bot/_transport/telegram/menu_engine.py                     │
│    - MenuEngine.send_menu_message(chat_id, bot, menu_id="main")           │
│    - registry.get("main") → MenuDefinition                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 7. MENU ENGINE OBTIENE LA CONFIGURACIÓN DEL GRUPO                         │
│    - config_storage.get(chat_id) → GroupConfig                            │
│    - GroupConfig contiene todos los settings del grupo                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 8. MENU ENGINE CONVIERTE MENU A KEYBOARD                                   │
│    - menu.to_keyboard(context={"config": GroupConfig})                   │
│    - Genera InlineKeyboardMarkup con los botones                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 9. TELEGRAM CLIENT ENVÍA EL MENSAJE                                        │
│    - telegram_client.send_message(chat_id, text, reply_markup)           │
│    - Bot responde con el menú interactivo                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Componentes del Flujo

### 1. Recepción del Update (Webhook)

**Archivo**: `app/webhook/handlers.py`

```python
async def handle_update(update: Dict[str, Any]):
    dispatch = router.route_update(update)
    # dispatch.kind = "enterprise_command"
    # dispatch.command = "/config"
    # dispatch.chat_id = <chat_id>
```

### 2. Clasificación del Router

**Archivo**: `app/manager_bot/_transport/telegram/router.py`

```python
class TelegramRouter:
    def route_update(self, update: Dict) -> RouterDispatchResult:
        # Extrae chat_id, text, user_id del update
        # Clasifica como "enterprise_command" si es /config
        return RouterDispatchResult(
            kind="enterprise_command",
            command="/config",
            chat_id=chat_id,
            user_id=user_id
        )
```

### 3. Procesamiento del Enterprise Module

**Archivo**: `app/manager_bot/_application/enterprise/__init__.py`

```python
class EnterpriseModule:
    def _config_handler(self, chat_id, args, user_id, raw_text, raw_update):
        # Retorna señal para mostrar menú
        return {
            "status": "menu",
            "menu_id": "main"
        }
```

### 4. Manejo del Status "menu" en Webhook

**Archivo**: `app/webhook/handlers.py:202-219`

```python
if result.get("status") == "menu":
    menu_engine = get_menu_engine()  # Obtiene instancia global
    menu_id = result.get("menu_id", "main")
    await menu_engine.send_menu_message(
        chat_id=chat_id,
        bot=telegram_client,
        menu_id=menu_id,
    )
```

### 5. Menu Engine - Obtención del Menú

**Archivo**: `app/manager_bot/_transport/telegram/menu_engine.py`

```python
class MenuEngine:
    async def send_menu_message(self, chat_id, bot, menu_id, text=None):
        # 1. Obtiene MenuDefinition del registry
        menu = self.registry.get(menu_id)  # "main"
        
        # 2. Obtiene configuración del grupo
        config = await self.config_storage.get(chat_id)
        
        # 3. Convierte a keyboard con contexto
        keyboard = menu.to_keyboard(context={"config": config})
        
        # 4. Envía mensaje
        await bot.send_message(chat_id, text, reply_markup=keyboard)
```

### 6. Menu Registry

**Archivo**: `app/manager_bot/_menus/registry.py`

```python
class MenuRegistry:
    def get(self, menu_id: str) -> Optional[MenuDefinition]:
        return self._menus.get(menu_id)
    
    # Los menús se registran en register_all_menus()
    # Ejemplo: registry.register(create_main_menu())
```

### 7. Config Storage - Obtención de GroupConfig

**Archivo**: `app/manager_bot/_config/storage.py`

```python
class ConfigStorage(ABC):
    async def get(self, chat_id: int) -> GroupConfig:
        # Puede ser InMemory, PostgreSQL o Redis
        # Retorna GroupConfig con todos los settings del grupo
```

**Modelo GroupConfig** (`app/manager_bot/_config/group_config.py`):

```python
@dataclass
class GroupConfig:
    chat_id: int
    tenant_id: str
    antiflood_enabled: bool = False
    antichannel_enabled: bool = False
    antilink_enabled: bool = False
    antispam_enabled: bool = False
    captcha_enabled: bool = False
    welcome_enabled: bool = False
    blocked_words: List[str] = field(default_factory=list)
    nightmode_enabled: bool = False
    # ... más campos
```

### 8. Conversión del Menú a Keyboard

**Archivo**: `app/manager_bot/_menus/base.py`

```python
class MenuDefinition:
    def to_keyboard(self, context: Optional[dict] = None) -> InlineKeyboardMarkup:
        config = context.get("config") if context else None
        
        keyboard = []
        for row in self.rows:
            buttons = []
            for action in row.actions:
                # Los callbacks incluyen estado dinámico:
                # "mod:antiflood:toggle:on" o "mod:antiflood:toggle:off"
                text = action.label  # ej: "✅ Anti-Flood"
                buttons.append(
                    InlineKeyboardButton(text, callback_data=action.callback_data)
                )
            keyboard.append(buttons)
        
        return InlineKeyboardMarkup(keyboard)
```

---

## Menús Disponibles

### Menú Principal (`main`)

**Archivo**: `app/manager_bot/_menus/main_menu.py`

```python
def create_main_menu() -> MenuDefinition:
    menu = MenuDefinition(
        menu_id="main",
        title="⚙️ Configuración del Grupo",
    )
    
    menu.add_row().add_action("mod:show", "🛡️ Moderación", "🛡️")
    menu.add_row() \
        .add_action("antispam:show", "🚫 Antispam", "🚫") \
        .add_action("filters:show", "🔤 Filtros", "🔤")
    menu.add_row() \
        .add_action("welcome:show", "👋 Bienvenida", "👋") \
        .add_action("goodbye:show", "👋 Despedida", "👋")
    menu.add_row() \
        .add_action("captcha:show", "🔐 Captcha", "🔐") \
        .add_action("reports:show", "📊 Reportes", "📊")
    menu.add_row().add_action("info:show", "ℹ️ Información", "ℹ️")
    
    return menu
```

### Otros Menús Registrados

| Menú ID | Archivo | Descripción |
|---------|---------|-------------|
| `main` | main_menu.py | Menú principal de configuración |
| `info` | main_menu.py | Información del grupo |
| `mod` | moderation_menu.py | Configuración de moderación |
| `mod:antichannel` | moderation_menu.py | Anti-Canal |
| `mod:antilink` | moderation_menu.py | Anti-Enlaces |
| `mod:media` | moderation_menu.py | Moderación multimedia |
| `mod:words` | moderation_menu.py | Palabras bloqueadas |
| `mod:nightmode` | moderation_menu.py | Modo nocturno |
| `antispam` | antispam_menu.py | Configuración antispam |
| `filters` | filters_menu.py | Filtros de contenido |
| `welcome` | welcome_menu.py | Mensaje de bienvenida |
| `goodbye` | welcome_menu.py | Mensaje de despedida |
| `captcha` | captcha_menu.py | Configuración de captcha |
| `reports` | reports_menu.py | Reportes y estadísticas |

---

## Flujo de Navegación (Callback Queries)

Cuando el usuario hace clic en un botón del menú:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. USUARIO HACE CLIC EN BOTÓN                                              │
│    - callback_data: "mod:show", "antispam:show", etc.                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. TELEGRAM ENVÍA CALLBACK_QUERY                                           │
│    - app/webhook/handlers.py:handle_callback_query()                       │
│    - O python-telegram-bot: MenuEngine.handle_callback()                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 3. CALLBACK ROUTER PROCESA EL callback_data                                │
│    app/manager_bot/_transport/telegram/callback_router.py                 │
│    - Busca handler registrado para el patrón                               │
│    - patterns registrados en MenuEngine._setup_navigation_callbacks()    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 4. SE EJECUTA EL HANDLER                                                   │
│    - handle_menu_show() para "X:show"                                     │
│    - handle_back() para "nav:back:X"                                      │
│    - Feature callbacks para toggles y acciones                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 5. MENU ENGINE MUESTRA EL NUEVO MENÚ                                       │
│    - show_menu_by_callback(callback, bot, menu_id)                        │
│    - registry.get(menu_id) → MenuDefinition                               │
│    - config_storage.get(chat_id) → GroupConfig                           │
│    - menu.to_keyboard() → InlineKeyboardMarkup                           │
│    - callback.edit_message_text()                                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Registro de Callbacks en MenuEngine

**Archivo**: `app/manager_bot/_transport/telegram/menu_engine.py:46-108`

```python
def _setup_navigation_callbacks(self):
    # Callbacks de navegación
    self.callback_router.register_exact("nav:back:main", handle_back)
    self.callback_router.register_exact("nav:home", handle_home)
    
    # Callbacks de mostrar menús
    self.callback_router.register_exact("mod:show", handle_menu_show)
    self.callback_router.register_exact("antispam:show", handle_menu_show)
    self.callback_router.register_exact("filters:show", handle_menu_show)
    # ... etc
    
    # Prefix para features
    self.callback_router.register_prefix("mod:", feature_handler)
```

### Handlers de Navegación

```python
async def handle_menu_show(callback, bot, data):
    """Muestra un menú basado en callback_data"""
    parts = data.split(":")  # ["antispam", "show"]
    menu_id = parts[0]  # "antispam"
    await self.show_menu_by_callback(callback, bot, menu_id)

async def handle_back(callback, bot, data):
    """Navega al menú anterior"""
    parts = data.split(":")  # ["nav", "back", "main"]
    target_menu = parts[2] if len(parts) >= 3 else "main"
    self.navigation.pop_menu(user_id)
    await self.show_menu_by_callback(callback, bot, target_menu)
```

---

## Inicialización del Sistema de Menús

El sistema se inicializa en `app/manager_bot/_menu_service.py`:

```python
def create_menu_engine(storage_type=None, database_url=None, redis_url=None):
    # 1. Crea MenuRegistry
    registry = MenuRegistry()
    
    # 2. Registra todos los menús
    register_all_menus(registry)
    
    # 3. Crea CallbackRouter
    callback_router = CallbackRouter()
    
    # 4. Crea NavigationManager
    navigation_manager = NavigationManager()
    
    # 5. Crea ConfigStorage
    config_storage = get_config_storage(storage_type, database_url, redis_url)
    
    # 6. Crea MenuEngine
    menu_engine = MenuEngine(
        menu_registry=registry,
        callback_router=callback_router,
        navigation_manager=navigation_manager,
        config_storage=config_storage,
    )
    
    # 7. Registra features (Antispam, Filters, Welcome, etc.)
    _register_features(callback_router, config_storage)
    
    # 8. Establece instancia global
    set_menu_engine(menu_engine)
    
    return menu_engine, rate_limiter
```

---

## Resumen de Clases y Métodos Clave

| Clase | Archivo | Método | Descripción |
|-------|---------|--------|-------------|
| TelegramRouter | router.py | route_update() | Clasifica el update |
| EnterpriseModule | enterprise/__init__.py | _config_handler() | Retorna status="menu" |
| MenuEngine | menu_engine.py | send_menu_message() | Envía menú al usuario |
| MenuEngine | menu_engine.py | show_menu_by_callback() | Muestra menú desde callback |
| MenuEngine | menu_engine.py | handle_callback() | Procesa callback queries |
| MenuRegistry | registry.py | get() | Obtiene MenuDefinition |
| CallbackRouter | callback_router.py | handle() | Dispatacha callbacks |
| NavigationManager | navigation.py | push_menu() | Gestiona stack de navegación |
| ConfigStorage | storage.py | get() | Obtiene GroupConfig |
| MenuDefinition | base.py | to_keyboard() | Convierte a InlineKeyboardMarkup |
| GroupConfig | group_config.py | - | Modelo de configuración |

---

## Ejemplo Completo: Mostrar Menú de Moderación

```
1. Usuario hace clic en botón "🛡️ Moderación"
   → callback_data = "mod:show"

2. Telegram envía CallbackQuery al webhook
   → handle_callback_query(callback_data, chat_id, user_id, message_id)

3. MenuEngine.handle_callback_query_raw()
   → callback_router.handle(callback, bot)

4. CallbackRouter.find_handler("mod:show")
   → Encuentra handler registrado: handle_menu_show

5. handle_menu_show(callback, bot, "mod:show")
   → menu_id = "mod"

6. MenuEngine.show_menu_by_callback()
   → menu = registry.get("mod")
   → config = await config_storage.get(chat_id)
   → keyboard = menu.to_keyboard(context={"config": config})

7. Telegram API
   → callback.edit_message_text(text, reply_markup=keyboard)

8. NavigationManager.push_menu(user_id, "mod", chat_id)
   → Guarda historial de navegación
```
