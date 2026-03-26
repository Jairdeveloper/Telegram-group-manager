# Debug 003 - /config responde "no response"

Fecha: 2026-03-23

## Resumen

El comando `/config` devuelve el texto `(no response)`. Este bug es similar al bug 002, pero la causa raíz es diferente.

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

## Causa raíz

El menú `reports` **no estaba registrado** en `app/manager_bot/_menus/__init__.py`.

Al agregar la funcionalidad de reportes, se crearon:
- `app/manager_bot/_menus/reports_menu.py`
- `app/manager_bot/_features/reports/__init__.py`
- `app/manager_bot/_features/reports/repository.py`

Pero **no se registró** en la función `register_all_menus()`.

Además, había un **import circular** entre:
- `reports_menu.py` → importa de `_features/reports`
- `_features/reports/__init__.py` → importa de `repository.py`
- `repository.py` → imports al inicio trataban de importar de `_features/reports`

## Bugs encontrados y corregidos

### Bug 3.1: Menú reports no registrado

**Archivo:** `app/manager_bot/_menus/__init__.py:93-95`

```python
# ❌ Antes (faltaba imports y registro)
# No había import de reports_menu

# ✅ Después
from app.manager_bot._menus.reports_menu import (
    create_reports_menu,
)
# ...
registry.register(create_reports_menu)
```

### Bug 3.2: Import circular en repository.py

**Archivo:** `app/manager_bot/_features/reports/repository.py`

El archivo importaba `Report`, `ReportAction`, `ReportStatus` al inicio:

```python
# ❌ Antes
from app.manager_bot._features.reports import Report, ReportAction, ReportStatus

class ReportRepository:
    ...
```

Esto causaba un import circular porque `_features/reports/__init__.py` importa de `repository.py`.

**Solución:** Usar `TYPE_CHECKING` para type hints e imports locales dentro de funciones:

```python
# ✅ Después
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.manager_bot._features.reports import Report, ReportAction, ReportStatus

class ReportRepository:
    def save(self, report: "Report") -> None:
        from app.manager_bot._features.reports import ReportAction, ReportStatus
        # usar los tipos aquí
```

### Bug 3.3: Type hints faltantes en repository.py

Se actualizaron todos los type hints para usar strings con comillas cuando referencian tipos del mismo módulo:

```python
# ❌ Antes
def get_by_chat(self, chat_id: int, status: Optional[ReportStatus] = None) -> List[Report]:

# ✅ Después  
def get_by_chat(self, chat_id: int, status: Optional["ReportStatus"] = None) -> List["Report"]:
```

## Verificación

```python
# Test de registro de menús
from app.manager_bot._menus import register_all_menus
from app.manager_bot._menus.registry import MenuRegistry

registry = MenuRegistry()
register_all_menus(registry)
print('Registered:', len(registry.list_menus()))
# Output: Registered: 89
print('Reports menu:', 'reports' in registry.list_menus())
# Output: Reports menu: True
```

## Resultado

- `register_all_menus()` ahora registra 89 menús (incluyendo `reports`)
- `/config` debería mostrar el menú principal correctamente
- Los comandos `/report` y `/reports` funcionan correctamente

---

## Bugs relacionados

| Bug | Archivo | Problema | Solución |
|-----|---------|----------|----------|
| 002 | `_menus/main_menu.py`, `_menus/antispam_menu.py` | Funciones sin parámetro `config` | Agregar `config: Optional[GroupConfig] = None` |
| 003 | `_menus/__init__.py` | Menú reports no registrado | Agregar import y registry.register() |
| 003 | `_features/reports/repository.py` | Import circular | Usar TYPE_CHECKING |

## Recomendación

1. **Validación en registry**: Agregar una función que verifique que todas las funciones de menú acepten el parámetro `config` opcional
2. **Test de integración**: Crear tests que verifiquen que todos los menús se registran correctamente
3. **Linting**: Usar herramientas como `mypy` para detectar inconsistencias de tipos
