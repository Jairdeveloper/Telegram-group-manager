# Propuesta de implementacion: Captcha

Fecha: 2026-03-20
Version: 2.0
Referencia: captcha.md

---

## Resumen

Proponer una implementacion completa del sistema de Captcha siguiendo el diseno de UI especificado en captcha.md.

---

## UI Propuesta

### Encabezado

```
🧠 Captcha
Al activar el captcha, cuando un usuario ingrese al grupo no podra enviar mensajes hasta que haya confirmado que no es un robot.

🕑 Tambien puedes decidir un CASTIGO en caso de que no resuelva el captcha dentro del tiempo establecido a continuacion y si se borrara o no el mensaje de servicio en caso de fallar al completarla.

Estado: Activo ✅
🕒 Tiempo: 3 Minutos
⛔️ Castigo: Kick
🗂 Modo: Matematicas
  └ El usuario tendra que resolver un sencillo cuestionario de matematicas.
🗑 Eliminar mensaje de servicio: Apagado
```

### Estados dinamicos

| Campo | Posibles valores | Icono |
|-------|-----------------|-------|
| Estado | Activo / Apagado | ✅ / ❌ |
| Tiempo | 15 seg, 30 seg, 1 min, 2 min, 3 min, 5 min, 10 min, 15 min, 20 min, 30 min | 🕒 |
| Castigo | Ban, Silenciar, Kick | ⛔️ |
| Modo | Boton, Presentacion, Matematicas, Reglamento, Prueba | 🗂 |
| Eliminar mensaje | Encendido, Apagado | 🗑 |

### Modos de Captcha

| Modo | Descripcion | Implementacion |
|------|-------------|----------------|
| Boton | Boton simple para verificar | Boton inline "Verificar" |
| Presentacion | Mensaje de bienvenida | Texto personalizado + boton |
| Matematicas | Cuestionario matematico | Sumas/restas simples |
| Reglamento | Aceptar reglas | Checkbox + aceptar |
| Prueba | Prueba configurable | Preguntas de opcion multiple |

---

## Estructura de menus

### Menu principal Captcha

```
🧠 Captcha

Estado: Activo ✅
🕒 Tiempo: 3 Minutos
⛔️ Castigo: Kick
🗂 Modo: Matematicas
🗑 Eliminar mensaje de servicio: Apagado

[Estado]
[Modo]
[Tiempo]
[Castigo]
[Eliminar mensaje]
[Volver]
```

### Submenu: Modo

```
Modo de Captcha

🗂 Modo actual: Matematicas

[Boton]
[Presentacion]
[Matematicas]
[Reglamento]
[Prueba]

[Volver]
```

### Submenu: Tiempo

```
Tiempo de Captcha

🕒 Tiempo actual: 3 Minutos

[15 seg]
[30 seg]
[1 min]
[2 min]
[3 min]
[5 min]
[10 min]
[15 min]
[20 min]
[30 min]

[Volver]
```

### Submenu: Castigo

```
Castigo por Fallar

⛔️ Castigo actual: Kick

[Ban]
[Silenciar]
[Kick]

[Volver]
```

### Submenu: Eliminar mensaje

```
Eliminar mensaje de servicio

🗑 Estado actual: Apagado

[Encendido]
[Apagado]

[Volver]
```

---

## Modelo de configuracion (GroupConfig)

### Campos requeridos

| Campo | Tipo | Default | Descripcion |
|-------|------|---------|-------------|
| captcha_enabled | bool | False | Habilitar/deshabilitar captcha |
| captcha_mode | str | "math" | Modo de captcha |
| captcha_timeout | int | 180 | Tiempo limite en segundos |
| captcha_fail_action | str | "kick" | Accion al fallar |
| captcha_delete_service_message | bool | False | Eliminar mensaje de servicio |

### Modos de Captcha

| Valor | Modo | Descripcion |
|-------|------|-------------|
| button | Boton | Boton simple "Verificar" |
| presentation | Presentacion | Mensaje de bienvenida |
| math | Matematicas | Cuestionario matematico |
| rules | Reglamento | Aceptar reglas |
| quiz | Prueba | Preguntas configurables |

### Acciones al fallar

| Valor | Accion | Descripcion |
|-------|--------|-------------|
| kick | Kick | Expulsar al usuario |
| ban | Ban | Banear permanentemente |
| mute | Silenciar | Silenciar al usuario |

### Tiempos disponibles

| Valor | Segundos | Descripcion |
|-------|----------|-------------|
| 15_seg | 15 | 15 segundos |
| 30_seg | 30 | 30 segundos |
| 1_min | 60 | 1 minuto |
| 2_min | 120 | 2 minutos |
| 3_min | 180 | 3 minutos |
| 5_min | 300 | 5 minutos |
| 10_min | 600 | 10 minutos |
| 15_min | 900 | 15 minutos |
| 20_min | 1200 | 20 minutos |
| 30_min | 1800 | 30 minutos |

---

## Formato de Callbacks

| Callback | Accion |
|----------|--------|
| captcha:toggle | Alternar enabled |
| captcha:mode:<modo> | Cambiar modo |
| captcha:time:<segundos> | Cambiar tiempo |
| captcha:fail_action:<accion> | Cambiar castigo |
| captcha:delete_toggle | Alternar eliminar mensaje |
| captcha:show | Mostrar menu principal |

---

## Plan de implementacion

### Fase 1: Modelo de datos
- Actualizar campos en GroupConfig
- Agregar nuevos campos: captcha_mode, captcha_fail_action, captcha_delete_service_message

### Fase 2: Menu principal
- Crear menu con estado dinamico
- Mostrar todos los valores actuales

### Fase 3: Submenus
- Crear submenu Modo
- Crear submenu Tiempo
- Crear submenu Castigo
- Crear submenu Eliminar mensaje

### Fase 4: Callbacks
- Registrar todos los callbacks
- Implementar handlers para cada accion

---

## Archivos a crear/modificar

| Archivo | Accion | Descripcion |
|---------|--------|-------------|
| app/manager_bot/_menus/captcha_menu.py | Crear | Todos los menus de captcha |
| app/manager_bot/_config/group_config.py | Modificar | Nuevos campos |
| app/manager_bot/_features/captcha/__init__.py | Modificar | Callbacks y logica |

---

## Estados de Conversation

| Estado | Descripcion |
|--------|------------|
| waiting_captcha_answer | Esperando respuesta de captcha |

---

## Notas

- El archivo captcha_menu.py aun no existe y debe crearse
- La implementacion debe seguir el patron de antispan para menus
- Los menus deben mostrar el estado dinamico en el titulo
