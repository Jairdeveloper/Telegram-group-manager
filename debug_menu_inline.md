# Debug: Botón "Volver" no funciona

## Problema
El botón de "volver" (`nav:back:*`) no funciona en ningún menú.

## Análisis del Código

### Handlers de navegación registrados (`menu_engine.py:88-108`)

```python
# Línea 88 - Exact para main
self.callback_router.register_exact("nav:back:main", handle_back, "Back to main")

# Línea 89-90 - Otros exactos
self.callback_router.register_exact("nav:home", handle_home, "Go to home")
self.callback_router.register_exact("nav:noop", handle_noop, "No-op")

# Línea 91 - Prefix para back (debería capturar nav:back:mod, nav:back:filters, etc)
self.callback_router.register_prefix("nav:back:", handle_back, "Back navigation")

# Línea 108 - Prefix general para NAV (PROBLEMA POTENCIAL!)
self.callback_router.register_prefix("nav", handle_noop, "General nav")
```

### Patterns generados

| Registro | Pattern Generado | Ejemplo de Match |
|----------|------------------|------------------|
| `register_exact("nav:back:main")` | `^nav:back:main$` | Solo `nav:back:main` |
| `register_prefix("nav:back:")` | `^nav:back:(:.*)?$` | `nav:back:mod`, `nav:back:filters` |
| `register_prefix("nav")` | `^nav(:.*)?$` | **TODOS** los que empiezan con `nav` |

### 🔴 PROBLEMA IDENTIFICADO

El orden de registro es:
1. `nav:back:main` (exact) - ✓ correcto
2. `nav:back:` (prefix) - ✓ correcto  
3. `nav` (prefix) - ❌ **CAPTURA TODO!**

El callback `nav:back:main` también hace match con el pattern `^nav(:.*)?$`, por lo que `handle_noop` se ejecuta en lugar de `handle_back`.

## Puntos de Interrupción para Debug

### 1. Verificar orden de handlers registrados

**Archivo:** `callback_router.py`  
**Línea:** ~135 (en el método `handle`)

```python
# Agregar breakpoint aquí para ver el orden de handlers
logger.debug(f"Available handlers ({len(self._handlers)}): {self.list_handlers()}")
```

### 2. Verificar qué handler hace match primero

**Archivo:** `callback_router.py`  
**Línea:** ~138-140

```python
for handler_pattern in self._handlers:
    match_result = handler_pattern.matches(data)
    logger.debug(f"Handler '{handler_pattern.pattern}' (desc: {handler_pattern.description}) vs '{data}': {match_result}")
    if match_result:
        # BREAKPOINT AQUÍ: ver cuál hace match primero
        logger.info(f"Handler matched: {handler_pattern.pattern} for callback '{data}'")
```

### 3. Verificar el flujo completo del callback

**Archivo:** `menu_engine.py`  
**Línea:** ~49-59 (handle_back)

```python
async def handle_back(callback, bot: "Bot", data: str):
    # BREAKPOINT 1: ¿Llega aquí?
    parts = data.split(":")
    if len(parts) >= 3:
        target_menu = parts[2]
    else:
        target_menu = "main"
    
    user_id = callback.from_user.id
    self.navigation.pop_menu(user_id)
    
    # BREAKPOINT 2: ¿Llega aquí?
    await self.show_menu_by_callback(callback, bot, target_menu)
```

### 4. Verificar si se ejecuta handle_noop

**Archivo:** `menu_engine.py`  
**Línea:** ~67-69

```python
async def handle_noop(callback, bot: "Bot", data: str):
    # BREAKPOINT: ¿Se ejecuta aquí en lugar de handle_back?
    await callback.answer()
```

## Solución Propuesta

### Opción A: Eliminar el registro problemático (Recomendado)

Eliminar la línea 108 que registra el prefix general "nav":

```python
# ELIMINAR ESTA LÍNEA (108):
self.callback_router.register_prefix("nav", handle_noop, "General nav")
```

### Opción B: Mover el registro general al final Y ser más específico

```python
# Registrar handle_noop solo para casos específicos
self.callback_router.register_exact("nav:noop", handle_noop, "No-op")
# NO usar register_prefix("nav", ...) que captura todo
```

### Opción C: Registrar back primero que el general

```python
# Mover el registro de "nav" al final, DESPUÉS de todos los back
# O eliminarlo completamente si no se necesita
```

## Verificación

Después de aplicar la corrección, verificar que:
1. `nav:back:main` → `handle_back` (mostrar menú main)
2. `nav:back:mod` → `handle_back` (mostrar menú mod)
3. `nav:home` → `handle_home`
4. `nav:noop` → `handle_noop`

## Logs a buscar

```
# Buscar en logs:
INFO: Callback received: 'nav:back:main' from user X in chat Y
DEBUG: Handler '^nav(:.*)?$' (desc: General nav) vs 'nav:back:main': True
# Si aparece esto, el problema es que "nav" está capturando todo
```

## Scripts de Test

```python
# Test rápido para verificar el problema
from app.manager_bot.transport.telegram.callback_router import CallbackRouter

router = CallbackRouter()

async def handler_back(callback, bot, data):
    print(f"handle_back called with: {data}")

async def handler_noop(callback, bot, data):
    print(f"handle_noop called with: {data}")

# Registrar en el mismo orden que menu_engine
router.register_exact("nav:back:main", handler_back, "Back to main")
router.register_prefix("nav:back:", handler_back, "Back navigation")
router.register_prefix("nav", handler_noop, "General nav")

# Test
print("Handlers:", router.list_handlers())

# Probar matching
test_data = "nav:back:main"
for hp in router._handlers:
    result = hp.matches(test_data)
    print(f"'{test_data}' vs '{hp.pattern}': {result}")
```
