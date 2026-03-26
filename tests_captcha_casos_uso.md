# Tests de Caso de Uso - Captcha

Fecha: 2026-03-20
Version: 1.0
Referencia: implementacion_captcha_completada.md

---

## Casos de Uso

### Caso de Uso 1: Activar Captcha

**Descripcion:** El administrador activa el sistema de captcha para su grupo.

**Pasos:**
1. El administrador ejecuta el comando /config
2. Navega al menu de Captcha
3. Presiona el boton "Estado"
4. Selecciona "Activar"

**Resultado esperado:**
- `captcha_enabled` = True
- El menu muestra "Estado: Activo ✅"
- Se muestra el menu de Captcha con todas las opciones habilitadas

**Datos de prueba:**
```
chat_id: 123456
callback: captcha:toggle:on
```

---

### Caso de Uso 2: Desactivar Captcha

**Descripcion:** El administrador desactiva el sistema de captcha.

**Pasos:**
1. El administrador esta en el menu de Captcha
2. Presiona el boton "Estado"
3. Selecciona "Desactivar"

**Resultado esperado:**
- `captcha_enabled` = False
- El menu muestra "Estado: Apagado ❌"

**Datos de prueba:**
```
chat_id: 123456
callback: captcha:toggle:off
```

---

### Caso de Uso 3: Cambiar Modo a Boton

**Descripcion:** El administrador cambia el tipo de captcha a modo boton.

**Pasos:**
1. El administrador esta en el menu de Captcha
2. Presiona el boton "Modo"
3. Selecciona "Boton"

**Resultado esperado:**
- `captcha_mode` = "button"
- El menu muestra "Modo: Boton"
- El captcha enviado sera un boton simple "Verificar"

**Datos de prueba:**
```
chat_id: 123456
callback: captcha:mode:button
```

---

### Caso de Uso 4: Cambiar Modo a Matematicas

**Descripcion:** El administrador cambia el tipo de captcha a modo matematico.

**Pasos:**
1. El administrador esta en el menu de Captcha
2. Presiona el boton "Modo"
3. Selecciona "Matematicas"

**Resultado esperado:**
- `captcha_mode` = "math"
- El menu muestra "Modo: Matematicas"
- El captcha enviado sera una suma/resta de numeros pequenos

**Datos de prueba:**
```
chat_id: 123456
callback: captcha:mode:math
```

---

### Caso de Uso 5: Cambiar Tiempo a 5 Minutos

**Descripcion:** El administrador cambia el tiempo limite del captcha a 5 minutos.

**Pasos:**
1. El administrador esta en el menu de Captcha
2. Presiona el boton "Tiempo"
3. Selecciona "5 min"

**Resultado esperado:**
- `captcha_timeout` = 300
- El menu muestra "Tiempo: 5 Minutos"

**Datos de prueba:**
```
chat_id: 123456
callback: captcha:time:300
```

---

### Caso de Uso 6: Cambiar Tiempo a 30 Minutos

**Descripcion:** El administrador cambia el tiempo limite del captcha a 30 minutos.

**Pasos:**
1. El administrador esta en el menu de Captcha
2. Presiona el boton "Tiempo"
3. Selecciona "30 min"

**Resultado esperado:**
- `captcha_timeout` = 1800
- El menu muestra "Tiempo: 30 Minutos"

**Datos de prueba:**
```
chat_id: 123456
callback: captcha:time:1800
```

---

### Caso de Uso 7: Cambiar Castigo a Ban

**Descripcion:** El administrador cambia la accion al fallar el captcha a ban.

**Pasos:**
1. El administrador esta en el menu de Captcha
2. Presiona el boton "Castigo"
3. Selecciona "Ban"

**Resultado esperado:**
- `captcha_fail_action` = "ban"
- El menu muestra "Castigo: Ban"
- Si el usuario falla, sera baneado permanentemente

**Datos de prueba:**
```
chat_id: 123456
callback: captcha:fail_action:ban
```

---

### Caso de Uso 8: Cambiar Castigo a Silenciar

**Descripcion:** El administrador cambia la accion al fallar el captcha a silenciar.

**Pasos:**
1. El administrador esta en el menu de Captcha
2. Presiona el boton "Castigo"
3. Selecciona "Silenciar"

**Resultado esperado:**
- `captcha_fail_action` = "mute"
- El menu muestra "Castigo: Silenciar"

**Datos de prueba:**
```
chat_id: 123456
callback: captcha:fail_action:mute
```

---

### Caso de Uso 9: Activar Eliminacion de Mensaje

**Descripcion:** El administrador activa la eliminacion del mensaje de servicio.

**Pasos:**
1. El administrador esta en el menu de Captcha
2. Presiona el boton "Eliminar mensaje"
3. Selecciona "Encendido"

**Resultado esperado:**
- `captcha_delete_service_message` = True
- El menu muestra "Eliminar mensaje de servicio: Encendido"

**Datos de prueba:**
```
chat_id: 123456
callback: captcha:delete:toggle:on
```

---

### Caso de Uso 10: Generar Captcha Matematico

**Descripcion:** Se genera un captcha de tipo matematico para un nuevo usuario.

**Pasos:**
1. Un nuevo usuario se une al grupo
2. El sistema detecta que `captcha_enabled` = True
3. El sistema genera un captcha matematico

**Resultado esperado:**
- Se genera un desafio con pregunta matematica
- La respuesta es un numero entero
- El desafio se almacena en memoria

**Datos de prueba:**
```
user_id: 789
chat_id: 123456
captcha_mode: math
```

---

### Caso de Uso 11: Resolver Captcha Correctamente

**Descripcion:** El usuario resuelve el captcha correctamente.

**Pasos:**
1. El usuario recibe el captcha matematico
2. El usuario envia la respuesta correcta

**Resultado esperado:**
- La verificacion devuelve True
- El desafio se elimina de memoria
- El usuario obtiene permisos para enviar mensajes

**Datos de prueba:**
```
challenge_id: "123456:789:1234"
answer: "8" (ejemplo)
```

---

### Caso de Uso 12: Fallar Captcha

**Descripcion:** El usuario falla el captcha (respuesta incorrecta o tiempo agotado).

**Pasos:**
1. El usuario recibe el captcha matematico
2. El usuario envia una respuesta incorrecta
3. Se agotan los intentos o el tiempo

**Resultado esperado:**
- La verificacion devuelve False
- Se ejecuta la accion configurada (`captcha_fail_action`)
- Puede ser: kick, ban, o mute

**Datos de prueba:**
```
challenge_id: "123456:789:1234"
answer: "5" (incorrecto)
captcha_fail_action: kick
```

---

### Caso de Uso 13: Ver Menu de Captcha

**Descripcion:** El administrador ve el menu de configuracion de Captcha.

**Pasos:**
1. El administrador ejecuta /config
2. Navega a la seccion de Captcha

**Resultado esperado:**
- Se muestra el menu con todos los valores actuales
- Todos los valores dinamicos se muestran correctamente

**Verificaciones:**
- Estado muestra iconos correctos (✅/❌)
- Tiempo muestra formato legible ("3 Minutos")
- Modo muestra el modo actual
- Castigo muestra la accion actual
- Eliminar mensaje muestra el estado actual

---

### Caso de Uso 14: Navegacion entre Submenus

**Descripcion:** El administrador navega entre los submenus de Captcha.

**Pasos:**
1. El administrador esta en el menu de Captcha
2. Presiona "Modo"
3. Ve las opciones de modo
4. Presiona "Volver"
5. Presiona "Tiempo"
6. Ve las opciones de tiempo
7. Presiona "Volver"

**Resultado esperado:**
- Cada submenu muestra el valor actual resaltado
- Los cambios se reflejan en el menu principal

**Callbacks de navegacion:**
```
captcha:mode:show -> Submenu modo
captcha:time:show -> Submenu tiempo
captcha:fail_action:show -> Submenu castigo
captcha:show -> Menu principal
```

---

### Caso de Uso 15: Configuracion Completa

**Descripcion:** El administrador configura todos los parametros del captcha.

**Pasos:**
1. Activa el captcha
2. Selecciona modo "Matematicas"
3. Configura tiempo "5 minutos"
4. Selecciona castigo "Ban"
5. Activa eliminacion de mensajes

**Resultado esperado:**
- Todos los valores se guardan correctamente
- La configuracion es persistente

**Estado final:**
```python
captcha_enabled = True
captcha_mode = "math"
captcha_timeout = 300
captcha_fail_action = "ban"
captcha_delete_service_message = True
```

---

## Matriz de Test Cases

| ID | Caso | Input | Output | Estado |
|----|------|-------|--------|--------|
| TC01 | Activar Captcha | toggle:on | enabled=True | ⏳ |
| TC02 | Desactivar Captcha | toggle:off | enabled=False | ⏳ |
| TC03 | Modo Boton | mode:button | mode="button" | ⏳ |
| TC04 | Modo Matematicas | mode:math | mode="math" | ⏳ |
| TC05 | Modo Reglamento | mode:rules | mode="rules" | ⏳ |
| TC06 | Modo Prueba | mode:quiz | mode="quiz" | ⏳ |
| TC07 | Tiempo 15 seg | time:15 | timeout=15 | ⏳ |
| TC08 | Tiempo 1 min | time:60 | timeout=60 | ⏳ |
| TC09 | Tiempo 5 min | time:300 | timeout=300 | ⏳ |
| TC10 | Tiempo 30 min | time:1800 | timeout=1800 | ⏳ |
| TC11 | Castigo Kick | fail_action:kick | action="kick" | ⏳ |
| TC12 | Castigo Ban | fail_action:ban | action="ban" | ⏳ |
| TC13 | Castigo Silenciar | fail_action:mute | action="mute" | ⏳ |
| TC14 | Eliminar On | delete:toggle:on | delete=True | ⏳ |
| TC15 | Eliminar Off | delete:toggle:off | delete=False | ⏳ |
| TC16 | Generar Math | generate(math) | challenge created | ⏳ |
| TC17 | Generar Boton | generate(button) | challenge created | ⏳ |
| TC18 | Verificar Correcto | verify(id, answer) | True | ⏳ |
| TC19 | Verificar Incorrecto | verify(id, wrong) | False | ⏳ |
| TC20 | Ver Menu | show | menu displayed | ⏳ |
