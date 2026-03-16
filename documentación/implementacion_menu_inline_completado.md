# Implementación - Tarea 1 y 2: Corrección FakeCallbackQuery + Mejorar Logging

**Fecha**: 2026-03-13
**Estado**: ✅ Completado (ambas tareas)

---

## Problema identificado

El menú inline se mostraba correctamente pero al pulsar botones:
- El log mostraba `INFO Callback received: 'antispam:show'`
- Pero el bot no respondía en el chat

**Causa raíz (Tarea 1)**: En `menu_engine.py`, el `FakeCallbackQuery.answer()` usaba incorrectamente `self.data` (el callback_data como "antispam:show") como `callback_query_id`, cuando debería usar el ID real del callback query de Telegram.

---

## Tarea 1: Cambios realizados

### Archivo: `app/manager_bot/transport/telegram/menu_engine.py`

#### 1. Agregado parámetro `callback_query_id` a `handle_callback_query_raw`

```python
# Antes:
async def handle_callback_query_raw(
    self,
    callback_data: str,
    chat_id: int,
    message_id: Optional[int],
    user_id: int,
) -> Any:

# Después:
async def handle_callback_query_raw(
    self,
    callback_data: str,
    callback_query_id: Optional[str],  # NUEVO
    chat_id: int,
    message_id: Optional[int],
    user_id: int,
) -> Any:
```

#### 2. Modificado constructor de FakeCallbackQuery

```python
# Añadido: self.callback_query_id = callback_query_id
```

#### 3. Corregido método answer()

```python
# Antes (BUG):
callback_query_id=self.data  # usaba el callback_data

# Después (CORRECTO):
callback_query_id=self.callback_query_id  # usa el ID real
```

---

## Tarea 2: Mejorar logging y manejo de errores ✅

(ya documentado anteriormente)

---

## Tarea 3: Registrar callbacks para toggles ✅

### Problema identificado

Los callbacks de toggle (ej: `antispam:toggle`) no se ejecutaban porque `register_prefix("antispam", ...)` los capturaba PRIMERO.

### Solución implementada

Cambiar `register_prefix` por `register_exact` para solo capturar `X:show`.

**Archivo**: `app/manager_bot/transport/telegram/menu_engine.py` (líneas 88-106)

### Verificación

| Componente | Estado |
|------------|--------|
| `_register_features` llamado | ✅ |
| Orden de prioridad corregido | ✅ |

---

## Tarea 4: Verificar RequestsTelegramClient ✅

### Estado: Ya implementado

El método `answer_callback_query` existe en `infrastructure.py:50-58`.

---

## Verificaciones realizadas

#### 1. handle_menu_show - Mejorado (líneas 71-84)

```python
async def handle_menu_show(callback, bot: "Bot", data: str):
    """Handle menu show callbacks like info:show, mod:show, etc."""
    logger.info(f"handle_menu_show called with data={data}")
    parts = data.split(":")
    if len(parts) >= 2:
        menu_id = parts[0]
        logger.debug(f"Attempting to show menu: {menu_id}")
        try:
            await self.show_menu_by_callback(callback, bot, menu_id)
            logger.info(f"Menu {menu_id} displayed successfully")
        except Exception as e:
            logger.error(f"Error showing menu {menu_id}: {e}", exc_info=True)
            await callback.answer(f"⚠️ Error al mostrar menú: {str(e)[:50]}", show_alert=True)
    else:
        logger.warning(f"Invalid menu callback data: {data}")
        await callback.answer("Menú no encontrado", show_alert=True)
```

#### 2. show_menu_by_callback - Logging mejorado (líneas 149-199)

- Reemplazados todos los `print()` con `logger.debug/info/warning/error`
- Agregado `exc_info=True` en errores para stack trace completo
- Mejorados mensajes de logging para mejor trazabilidad

#### 3. handle_callback_query_raw - Logging mejorado

```python
logger.info(f"Handling callback: data={callback_data}, callback_query_id={callback_query_id}, chat_id={chat_id}, user_id={user_id}")
```

### Archivo: `app/manager_bot/transport/telegram/callback_router.py`

#### 1. Método handle - Logging mejorado (líneas 96-140)

- Reemplazados `print()` con `logger.debug/info/warning`
- Agregado `exc_info=True` en manejo de excepciones
- Mejorada trazabilidad de matching de handlers

---

## Verificaciones realizadas

| Componente | Estado | Notas |
|------------|--------|-------|
| `RequestsTelegramClient.answer_callback_query` | ✅ | Ya existe en `infrastructure.py:50-58` |
| Parámetro en `handlers.py` | ✅ | Ya se pasaba `callback_query_id` |
| Logging estructurado | ✅ | Todos los print() reemplazados |
| Manejo de errores | ✅ | Try-catch con feedback al usuario |

---

## Flujo corregido

```
1. Usuario presiona botón en Telegram
2. Webhook recibe callback_query con:
   - callback_query.id (ej: "123456789:abc123")
   - callback_query.data (ej: "antispam:show")
3. handlers.py:115-121 llama a:
   handle_callback_query_raw(
       callback_data="antispam:show",
       callback_query_id="123456789:abc123",  // AHORA SE PASA
       chat_id=...,
       message_id=...,
       user_id=...
   )
4. FakeCallbackQuery ahora tiene callback_query_id correcto
5. callback.answer("Texto") ahora llama a answerCallbackQuery con ID correcto
6. Telegram muestra el alert/toast al usuario
7. Logging muestra trazabilidad completa
```

---

## Tarea 4: Verificar RequestsTelegramClient ✅

### Estado: Ya implementado

El método `answer_callback_query` ya existe correctamente implementado.

**Archivo**: `app/webhook/infrastructure.py:50-58`

```python
def answer_callback_query(self, *, callback_query_id: str, text: Optional[str] = None, show_alert: bool = False) -> Dict[str, Any]:
    url = f"https://api.telegram.org/bot{self._bot_token}/answerCallbackQuery"
    payload = {"callback_query_id": callback_query_id}
    if text:
        payload["text"] = text
    if show_alert:
        payload["show_alert"] = True
    response = self._requests.post(url, json=payload, timeout=self._timeout)
    return {"status_code": response.status_code, "text": response.text}
```

### Verificación

| Método | Estado |
|--------|--------|
| `answer_callback_query` existe | ✅ `infrastructure.py:50` |
| Envía a API de Telegram | ✅ |
| Soporta text y show_alert | ✅ |

---

## Tarea 5: Implementar persistencia de configuración ✅

### Estado anterior

- Usaba `InMemoryConfigStorage` por defecto (no persistía entre sesiones)
- Los toggles no se guardaban

### Solución implementada

Modificado `create_menu_engine` en `app/manager_bot/menu_service.py` para leer configuración del entorno:

```python
def create_menu_engine(
    storage_type: str = None,  # Lee de STORAGE_TYPE env var
    database_url: str = None,  # Lee de DATABASE_URL env var
    redis_url: str = None,     # Lee de REDIS_URL env var
):
    if storage_type is None:
        storage_type = os.getenv("STORAGE_TYPE", "memory")
    if database_url is None:
        database_url = os.getenv("DATABASE_URL")
    if redis_url is None:
        redis_url = os.getenv("REDIS_URL")
```

### Implementaciones disponibles

| Storage | Estado | Ubicación |
|---------|--------|-----------|
| InMemoryConfigStorage | ✅ | `storage.py:37-53` |
| PostgresConfigStorage | ✅ | `storage.py:56-133` |
| RedisConfigStorage | ✅ | `storage.py:136-189` |

### Variables de entorno requeridas

```bash
# Para PostgreSQL
STORAGE_TYPE=postgres
DATABASE_URL=postgresql://user:pass@host/db

# O para Redis
STORAGE_TYPE=redis
REDIS_URL=redis://localhost:6379/0
```

---

## Tarea 7: Testing del flujo completo ✅

### Tests creados

Archivo: `tests/manager_bot/test_callback_flow.py`

| Test | Estado |
|------|--------|
| test_exact_callback_matching | ✅ Pasa |
| test_prefix_callback_matching | ✅ Pasa |
| test_priority_exact_over_prefix | ✅ Pasa |
| test_callback_answer_is_called | ✅ Pasa |
| test_fallback_handler | ✅ Pasa |
| test_show_menu_callback_data | ⏭️ Saltado (requiere integración completa) |
| test_antispam_toggle_callback | ✅ Pasa |
| test_full_callback_flow | ✅ Pasa |
| test_callback_data_extraction | ✅ Pasa |

**Resultado**: 8 passed, 1 skipped

### Bug corregido durante testing

Se encontró y corrigió un bug en `callback_router.py`:
- El método `matches()` no manejaba correctamente los patrones de prefijo
- Corregido para verificar `data.startswith(pattern)` cuando el patrón termina con `:`

### Archivo corregido
- `app/manager_bot/transport/telegram/callback_router.py` (línea 34-42)

---

## Resumen de cambios

| Tarea | Archivo | Estado |
|-------|---------|--------|
| Tarea 1 | menu_engine.py | ✅ FakeCallbackQuery |
| Tarea 2 | menu_engine.py, callback_router.py | ✅ Logging |
| Tarea 3 | menu_engine.py | ✅ register_exact |
| Tarea 4 | infrastructure.py | ✅ Ya existía |
| Tarea 5 | menu_service.py | ✅ Persistencia env |
| Tarea 6 | handlers.py | ✅ Fallback |
| Tarea 7 | callback_router.py, test_callback_flow.py | ✅ Tests |

---

*Documento actualizado: 2026-03-13*
