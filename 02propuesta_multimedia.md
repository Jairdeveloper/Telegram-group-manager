# Propuesta de implementacion: Menu Multimedia v2

Objetivo
- Implementar un menu Multimedia con una interfaz que muestre dinamicamente el estado actual de cada tipo de contenido.
- El encabezado 1 muestra informacion estatica de los iconos de acciones.
- El encabezado 2 (estado actual) es dinamico y cambia segun la seleccion del usuario.
- Los botones permiten cambiar el estado de cada tipo de contenido.

Contexto actual (Manager Bot)
- Existe un menu de moderation basico en media_menu.py.
- No existe configuracion granular por tipo de contenido multimedia.
- La implementacion actual tiene callbacks mal estructurados.

Propuesta de arquitectura corregida

1) Modelo de configuracion (GroupConfig)

Mantener los 26 campos de accion + 2 de duracion.

2) Estructura del menu

### Encabezado 1 (Estatico)
```
❕ = Warn | ❗️ = Kick | 🔇 = Silenciar | 🚷 = Ban | 🗑 = Eliminacion | ☑️ = Off
______________________________
```

### Encabezado 2 (Dinamico - Estado actual de cada tipo)
```
📲 Historia = ❕ Warn
📸 Foto = ❕ Warn
🎞 Video = ❕ Warn
🖼 Album = ☑️ Off
🎥 Gif = ☑️ Off
...
```

El estado actual se lee de `config.multimedia_<tipo>_action` y se muestra con el icono correspondiente.

### Matriz de botones (para cambiar estado)
```
📲|❕|🔇|🗑|❗️|🚷|☑️|
📸|❕|🔇|🗑|❗️|🚷|☑️|
...
[🔙 Volver]   [⏱ Tiempo]         [Mas →]
```

3) Ejemplo de titulo del menu (como antispan)

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
    
    # Matriz de botones para cambiar estado
    # Cada fila tiene: emoji + 6 botones de accion
    for tipo, emoji, field in MULTIMEDIA_TYPES_PAGE1:
        row = menu.add_row()
        row.add_action(f"multimedia:{tipo}:select", emoji)
        for action in ACTIONS:
            row.add_action(f"multimedia:{tipo}:action:{action}", ACTION_ICONS[action])
    
    menu.add_row() \
        .add_action("nav:back:main", "🔙 Volver") \
        .add_action("multimedia:duration:show", "⏱ Tiempo") \
        .add_action("multimedia:page2:show", "Mas")
    
    return menu
```

4) Formato de callbacks

- `multimedia:<tipo>:action:warn` - Cambiar tipo a warn
- `multimedia:<tipo>:action:off` - Cambiar tipo a off
- `multimedia:<tipo>:action:mute` - Cambiar tipo a silenciar
- `multimedia:<tipo>:action:kick` - Cambiar tipo a kick
- `multimedia:<tipo>:action:ban` - Cambiar tipo a ban
- `multimedia:<tipo>:action:delete` - Cambiar tipo a eliminacion

5) Valores por defecto por tipo (desde mulmedia.md)

| Tipo | Emoji | Default |
|------|-------|---------|
| Historia | 📲 | warn |
| Foto | 📸 | warn |
| Video | 🎞 | warn |
| Album | 🖼 | off |
| Gif | 🎥 | off |
| Voz | 🎤 | off |
| Audio | 🎧 | off |
| Sticker | 🃏 | off |
| Sticker anim | 🎭 | off |
| Sticker juego | 🎲 | off |
| Emoji anim | 😀 | off |
| Emoji custom | 👾 | off |
| Archivo | 💾 | off |
| Juegos | 🎮 | off |
| Contactos | ☎️ | ban |
| Encuestas | 📊 | mute |
| Checklist | 📋 | off |
| Ubicacion | 📍 | warn |
| Mayusculas | 🆎 | ban |
| Pagos | 💶 | off |
| Bot Inline | 🤖 | kick |
| Spoiler | 🗯 | warn |
| Spoiler media | 🌌 | kick |
| Video note | 👁‍🗨 | off |
| Sorteo | 🎁 | off |

6) Iconos de acciones

```python
ACTION_ICONS = {
    "warn": "❕",
    "mute": "🔇",
    "delete": "🗑",
    "kick": "❗️",
    "ban": "🚷",
    "off": "☑️",
}

ACTIONS = ["warn", "mute", "delete", "kick", "ban", "off"]
```

7) Navegacion

- **Pagina 1**: Primeros 13 tipos (Historia hasta Archivo)
- **Pagina 2**: Siguientes 12 tipos (Juegos hasta Sorteo)
- **Botones de navegacion**: `🔙 Volver | ⏱ Tiempo | Mas →`

8) Menu Duracion

```
⏱ Duracion de Ban/Silenciar/Warn

Envia ahora la duracion del castigo establecido.

Minimo: 30 segundos
Maximo: 365 dias

Ejemplo de formato: 3 months 2 days 12 hours 4 minutes 34 seconds

Duracion actual: Apagado
```

9) ConversationState

Estados para duracion:
- `waiting_multimedia_duration_mute`
- `waiting_multimedia_duration_ban`
- `waiting_multimedia_duration_warn`

Plan de implementacion

1) Modificar menus para generar titulo dinamico con estado actual
2) Corregir formato de callbacks
3) Actualizar MultimediaFeature para parsear callbacks
4) Testing

Notas
- El titulo del menu cambia dinamicamente para mostrar el estado actual
- Los botones permiten cambiar el estado y el menu se refresca con el nuevo estado
- Seguir el patron de antispan para consistencia
