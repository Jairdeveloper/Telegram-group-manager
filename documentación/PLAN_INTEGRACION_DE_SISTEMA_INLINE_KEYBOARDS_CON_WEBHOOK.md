# Plan de Integración - Sistema Inline Keyboards con Webhook

## Resumen

Este documento detalla el plan de integración para conectar el sistema de menús interactivos (Inline Keyboards) con el webhook existente del Manager Bot.

---

## Estado Actual

### Sistema de Menús (Implementado)
- **Core:** MenuEngine, CallbackRouter, NavigationManager
- **Features:** 11 módulos (Antispam, Filters, Welcome, AntiFlood, AntiChannel, Captcha, Warnings, Reports, NightMode, AntiLink, Media)
- **Menús:** 22+ definiciones registradas
- **Callbacks:** 50+ handlers

### Webhook Existente
- **Archivo:** `app/webhook/handlers.py`
- **Procesamiento:** `process_update_impl()` maneja comandos y mensajes
- **Tipos de update:** `ops_command`, `enterprise_command`, `chat_message`
- **Falta:** Manejo de `callback_query` para Inline Keyboards

---

## Arquitectura de Integración

```
Telegram Update
      │
      ▼
┌─────────────────┐
│ handle_webhook  │  ← Entry point
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ dispatch type   │  ← Verificar callback_query
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌───────┐ ┌──────────────┐
│ Mensaje│ │ Callback    │
│ Normal │ │ Query       │
└───┬───┘ └──────┬──────┘
    │             │
    ▼             ▼
┌───────────┐ ┌────────────────────┐
│ Handlers  │ │ MenuEngine          │
│ Existentes│ │ .handle_callback()  │
└───────────┘ └────────────────────┘
```

---

## Tareas de Integración

### 1. Inicialización del MenuEngine

**Objetivo:** Crear una instancia global de MenuEngine accesible desde el webhook.

**Pasos:**
- [ ] Crear módulo `app/manager_bot/menu_service.py` con factory function
- [ ] Integrar inicialización en `app/webhook/bootstrap.py`
- [ ] Registrar todos los features en el callback router

**Archivo a crear:** `app/manager_bot/menu_service.py`

```python
"""Menu service factory for webhook integration."""

from app.manager_bot.menus import MenuRegistry, register_all_menus, NavigationManager
from app.manager_bot.menus.base import MenuDefinition
from app.manager_bot.config.storage import get_config_storage, InMemoryConfigStorage
from app.manager_bot.config.rate_limiter import RateLimiter
from app.manager_bot.transport.telegram.callback_router import CallbackRouter
from app.manager_bot.transport.telegram.menu_engine import MenuEngine

# Features
from app.manager_bot.features.antispam import AntispamFeature
from app.manager_bot.features.filters import FiltersFeature
from app.manager_bot.features.welcome import WelcomeFeature
from app.manager_bot.features.antiflood import AntiFloodFeature
from app.manager_bot.features.antichannel import AntiChannelFeature
from app.manager_bot.features.captcha import CaptchaFeature
from app.manager_bot.features.warnings import WarningsFeature
from app.manager_bot.features.reports import ReportsFeature
from app.manager_bot.features.nightmode import NightModeFeature
from app.manager_bot.features.antilink import AntiLinkFeature
from app.manager_bot.features.media import MediaFeature


def create_menu_engine(
    storage_type: str = "memory",
    database_url: str = None,
    redis_url: str = None,
) -> MenuEngine:
    """Create and initialize the menu engine with all features."""
    
    # Create registry and register menus
    registry = MenuRegistry()
    register_all_menus(registry)
    
    # Create storage
    config_storage = get_config_storage(storage_type, database_url, redis_url)
    
    # Create callback router
    callback_router = CallbackRouter()
    
    # Create navigation manager
    navigation_manager = NavigationManager()
    
    # Create rate limiter
    rate_limiter = RateLimiter(max_calls=30, window_seconds=60)
    
    # Create menu engine
    menu_engine = MenuEngine(
        menu_registry=registry,
        callback_router=callback_router,
        navigation_manager=navigation_manager,
        config_storage=config_storage,
    )
    
    # Register all features
    features = [
        AntispamFeature(config_storage),
        FiltersFeature(config_storage),
        WelcomeFeature(config_storage),
        AntiFloodFeature(config_storage),
        AntiChannelFeature(config_storage),
        CaptchaFeature(config_storage),
        WarningsFeature(config_storage),
        ReportsFeature(config_storage),
        NightModeFeature(config_storage),
        AntiLinkFeature(config_storage),
        MediaFeature(config_storage),
    ]
    
    for feature in features:
        feature.register_callbacks(callback_router)
    
    return menu_engine, rate_limiter


# Global instance
_menu_engine: MenuEngine = None
_rate_limiter: RateLimiter = None


def get_menu_engine() -> MenuEngine:
    """Get the global menu engine instance."""
    global _menu_engine
    if _menu_engine is None:
        _menu_engine, _rate_limiter = create_menu_engine()
    return _menu_engine


def get_rate_limiter() -> RateLimiter:
    """Get the global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _menu_engine, _rate_limiter = create_menu_engine()
    return _rate_limiter
```

---

### 2. Modificar Webhook Handlers

**Objetivo:** Agregar soporte para `callback_query` en `app/webhook/handlers.py`.

**Cambios requeridos:**

```python
# Agregar al inicio del archivo
from app.manager_bot.menu_service import get_menu_engine, get_rate_limiter
from app.telegram.dispatcher import dispatch_telegram_update

# Modificar process_update_impl para manejar callback_query

async def process_update_impl(
    update: Dict[str, Any],
    *,
    # ... parámetros existentes ...
) -> None:
    # ... código existente ...
    
    # AGREGAR: Verificar si es callback_query
    if dispatch.kind == "callback_query":
        menu_engine = get_menu_engine()
        rate_limiter = get_rate_limiter()
        
        user_id = dispatch.user_id
        
        # Verificar rate limit
        if not rate_limiter.is_allowed(user_id, "callback"):
            await telegram_client.answer_callback_query(
                callback_query_id=dispatch.callback_query_id,
                text="⚠️ Demasiadas solicitudes. Intenta más tarde.",
                show_alert=True
            )
            return
        
        # Procesar callback
        await menu_engine.handle_callback(update, context)
        
        record_event(
            component="webhook",
            event="webhook.menu_callback.ok",
            user_id=user_id,
        )
        return
    
    # ... resto del código existente ...
```

---

### 3. Actualizar Telegram Dispatcher

**Objetivo:** Asegurar que el dispatcher reconozca `callback_query`.

**Cambios en `app/telegram/dispatcher.py`:**

```python
@dataclass
class DispatchResult:
    kind: str  # "callback_query", "ops_command", "enterprise_command", "chat_message", "unsupported"
    # ... campos existentes ...

def dispatch_telegram_update(update: Dict[str, Any]) -> DispatchResult:
    # ... código existente ...
    
    # AGREGAR: Verificar callback_query
    if "callback_query" in update:
        callback = update["callback_query"]
        return DispatchResult(
            kind="callback_query",
            callback_query_id=callback.get("id"),
            user_id=callback.get("from", {}).get("id"),
            chat_id=callback.get("message", {}).get("chat", {}).get("id"),
            text=callback.get("data"),
            raw_update=update,
        )
    
    # ... resto del código ...
```

---

### 4. Integrar con EnterpriseModule

**Objetivo:** El comando `/config` debe invocar el menú interactivo.

**Cambios en `app/manager_bot/application/enterprise/__init__.py`:**

```python
def _config_handler(
    self,
    chat_id: int,
    args: Sequence[str],
    user_id: int,
    raw_text: str,
    raw_update: Dict,
) -> Dict[str, Any]:
    # Indicar que debe mostrarse el menú
    return {
        "status": "menu",
        "menu_id": "main",
        "action": "show",
    }
```

**Modificar el response handler en webhook:**

```python
# En process_update_impl, después de obtener el resultado
if result.get("status") == "menu":
    menu_id = result.get("menu_id", "main")
    await menu_engine.show_menu(update, context, menu_id, edit=False)
    return
```

---

### 5. Manejo de Estados de Conversación

**Objetivo:** Soportar edición de texto (bienvenida, reglas, etc.).

**Nueva funcionalidad:**

```python
# En menu_service.py agregar

class ConversationState:
    """Manage conversation states for text input."""
    
    def __init__(self):
        self._states: Dict[int, Dict[str, str]] = {}
    
    def set_state(self, user_id: int, chat_id: int, state: str, context: Dict = None):
        key = (user_id, chat_id)
        self._states[key] = {
            "state": state,
            "context": context or {},
        }
    
    def get_state(self, user_id: int, chat_id: int) -> Optional[Dict]:
        key = (user_id, chat_id)
        return self._states.get(key)
    
    def clear_state(self, user_id: int, chat_id: int):
        key = (user_id, chat_id)
        self._states.pop(key, None)


# Estados de conversación
CONVERSATION_STATES = {
    "waiting_welcome_text": "Bienvenida",
    "waiting_goodbye_text": "Despedida", 
    "waiting_filter_pattern": "Filtro",
    "waiting_blocked_word": "Palabra bloqueada",
    "waiting_whitelist_domain": "Dominio whitelist",
}
```

---

### 6. Actualizar Bootstrap

**Objetivo:** Inicializar el MenuEngine al arrancar la aplicación.

**Cambios en `app/webhook/bootstrap.py`:**

```python
async def bootstrap():
    """Bootstrap the application."""
    # ... código existente ...
    
    # NUEVO: Inicializar menú engine
    from app.manager_bot.menu_service import create_menu_engine
    
    storage_type = os.getenv("MENU_STORAGE_TYPE", "memory")
    database_url = os.getenv("DATABASE_URL")
    redis_url = os.getenv("REDIS_URL")
    
    menu_engine, rate_limiter = create_menu_engine(
        storage_type=storage_type,
        database_url=database_url,
        redis_url=redis_url,
    )
    
    logger.info("Menu engine initialized", extra={
        "storage": storage_type,
        "menus_count": len(menu_engine.registry.list_menus()),
    })
    
    # ... resto del código ...
```

---

## Flujo de Integración

```
1. Bot inicia
   │
   ▼
2. bootstrap() ejecuta create_menu_engine()
   │
   ├── Registry carga 22+ menús
   ├── CallbackRouter registra 50+ handlers
   └── RateLimiter inicializado
   │
   ▼
3. Telegram envía update
   │
   ▼
4. handle_webhook() recibe request
   │
   ▼
5. dispatch_telegram_update()
   │
   ├── Si es callback_query → kind="callback_query"
   ├── Si es /config → kind="enterprise_command" + status="menu"
   └── Otros → flujo existente
   │
   ▼
6. process_update_impl()
   │
   ├── Si callback_query:
   │   ├── Rate limit check
   │   └── menu_engine.handle_callback()
   │
   └── Si status="menu":
       └── menu_engine.show_menu()
   │
   ▼
7. Telegram responde con InlineKeyboard
```

---

## Configuración Requerida

### Variables de Entorno

```bash
# Storage
MENU_STORAGE_TYPE=memory  # memory | postgres | redis
DATABASE_URL=postgresql://...
REDIS_URL=redis://...

# Rate Limiting
RATE_LIMIT_CALLS=30
RATE_LIMIT_WINDOW=60
```

---

## Pruebas de Integración

### Tests a crear:

```python
# tests/test_menu_webhook_integration.py

async def test_callback_query_routing():
    """Test that callback queries are routed to menu engine."""
    # 1. Crear update con callback_query
    # 2. Dispatch debe retornar kind="callback_query"
    # 3. Menu engine debe procesar el callback
    pass

async def test_config_command_shows_menu():
    """Test that /config shows the main menu."""
    # 1. Enviar comando /config
    # 2. Verificar que retorna status="menu"
    # 3. Verificar que se envía InlineKeyboardMarkup
    pass

async def test_rate_limiting():
    """Test rate limiting on callbacks."""
    # 1. Simular múltiples callbacks
    # 2. Verificar que se bloquean después del límite
    pass

async def test_navigation_flow():
    """Test complete navigation flow."""
    # 1. Usuario envía /config
    # 2. Click en "Moderación"
    # 3. Click en "Anti-Flood"
    # 4. Toggle
    # 5. Volver al menú principal
    pass
```

---

## Checklist de Implementación

### Fase 1: Inicialización
- [ ] Crear `app/manager_bot/menu_service.py`
- [ ] Agregar factory function `create_menu_engine()`
- [ ] Registrar todos los features
- [ ] Crear instance global

### Fase 2: Webhook Integration
- [ ] Modificar `app/webhook/handlers.py`
- [ ] Agregar handling de `callback_query`
- [ ] Integrar rate limiter
- [ ] Actualizar dispatcher

### Fase 3: EnterpriseModule
- [ ] Verificar `/config` retorna status="menu"
- [ ] Agregar handling de menu en response
- [ ] Probar flujo completo

### Fase 4: Estados de Conversación
- [ ] Implementar ConversationState
- [ ] Agregar handlers para input de texto
- [ ] Testing de flujos

### Fase 5: Optimización
- [ ] Agregar métricas de performance
- [ ] Testing de carga
- [ ] Documentación

---

## Métricas de Éxito

| Métrica | Objetivo |
|---------|----------|
| Latencia callback | < 200ms |
| Menús registrados | 22+ |
| Features activos | 11 |
| Tests de integración | 10+ |
| Uptime | 99.9% |

---

## Notas

- El sistema está diseñado para ser backward compatible
- Los comandos existentes (/filter, /welcome, etc.) siguen funcionando
- Los menús proporcionan interfaz visual adicional
- Rate limiting previene abuso

---

*Documento generado el 2026-03-12*
*Versión: 1.0*