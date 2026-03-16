# Implementación Feature Welcome Menu

## Fecha: 2026-03-15

## Resumen

Este documento presenta un plan de implementación detallado para la funcionalidad del menú de Bienvenida (Welcome Menu), basado en el análisis del código existente y la propuesta de solución del sistema de menús inline.

---

## Análisis del Código Existente

### Estado Actual

| Componente | Estado | Notas |
|------------|--------|-------|
| Menú welcome | ✅ Implementado | `welcome_menu.py` |
| Toggle on/off | ✅ Funcionando | Callback con estado on/off |
| Handlers de callbacks | ✅ Registrados | `welcome/__init__.py` |
| Edición de texto | ⚠️ Parcial | Solo muestra instrucción por alert |
| Edición de media | ⚠️ Parcial | Solo muestra instrucción por alert |

### Archivos Involucrados

```
app/manager_bot/
├── menus/
│   └── welcome_menu.py          # Definición de menús
├── features/
│   └── welcome/
│       └── __init__.py          # Handlers de callbacks
└── config/
    └── group_config.py          # Configuración de grupo
```

---

## Funcionalidades Requeridas

### 1. Toggle de Activación/Desactivación ✅ YA IMPLEMENTADO

**Estado:** El toggle con estado on/off ya está implementado.

**Callback:** `welcome:toggle:on` / `welcome:toggle:off`

**Handler:** `handle_welcome_toggle()` en `welcome/__init__.py:27-47`

```python
# Menú (welcome_menu.py:20-24)
menu.add_row().add_action(
    f"welcome:toggle:{'on' if welcome_enabled else 'off'}",
    f"{welcome_status} Bienvenida",
    "👋"
)
```

### 2. Edición de Mensaje de Bienvenida

**Estado:** Parcialmente implementado - solo muestra instrucción por alert.

**Requerido:** Implementar flujo completo de edición de texto.

---

## Plan de Implementación

### Fase 1: Verificar Estructura Existente (10 min)

#### Paso 1.1: Verificar estados de conversación

**Archivo:** `app/manager_bot/menu_service.py`

Verificar que existen los estados:
- `waiting_welcome_text` → "Bienvenida"
- `waiting_goodbye_text` → "Despedida"

**Verificar código actual:**
```python
class ConversationState:
    CONVERSATION_STATES = {
        "waiting_welcome_text": "Bienvenida",
        "waiting_goodbye_text": "Despedida", 
        "waiting_filter_pattern": "Filtro",
        # ...
    }
```

#### Paso 1.2: Verificar handlers existentes

**Archivo:** `app/manager_bot/features/welcome/__init__.py`

| Handler | Línea | Estado |
|---------|-------|--------|
| `handle_welcome_toggle` | 27-47 | ✅ Implementado |
| `handle_goodbye_toggle` | 49-69 | ✅ Implementado |
| `handle_edit_text` | 71-76 | ⚠️ Básico |
| `handle_edit_media` | 78-82 | ⚠️ Básico |
| `handle_show_welcome` | 84-101 | ✅ Implementado |
| `handle_show_goodbye` | 103-120 | ✅ Implementado |

#### Paso 1.3: Verificar registro de callbacks

**Archivo:** `welcome/__init__.py:122-128`

```python
router.register_callback("welcome:toggle", handle_welcome_toggle)
router.register_callback("goodbye:toggle", handle_goodbye_toggle)
router.register_exact("welcome:edit:text", handle_edit_text)
router.register_exact("welcome:edit:media", handle_edit_media)
router.register_exact("goodbye:edit:text", handle_edit_text)
router.register_exact("welcome:show", handle_show_welcome)
router.register_exact("goodbye:show", handle_show_goodbye)
```

---

### Fase 2: Implementar Edición de Texto (30 min)

#### Paso 2.1: Modificar handler handle_edit_text

**Archivo:** `app/manager_bot/features/welcome/__init__.py`

**Función a modificar:** `handle_edit_text()` (líneas 71-76)

**Código actual:**
```python
async def handle_edit_text(callback: "CallbackQuery", bot: "Bot", data: str):
    prefix = data.split(":")[0]
    await callback.answer(
        f"Usa /set{prefix} <texto> para configurar el mensaje",
        show_alert=True
    )
```

**Código mejorado:**
```python
async def handle_edit_text(callback: "CallbackQuery", bot: "Bot", data: str):
    """Handle edit text for welcome/goodbye messages."""
    from app.manager_bot.menu_service import get_conversation_state
    
    parts = data.split(":")
    prefix = parts[0] if parts else "welcome"  # "welcome" o "goodbye"
    
    chat_id = callback.message.chat.id if callback.message else None
    user_id = callback.from_user.id
    
    if not chat_id:
        await callback.answer("Chat no identificado", show_alert=True)
        return
    
    conversation = get_conversation_state()
    
    if prefix == "welcome":
        conversation.set_state(user_id, chat_id, "waiting_welcome_text")
        await callback.answer(
            "📝 *Envía el mensaje de bienvenida*\n\n"
            "Variables disponibles:\n"
            "• {username} - Nombre del usuario\n"
            "• {title} - Nombre del grupo\n"
            "• {count} - Número de miembros",
            show_alert=True
        )
    elif prefix == "goodbye":
        conversation.set_state(user_id, chat_id, "waiting_goodbye_text")
        await callback.answer(
            "📝 *Envía el mensaje de despedida*\n\n"
            "Variables disponibles:\n"
            "• {username} - Nombre del usuario\n"
            "• {title} - Nombre del grupo",
            show_alert=True
        )
```

#### Paso 2.2: Agregar handler para procesar texto recibido

**Archivo:** `app/manager_bot/features/welcome/__init__.py`

**Nueva función a agregar:**
```python
async def handle_welcome_text_input(chat_id: int, user_id: int, text: str, config: GroupConfig) -> str:
    """Process welcome text input from conversation."""
    config.welcome_text = text
    config.update_timestamp(user_id)
    return f"✅ Mensaje de bienvenida configurado:\n\n{text}"

async def handle_goodbye_text_input(chat_id: int, user_id: int, text: str, config: GroupConfig) -> str:
    """Process goodbye text input from conversation."""
    config.goodbye_text = text
    config.update_timestamp(user_id)
    return f"✅ Mensaje de despedida configurado:\n\n{text}"
```

#### Paso 2.3: Integrar con el sistema de mensajes

Se necesita verificar cómo se manejan los mensajes de texto entrantes. Esto típicamente se hace en el dispatcher o handler principal.

---

### Fase 3: Implementar Edición de Media (20 min)

#### Paso 3.1: Modificar handler handle_edit_media

**Archivo:** `app/manager_bot/features/welcome/__init__.py`

**Función a modificar:** `handle_edit_media()` (líneas 78-82)

**Código mejorado:**
```python
async def handle_edit_media(callback: "CallbackQuery", bot: "Bot", data: str):
    """Handle edit media for welcome messages."""
    from app.manager_bot.menu_service import get_conversation_state
    
    chat_id = callback.message.chat.id if callback.message else None
    user_id = callback.from_user.id
    
    if not chat_id:
        await callback.answer("Chat no identificado", show_alert=True)
        return
    
    conversation = get_conversation_state()
    conversation.set_state(user_id, chat_id, "waiting_welcome_media")
    
    await callback.answer(
        "🖼️ *Envía una foto o video para la bienvenida*\n\n"
        "El archivo debe ser una imagen o video válido.",
        show_alert=True
    )
```

---

### Fase 4: Agregar Preview/Mostrar Mensaje Actual (15 min)

#### Paso 4.1: Agregar opción de previsualización

**Archivo:** `app/manager_bot/menus/welcome_menu.py`

**Agregar botón de preview:**
```python
# En create_welcome_menu(), después de los botones de edición
if welcome_enabled and config.welcome_text:
    menu.add_row().add_action(
        "welcome:preview",
        "👁️ Previsualizar",
        "👁️"
    )
```

#### Paso 4.2: Crear handler para preview

**Archivo:** `welcome/__init__.py`

```python
async def handle_preview(callback: "CallbackQuery", bot: "Bot", data: str):
    """Handle preview of welcome message."""
    chat_id = callback.message.chat.id if callback.message else None
    if not chat_id:
        return
    
    config = await self.get_config(chat_id)
    if not config:
        return
    
    prefix = data.split(":")[0]
    if prefix == "welcome":
        text = config.welcome_text or "No hay mensaje configurado"
    else:
        text = config.goodbye_text or "No hay mensaje configurado"
    
    # Procesar variables
    user = callback.from_user
    text = text.format(
        username=user.first_name,
        title=callback.message.chat.title or "Grupo",
        count="..."
    )
    
    await callback.answer(text, show_alert=True)
```

**Registrar el handler:**
```python
router.register_callback("welcome:preview", handle_preview)
router.register_callback("goodbye:preview", handle_preview)
```

---

### Fase 5: Testing (20 min)

#### Paso 5.1: Tests unitarios

```python
# tests/manager_bot/test_welcome_feature.py
def test_welcome_toggle_on():
    """Test welcome toggle on."""
    # Simular callback con data "welcome:toggle:on"
    pass

def test_welcome_toggle_off():
    """Test welcome toggle off."""
    # Simular callback con data "welcome:toggle:off"
    pass

def test_edit_text_handler():
    """Test edit text handler sets conversation state."""
    pass

def test_preview_handler():
    """Test preview handler shows formatted message."""
    pass
```

#### Paso 5.2: Testing manual

| Acción | Resultado Esperado |
|--------|-------------------|
| Click en "welcome:toggle:on" | Alert: "Bienvenida activada" |
| Click en "welcome:edit:text" | Alert con instrucciones para enviar texto |
| Enviar texto después de click | Mensaje guardado, confirmación |
| Click en "welcome:preview" | Alert con mensaje formateado |

---

## Resumen de Archivos a Modificar

| Archivo | Función | Descripción |
|---------|---------|-------------|
| `features/welcome/__init__.py` | `handle_edit_text()` | Implementar flujo de edición |
| `features/welcome/__init__.py` | `handle_edit_media()` | Implementar flujo de media |
| `features/welcome/__init__.py` | `handle_preview()` | Crear handler para preview |
| `features/welcome/__init__.py` | `register_callbacks()` | Registrar nuevos callbacks |
| `menus/welcome_menu.py` | `create_welcome_menu()` | Agregar botón preview |
| `menus/welcome_menu.py` | `create_goodbye_menu()` | Agregar botón preview |

---

## Estados de Conversión Necesarios

Verificar en `menu_service.py`:

```python
CONVERSATION_STATES = {
    "waiting_welcome_text": "Bienvenida",      # ✅ Necesario
    "waiting_goodbye_text": "Despedida",       # ✅ Necesario
    "waiting_welcome_media": "Media Bienvenida", # ✅ Necesario
    # ... otros estados
}
```

---

## Checklist de Implementación

- [ ] Verificar estados de conversación existentes
- [ ] Modificar handle_edit_text para iniciar conversación
- [ ] Modificar handle_edit_media para iniciar conversación
- [ ] Crear handler handle_preview
- [ ] Registrar nuevos callbacks
- [ ] Agregar botones de preview en menús
- [ ] Testing unitario
- [ ] Testing manual

---

## Notas Adicionales

1. El sistema de conversación actual usa estados en `ConversationState`
2. Los mensajes de texto entrantes deben ser manejados por el message handler principal
3. Se debe verificar cómo se procesa el texto recibido cuando hay un estado de conversación activo
