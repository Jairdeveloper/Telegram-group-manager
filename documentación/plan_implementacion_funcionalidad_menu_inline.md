# Plan de Implementación - Funcionalidad Menú Inline

## Diagnóstico del Problema Actual

El menú inline se muestra correctamente con `/config`, pero al pulsar botones:
- **Síntoma**: Console log muestra `INFO Callback received: 'antispam:show'` pero el bot no responde en el chat
- **Causa raíz**: La implementación de `handle_callback_query_raw` en `menu_engine.py` tiene bugs en el `FakeCallbackQuery`:
  1. `answer()` pasa `callback_query_id=self.data` (debería ser el ID real del callback query)
  2. `edit_message_text()` no responde correctamente al usuario
  3. Falta `answer_callback_query` real en el cliente de Telegram

---

## Tarea 1: Corregir FakeCallbackQuery en MenuEngine

**Archivo**: `app/manager_bot/transport/telegram/menu_engine.py`

### Problema identificado (líneas 219-225):
```python
async def answer(self, text: str = None, show_alert: bool = False):
    if text:
        self._client.answer_callback_query(
            callback_query_id=self.data,  # BUG: debería ser el ID real
            text=text,
            show_alert=show_alert
        )
```

### Solución:
- Agregar `callback_query_id` al constructor de `FakeCallbackQuery`
- Asegurar que `answer_callback_query` se llama correctamente

**Cambios necesarios**:
1. Modificar `FakeCallbackQuery.__init__` para aceptar `callback_query_id`
2. Modificar `FakeCallbackQuery.answer` para usar el ID correcto
3. Verificar que `RequestsTelegramClient` tiene método `answer_callback_query`

---

## Tarea 2: Mejorar logging y manejo de errores

**Archivos**: 
- `app/manager_bot/transport/telegram/menu_engine.py`
- `app/manager_bot/transport/telegram/callback_router.py`

### Mejoras:
1. Agregar logs más descriptivos en cada paso del flujo
2. Manejar excepciones en `handle_menu_show` para mostrar errores al usuario
3. Agregar fallback cuando `edit_message_text` falla

### Código a agregar en `handle_menu_show` (menu_engine.py:71-80):
```python
async def handle_menu_show(callback, bot: "Bot", data: str):
    parts = data.split(":")
    if len(parts) >= 2:
        menu_id = parts[0]
        try:
            await self.show_menu_by_callback(callback, bot, menu_id)
        except Exception as e:
            logger.error(f"Error showing menu {menu_id}: {e}")
            await callback.answer(f"Error: {str(e)[:50]}", show_alert=True)
    else:
        await callback.answer("Menú no encontrado", show_alert=True)
```

---

## Tarea 3: Registrar callbacks para toggles

**Archivo**: `app/manager_bot/menu_service.py`

### Problema: Los callbacks de toggle (ej: `antispam:toggle`) están registrados en los features pero pueden no ejecutarse correctamente.

### Verificar:
1. Que `_register_features` se llama durante inicialización
2. Que los callbacks `antispam:toggle`, `antispam:spamwatch:toggle`, etc. funcionan

### Verificar en `menu_service.py:145-176`:
- `_register_features(callback_router, config_storage)` se ejecuta
- Cada feature tiene `register_callbacks` correctamente implementado

---

## Tarea 4: Verificar RequestsTelegramClient

**Archivo**: `app/webhook/infrastructure.py`

### Método necesario:
```python
def answer_callback_query(self, callback_query_id: str, text: str = None, show_alert: bool = False):
    """Answer a callback query."""
    # Implementar si no existe
```

### Verificar que existe y funciona correctamente.

---

## Tarea 5: Implementar persistencia de configuración

**Archivos**:
- `app/manager_bot/config/storage.py`
- `app/manager_bot/config/group_config.py`

### Estado actual: 
- Usa `InMemoryConfigStorage` por defecto
- Los toggles no persisten entre sesiones

### Solución:
- Implementar `PostgresConfigStorage` para persistencia real
- O asegurar que Redis está configurado para caché

---

## Tarea 6: Flujo completo de respuesta al callback

**Flujo esperado**:
1. Usuario presiona botón → Telegram envía `callback_query`
2. Webhook recibe update tipo `callback_query`
3. `handlers.py:process_update_impl` detecta `dispatch.kind == "callback_query"`
4. Llama a `menu_engine.handle_callback_query_raw()`
5. `callback_router.handle()` encuentra el handler correcto
6. Handler ejecuta lógica (toggle, show menu, etc.)
7. **Handler debe llamar `callback.answer()` para mostrar feedback**
8. Si es navegación, llama `callback.edit_message_text()` para actualizar menú

### Puntos de verificación:
| Paso | Verificar |
|------|-----------|
| 1 | Callback llega al webhook |
| 2 | `dispatch.kind == "callback_query"` es True |
| 3 | `menu_engine.handle_callback_query_raw` es llamado |
| 4 | `callback_router.handle()` encuentra handler |
| 5 | Handler ejecuta lógica correctamente |
| 6 | `callback.answer()` responde al usuario |
| 7 | Si navegación, `edit_message_text` actualiza el menú |

---

## Tarea 7: Testing del flujo completo

### Tests a crear/verificar:
1. **Test de integración**: `test_callback_query_flow`
2. **Test unitario**: `test_antispam_toggle_callback`
3. **Test manual**: Verificar con BotFather

### Comandos de verificación:
```bash
# Ver logs en tiempo real
tail -f logs/app.log | grep -i callback

# Verificar menús registrados
curl -X POST http://localhost:8080/debug/menus
```

---

## Orden de implementación recomendado

| Prioridad | Tarea | Complejidad | Impacto |
|-----------|-------|-------------|---------|
| 1 | Corregir FakeCallbackQuery | Media | **Alto** - Bloquea toda funcionalidad |
| 2 | Mejorar logging | Baja | Medio - Facilita debug |
| 3 | Verificar callbacks de features | Baja | **Alto** - Habilita toggles |
| 4 | Verificar TelegramClient | Media | **Alto** - Necesario para ответ |
| 5 | Implementar persistencia | Alta | Bajo - Mejora UX |
| 6 | Testing | Media | Medio - Garantiza calidad |

---

## Archivos a modificar

1. `app/manager_bot/transport/telegram/menu_engine.py` - FakeCallbackQuery, handle_menu_show
2. `app/webhook/infrastructure.py` - answer_callback_query en RequestsTelegramClient
3. `app/manager_bot/transport/telegram/callback_router.py` - Mejorar logging

---

## Éxito medible

- [ ] Al presionar cualquier botón, el bot muestra feedback visual (toast/alert)
- [ ] Los toggles guardan el estado en configuración
- [ ] La navegación entre menús funciona correctamente
- [ ] Los logs muestran el flujo completo de ejecución

---

*Documento generado: 2026-03-13*
*Basado en análisis de código existente*
