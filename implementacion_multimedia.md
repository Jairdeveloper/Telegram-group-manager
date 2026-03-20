Fecha: 2026-03-20
Version: 1.0
Referencia: propuesta_multimedia.md

---

# Resumen de la implementacion

Implementar un menu Multimedia que permita configurar el comportamiento del bot ante diferentes tipos de contenido multimedia enviado por los usuarios. El menu presentara una matriz unica con navegacion por paginas y configuracion de duracion para castigos.

---

# Arquitectura final

## Campos en GroupConfig

| Campo | Tipo | Valores | Default |
|-------|------|---------|---------|
| multimedia_story_action | str | off\|warn\|mute\|kick\|ban\|delete | warn |
| multimedia_photo_action | str | off\|warn\|mute\|kick\|ban\|delete | warn |
| multimedia_video_action | str | off\|warn\|mute\|kick\|ban\|delete | warn |
| multimedia_album_action | str | off\|warn\|mute\|kick\|ban\|delete | off |
| multimedia_gif_action | str | off\|warn\|mute\|kick\|ban\|delete | off |
| multimedia_voice_action | str | off\|warn\|mute\|kick\|ban\|delete | off |
| multimedia_audio_action | str | off\|warn\|mute\|kick\|ban\|delete | off |
| multimedia_sticker_action | str | off\|warn\|mute\|kick\|ban\|delete | off |
| multimedia_animated_sticker_action | str | off\|warn\|mute\|kick\|ban\|delete | off |
| multimedia_game_sticker_action | str | off\|warn\|mute\|kick\|ban\|delete | off |
| multimedia_animated_emoji_action | str | off\|warn\|mute\|kick\|ban\|delete | off |
| multimedia_custom_emoji_action | str | off\|warn\|mute\|kick\|ban\|delete | off |
| multimedia_file_action | str | off\|warn\|mute\|kick\|ban\|delete | off |
| multimedia_game_action | str | off\|warn\|mute\|kick\|ban\|delete | off |
| multimedia_contact_action | str | off\|warn\|mute\|kick\|ban\|delete | ban |
| multimedia_poll_action | str | off\|warn\|mute\|kick\|ban\|delete | mute |
| multimedia_checklist_action | str | off\|warn\|mute\|kick\|ban\|delete | off |
| multimedia_location_action | str | off\|warn\|mute\|kick\|ban\|delete | warn |
| multimedia_caps_action | str | off\|warn\|mute\|kick\|ban\|delete | ban |
| multimedia_payment_action | str | off\|warn\|mute\|kick\|ban\|delete | off |
| multimedia_inline_bot_action | str | off\|warn\|mute\|kick\|ban\|delete | kick |
| multimedia_spoiler_action | str | off\|warn\|mute\|kick\|ban\|delete | warn |
| multimedia_spoiler_media_action | str | off\|warn\|mute\|kick\|ban\|delete | kick |
| multimedia_video_note_action | str | off\|warn\|mute\|kick\|ban\|delete | off |
| multimedia_giveaway_action | str | off\|warn\|mute\|kick\|ban\|delete | off |
| multimedia_mute_duration_sec | int\|None | - | None |
| multimedia_ban_duration_sec | int\|None | - | None |

## Menus

| menu_id | Descripcion |
|---------|------------|
| multimedia | Pagina 1 con 13 tipos de contenido |
| multimedia:page2 | Pagina 2 con 12 tipos de contenido |
| multimedia:duration | Configuracion de duraciones |

## Callbacks

| Callback | Accion |
|----------|--------|
| multimedia:show | Mostrar pagina 1 |
| multimedia:page2:show | Mostrar pagina 2 |
| multimedia:page1:show | Volver a pagina 1 |
| multimedia:duration:show | Mostrar menu duracion |
| multimedia:duration:mute:show | Iniciar input mute duration |
| multimedia:duration:ban:show | Iniciar input ban duration |
| multimedia:duration:clear | Limpiar duraciones |
| multimedia:<type>:action:<action> | Cambiar accion |
| nav:back:main | Volver al menu principal |

## ConversationState

| Estado | Uso |
|--------|-----|
| waiting_multimedia_duration_mute | Input duracion silenciar |
| waiting_multimedia_duration_ban | Input duracion ban |

---

# Tabla de tareas

| # | Tarea | Archivo | Prioridad |
|---|-------|---------|-----------|
| 1 | Agregar campos multimedia_*_action a GroupConfig | _config/group_config.py | alta |
| 2 | Agregar campos multimedia_*_duration_sec a GroupConfig | _config/group_config.py | alta |
| 3 | Crear archivo multimedia_menu.py | _menus/multimedia_menu.py | alta |
| 4 | Crear create_multimedia_menu (pagina 1) | _menus/multimedia_menu.py | alta |
| 5 | Crear create_multimedia_page2_menu (pagina 2) | _menus/multimedia_menu.py | alta |
| 6 | Crear create_multimedia_duration_menu | _menus/multimedia_menu.py | alta |
| 7 | Registrar menus en __init__.py | _menus/__init__.py | alta |
| 8 | Crear MultimediaFeature | _features/multimedia/__init__.py | alta |
| 9 | Implementar callbacks de acciones | _features/multimedia/__init__.py | alta |
| 10 | Implementar callbacks de navegacion | _features/multimedia/__init__.py | alta |
| 11 | Agregar ConversationState en handlers.py | webhook/handlers.py | media |
| 12 | Registrar feature en ManagerBot | core.py | media |

---

# Fase 1: Modelo de datos

**Objetivo fase:** Agregar campos de configuracion multimedia a GroupConfig

**Implementacion fase:**

1. Editar `app/manager_bot/_config/group_config.py`:
   - Agregar 26 campos `multimedia_*_action` con valores por defecto segun tabla
   - Agregar campos `multimedia_mute_duration_sec` y `multimedia_ban_duration_sec`
   - Asegurar serializacion correcta en `to_dict()` y `from_dict()`

---

# Fase 2: Menus

**Objetivo fase:** Crear la estructura de menus con navegacion por paginas

**Implementacion fase:**

1. Crear `app/manager_bot/_menus/multimedia_menu.py`:
   - Funcion `create_multimedia_menu(config)`: Pagina 1 con 13 tipos
   - Funcion `create_multimedia_page2_menu(config)`: Pagina 2 con 12 tipos
   - Funcion `create_multimedia_duration_menu(config)`: Menu duraciones

2. Editar `app/manager_bot/_menus/__init__.py`:
   - Importar funciones de multimedia_menu
   - Registrar los 3 menus en `register_all_menus()`

---

# Fase 3: Feature y Callbacks

**Objetivo fase:** Implementar logica de callbacks para acciones y navegacion

**Implementacion fase:**

1. Crear `app/manager_bot/_features/multimedia/__init__.py`:
   - Clase `MultimediaFeature(FeatureModule)`
   - Callbacks para cada tipo de contenido
   - Callbacks de navegacion (page1, page2, duration)
   - Metodo para construir menu dinamico segun accion actual

2. Editar `app/manager_bot/core.py`:
   - Importar y registrar `MultimediaFeature` en `ManagerBot`

---

# Fase 4: ConversationState

**Objetivo fase:** Agregar estados de conversacion para entrada de duraciones

**Implementacion fase:**

1. Editar `app/webhook/handlers.py`:
   - Agregar casos en handler de chat_message para estados:
     - `waiting_multimedia_duration_mute`
     - `waiting_multimedia_duration_ban`
   - Usar `parse_duration_to_seconds()` para convertir input
   - Validar rango (30 segundos - 365 dias)

---

# Fase 5: Testing

**Objetivo fase:** Verificar correcto funcionamiento de la implementacion

**Implementacion fase:**

1. Verificar inicializacion de MenuEngine
2. Verificar navegacion entre paginas
3. Verificar cambios de accion persisten en GroupConfig
4. Verificar entrada de duracion
