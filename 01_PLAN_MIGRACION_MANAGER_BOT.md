# Plan de Migración - Manager Bot

## Estado Actual del Proyecto

El proyecto cuenta con una arquitectura modular que incluye:
- ManagerBot como núcleo con registry de módulos
- Módulos: OpsModule, EnterpriseModule, AgentModule
- Sistema de routing para comandos Telegram
- Repositorios para persistencia de configuración
- Servicios de moderación y contenido

**Limitación actual**: Todo funciona mediante comandos de texto, sin menús interactivos.

---

## Arquitectura Propuesta

```
Bot Core
│
├── Command Router      → Maneja /comandos
├── Menu Engine         → Gestiona menú principal /config
├── Keyboard Builder    → Construye InlineKeyboards dinámicos
├── Callback Router     → Procesa callback_data
├── Feature Modules    → Módulos de funcionalidades
│   ├── Antispam Module
│   ├── Warnings Module
│   ├── Filters Module
│   ├── Welcome Module
│   ├── Captcha Module
│   └── Reports Module
└── Database Layer      → Persistencia de configuración
```

---

## 1. Estructura de Carpetas Propuesta

```
app/manager_bot/
├── __init__.py
├── core.py                           # ManagerBot base (existente)
├── registry.py                       # ModuleRegistry (existente)
│
├── transport/
│   └── telegram/
│       ├── router.py                 # Routing existente
│       ├── menu_engine.py            # NUEVO: Motor de menús
│       ├── callback_router.py        # NUEVO: Router de callbacks
│       └── keyboard_builder.py       # NUEVO: Constructor de keyboards
│
├── menus/                            # NUEVO: Definiciones de menús
│   ├── __init__.py
│   ├── base.py                       # Clase base MenuDefinition
│   ├── main_menu.py                  # Menú principal /config
│   ├── moderation_menu.py           # Menú de moderación
│   ├── antispam_menu.py              # Menú antispam
│   ├── filters_menu.py               # Menú de filtros
│   ├── welcome_menu.py                # Menú de bienvenida
│   ├── warnings_menu.py               # Menú de advertencias
│   └── navigation.py                 # Utilidades de navegación
│
├── features/                         # NUEVO: Módulos de funcionalidades
│   ├── __init__.py
│   ├── base.py                       # FeatureModule base
│   ├── antispam/
│   │   ├── __init__.py
│   │   ├── service.py               # Lógica de antispam
│   │   └── menu.py                   # Menú específico
│   ├── warnings/
│   │   ├── __init__.py
│   │   ├── service.py
│   │   └── menu.py
│   ├── filters/
│   │   ├── __init__.py
│   │   ├── service.py
│   │   └── menu.py
│   ├── welcome/
│   │   ├── __init__.py
│   │   ├── service.py
│   │   └── menu.py
│   ├── captcha/
│   │   ├── __init__.py
│   │   ├── service.py
│   │   └── menu.py
│   ├── reports/
│   │   ├── __init__.py
│   │   ├── service.py
│   │   └── menu.py
│   └── antiflood/
│       ├── __init__.py
│       ├── service.py
│       └── menu.py
│
├── config/                           # NUEVO: Almacenamiento de config
│   ├── __init__.py
│   ├── storage.py                    # ConfigStorage abstraction
│   └── group_config.py               # Modelo de configuración
│
└── permissions/                      # NUEVO: Sistema de permisos
    ├── __init__.py
    ├── checker.py                    # PermissionChecker
    └── decorators.py                 # @require_admin, etc.
```

---

## 2. Sistema de Gestión de Menús

### 2.1 Clase Base MenuDefinition

```python
# app/manager_bot/menus/base.py
from dataclasses import dataclass, field
from typing import Callable, Optional
from enum import Enum

@dataclass
class MenuAction:
    """Representa una acción dentro de un menú."""
    callback_data: str
    label: str
    emoji: Optional[str] = None
    
@dataclass 
class MenuRow:
    """Una fila de botones."""
    actions: list[MenuAction] = field(default_factory=list)
    
    def add_action(self, callback_data: str, label: str, emoji: str = None):
        self.actions.append(MenuAction(callback_data, label, emoji))
        return self

@dataclass
class MenuDefinition:
    """Define un menú completo."""
    menu_id: str                          # Identificador único
    title: str                             # Título del menú
    rows: list[MenuRow] = field(default_factory=list)
    back_button: Optional[str] = None      # Callback para volver
    parent_menu: Optional[str] = None      # Menú padre
    
    def add_row(self) -> MenuRow:
        row = MenuRow()
        self.rows.append(row)
        return row
        
    def to_keyboard(self, context: dict = None) -> list[list[InlineKeyboardButton]]:
        """Convierte a formato InlineKeyboard de python-telegram-bot."""
        from telegram import InlineKeyboardButton
        keyboard = []
        for row in self.rows:
            buttons = []
            for action in row.actions:
                text = f"{action.emoji} {action.label}" if action.emoji else action.label
                buttons.append(InlineKeyboardButton(text, callback_data=action.callback_data))
            if buttons:
                keyboard.append(buttons)
        return keyboard
```

### 2.2 Registro de Menús

```python
# app/manager_bot/menus/registry.py
from typing import Dict, Optional
from .base import MenuDefinition

class MenuRegistry:
    """Registro central de menús."""
    
    def __init__(self):
        self._menus: Dict[str, MenuDefinition] = {}
        
    def register(self, menu: MenuDefinition):
        self._menus[menu.menu_id] = menu
        
    def get(self, menu_id: str) -> Optional[MenuDefinition]:
        return self._menus.get(menu_id)
        
    def list_menus(self) -> list[str]:
        return list(self._menus.keys())
```

---

## 3. Sistema de Callbacks Escalable

### 3.1 Estructura de callback_data

```
Formato: {module}:{action}:{subaction}:{value}
Ejemplos:
  - antispam:toggle:on
  - antispam:spamwatch:toggle:on
  - filters:add:pattern:palabra
  - welcome:edit:text
  - navigation:back:main
```

### 3.2 Callback Router

```python
# app/manager_bot/transport/telegram/callback_router.py
from dataclasses import dataclass
from typing import Callable, Optional, Any
import logging
import re

logger = logging.getLogger(__name__)

@dataclass
class CallbackPattern:
    """Patrón para manejar un callback específico."""
    pattern: str                    # Regex o prefijo
    handler: Callable               # Función que maneja el callback
    description: str               # Para debugging
    
class CallbackRouter:
    """Router escalable para callbacks de InlineKeyboard."""
    
    def __init__(self):
        self._handlers: list[CallbackPattern] = []
        self._fallback: Optional[Callable] = None
        
    def register(self, pattern: str, handler: Callable, description: str = ""):
        """Registra un handler para un patrón de callback."""
        compiled = re.compile(pattern) if "*" in pattern or "^" in pattern else None
        self._handlers.append(CallbackPattern(pattern, handler, description))
        
    def register_prefix(self, prefix: str, handler: Callable):
        """Registra todos los callbacks que empiezan con un prefijo."""
        self.register(f"^{prefix}:", handler, f"Handler for {prefix}")
        
    def set_fallback(self, handler: Callable):
        """Handler para callbacks no reconocidos."""
        self._fallback = handler
        
    async def handle(self, callback: "CallbackQuery", bot: "Bot") -> Any:
        """Procesa un callback query."""
        data = callback.data
        chat_id = callback.message.chat.id if callback.message else None
        user_id = callback.from_user.id
        
        logger.info(f"Callback received: {data} from user {user_id}")
        
        # Buscar handler
        for handler in self._handlers:
            if re.match(handler.pattern, data):
                try:
                    return await handler.handler(callback, bot, data)
                except Exception as e:
                    logger.error(f"Error handling callback {data}: {e}")
                    await self._answer_callback(callback, f"Error: {str(e)}")
                    return
                    
        # Fallback
        if self._fallback:
            return await self._fallback(callback, bot, data)
            
        await self._answer_callback(callback, "Acción no reconocida")
        
    async def _answer_callback(self, callback, text: str):
        """Responde al callback query."""
        try:
            await callback.answer(text, show_alert=True)
        except Exception:
            pass
```

### 3.3 Módulo de Feature con Callbacks

```python
# app/manager_bot/features/antispam/service.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class AntispamConfig:
    chat_id: int
    enabled: bool = False
    spamwatch_enabled: bool = False
    sibyl_enabled: bool = False
    sensitivity: str = "medium"  # low, medium, high
    
class AntispamFeature:
    """Feature module para antispam."""
    
    MENU_ID = "antispam"
    
    def __init__(self, config_storage, moderation_service):
        self.config_storage = config_storage
        self.moderation_service = moderation_service
        
    async def get_config(self, chat_id: int) -> AntispamConfig:
        """Obtiene configuración actual."""
        data = await self.config_storage.get(chat_id, "antispam")
        if data:
            return AntispamConfig(**data)
        return AntispamConfig(chat_id=chat_id)
        
    async def toggle(self, chat_id: int, enabled: bool, actor_id: int) -> AntispamConfig:
        """Activa/desactiva antispam."""
        config = await self.get_config(chat_id)
        config.enabled = enabled
        await self.config_storage.set(chat_id, "antispam", asdict(config))
        return config
        
    def register_callbacks(self, router: CallbackRouter):
        """Registra los callbacks de este módulo."""
        
        async def handle_toggle(callback, bot, data):
            _, _, action, value = data.split(":")
            enabled = value == "on"
            config = await self.toggle(chat_id, enabled, callback.from_user.id)
            await self._answer_callback(callback, f"Antispam {'activado' if enabled else 'desactivado'}")
            
        async def handle_spamwatch(callback, bot, data):
            _, _, _, action, value = data.split(":")
            enabled = value == "on"
            config = await self.get_config(chat_id)
            config.spamwatch_enabled = enabled
            await self.config_storage.set(chat_id, "antispam", asdict(config))
            # Actualizar menú...
            
        router.register_prefix(f"{self.MENU_ID}:toggle", handle_toggle)
        router.register_prefix(f"{self.MENU_ID}:spamwatch", handle_spamwatch)
```

---

## 4. Sistema de Keyboard Builder Dinámico

```python
# app/manager_bot/transport/telegram/keyboard_builder.py
from typing import Any, Callable, Optional
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class KeyboardBuilder:
    """Builder para crear keyboards dinámicamente."""
    
    def __init__(self):
        self._rows: list[list[InlineKeyboardButton]] = []
        
    @staticmethod
    def create() -> "KeyboardBuilder":
        return KeyboardBuilder()
        
    def add_button(self, text: str, callback_data: str, emoji: str = None) -> "KeyboardBuilder":
        """Añade un botón."""
        display_text = f"{emoji} {text}" if emoji else text
        self._rows.append([InlineKeyboardButton(display_text, callback_data=callback_data)])
        return self
        
    def add_toggle(self, label: str, current_value: bool, callback_prefix: str) -> "KeyboardBuilder":
        """Añade un botón toggle conmutativo."""
        emoji = "✅" if current_value else "❌"
        value = "off" if current_value else "on"
        return self.add_button(f"{label}: {value}", f"{callback_prefix}:{value}", emoji)
        
    def add_row(self, *buttons: InlineKeyboardButton) -> "KeyboardBuilder":
        """Añade una fila de botones."""
        self._rows.append(list(buttons))
        return self
        
    def add_back(self, menu_id: str, label: str = "🔙 Volver") -> "KeyboardBuilder":
        """Añade botón de volver."""
        return self.add_button(label, f"nav:back:{menu_id}")
        
    def add_home(self, label: str = "🏠 Menú Principal") -> "KeyboardBuilder":
        """Añade botón de inicio."""
        return self.add_button(label, "nav:home")
        
    def build(self) -> InlineKeyboardMarkup:
        """Construye el keyboard."""
        return InlineKeyboardMarkup(self._rows)
        
    def build_pagination(self, items: list, page: int, per_page: int, callback_prefix: str) -> "KeyboardBuilder":
        """Construye keyboard con paginación."""
        total_pages = (len(items) + per_page - 1) // per_page
        start = page * per_page
        end = start + per_page
        
        # Botones de items
        for item in items[start:end]:
            self.add_button(item["label"], f"{callback_prefix}:view:{item['id']}")
            
        # Botones de navegación
        nav_row = []
        if page > 0:
            nav_row.append(InlineKeyboardButton("◀️", callback_data=f"{callback_prefix}:page:{page-1}"))
        nav_row.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data="nav:noop"))
        if page < total_pages - 1:
            nav_row.append(InlineKeyboardButton("▶️", callback_data=f"{callback_prefix}:page:{page+1}"))
            
        if nav_row:
            self.add_row(*nav_row)
            
        return self
```

---

## 5. Estrategia de Navegación entre Menús

### 5.1 Navigation Manager

```python
# app/manager_bot/menus/navigation.py
from typing import Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class NavigationContext:
    """Contexto de navegación por usuario."""
    user_id: int
    chat_id: int
    current_menu: str
    menu_stack: list[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_update: datetime = field(default_factory=datetime.utcnow)

class NavigationManager:
    """Gestiona navegación entre menús."""
    
    def __init__(self):
        self._contexts: Dict[int, NavigationContext] = {}  # user_id -> context
        
    def push_menu(self, user_id: int, menu_id: str, chat_id: int):
        """Entra a un nuevo menú."""
        ctx = self._contexts.get(user_id)
        if ctx:
            ctx.menu_stack.append(ctx.current_menu)
        else:
            ctx = NavigationContext(user_id=user_id, chat_id=chat_id, current_menu="")
        ctx.current_menu = menu_id
        ctx.last_update = datetime.utcnow()
        self._contexts[user_id] = ctx
        
    def pop_menu(self, user_id: int) -> Optional[str]:
        """Vuelve al menú anterior."""
        ctx = self._contexts.get(user_id)
        if ctx and ctx.menu_stack:
            ctx.current_menu = ctx.menu_stack.pop()
            ctx.last_update = datetime.utcnow()
            return ctx.current_menu
        return None
        
    def go_home(self, user_id: int) -> str:
        """Vuelve al menú principal."""
        ctx = self._contexts.get(user_id)
        if ctx:
            ctx.menu_stack.clear()
            ctx.current_menu = "main"
            ctx.last_update = datetime.utcnow()
        return "main"
        
    def get_current(self, user_id: int) -> Optional[str]:
        """Obtiene menú actual."""
        ctx = self._contexts.get(user_id)
        return ctx.current_menu if ctx else None
```

### 5.2 Menú Principal Ejemplo

```python
# app/manager_bot/menus/main_menu.py
from .base import MenuDefinition, MenuRow
from .registry import MenuRegistry

def create_main_menu() -> MenuDefinition:
    """Crea el menú principal /config."""
    menu = MenuDefinition(
        menu_id="main",
        title="⚙️ Configuración del Grupo",
        back_button="nav:home"
    )
    
    # Fila 1: Moderación
    menu.add_row() \
        .add_action("mod:show", "🛡️ Moderación", "🛡️")
        
    # Fila 2: Antispam y Filtros
    menu.add_row() \
        .add_action("antispam:show", "🚫 Antispam", "🚫") \
        .add_action("filters:show", "🔤 Filtros", "🔤")
        
    # Fila 3: Bienvenida y Despedida
    menu.add_row() \
        .add_action("welcome:show", "👋 Bienvenida", "👋") \
        .add_action("goodbye:show", "👋 Despedida", "👋")
        
    # Fila 4: Extras
    menu.add_row() \
        .add_action("captcha:show", "🔐 Captcha", "🔐") \
        .add_action("reports:show", "📊 Reportes", "📊")
        
    # Fila 5: Información
    menu.add_row() \
        .add_action("info:show", "ℹ️ Información", "ℹ️")
        
    return menu

def create_moderation_menu() -> MenuDefinition:
    """Menú de configuración de moderación."""
    menu = MenuDefinition(
        menu_id="mod",
        title="🛡️ Configuración de Moderación",
        parent_menu="main"
    )
    
    menu.add_row() \
        .add_action("mod:antiflood:toggle", "Anti-Flood", "🌊")
        
    menu.add_row() \
        .add_action("mod:antichannel:toggle", "Anti-Canal", "📢") \
        .add_action("mod:antilink:toggle", "Anti-Enlaces", "🔗")
        
    menu.add_row() \
        .add_action("mod:media:show", "📸 Moderación Media", "📸")
        
    menu.add_row() \
        .add_action("mod:words:show", "🔇 Palabras Bloqueadas", "🔇")
        
    menu.add_row() \
        .add_action("mod:nightmode:show", "🌙 Modo Nocturno", "🌙")
        
    menu.add_back("main")
    
    return menu

# Registrar en el registry
def register_main_menus(registry: MenuRegistry):
    registry.register(create_main_menu())
    registry.register(create_moderation_menu())
```

---

## 6. Estrategia de Persistencia de Configuración

### 6.1 GroupConfig Model

```python
# app/manager_bot/config/group_config.py
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any
from datetime import datetime

@dataclass
class GroupConfig:
    """Configuración completa de un grupo."""
    chat_id: int
    tenant_id: str
    
    # Moderación
    antiflood_enabled: bool = False
    antiflood_limit: int = 5
    antiflood_interval: int = 5
    
    antichannel_enabled: bool = False
    antilink_enabled: bool = False
    
    # Antispam
    antispam_enabled: bool = False
    spamwatch_enabled: bool = False
    sibyl_enabled: bool = False
    
    # Captcha
    captcha_enabled: bool = False
    captcha_timeout: int = 300
    
    # Welcome/Goodbye
    welcome_enabled: bool = False
    welcome_text: str = ""
    welcome_media: Optional[str] = None
    
    goodbye_enabled: bool = False
    goodbye_text: str = ""
    
    # Palabras bloqueadas
    blocked_words: list[str] = field(default_factory=list)
    
    # Filtros
    filters: list[Dict[str, str]] = field(default_factory=list)
    
    # Modo nocturno
    nightmode_enabled: bool = False
    nightmode_start: str = "23:00"
    nightmode_end: str = "07:00"
    
    # Advertencias
    max_warnings: int = 3
    auto_ban_on_max: bool = True
    
    # Actualización
    updated_at: datetime = field(default_factory=datetime.utcnow)
    updated_by: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["updated_at"] = self.updated_at.isoformat()
        return data
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GroupConfig":
        if "updated_at" in data and isinstance(data["updated_at"], str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        return cls(**data)
```

### 6.2 ConfigStorage

```python
# app/manager_bot/config/storage.py
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from .group_config import GroupConfig

class ConfigStorage(ABC):
    """Interfaz para almacenamiento de configuración."""
    
    @abstractmethod
    async def get(self, chat_id: int) -> Optional[GroupConfig]:
        pass
        
    @abstractmethod
    async def set(self, config: GroupConfig):
        pass
        
    @abstractmethod
    async def delete(self, chat_id: int):
        pass
        
    @abstractmethod
    async def list_groups(self) -> list[int]:
        pass

class PostgresConfigStorage(ConfigStorage):
    """Implementación con PostgreSQL."""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        # Inicializar SQLAlchemy...
        
    async def get(self, chat_id: int) -> Optional[GroupConfig]:
        # Query a tabla group_configs
        pass
        
    async def set(self, config: GroupConfig):
        # Upsert en tabla group_configs
        pass
        
    async def delete(self, chat_id: int):
        pass
        
    async def list_groups(self) -> list[int]:
        pass

class RedisConfigStorage(ConfigStorage):
    """Implementación con Redis para caché."""
    
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
        self._ttl = 3600
        
    async def get(self, chat_id: int) -> Optional[GroupConfig]:
        key = f"group_config:{chat_id}"
        data = await self.redis.get(key)
        if data:
            return GroupConfig.from_dict(eval(data))
        return None
        
    async def set(self, config: GroupConfig):
        key = f"group_config:{config.chat_id}"
        await self.redis.set(key, str(config.to_dict()), ex=self._ttl)
        
    async def delete(self, chat_id: int):
        await self.redis.delete(f"group_config:{chat_id}")
        
    async def list_groups(self) -> list[int]:
        # Scan keys...
        pass

# Factory
def get_config_storage() -> ConfigStorage:
    # Leer de settings y devolver implementación apropiada
    pass
```

---

## 7. Sistema de Permisos

```python
# app/manager_bot/permissions/checker.py
from typing import Optional
from enum import Enum
from functools import wraps

class Permission(Enum):
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"
    EVERYONE = "everyone"

class PermissionChecker:
    """Verifica permisos de usuarios en grupos."""
    
    def __init__(self, user_service):
        self.user_service = user_service
        
    async def is_admin(self, chat_id: int, user_id: int) -> bool:
        """Verifica si es admin del grupo."""
        # Usar telegram API o cache local
        pass
        
    async def is_moderator(self, chat_id: int, user_id: int) -> bool:
        """Verifica si es moderador."""
        user = await self.user_service.get_user(chat_id, user_id)
        return user and user.role in (Permission.ADMIN, Permission.MODERATOR)
        
    async def get_user_permission(self, chat_id: int, user_id: int) -> Permission:
        """Obtiene el nivel de permiso del usuario."""
        if await self.is_admin(chat_id, user_id):
            return Permission.ADMIN
        if await self.is_moderator(chat_id, user_id):
            return Permission.MODERATOR
        return Permission.USER

def require_permissions(*permissions: Permission):
    """Decorador para requerir permisos."""
    def decorator(func):
        @wraps(func)
        async def wrapper(callback, bot, data, *args, **kwargs):
            checker = get_permission_checker()
            user_id = callback.from_user.id
            chat_id = callback.message.chat.id if callback.message else None
            
            if not chat_id:
                await callback.answer("Error: Chat no identificado", show_alert=True)
                return
                
            user_perm = await checker.get_user_permission(chat_id, user_id)
            
            for perm in permissions:
                if perm == Permission.ADMIN and user_perm != Permission.ADMIN:
                    await callback.answer("⛔ Requiere permisos de admin", show_alert=True)
                    return
                    
            return await func(callback, bot, data, *args, **kwargs)
        return wrapper
    return decorator
```

---

## 8. Menu Engine - Integración con python-telegram-bot

```python
# app/manager_bot/transport/telegram/menu_engine.py
from typing import Optional, Any
import logging
from telegram import Update, Bot
from telegram.ext import ContextTypes

from app.manager_bot.menus.base import MenuDefinition
from app.manager_bot.menus.registry import MenuRegistry
from app.manager_bot.menus.navigation import NavigationManager
from app.manager_bot.transport.telegram.callback_router import CallbackRouter
from app.manager_bot.config.storage import ConfigStorage

logger = logging.getLogger(__name__)

class MenuEngine:
    """Motor de menús interactivos."""
    
    def __init__(
        self,
        menu_registry: MenuRegistry,
        callback_router: CallbackRouter,
        navigation_manager: NavigationManager,
        config_storage: ConfigStorage,
    ):
        self.registry = menu_registry
        self.callback_router = callback_router
        self.navigation = navigation_manager
        self.config_storage = config_storage
        
    async def show_menu(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        menu_id: str,
        edit: bool = True,
    ) -> Optional[Any]:
        """Muestra un menú al usuario."""
        menu = self.registry.get(menu_id)
        if not menu:
            logger.error(f"Menu not found: {menu_id}")
            return
            
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        
        # Obtener contexto adicional (configuración actual)
        config = await self.config_storage.get(chat_id)
        
        # Construir keyboard con contexto
        keyboard = menu.to_keyboard(context={"config": config})
        
        text = menu.title
        
        if edit and update.callback_query:
            # Editar mensaje existente
            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=keyboard,
            )
        else:
            # Enviar nuevo mensaje
            await context.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=keyboard,
            )
            
        # Actualizar navegación
        self.navigation.push_menu(user_id, menu_id, chat_id)
        
    async def handle_callback(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> Any:
        """Maneja un callback query."""
        callback = update.callback_query
        await callback.answer()
        
        data = callback.data
        
        # Manejar navegación
        if data.startswith("nav:"):
            return await self._handle_navigation(callback, context, data)
            
        # Delegar al callback router
        return await self.callback_router.handle(callback, context.bot)
        
    async def _handle_navigation(
        self,
        callback,
        context,
        data: str,
    ):
        """Maneja callbacks de navegación."""
        parts = data.split(":")
        action = parts[1]
        
        user_id = callback.from_user.id
        
        if action == "back":
            prev_menu = self.navigation.pop_menu(user_id)
            if prev_menu:
                await self.show_menu_by_callback(callback, context, prev_menu)
            else:
                await self.show_menu_by_callback(callback, context, "main")
                
        elif action == "home":
            self.navigation.go_home(user_id)
            await self.show_menu_by_callback(callback, context, "main")
            
        elif action == "noop":
            pass  # No hacer nada (solo actualizar estado)
            
    async def show_menu_by_callback(
        self,
        callback,
        context,
        menu_id: str,
    ):
        """Muestra menú desde callback query."""
        menu = self.registry.get(menu_id)
        if not menu:
            return
            
        config = await self.config_storage.get(callback.message.chat.id)
        keyboard = menu.to_keyboard(context={"config": config})
        
        try:
            await callback.edit_message_text(
                text=menu.title,
                reply_markup=keyboard,
            )
        except Exception as e:
            logger.error(f"Error editing menu: {e}")
```

---

## 9. Integración con el Bot Existente

### 9.1 Actualizar EnterpriseModule

```python
# app/manager_bot/application/enterprise/__init__.py
class EnterpriseModule(Module):
    """Actualizado con menús interactivos."""
    
    def __init__(self):
        self._commands = self._get_commands()
        self._setup_menu_engine()  # NUEVO
        
    def _setup_menu_engine(self):
        """Inicializa el motor de menús."""
        from app.manager_bot.transport.telegram.menu_engine import MenuEngine
        from app.manager_bot.transport.telegram.callback_router import CallbackRouter
        from app.manager_bot.menus.registry import MenuRegistry
        from app.manager_bot.menus import main_menu, moderation_menu
        from app.manager_bot.menus.navigation import NavigationManager
        from app.manager_bot.config.storage import get_config_storage
        
        self.menu_registry = MenuRegistry()
        self.navigation = NavigationManager()
        self.config_storage = get_config_storage()
        self.callback_router = CallbackRouter()
        
        # Registrar menús
        main_menu.register_main_menus(self.menu_registry)
        
        # Registrar callbacks de features
        self._register_feature_callbacks()
        
        self.menu_engine = MenuEngine(
            menu_registry=self.menu_registry,
            callback_router=self.callback_router,
            navigation_manager=self.navigation,
            config_storage=self.config_storage,
        )
        
    def _register_feature_callbacks(self):
        """Registra callbacks de todos los features."""
        from app.manager_bot.features.antispam.service import AntispamFeature
        from app.manager_bot.features.filters.service import FiltersFeature
        
        antispam = AntispamFeature(self.config_storage, get_moderation_service())
        antispam.register_callbacks(self.callback_router)
        
    def get_handlers(self) -> Dict[str, Callable]:
        handlers = {cmd.name: cmd.handler for cmd in self._commands}
        handlers["/config"] = self._handle_config_command  # NUEVO
        return handlers
        
    async def _handle_config_command(
        self,
        chat_id: int,
        args: Sequence[str],
        user_id: int,
        raw_text: str,
        raw_update: Dict,
    ) -> Dict[str, Any]:
        """Muestra el menú de configuración."""
        # Obtener Update simulado o usar el original
        # El menú se muestra directamente
        return {
            "status": "menu",
            "menu_id": "main",
            "action": "show", 
        }
```

### 9.2 Actualizar Webhook Handlers

```python
# app/webhook/handlers.py
async def handle_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming updates."""
    
    # Verificar si es callback query
    if update.callback_query:
        menu_engine = get_menu_engine()  # Obtener instancia global
        return await menu_engine.handle_callback(update, context)
        
    # Continuar con manejo normal de comandos...
```

---

## 10. Fases de Implementación

### Fase 1: Core de Menús (Semana 1)
- [ ] MenuDefinition y MenuRegistry
- [ ] KeyboardBuilder
- [ ] CallbackRouter básico
- [ ] NavigationManager

### Fase 2: Menús Base (Semana 2)
- [ ] Menú principal /config
- [ ] Menú de moderación
- [ ] Integración con grupo de configuración

### Fase 3: Features Initiales (Semana 3)
- [ ] Antispam con menús
- [ ] Filtros con menús
- [ ] Bienvenida con menús

### Fase 4: Features Avanzados (Semana 4)
- [ ] Captcha
- [ ] Warnings
- [ ] Reportes
- [ ] Modo nocturno

### Fase 5: Optimización (Semana 5)
- [ ] Caché con Redis
- [ ] Paginación
- [ ] Tests de integración

---

## 11. Ejemplo de Flujo Completo

```
1. Admin ejecuta /config
   → EnterpriseModule._handle_config_command()
   → Retorna {"status": "menu", "menu_id": "main"}

2. MenuEngine.show_menu("main")
   → Obtiene MenuDefinition("main")
   → Obtiene GroupConfig del chat
   → Construye InlineKeyboard
   → Envía mensaje con keyboard

3. Admin hace click en "🛡️ Moderación"
   → Llega callback: "mod:show"
   → CallbackRouter.match("^mod:") → handle_moderation_menu
   → NavigationManager.push_menu("mod")
   → MenuEngine.show_menu("mod")

4. Admin activa Anti-Flood
   → Callback: "mod:antiflood:toggle:on"
   → AntispamFeature.handle_toggle()
   → ConfigStorage.update(config)
   → MenuEngine.show_menu("mod")  # Actualiza vista
```

---

## 12. Beneficios de la Arquitectura

1. **Modularidad**: Cada feature es independiente y puede agregarse sin modificar el core
2. **Escalabilidad**: El CallbackRouter permite registrar infinitos handlers
3. **Mantenibilidad**: Navegación centralizada, configuración en un solo lugar
4. **UX**: Menús interactivos intuitivos en lugar de comandos de texto
5. **Rendimiento**: Redis caching para configuración de grupos
6. **Extensibilidad**: Sistema de plugins para nuevos features

---

## 13. Próximos Pasos Inmediatos

1. Crear la estructura de carpetas propuesta
2. Implementar MenuDefinition y MenuRegistry
3. Implementar CallbackRouter
4. Crear menú principal /config
5. Integrar con EnterpriseModule existente
6. Testing y validación

Esta arquitectura permite construir un bot profesional similar a GroupHelp o Rose, manteniendo la modularidad del sistema actual y permitiendo agregar funcionalidades futuras de manera escalable.