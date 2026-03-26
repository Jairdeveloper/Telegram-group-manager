# Debug 002 - /config responde "no response"

Fecha: 2026-03-20

## Resumen
El comando `/config` devuelve el texto `(no response)` porque **el MenuEngine no llega a inicializarse**. Esto ocurre por múltiples **TypeError** en las funciones de menú que no aceptan el argumento `config`. Al no existir MenuEngine, el handler de `/config` no puede renderizar menús y termina enviando el fallback `(no response)`.

## Causa raíz
- El `MenuRegistry.register()` en `app/manager_bot/_menus/registry.py:23` llama a `menu(None)` (invoca la función pasando `None` como argumento).
- Varias funciones de menú **no aceptan el argumento `config`**, causando `TypeError`.
- El error ocurre al ejecutar:
  - `create_menu_engine()` → `register_all_menus()` → `registry.register(...)` → `menu(None)`.
- Al fallar esta importación, el MenuEngine **no se crea**, por lo que `get_menu_engine()` devuelve `None`.

## Bugs encontrados y corregidos

### Bug 2.1: `create_info_menu()` en `main_menu.py:53`
```python
# ❌ Antes
def create_info_menu() -> MenuDefinition:

# ✅ Después
def create_info_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
```

### Bug 2.2: `create_antispan_telegram_exceptions_menu()` en `antispam_menu.py:174`
```python
# ❌ Antes
def create_antispan_telegram_exceptions_menu() -> MenuDefinition:

# ✅ Después
def create_antispan_telegram_exceptions_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
```

### Bug 2.3: `create_antispan_forward_exceptions_menu()` en `antispam_menu.py:276`
```python
# ❌ Antes
def create_antispan_forward_exceptions_menu() -> MenuDefinition:

# ✅ Después
def create_antispan_forward_exceptions_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
```

### Bug 2.4: `create_antispan_quotes_exceptions_menu()` en `antispam_menu.py:367`
```python
# ❌ Antes
def create_antispan_quotes_exceptions_menu() -> MenuDefinition:

# ✅ Después
def create_antispan_quotes_exceptions_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
```

### Bug 2.5: `create_antispan_internet_exceptions_menu()` en `antispam_menu.py:437`
```python
# ❌ Antes
def create_antispan_internet_exceptions_menu() -> MenuDefinition:

# ✅ Después
def create_antispan_internet_exceptions_menu(config: Optional[GroupConfig] = None) -> MenuDefinition:
```

## Archivos corregidos
- `app/manager_bot/_menus/main_menu.py:53`
- `app/manager_bot/_menus/antispam_menu.py:174`
- `app/manager_bot/_menus/antispam_menu.py:276`
- `app/manager_bot/_menus/antispam_menu.py:367`
- `app/manager_bot/_menus/antispam_menu.py:437`

## Evidencia técnica
- Error reproducido al ejecutar `create_menu_engine()`:
  ```
  TypeError: create_info_menu() takes 0 positional arguments but 1 was given
  ```
- El flujo de `/config` en `app/webhook/handlers.py`:
  - Si `menu_engine` es `None`, no se envía el menú (líneas 468-484).
  - Luego cae en `reply = result.get("response_text", "(no response)")` (línea 486).
  - `/config` solo devuelve `{"status": "menu", "menu_id": "main"}` (sin `response_text`).

## Resultado
- `create_menu_engine()` vuelve a inicializar correctamente.
- Los menús se registran.
- `/config` vuelve a mostrar el menú principal en lugar de `(no response)`.

---

## Análisis de otros archivos verificados

Se verificó que los siguientes archivos NO tienen errores de sintaxis:

### ✅ `app/manager_bot/_features/welcome/__init__.py`
- Strings multilínea correctamente formados usando paréntesis implícitos.

### ✅ `app/manager_bot/_menus/welcome_menu.py`
- Strings multilínea correctamente formados con `\n` dentro de las comillas.

## Patrón recurrente identificado

Este bug es similar a los bugs reportados en el archivo `001debug.md`:

| Bug | Archivo | Problema | Tipo de Error |
|-----|---------|----------|---------------|
| 001 | `_features/welcome/__init__.py` | String mal formado | `SyntaxError` |
| 002 | `_menus/welcome_menu.py` | String mal formado | `SyntaxError` |
| 003 | `_menus/main_menu.py` | Falta argumento `config` | `TypeError` |
| 004 | `_menus/antispam_menu.py` (x4) | Falta argumento `config` | `TypeError` |

**Recomendación**: Agregar validación en `registry.register()` para detectar funciones con firmas incorrectas antes de la invocación, o usar type hints y linting para detectar inconsistencias en las firmas de las funciones de menú.
