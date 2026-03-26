# Casos de Uso - Menú Modo Nocturno

## Casos de Uso

### Caso 1: Activar modo nocturno con eliminación de multimedia

**Actor:** Administrador del grupo

**Flujo:**
1. El administrador accede al menú de Modo Nocturno
2. Selecciona "🌙 Activar"
3. El sistema activa el modo con eliminación de multimedia por defecto
4. El menú muestra el estado actualizado

**Resultado esperado:**
- `nightmode_enabled = True`
- `nightmode_delete_media = True`
- `nightmode_silence = False`

---

### Caso 2: Cambiar a modo silencio global

**Actor:** Administrador del grupo

**Flujo:**
1. El administrador accede al menú de Modo Nocturno
2. Selecciona "Cambiar modo de acción"
3. Selecciona "🔇 Silencio global" para activar
4. Opcionalmente desactiva "📸 Eliminación multimedia"

**Resultado esperado:**
- `nightmode_delete_media = False`
- `nightmode_silence = True`

---

### Caso 3: Configurar horario personalizado

**Actor:** Administrador del grupo

**Flujo:**
1. El administrador accede al menú de Modo Nocturno
2. Selecciona "⏰ Establecer franquicia horaria"
3. Selecciona "🕐 Hora inicio: 22:00"
4. Elige la hora de la matriz
5. Repite para hora fin

**Resultado esperado:**
- `nightmode_start = "22:00"`
- `nightmode_end = "06:00"`

---

### Caso 4: Desactivar anuncios

**Actor:** Administrador del grupo

**Flujo:**
1. El administrador accede al menú de Modo Nocturno
2. Selecciona "🔔 Anuncios: Activar" para desactivar
3. El sistema guarda la configuración sin anuncios

**Resultado esperado:**
- `nightmode_announcements = False`
- No se enviarán notificaciones de inicio/fin

---

## Ejemplos de Configuración

### Configuración 1: Solo eliminación multimedia

```python
config.nightmode_enabled = True
config.nightmode_delete_media = True
config.nightmode_silence = False
config.nightmode_start = "23:00"
config.nightmode_end = "07:00"
```

### Configuración 2: Solo silencio global

```python
config.nightmode_enabled = True
config.nightmode_delete_media = False
config.nightmode_silence = True
config.nightmode_start = "23:00"
config.nightmode_end = "07:00"
```

### Configuración 3: Ambos modos activos

```python
config.nightmode_enabled = True
config.nightmode_delete_media = True
config.nightmode_silence = True
config.nightmode_start = "22:00"
config.nightmode_end = "09:00"
```

---

## Diagramas de Flujo

### Flujo de activación

```
Admin accede al menú
        ↓
Selecciona "🌙 Activar"
        ↓
nightmode_enabled = True
        ↓
Se habilita delete_media por defecto
        ↓
Menú se actualiza con nuevo estado
```

### Flujo de cambio de modo

```
Admin accede al menú
        ↓
Selecciona "Cambiar modo de acción"
        ↓
Muestra menú de selección
        ↓
Admin toggla opciones
        ↓
Guarda configuración
        ↓
Menú principal se actualiza
```

### Flujo de configuración de horario

```
Admin accede al menú
        ↓
Selecciona "⏰ Establecer horario"
        ↓
Muestra submenú con inicio/fin
        ↓
Admin selecciona hora
        ↓
Matriz de 0-23 se muestra
        ↓
Admin elige hora
        ↓
Guarda y actualiza
```

---

## Notas de Implementación

1. Por defecto se activa "eliminación de multimedia"
2. Ambos modos pueden estar activos simultáneamente
3. El horario se configura en formato HH:00
4. Los anuncios están habilitados por defecto
5.兼容旧版本 con configuraciones anteriores