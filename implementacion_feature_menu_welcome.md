# Propuesta de Implementación: Feature Menú Welcome

## Fecha: 2026-03-15

## Objetivo

Implementar las siguientes funcionalidades para el menú de bienvenida:

1. **Estado de activación**: Crear menuRows con 2 botones para activar/desactivar la funcionalidad de bienvenida, mostrando el estado actual en la descripción
2. **Edición de mensajes**: Crear menuRows con funcionalidad para editar el mensaje de bienvenida

---

## Análisis del Código Existente

### Archivos Relevantes

| Archivo | Descripción |
|---------|-------------|
| `app/manager_bot/menus/welcome_menu.py` | Definición de menús de bienvenida |
| `app/manager_bot/features/welcome/__init__.py` | Feature con handlers de callbacks |
| `app/manager_bot/menus/base.py` | Clase base MenuDefinition |

### Estructura Actual

```python
# welcome_menu.py
def create_welcome_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    menu = MenuDefinition(
        menu_id="welcome",
        title="👋 Configuración de Bienvenida",
        parent_menu="main",
    )
    
    welcome_enabled = config.welcome_enabled if config else False
    welcome_status = "✅ Activada" if welcome_enabled else "❌ Desactivada"
    
    # Toggle sin estado on/off
    menu.add_row().add_action(
        f"welcome:toggle:{'on' if welcome_enabled else 'off'}",
        f"{welcome_status} Bienvenida",
        "👋"
    )
```

---

## Tareas a Ejecutar

### Tarea 1: Crear menú de bienvenida con estado on/off en descripción

**Archivos a modificar:**

1. **`app/manager_bot/menus/welcome_menu.py`**
   - Modificar `create_welcome_menu()` para mostrar el estado en la descripción del botón
   - El callback ya incluye el estado: `welcome:toggle:on` o `welcome:toggle:off`

**Cambio requerido:**
```python
# El estado ya está incluido en el callback_data
# Verificar que el handler procesa correctamente el estado

# En welcome/__init__.py - handle_welcome_toggle ya extrae el estado:
enabled = data.split(":")[-1] == "on"
```

### Tarea 2: Crear menú con funcionalidad para editar mensajes

**Archivos a modificar:**

1. **`app/manager_bot/menus/welcome_menu.py`**
   - Crear nuevo menú `create_welcome_edit_menu()` o añadir opciones en menú existente
   - Añadir botón que inicie el flujo de edición de texto

2. **`app/manager_bot/features/welcome/__init__.py`**
   - Verificar que existe handler para `welcome:edit:text`
   - El handler debe iniciar conversación para recibir texto

3. **`app/manager_bot/menu_service.py`** (si es necesario)
   - Verificar que existe el estado de conversación para edición de texto

---

## Funciones a Modificar

### 1. `app/manager_bot/menus/welcome_menu.py`

#### Función: `create_welcome_menu()`

**Propósito:** Crear menú de configuración de bienvenida

**Cambios:**
- Ya tiene toggle con estado on/off en callback_data
- Verificar que el botón muestre correctamente el estado actual

**Código actual (ya corregido):**
```python
menu.add_row().add_action(
    f"welcome:toggle:{'on' if welcome_enabled else 'off'}",
    f"{welcome_status} Bienvenida",
    "👋"
)
```

#### Nueva Función: `create_welcome_edit_menu()`

**Propósito:** Menú para editar mensaje de bienvenida

**Implementación sugerida:**
```python
def create_welcome_edit_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the welcome message editor menu."""
    menu = MenuDefinition(
        menu_id="welcome:edit",
        title="📝 Editar Mensaje de Bienvenida",
        parent_menu="welcome",
    )
    
    # Mostrar texto actual o indicar que no hay texto
    current_text = config.welcome_text if config else None
    has_text = bool(current_text)
    
    menu.add_row().add_action(
        "welcome:edit:text",
        f"📝 {'Ver/Editar texto' if has_text else 'Agregar texto'}",
        "📝"
    )
    
    menu.add_row().add_action(
        "welcome:edit:preview",
        "👁️ Previsualizar",
        "👁️"
    )
    
    menu.add_row().add_action("nav:back:welcome", "🔙 Volver", "🔙")
    
    return menu
```

### 2. `app/manager_bot/features/welcome/__init__.py`

#### Función: `register_callbacks()`

**Propósito:** Registrar handlers para callbacks de welcome

**Handlers existentes:**
- `welcome:toggle` → `handle_welcome_toggle`
- `goodbye:toggle` → `handle_goodbye_toggle`
- `welcome:edit:text` → `handle_edit_text`
- `welcome:edit:media` → `handle_edit_media`
- `welcome:show` → `handle_show_welcome`
- `goodbye:show` → `handle_show_goodbye`

**Verificar que existen estos registros:**
```python
router.register_callback("welcome:toggle", handle_welcome_toggle)
router.register_exact("welcome:edit:text", handle_edit_text)
router.register_exact("welcome:edit:media", handle_edit_media)
```

#### Handler: `handle_edit_text()`

**Propósito:** Iniciar conversación para editar texto de bienvenida

**Implementación sugerida:**
```python
async def handle_edit_text(callback: "CallbackQuery", bot: "Bot", data: str):
    from app.manager_bot.menu_service import get_conversation_state
    
    chat_id = callback.message.chat.id if callback.message else None
    user_id = callback.from_user.id
    
    if not chat_id:
        await callback.answer("Chat no identificado", show_alert=True)
        return
    
    # Establecer estado de conversación
    conversation = get_conversation_state()
    conversation.set_state(user_id, chat_id, "waiting_welcome_text")
    
    await callback.answer(
        "Envía el mensaje de bienvenida que deseas configurar.\n\n"
        "Usa {username} para mencionar al usuario\n"
        "Usa {title} para el nombre del grupo",
        show_alert=True
    )
```

---

## Plan de Implementación

### Fase 1: Verificar estado actual (5 min)

1. Verificar que `welcome_menu.py` tiene el toggle con estado
2. Verificar que los handlers en `welcome/__init__.py` están registrados

### Fase 2: Implementar edición de texto (30 min)

1. Crear/verificar handler `handle_edit_text` en `welcome/__init__.py`
2. Añadir botón de edición en `welcome_menu.py`
3. Registrar nuevo menú si es necesario

### Fase 3: Integrar con sistema de conversaciones (15 min)

1. Verificar estados de conversación en `menu_service.py`
2. Añadir handler para procesar texto recibido

### Fase 4: Testing (15 min)

1. Probar toggle on/off
2. Probar edición de texto
3. Verificar navegación

---

## Estados de Conversión a Implementar

En `app/manager_bot/menu_service.py`, verificar que existen:

```python
CONVERSATION_STATES = {
    "waiting_welcome_text": "Bienvenida",
    "waiting_goodbye_text": "Despedida",
    # ... otros estados
}
```

Si no existe, agregar el estado `waiting_welcome_text`.

---

## Resumen de Archivos a Modificar

| Archivo | Función | Cambio |
|---------|---------|--------|
| `welcome_menu.py` | `create_welcome_menu()` | Verificar toggle con estado |
| `welcome_menu.py` | Nueva: `create_welcome_edit_menu()` | Crear menú de edición |
| `welcome/__init__.py` | `handle_edit_text()` | Implementar handler de edición |
| `menu_service.py` | `CONVERSATION_STATES` | Agregar estado si no existe |
| `menus/__init__.py` | Registro de menús | Registrar nuevo menú si es necesario |

---

## Pendiente de Información

1. ¿El handler `handle_edit_text` ya está implementado en `welcome/__init__.py`?
2. ¿Hay algún sistema existente para procesar mensajes de texto entrantes?
3. ¿Se requiere previsualización del mensaje?
