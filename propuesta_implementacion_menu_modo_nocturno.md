Fecha: 24/03/2026
Version: 1.0
Referencia: menu_modo_nocturno.md

---

## Resumen de la implementacion

Se implementará una nueva versión del menú de Modo Nocturno que permitirá configurar dos tipos de acciones durante la noche: **Eliminación de Multimedia** y **Silencio Global**. El menú mostrará un encabezado en forma de árbol con el estado global y el horario activo.

La funcionalidad existente en `NightModeFeature` se extenderá para soportar:
- Alternar entre modos de acción (eliminar multimedia / silencio global)
- Configuración de horario mediante interfaz visual de matriz 5x4
- Visualización del estado actual en formato árbol

---

## Arquitectura final

```
┌─────────────────────────────────────────────────────────────────┐
│                      Menú Modo Nocturno                         │
├─────────────────────────────────────────────────────────────────┤
│  Estado: 📷 Eliminación multimedia                              │
│  ├ Activo entre las horas 23:00 - 09:00                        │
│  └ Anuncios de inicio y fin: ✅                                 │
├─────────────────────────────────────────────────────────────────┤
│  🌙 Activar/Desactivar                                          │
│  📸 Eliminar multimedia (On/Off)                                │
│  🔇 Silencio Global (On/Off)                                    │
│  ⏰ Establecer franja horaria                                   │
│  🔙 Volver                                                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Submenú Franja Horaria                       │
├─────────────────────────────────────────────────────────────────┐
│  Matriz 5x4 (20 celdas) para seleccionar hora de inicio/fin   │
│  ┌───┬───┬───┬───┬───┬───┐                                      │
│  │ 0 │ 1 │ 2 │ 3 │ 4 │...│  (horas del día)                     │
│  └───┴───┴───┴───┴───┴───┘                                      │
└─────────────────────────────────────────────────────────────────┘
```

**Componentes a modificar:**
- `nightmode_menu.py` - Nuevo diseño de menú con árbol
- `nightmode/__init__.py` - Nuevos callbacks para modos y horario
- `group_config.py` - Nuevos campos de configuración
- `callback_router` - Registro de nuevos handlers

---

## Tabla de tareas

| ID  | Tarea                                        | Prioridad | Estado      |
|-----|---------------------------------------------|-----------|-------------|
| 01  | Extender `GroupConfig` con nuevos campos    | Alta      | Pendiente   |
| 02  | Rediseñar `nightmode_menu.py` con formato árbol | Alta      | Pendiente   |
| 03  | Implementar menú de matriz de horario       | Alta      | Pendiente   |
| 04  | Registrar callbacks para nuevos handlers    | Alta      | Pendiente   |
| 05  | Implementar handler de cambio de modo       | Alta      | Pendiente   |
| 06  | Implementar handler de configuración horario| Alta      | Pendiente   |
| 07  | Integrar con sistema de anuncios (inicio/fin)| Media     | Pendiente   |
| 08  | Pruebas unitarias                           | Alta      | Pendiente   |
| 09  | Documentación técnica                      | Baja      | Pendiente   |

---

## Fase 1: Extensión de Datos

**Objetivo fase:**
Extender el modelo de datos para soportar los nuevos campos de configuración.

**Implementacion fase:**
1. Añadir campos a `GroupConfig`:
   - `nightmode_mode`: str ("multimedia" | "silencio")
   - `nightmode_delete_media`: bool
   - `nightmode_silence`: bool
   - `nightmode_announcements`: bool
   - `nightmode_start_hour`: int (0-23)
   - `nightmode_end_hour`: int (0-23)

2. Mantener backward compatibility con campos existentes

---

## Fase 2: Interfaz de Usuario

**Objetivo fase:**
Implementar el nuevo diseño del menú con formato árbol y matriz de horario.

**Implementacion fase:**
1. Rediseñar `create_nightmode_menu()`:
   - Encabezado dinámico con estado del modo
   - Sección "Activo entre las horas" dinámica
   - Sección de anuncios (inicio/fin)

2. Crear `create_schedule_menu()`:
   - Matriz de 5x4 con botones para horas 0-23
   - Dos submenús: hora de inicio y hora de fin

3. Crear `create_mode_selection_menu()`:
   - Opciones: Eliminar multimedia / Silencio Global
   - Toggle para activar/desactivar cada modo

---

## Fase 3: Callbacks y Lógica

**Objetivo fase:**
Implementar los handlers para procesar las interacciones del usuario.

**Implementacion fase:**
1. Implementar `handle_toggle_nightmode` - Activar/desactivar modo nocturno

2. Implementar `handle_set_mode` - Cambiar entre modos:
   - `nightmode:mode:multimedia`
   - `nightmode:mode:silencio`

3. Implementar `handle_toggle_mode_action` - Alternar acción específica:
   - `nightmode:action:delete_media:on|off`
   - `nightmode:action:silence:on|off`

4. Implementar `handle_set_schedule_hour` - Seleccionar hora:
   - `nightmode:schedule:start:{hour}`
   - `nightmode:schedule:end:{hour}`

5. Implementar `handle_toggle_announcements` - Alternar anuncios

---

## Fase 4: Integración y Anuncios

**Objetivo fase:**
Conectar la configuración con el sistema de ejecución y anuncios.

**Implementacion fase:**
1. Modificar `is_active()` en `NightModeFeature`:
   - Verificar configuración de horario
   - Evaluar modo activo

2. Implementar lógica de acción según modo:
   - `Eliminación multimedia`: Eliminar mensajes con media
   - `Silencio global`: Silenciar/mutar usuarios nuevos

3. Implementar sistema de anuncios:
   - Notificación al activar modo nocturno
   - Notificación al desactivar modo nocturno

4. Integrar con sistema de ejecución del bot

---

## Fase 5: Pruebas y Documentación

**Objetivo fase:**
Garantizar funcionamiento correcto y documentar la implementación.

**Implementacion fase:**
1. Crear pruebas unitarias para los nuevos handlers

2. Probar flujo completo de configuración

3. Documentar casos de uso

4. Actualizar documentación técnica

---

## Notas de implementación

1. El valor por defecto será "Eliminación multimedia" para mantener compatibilidad
2. La matriz de horario usará botones inline para selección rápida
3. El encabezado mostrará el modo activo actualmente (dinámico)
4. Los anuncios de inicio/fin serán opcionales y configurables
5. Backward compatibility con la implementación anterior

---

## Descripción de Funcionalidad del Menú

Basado en el archivo `menu_modo_nocturno.md`, esta sección describe el comportamiento esperado del menú de Modo Nocturno.

### Encabezado del Menú (Formato Árbol)

El encabezado debe mostrar el estado actual en formato árbol:

```
Estado: 📸 Eliminar multimedia
├ Activo entre las horas 23:00 - 09:00
└ Anuncios de inicio y fin: ✅
```

**Componentes del encabezado:**
- **Estado** (nodo padre): Representa el estado global del modo nocturno. Descripción dinámica según el modo establecido:
  - "📸 Eliminación multimedia"
  - "🔇 Silencio global"
  - "📸 Eliminación multimedia + 🔇 Silencio global"
  
- **Activo entre las horas** (nodo hijo): Muestra el horario configurado. Es dinámico y refleja la configuración establecida en el menú "Establecer franquicia horaria"

- **Anuncios de inicio y fin**: Indicador de si los anuncios están activos (✅/❌)

### Opciones del Menú

| Opción | Descripción |
|--------|-------------|
| Apagado/Encendido | Menú para establecer el estado global del modo nocturno |
| Eliminar multimedia | Toggle para activar/desactivar eliminación de multimedia |
| Silencio Global | Toggle para activar/desactivar silencio global |
| Establecer franquicia horaria | Submenú para configurar horario de inicio/fin |

### Submenú Franja Horaria

```
⏰ Establecer franquicia horaria
├ 🕐 Hora inicio: 23:00
└ 🕑 Hora fin: 09:00
```

- Matriz de 5x4 con números del 0 al 23 (representando cada hora del día)
- Dos submenús: "Hora de inicio" y "Hora de fin"

### Descripción de Funcionalidad de Retorno

| Acción | Comportamiento Esperado |
|--------|------------------------|
| Toggle Estado (On/Off) | Actualiza el estado global del modo nocturno |
| Eliminar multimedia | Activa/desactiva el modo "Eliminación multimedia" |
| Silencio global | Activa/desactiva el modo "Silencio global" |
| Hora de inicio | Retorna matriz de horas (0-23) para seleccionar hora de inicio |
| Hora de fin | Retorna matriz de horas (0-23) para seleccionar hora de fin |

### Estados del Menú

**Modo Eliminar multimedia activo:**
```
Estado: 📸 Eliminación multimedia
├ Activo entre las horas 23:00 - 09:00
└ Anuncios de inicio y fin: ✅
```

**Modo Silencio global activo:**
```
Estado: 🔇 Silencio global
├ Activo entre las horas 23:00 - 09:00
└ Anuncios de inicio y fin: ✅
```

### Flujo de Interacción

1. **Activar/Desactivar**: Al tocar el nodo padre "Estado", se toggla el modo nocturno
2. **Cambiar modo**: Los nodos hijos permiten cambiar entre "Eliminar multimedia" y "Silencio global"
3. **Configurar horario**: Al seleccionar "Establecer franquicia horaria", se muestra submenú con opciones de inicio/fin
4. **Seleccionar hora**: Al tocar "Hora inicio" o "Hora fin", se muestra matriz 5x4 para selección

### Notas de la Descripción

1. El horario se muestra en formato HH:MM
2. La matriz de selección usa formato 5x4 (5 columnas x 4 filas para 20 horas)
3. El encabezado siempre muestra la hora actual del sistema
4. Los modos pueden combinarse (ambos activos simultáneamente)

---

## Verificación y Correcciones

Se realizaron las siguientes correcciones para asegurar que el menú cumpla con la descripción esperada:

### Corrección 1: Handler de horario

**Problema:** El handler `handle_time` mostraba un mensaje obsoleto en lugar del menú de horario.

**Solución:** Se modificó para mostrar el submenú de configuración de horario (`create_schedule_menu`).

```python
# Antes (incorrecto):
async def handle_time(callback, bot, data):
    await callback.answer("Usa /nightmode start/end <hora>...")

# Después (correcto):
async def handle_time(callback, bot, data):
    menu = create_schedule_menu(config)
    await callback.edit_message_text(text=menu.title, reply_markup=menu.to_keyboard())
```

### Corrección 2: Matriz de selección de hora

**Problema:** Al tocar "Hora inicio" o "Hora fin" no se mostraba la matriz de selección.

**Solución:** Se agregó el handler `handle_schedule_select_hour` para mostrar la matriz de horas (0-23) cuando se toca alguna de las opciones.

```python
async def handle_schedule_select_hour(callback, bot, data):
    # Muestra la matriz de selección de hora
    keyboard = build_schedule_keyboard(selecting_start, current_hour)
    await callback.edit_message_text(text=title, reply_markup=keyboard)
```

### Corrección 3: Registro de callbacks

Se actualizó el registro de callbacks para manejar correctamente las diferentes acciones:

```python
router.register_exact("mod:nightmode:schedule", handle_schedule_show)
router.register_exact("mod:nightmode:schedule:start", handle_schedule_select_hour)
router.register_exact("mod:nightmode:schedule:end", handle_schedule_select_hour)
router.register_callback("mod:nightmode:schedule:start", handle_schedule_hour)
router.register_callback("mod:nightmode:schedule:end", handle_schedule_hour)
```

### Corrección 4: Conflictos en callbacks de modo

**Problema:** Los callbacks "Cambiar modo de acción" respondían con "acción no reconocida" porque había conflictos entre `handle_action` y `handle_action_toggle`.

**Solución:** 
- Se eliminó el handler `handle_action` conflictivo
- Se registraron callbacks específicos para cada acción:
  - `mod:nightmode:action:delete_media` -> handle_action_toggle
  - `mod:nightmode:action:silence` -> handle_action_toggle

### Corrección 5: Registro de callbacks de horario

**Problema:** Los callbacks de horario no actualizaban el estado porque los patrones coincidían incorrectamente.

**Solución:**
- Se usa `register_exact` para mostrar menús (schedule, schedule:start, schedule:end)
- Se usa `register_callback` para guardar configuraciones (schedule:start:XX, schedule:end:XX)

```python
router.register_callback("mod:nightmode:toggle", handle_toggle)
router.register_callback("mod:nightmode:time", handle_time)
router.register_exact("mod:nightmode:show", handle_show_menu)
router.register_exact("mod:nightmode:mode", handle_mode_show)
router.register_callback("mod:nightmode:action:delete_media", handle_action_toggle)
router.register_callback("mod:nightmode:action:silence", handle_action_toggle)
router.register_exact("mod:nightmode:schedule", handle_schedule_show)
router.register_exact("mod:nightmode:schedule:start", handle_schedule_select_hour)
router.register_exact("mod:nightmode:schedule:end", handle_schedule_select_hour)
router.register_callback("mod:nightmode:schedule:start", handle_schedule_hour)
router.register_callback("mod:nightmode:schedule:end", handle_schedule_hour)
router.register_callback("mod:nightmode:announcements", handle_announcements)
```

### Archivos modificados

| Archivo | Cambios |
|---------|---------|
| `app/manager_bot/_features/nightmode/__init__.py` | handlers actualizados y nuevos callbacks registrados |
| `app/manager_bot/_menus/nightmode_menu.py` | Verificado que los callbacks son correctos |

### Estado de verificación

| Requisito | Estado |
|-----------|--------|
| Encabezado formato árbol | ✅ |
| Estado dinámico (multimedia/silencio) | ✅ |
| Horario dinámico | ✅ |
| Indicador de anuncios | ✅ |
| Toggle activar/desactivar | ✅ |
| Submenú cambio de modo | ✅ |
| Submenú horario | ✅ |
| Matriz de selección hora (0-23) | ✅ |
| Retorno de matriz al seleccionar hora | ✅ |