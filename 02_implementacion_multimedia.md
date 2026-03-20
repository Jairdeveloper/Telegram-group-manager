# Implementacion Multimedia v2

Fecha: 2026-03-20
Version: 2.0
Referencia: 02propuesta_multimedia.md, mulmedia.md

---

# Resumen de la correccion

La implementacion debe mostrar:
1. **Encabezado 1 (estatico)**: Informacion de los iconos de acciones
2. **Encabezado 2 (dinamico)**: Estado actual de cada tipo de contenido segun configuracion

---

# Problema identificado

La implementacion actual no muestra el estado dinamico en el titulo del menu.

## Solucion

Modificar el titulo del menu para incluir:
- Encabezado estatico con iconos
- Lista dinamica de estados actuales por tipo

---

# Arquitectura corregida

## Modelo de configuracion (GroupConfig)

Mantener los campos existentes.

## Estructura del titulo del menu

```python
def create_multimedia_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    """Create the main Multimedia menu."""
    
    # Encabezado 1 (estatico)
    static_header = "❕=Warn | ❗️=Kick | 🔇=Silenciar | 🚷=Ban | 🗑=Eliminacion | ☑️=Off"
    
    # Encabezado 2 (dinamico - estado actual)
    states = []
    for tipo, emoji, field in MULTIMEDIA_TYPES_PAGE1:
        action = getattr(config, field, "off") if config else "off"
        icon = ACTION_ICONS.get(action, "☑️")
        states.append(f"{emoji} {tipo.capitalize()} = {icon} {action.capitalize()}")
    
    title = (
        f"Multimedia\n"
        f"{static_header}\n"
        f"______________________________\n\n"
        + "\n".join(states)
    )
    
    menu = MenuDefinition(
        menu_id="multimedia",
        title=title,
        parent_menu="main",
    )
    # ...
```

## Formato de titulo esperado

```
Multimedia

❕=Warn | ❗️=Kick | 🔇=Silenciar | 🚷=Ban | 🗑=Eliminacion | ☑️=Off
______________________________

📲 Historia = ❕ Warn
📸 Foto = ❕ Warn
🎞 Video = ❕ Warn
🖼 Album = ☑️ Off
🎥 Gif = ☑️ Off
🎤 Voz = ☑️ Off
🎧 Audio = ☑️ Off
🃏 Sticker = ☑️ Off
🎭 Sticker Anim = ☑️ Off
🎲 Sticker Juego = ☑️ Off
😀 Emoji Anim = ☑️ Off
👾 Emoji Custom = ☑️ Off
💾 Archivo = ☑️ Off
```

---

# Tabla de correcciones

| # | Tarea | Archivo | Prioridad |
|---|-------|---------|-----------|
| 1 | Generar titulo con estado dinamico | _menus/multimedia_menu.py | alta |
| 2 | Corregir formato de callback | _menus/multimedia_menu.py | alta |
| 3 | Corregir parsing en MultimediaFeature | _features/multimedia/__init__.py | alta |
| 4 | Testing completo | - | media |

---

# Fase 1: Generar titulo con estado dinamico

**Objetivo:** Modificar create_multimedia_menu para generar titulo con estado actual

**Implementacion:**

1. Editar `app/manager_bot/_menus/multimedia_menu.py`:

   Crear funcion helper para generar el titulo:

```python
def _build_multimedia_title(config: Optional[GroupConfig], types: list) -> str:
    """Build the dynamic title with current states."""
    static_header = "❕=Warn | ❗️=Kick | 🔇=Silenciar | 🚷=Ban | 🗑=Eliminacion | ☑️=Off"
    
    states = []
    for tipo, emoji, field in types:
        action = getattr(config, field, "off") if config else "off"
        icon = ACTION_ICONS.get(action, "☑️")
        states.append(f"{emoji} {tipo.capitalize()} = {icon} {action.capitalize()}")
    
    return (
        f"Multimedia\n"
        f"{static_header}\n"
        f"______________________________\n\n"
        + "\n".join(states)
    )
```

2. Modificar create_multimedia_menu:

```python
def create_multimedia_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
    title = _build_multimedia_title(config, MULTIMEDIA_TYPES_PAGE1)
    
    menu = MenuDefinition(
        menu_id="multimedia",
        title=title,
        parent_menu="main",
    )
    # ...
```

---

# Fase 2: Corregir formato de callbacks

**Objetivo:** Usar formato `multimedia:<tipo>:action:<accion>`

**Implementacion:**

```python
def _build_matrix_row(menu, tipo, emoji, field, config):
    """Build a matrix row with emoji and action buttons."""
    row = menu.add_row()
    row.add_action(f"multimedia:{tipo}:select", emoji)
    for action in ACTIONS:
        row.add_action(f"multimedia:{tipo}:action:{action}", ACTION_ICONS[action])
```

---

# Fase 3: Corregir MultimediaFeature

**Objetivo:** Parsear callbacks correctamente

**Implementacion:**

```python
async def handle_action(callback: "CallbackQuery", bot: "Bot", data: str):
    # Formato: multimedia:story:action:warn
    parts = data.split(":")  # ["multimedia", "story", "action", "warn"]
    
    if len(parts) < 4:
        await callback.answer("Accion no reconocida", show_alert=True)
        return
    
    tipo = parts[1]  # "story"
    action = parts[3]  # "warn"
    
    valid_actions = {"off", "warn", "mute", "delete", "kick", "ban"}
    if action not in valid_actions:
        await callback.answer("Accion no reconocida", show_alert=True)
        return
    
    # Construir nombre del campo en config
    field_name = f"multimedia_{tipo}_action"
    
    # Verificar que el campo existe
    if not hasattr(GroupConfig, field_name):
        await callback.answer("Tipo no reconocido", show_alert=True)
        return
    
    # Actualizar configuracion
    chat_id = callback.message.chat.id if callback.message else None
    if not chat_id:
        return
    
    config = await self.get_config(chat_id)
    
    def _apply(cfg: GroupConfig) -> None:
        setattr(cfg, field_name, action)
    
    await self.update_config_and_refresh(callback, bot, "multimedia", _apply)
```

---

# Fase 4: Verificacion

**Objetivo:** Verificar funcionamiento

**Verificar:**
1. Titulo muestra estado dinamico
2. Callbacks funcionan correctamente
3. Menu se refresca con nuevo estado

---

# Archivos a modificar

| Archivo | Cambio |
|---------|--------|
| app/manager_bot/_menus/multimedia_menu.py | Titulo dinamico + callbacks corregidos |
| app/manager_bot/_features/multimedia/__init__.py | Parsing de callbacks corregido |

---

# Estado de las fases

| Fase | Estado | Descripcion |
|------|--------|------------|
| Fase 1: Titulo dinamico | ⏳ Pendiente | Generar titulo con estado actual |
| Fase 2: Callbacks | ⏳ Pendiente | Corregir formato |
| Fase 3: Feature | ⏳ Pendiente | Corregir parsing |
| Fase 4: Testing | ⏳ Pendiente | Verificar |

---

# Siguiente paso

Ejecutar **Fase 1**: Generar titulo con estado dinamico en `multimedia_menu.py`
