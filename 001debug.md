# Debug 001 - /config responde "no response"

Fecha: 2026-03-19

## Resumen
El comando `/config` devolvia el texto `(no response)` porque **el MenuEngine no llegaba a inicializarse**. Esto ocurria por un **SyntaxError** en `app/manager_bot/_features/welcome/__init__.py` que detenia `create_menu_engine()` durante el registro de features. Al no existir MenuEngine, el handler de `/config` no podia renderizar menus y terminaba enviando el fallback `(no response)`.

## Causa raiz
- El archivo `app/manager_bot/_features/welcome/__init__.py` tenia **strings multilinea mal formados** (saltos de linea sin `
` dentro de comillas).
- Esto generaba: `SyntaxError: unterminated string literal`.
- El error ocurre al ejecutar:
  - `create_menu_engine()` ? `_register_features()` ? `from app.manager_bot._features.welcome import WelcomeFeature`.
- Al fallar esta importacion, el MenuEngine **no se crea**, por lo que `get_menu_engine()` devuelve `None`.

## Evidencia tecnica
- Error reproducido al ejecutar `create_menu_engine()`:
  - `SyntaxError: unterminated string literal (detected at line 74) (__init__.py, line 74)`.
- El flujo de `/config` en `app/webhook/handlers.py`:
  - Si `menu_engine` es `None`, no se envia el menu.
  - Luego cae en `reply = result.get("response_text", "(no response)")`.
  - `/config` solo devuelve `{status: "menu", menu_id: "main"}` (sin `response_text`).

## Fix aplicado
Se corrigieron los strings en:
- `app/manager_bot/_features/welcome/__init__.py`

Ejemplo de correccion:
```python
instruction = (
    "Envia el mensaje de bienvenida

"
    "Variables disponibles:
"
    "- {username} Nombre del usuario
"
    "- {title} Nombre del grupo
"
    "- {count} Numero de miembros"
)
```

## Resultado
- `create_menu_engine()` vuelve a inicializar correctamente.
- Los menus se registran.
- `/config` vuelve a mostrar el menu principal en lugar de `(no response)`.

---

# Debug 002 - /config responde "no response" (RECURRENCIA)

Fecha: 2026-03-19

## Resumen
El comando `/config` devuelve el texto `(no response)` porque **el MenuEngine no llega a inicializarse**. Esto ocurre por un **SyntaxError** en `app/manager_bot/_menus/welcome_menu.py` que detiene `create_menu_engine()` durante el registro de menus. Al no existir MenuEngine, el handler de `/config` no puede renderizar menus y termina enviando el fallback `(no response)`.

## Causa raiz
- El archivo `app/manager_bot/_menus/welcome_menu.py` tiene un **string multilinea mal formado** en la variable `base` (lineas 15-19).
- El problema es que el string en la linea 16 tiene un salto de linea literal `\n` **fuera de las comillas**, lo que corta la cadena prematurely.
- Esto generaba: `SyntaxError: unterminated string literal (detected at line 16)`.
- El error ocurre al ejecutar:
  - `create_menu_engine()` -> `register_all_menus()` -> `from app.manager_bot._menus.welcome_menu import ...`
- Al fallar esta importacion, el MenuEngine **no se crea**, por lo que `get_menu_engine()` devuelve `None`.

## Codigo problematico (lineas 15-19)
```python
    base = (
        "Mensaje de bienvenida
"
        "Desde este menu puedes configurar un mensaje que se enviara cuando alguien se una al grupo."
    )
```

## Fix requerido
```python
    base = (
        "Mensaje de bienvenida\n"
        "Desde este menu puedes configurar un mensaje que se enviara cuando alguien se una al grupo."
    )
```

## Evidencia tecnica
- Error reproducido al ejecutar `create_menu_engine()`:
  - `SyntaxError: unterminated string literal (detected at line 16) (_menus/welcome_menu.py, line 16)`.
- El flujo de `/config` en `app/webhook/handlers.py`:
  - Si `menu_engine` es `None`, no se envia el menu (lineas 468-484).
  - Luego cae en `reply = result.get("response_text", "(no response)")` (linea 486).
  - `/config` solo devuelve `{"status": "menu", "menu_id": "main"}` (sin `response_text`).

## Archivo a corregir
- `app/manager_bot/_menus/welcome_menu.py`
