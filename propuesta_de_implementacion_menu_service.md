# Propuesta de Implementación: Sistema de Menú Inline para ManagerBot

## Análisis del Problema

### Síntomas
- Todos los botones de menús inline responden con el mensaje: **"Acción no reconocida"**
- Los comandos del bot funcionan correctamente (`/config`, `/antispam`, etc.)
- Los menús se muestran correctamente al inicializar

### Flujo Actual
```
Telegram CallbackQuery → Webhook → dispatcher.py → handlers.py → 
menu_engine.handle_callback_query_raw() → callback_router.handle() → "Acción no reconocida"
```

### Causa Raíz Identificada

El problema está en el **pattern matching** del `CallbackRouter` (`callback_router.py:34-41`).

Cuando se registra un handler con `register_prefix("antispam:toggle", handler)`:

```python
# En register_prefix (línea 83)
pattern = f"^{prefix}:"
# Resultado: "^antispam:toggle:"
```

Pero el callback_data del botón en el menú es simplemente `"antispam:toggle"` (sin los dos puntos finales).

En el método `matches()`:

```python
def matches(self, data: str) -> bool:
    if self.compiled:
        return bool(self.compiled.match(data))  # "^antispam:toggle:" no hace match con "antispam:toggle"
    pattern = self.pattern.rstrip("$").lstrip("^")  # "antispam:toggle:"
    if pattern.endswith(":"):
        return data.startswith(pattern)  # "antispam:toggle".startswith("antispam:toggle:") = False
    return data == pattern or data.startswith(pattern + ":")
```

**El resultado es que ningún callback hace match, y se cae al fallback que muestra "Acción no reconocida".**

---

## Propuesta de Solución

### Opción 1: Corregir el Pattern Matching (Recomendada)

**Cambios en `callback_router.py`:**

```python
def matches(self, data: str) -> bool:
    if self.compiled:
        return bool(self.compiled.match(data))
    
    pattern = self.pattern.rstrip("$").lstrip("^")
    
    # Si el patrón termina en ":", hacer match con startswith
    if pattern.endswith(":"):
        return data.startswith(pattern)
    
    # Si no hay ":" al final, verificar match exacto o con prefijo ":"
    # "antispam:toggle" debe hacer match con "antispam:toggle" Y "antispam:toggle:on"
    return data == pattern or data.startswith(pattern + ":")
```

**O mejor aún, corregir `register_prefix` para que no agregue `:` si ya existe:**

```python
def register_prefix(
    self,
    prefix: str,
    handler: CallbackHandler,
    description: str = ""
) -> None:
    """Register a handler for all callbacks starting with a prefix."""
    # No agregar ":" si ya termina en ":"
    if prefix.endswith(":"):
        pattern = f"^{prefix.rstrip(':')}"
    else:
        pattern = f"^{prefix}"
    self.register(pattern, handler, description or f"Handler for {prefix}")
```

### Opción 2: Registrar Todos los Callbacks de Forma Explícita

En cada feature (ej: `antispam/__init__.py`), cambiar:

```python
# De:
router.register_prefix("antispam:toggle", handle_toggle)

# A:
router.register("^antispam:toggle(:.*)?$", handle_toggle)
```

**Contras:** Requiere cambios en todos los features existentes.

---

## Plan de Implementación

### Fase 1: Diagnóstico y Verificación (30 min)

1. **Agregar logs de debug** en `callback_router.py`:
   ```python
   def matches(self, data: str) -> bool:
       logger.debug(f"Checking pattern '{self.pattern}' against data '{data}'")
       # ... existing logic
   ```

2. **Listar handlers registrados** al iniciar para verificar qué callbacks están conectados:
   ```python
   # En menu_service.py, después de _register_features
   logger.info(f"Registered callbacks: {callback_router.list_handlers()}")
   ```

### Fase 2: Corrección del Pattern Matching (1 hora)

1. Modificar `CallbackRouter.matches()` para manejar correctamente los prefix patterns
2. Verificar que `register_prefix` no introduzca el bug del doble `:`
3. Agregar tests unitarios para el matching

### Fase 3: Testing Integral (30 min)

1. Probar cada tipo de botón en todos los menús:
   - Main menu → Moderación → Toggle antispam
   - Main menu → Antispam → SpamWatch toggle
   - Main menu → Filtros → Añadir filtro
   - Main menu → Bienvenida → Editar texto
   - Navigation: Volver, Home

2. Verificar rate limiting

### Fase 4: Documentación (15 min)

1. Documentar el formato de callback_data
2. Crear guía para registrar nuevos callbacks

---

## Archivos a Modificar

| Archivo | Cambio |
|---------|--------|
| `app/manager_bot/transport/telegram/callback_router.py` | Corregir `matches()` y `register_prefix()` |
| `app/manager_bot/menu_service.py` | Agregar logging de callbacks registrados |

---

## Métricas de Éxito

- [ ] Todos los botones de menús responden correctamente
- [ ] Las toggles actualizan la configuración
- [ ] La navegación entre menús funciona (back, home)
- [ ] No hay regresiones en comandos existentes
- [ ] Los logs muestran qué callbacks están registrados al iniciar
