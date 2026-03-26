# Debug 004 - /config responde "no response"

Fecha: 2026-03-24

## Resumen

El comando `/config` devuelve el texto `(no response)`. Este bug es similar al bug 003, pero la causa raíz es diferente.

## Síntomas

- Al enviar `/config`, el bot responde `(no response)`
- No se muestra ningún menú

## Diagnóstico

Se verificó el flujo del comando `/config`:

1. `handle_enterprise_command()` en `app/enterprise/transport/handlers.py:219` retorna:
   ```python
   return {"status": "menu", "menu_id": "main"}
   ```

2. En `app/webhook/handlers.py:512`:
   ```python
   if result.get("status") == "menu":
       menu_engine = get_menu_engine()
       if menu_engine:
           await menu_engine.send_menu_message(...)
           return
   ```

3. Si `menu_engine` es `None`, el código cae a la línea 530:
   ```python
   reply = result.get("response_text", "(no response)")
   ```

## Pruebas de diagnóstico

```python
from app.manager_bot._menu_service import create_menu_engine
engine, limiter = create_menu_engine()
```

**Error encontrado:**
```
NameError: name 'handle_show_menu' is not defined
```

## Causa raíz

El handler `handle_show_menu` estaba siendo registrado en `NightModeFeature.register_callbacks()` pero **la función no estaba definida** en el módulo.

Durante las iteraciones de desarrollo del menú de modo nocturno, se realizaron modificaciones que accidentalmente eliminaron la definición de la función `handle_show_menu`, pero el registro del callback remained intact.

Esto causaba un `NameError` durante la inicialización del menú engine, lo que hacía que fallara silenciosamente y `get_menu_engine()` retornara `None`.

## Bug encontrado

**Archivo:** `app/manager_bot/_features/nightmode/__init__.py`

El callback estaba registrado pero la función no existía:

```python
# ❌ Registro sin función definida
router.register_exact("mod:nightmode:show", handle_show_menu)  # NameError!
```

## Solución

Se añadió la función `handle_show_menu` faltante:

```python
# ✅ Solución
async def handle_show_menu(callback: "CallbackQuery", bot: "Bot", data: str):
    from app.manager_bot._menus.nightmode_menu import create_nightmode_menu
    
    chat_id = callback.message.chat.id if callback.message else None
    if not chat_id:
        await callback.answer("Chat no identificado", show_alert=True)
        return

    config = await self.get_config(chat_id)
    menu = create_nightmode_menu(config)

    try:
        await callback.edit_message_text(
            text=menu.title,
            reply_markup=menu.to_keyboard(),
        )
    except Exception:
        pass
```

## Verificación

```python
# Test de creación del menu engine
from app.manager_bot._menu_service import create_menu_engine

engine, limiter = create_menu_engine()
print('Engine created:', engine is not None)
print('Menus registered:', len(engine.registry.list_menus()))

# Output:
# Engine created: True
# Menus registered: 89
```

## Resultado

- El menú engine ahora se inicializa correctamente
- `/config` muestra el menú principal correctamente
- Se registran 89 menús

---

## Bugs relacionados

| Bug | Archivo | Problema | Solución |
|-----|---------|----------|----------|
| 003 | `_menus/__init__.py` | Menú reports no registrado | Agregar import y registry.register() |
| 003 | `_features/reports/repository.py` | Import circular | Usar TYPE_CHECKING |
| 004 | `_features/nightmode/__init__.py` | Handler `handle_show_menu` no definido | Añadir función faltante |

## Recomendación

1. **Validación de inicialización**: Agregar verificaciones en `create_menu_engine` para detectar errores temprano
2. **Test de inicialización**: Crear tests que verifiquen que todos los módulos se inicializan sin errores
3. **Revisión de código**: Revisar que todas las funciones registradas en callbacks estén definidas
