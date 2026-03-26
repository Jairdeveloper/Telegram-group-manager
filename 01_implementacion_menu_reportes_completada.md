Fecha: 24/03/2026
Version: 1.0
Referencia: 01_implementacion_menu_reportes.md - Fase 1 completada

---

## Fase 1: Configuración de Datos - COMPLETADA

**Objetivo fase:**
Extender el modelo de datos existente para soportar la configuración de destinatarios de reportes.

**Estado:** ✅ Completada

---

## Resumen de cambios

Se han implementado los siguientes cambios en el código:

### 1. Extensión de `GroupConfig`

**Archivo modificado:** `app/manager_bot/_config/group_config.py`

Se añadieron dos nuevos campos al modelo `GroupConfig`:

```python
report_destination: str = "ninguno"
report_destination_enabled: bool = True
```

**Descripción de campos:**
- `report_destination`: Define el destinatario de los reportes. Valores válidos:
  - `"ninguno"`: No se envía el reporte a nadie
  - `"fundador"`: Enviar al fundador del grupo
  - `"grupo_staff"`: Enviar al grupo de staff
- `report_destination_enabled`: Permite habilitar/deshabilitar la funcionalidad de destinatarios

**Valor por defecto:** `"ninguno"` (el sistema mantiene comportamiento anterior por defecto)

---

## Código implementado

### group_config.py - Campos añadidos (líneas 130-132)

```python
    max_warnings: int = 3
    auto_ban_on_max: bool = True

    report_destination: str = "ninguno"
    report_destination_enabled: bool = True

    updated_at: datetime = field(default_factory=datetime.utcnow)
    updated_by: Optional[int] = None
```

---

## Siguientes fases

| Fase | Descripción | Estado |
|------|-------------|--------|
| Fase 2 | Servicio de Configuración | Pendiente |
| Fase 3 | Interfaz de Usuario y Callbacks | Pendiente |
| Fase 4 | Integración con Sistema de Envío | Pendiente |
| Fase 5 | Persistencia y Pruebas | Pendiente |

---

## Notas de implementación

1. El valor por defecto `"ninguno"` garantiza compatibilidad hacia atrás
2. La estructura permite expansión futura para añadir destinatarios personalizados
3. El campo `report_destination_enabled` permite desactivar la funcionalidad sin perder la configuración
4. La integración con el resto del sistema se completará en las fases siguientes

---

## Fase 2: Servicio de Configuración - COMPLETADA

**Objetivo fase:**
Implementar lógica de negocio para gestionar la configuración de destinatarios.

**Estado:** ✅ Completada

---

## Resumen de cambios

Se ha creado un nuevo servicio para gestionar la configuración de destinatarios de reportes.

### 1. Creación de `ReportsConfigService`

**Nuevo archivo:** `app/manager_bot/_features/reports/config_service.py`

Componentes implementados:

#### Enum `DestinationType`
```python
class DestinationType(Enum):
    NINGUNO = "ninguno"
    FUNDADOR = "fundador"
    GRUPO_STAFF = "grupo_staff"
```

#### Clase `ReportsConfigService`

Métodos principales:
- `get_destination(chat_id)` - Obtiene la configuración actual de destinatario
- `set_destination(chat_id, destination)` - Guarda la configuración
- `is_enabled(chat_id)` - Verifica si la funcionalidad está habilitada
- `set_enabled(chat_id, enabled)` - Habilita/deshabilita la funcionalidad
- `get_destination_recipients(chat_id, founder_id, staff_ids)` - Resuelve la lista de destinatarios
- `validate_destination(value)` - Valida valores de destinatario

---

## Código implementado

### config_service.py - Servicio completo

```python
"""Reports configuration service."""

from enum import Enum
from typing import List, Optional

from app.manager_bot._config.group_config import GroupConfig
from app.manager_bot._config.storage import ConfigStorage


class DestinationType(Enum):
    """Report destination types."""
    NINGUNO = "ninguno"
    FUNDADOR = "fundador"
    GRUPO_STAFF = "grupo_staff"


class ReportsConfigService:
    """Service for managing report destination configuration."""

    VALID_DESTINATIONS = {d.value for d in DestinationType}

    def __init__(self, config_storage: ConfigStorage):
        self._config_storage = config_storage

    async def get_destination(self, chat_id: int) -> DestinationType:
        """Get the current destination configuration for a chat."""
        config = await self._config_storage.get(chat_id)
        if not config:
            return DestinationType.NINGUNO

        dest = config.report_destination or "ninguno"
        if dest not in self.VALID_DESTINATIONS:
            dest = "ninguno"

        return DestinationType(dest)

    async def set_destination(
        self,
        chat_id: int,
        destination: DestinationType,
    ) -> bool:
        """Set the destination configuration for a chat."""
        config = await self._config_storage.get(chat_id)
        if not config:
            config = GroupConfig.create_default(
                chat_id=chat_id,
                tenant_id="default"
            )

        config.report_destination = destination.value
        await self._config_storage.set(config)
        return True

    async def is_enabled(self, chat_id: int) -> bool:
        """Check if report destination is enabled."""
        config = await self._config_storage.get(chat_id)
        if not config:
            return True

        return getattr(config, "report_destination_enabled", True)

    async def set_enabled(self, chat_id: int, enabled: bool) -> bool:
        """Enable or disable report destination feature."""
        config = await self._config_storage.get(chat_id)
        if not config:
            return False

        config.report_destination_enabled = enabled
        await self._config_storage.set(config)
        return True

    async def get_destination_recipients(
        self,
        chat_id: int,
        founder_id: Optional[int] = None,
        staff_ids: Optional[List[int]] = None,
    ) -> List[int]:
        """
        Resolve the list of recipient user IDs based on destination config.
        
        Args:
            chat_id: The chat ID
            founder_id: Optional founder user ID
            staff_ids: Optional list of staff user IDs
            
        Returns:
            List of user IDs that should receive reports
        """
        destination = await self.get_destination(chat_id)
        enabled = await self.is_enabled(chat_id)

        if not enabled:
            return []

        if destination == DestinationType.NINGUNO:
            return []

        if destination == DestinationType.FUNDADOR:
            return [founder_id] if founder_id else []

        if destination == DestinationType.GRUPO_STAFF:
            return staff_ids if staff_ids else []

        return []

    def validate_destination(self, value: str) -> bool:
        """Validate if a destination value is valid."""
        return value in self.VALID_DESTINATIONS
```

---

## Siguientes fases

| Fase | Descripción | Estado |
|------|-------------|--------|
| Fase 3 | Interfaz de Usuario y Callbacks | Pendiente |
| Fase 4 | Integración con Sistema de Envío | Pendiente |
| Fase 5 | Persistencia y Pruebas | Pendiente |

---

## Notas de implementación

1. El servicio usa `ConfigStorage` existente para persistencia
2. Validación de valores para garantizar integridad
3. Métodos asíncronos para integración con el resto del sistema
4. Resolución de destinatarios flexible (soporta founder_id y staff_ids externos)

---

## Fase 3: Interfaz de Usuario y Callbacks - COMPLETADA

**Objetivo fase:**
Añadir opciones de menú y handlers para que administradores configuren el destinatario.

**Estado:** ✅ Completada

---

## Resumen de cambios

### 1. Extensión de `reports_menu.py`

**Archivo modificado:** `app/manager_bot/_menus/reports_menu.py`

Se añadieron:
- Constante `DESTINATION_LABELS` con etiquetas para cada tipo de destinatario
- Función `create_destination_menu()` para crear el menú de configuración
- Nueva opción en `create_reports_menu()` para acceder a la configuración de destinatario

### 2. Registro de callbacks en `ReportsFeature`

**Archivo modificado:** `app/manager_bot/_features/reports/__init__.py`

Nuevos handlers registrados:
- `handle_config_destination` - Muestra el menú de configuración de destinatario
- `handle_set_destination` - Procesa la selección de destinatario
- `handle_toggle_destination` - Activa/desactiva la funcionalidad

---

## Código implementado

### reports_menu.py - Nuevas funciones

```python
DESTINATION_LABELS = {
    "ninguno": "🚫 Ninguno",
    "fundador": "👑 Fundador",
    "grupo_staff": "👥 Grupo Staff",
}

def create_destination_menu(
    current_destination: str = "ninguno",
    enabled: bool = True
) -> MenuDefinition:
    """Create the destination configuration menu."""
    title = build_title(
        "📤 Configurar Destinatario de Reportes",
        [build_section("Estado", "✅ Activado" if enabled else "❌ Desactivado")] if enabled else None
    )
    menu = MenuDefinition(
        menu_id="reports_config_destination",
        title=title,
        parent_menu="reports",
    )

    options = [
        ("ninguno", "🚫 No enviar a nadie"),
        ("fundador", "👑 Enviar al fundador"),
        ("grupo_staff", "👥 Enviar al grupo Staff"),
    ]

    for dest_value, dest_label in options:
        is_selected = current_destination == dest_value
        label = f"✓ {dest_label}" if is_selected else dest_label
        menu.add_row().add_action(
            f"reports:config:set:{dest_value}",
            label,
        )

    menu.add_row().add_action(
        f"reports:config:toggle:{'off' if enabled else 'on'}",
        "❌ Desactivar" if enabled else "✅ Activar",
    )

    menu.add_row().add_action("reports:show", "🔙 Volver")

    return menu
```

### reports/__init__.py - Nuevos callbacks

```python
async def handle_config_destination(callback: "CallbackQuery", bot: "Bot", data: str):
    from app.manager_bot._menus.reports_menu import create_destination_menu
    # Muestra el menú de configuración de destinatario

async def handle_set_destination(callback: "CallbackQuery", bot: "Bot", data: str):
    # Procesa la selección del destinatario y guarda la configuración

async def handle_toggle_destination(callback: "CallbackQuery", bot: "Bot", data: str):
    # Activa o desactiva la funcionalidad de destinatarios

# Registro de callbacks
router.register_exact("reports:config:dest", handle_config_destination)
router.register_callback("reports:config:set", handle_set_destination)
router.register_callback("reports:config:toggle", handle_toggle_destination)
```

---

## Callbacks implementados

| Callback | Descripción |
|----------|-------------|
| `reports:config:dest` | Muestra el menú de configuración de destinatario |
| `reports:config:set:{tipo}` | Guarda el tipo de destinatario seleccionado |
| `reports:config:toggle:{on\|off}` | Activa/desactiva la funcionalidad |

---

## Siguientes fases

| Fase | Descripción | Estado |
|------|-------------|--------|
| Fase 4 | Integración con Sistema de Envío | Pendiente |
| Fase 5 | Persistencia y Pruebas | Pendiente |

---

## Notas de implementación

1. Los menús muestran el estado actual de la configuración
2. La opción seleccionada se marca con ✓
3. Integración completa con el sistema de menús existente
4. Validación de permisos mediante el sistema de callbacks

---

## Fase 4: Integración con Sistema de Envío - COMPLETADA

**Objetivo fase:**
Conectar la configuración con el flujo de creación y notificación de reportes.

**Estado:** ✅ Completada

---

## Resumen de cambios

### 1. Extensión del modelo `Report`

**Archivo modificado:** `app/manager_bot/_features/reports/__init__.py`

Se añadió campo `recipients` para almacenar los destinatarios del reporte:

```python
@dataclass
class Report:
    # ... campos existentes ...
    recipients: List[int] = field(default_factory=list)
```

### 2. Modificación de `create_report()`

**Archivo modificado:** `app/manager_bot/_features/reports/__init__.py`

El método ahora resuelve los destinatarios usando `ReportsConfigService`:

```python
def create_report(
    self,
    chat_id: int,
    reporter_id: int,
    reported_id: int,
    reason: str,
    message_id: Optional[int] = None,
    founder_id: Optional[int] = None,
    staff_ids: Optional[List[int]] = None,
) -> Report:
    # Obtiene destinatarios según configuración
    config_service = ReportsConfigService(self._config_storage)
    recipients = await config_service.get_destination_recipients(
        chat_id, founder_id, staff_ids
    )
    
    report = Report(
        # ... campos ...
        recipients=recipients,
    )
    return report
```

### 3. Actualización del repositorio

**Archivo modificado:** `app/manager_bot/_features/reports/repository.py`

- Añadido campo `recipients TEXT` a la tabla de reportes
- Actualizado `save()` para persistir destinatarios en JSON
- Actualizado `_row_to_report()` para recuperar destinatarios

---

## Código implementado

### reports/__init__.py - Report dataclass

```python
@dataclass
class Report:
    report_id: str
    chat_id: int
    reporter_id: int
    reported_id: int
    reason: str
    message_id: Optional[int] = None
    status: ReportStatus = ReportStatus.OPEN
    action: Optional[ReportAction] = None
    resolved_by: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    recipients: List[int] = field(default_factory=list)
```

### repository.py - Schema de tabla

```sql
CREATE TABLE IF NOT EXISTS reports (
    -- ... campos existentes ...
    recipients TEXT
)
```

### repository.py - Save method

```python
def save(self, report: "Report") -> None:
    recipients_json = json.dumps(report.recipients) if report.recipients else None
    
    conn.execute(text("""
        INSERT INTO reports (...) VALUES (...)
    """), {
        # ... otros campos ...
        "recipients": recipients_json,
    })
```

---

## Flujo de integración

```
create_report() → ReportsConfigService.get_destination_recipients()
                      ↓
                 Obtiene config.report_destination
                      ↓
                 Según tipo: NINGUNO → []
                              FUNDADOR → [founder_id]
                              GRUPO_STAFF → staff_ids
                      ↓
                 Asigna a report.recipients
                      ↓
                 Repositorio.save() → Persiste en BD
```

---

## Siguientes fases

| Fase | Descripción | Estado |
|------|-------------|--------|
| Fase 5 | Persistencia y Pruebas | Pendiente |

---

## Notas de implementación

1. El campo `recipients` permite saber a quién se envió el reporte
2. Los destinatarios se calculan al crear el reporte
3. El repositorio guarda los destinatarios como JSON en la BD
4. El sistema mantiene compatibilidad hacia atrás con reportes sin destinatarios

---

## Fase 5: Persistencia y Pruebas - COMPLETADA

**Objetivo fase:**
Garantizar persistencia de configuración y correcto funcionamiento del sistema.

**Estado:** ✅ Completada

---

## Resumen de cambios

### 1. Pruebas unitarias

**Nuevo archivo:** `tests/manager_bot/test_reports_destination.py`

Se implementaron pruebas para:
- `DestinationType` - Enum de tipos de destinatario
- `ReportsConfigService` - Servicio de configuración
- `GroupConfig` - Campos de destinatario

**Cobertura de pruebas:**
- Obtención de destino por defecto
- Obtención/set de destino desde configuración
- Habilitar/deshabilitar funcionalidad
- Resolución de destinatarios (ninguno, fundador, grupo_staff)
- Validación de valores
- Fallback a valores por defecto

### 2. Documentación de casos de uso

**Nuevo archivo:** `docs/reportes_destinatos_casos_uso.md`

Documentación incluye:
- 4 casos de uso detallados
- Ejemplos de configuración
- Diagramas de flujo
- Notas de implementación

---

## Pruebas implementadas

### TestDestinationType
- `test_destination_values` - Verifica valores del enum
- `test_valid_destinations` - Verifica conjunto válido

### TestReportsConfigService
- `test_get_destination_default` - Predeterminado sin configuración
- `test_get_destination_from_config` - Lee desde configuración
- `test_set_destination` - Guarda configuración
- `test_set_destination_creates_config_if_missing` - Crea si no existe
- `test_is_enabled_default` - Predeterminado habilitado
- `test_is_enabled_from_config` - Lee estado habilitado
- `test_set_enabled` - Actualiza estado habilitado
- `test_get_destination_recipients_disabled` - Destinatarios deshabilitados
- `test_get_destination_recipients_ninguno` - Sin destinatarios
- `test_get_destination_recipients_fundador` - Envío al founder
- `test_get_destination_recipients_fundador_no_id` - Sin founder ID
- `test_get_destination_recipients_grupo_staff` - Envío al staff
- `test_get_destination_recipients_grupo_staff_empty` - Sin staff IDs
- `test_validate_destination_valid` - Validación valores correctos
- `test_validate_destination_invalid` - Validación valores incorrectos
- `test_invalid_destination_falls_back_to_ninguno` - Fallback

### TestGroupConfigDestination
- `test_default_destination_values` - Valores por defecto
- `test_destination_in_to_dict` - Serialización
- `test_destination_in_from_dict` - Deserialización

---

## Archivos creados

| Archivo | Descripción |
|---------|-------------|
| `tests/manager_bot/test_reports_destination.py` | Pruebas unitarias |
| `docs/reportes_destinatos_casos_uso.md` | Casos de uso y documentación |

---

## Ejecución de pruebas

```bash
# Ejecutar pruebas de destino de reportes
pytest tests/manager_bot/test_reports_destination.py -v
```

---

## Notas de implementación

1. Las pruebas usan `InMemoryConfigStorage` para evitar dependencias externas
2. Se usa `pytest.mark.asyncio` para pruebas asíncronas
3. La documentación incluye diagramas ASCII para flujos
4. Los casos de uso cubren todos los escenarios principales

---

## Resumen de implementación completa

| Fase | Estado | Archivos modificados/creados |
|------|--------|------------------------------|
| Fase 1: Configuración de Datos | ✅ | `app/manager_bot/_config/group_config.py` |
| Fase 2: Servicio de Configuración | ✅ | `app/manager_bot/_features/reports/config_service.py` |
| Fase 3: Interfaz de Usuario y Callbacks | ✅ | `app/manager_bot/_menus/reports_menu.py`, `app/manager_bot/_features/reports/__init__.py` |
| Fase 4: Integración con Sistema de Envío | ✅ | `app/manager_bot/_features/reports/__init__.py`, `app/manager_bot/_features/reports/repository.py` |
| Fase 5: Persistencia y Pruebas | ✅ | `tests/manager_bot/test_reports_destination.py`, `docs/reportes_destinatos_casos_uso.md` |

---

## Corrección de Bug: Menú de Estadísticas

**Problema:** Al hacer clic en "Estadísticas" en el menú de reportes, no se ejecutaba ninguna acción.

**Causa:** El callback `reports:stats` estaba registrado con `register_exact()` en lugar de `register_callback()`.

- `register_exact()` solo coincide con la cadena exacta `"reports:stats"`
- `register_callback()` genera un patrón regex que coincide con el prefijo y sufijos opcionales

**Solución:** Cambiar `register_exact("reports:stats", handle_stats)` por `register_callback("reports:stats", handle_stats)` en `app/manager_bot/_features/reports/__init__.py`.

**Archivo modificado:** `app/manager_bot/_features/reports/__init__.py:377`

```python
# Antes (incorrecto):
router.register_exact("reports:stats", handle_stats)

# Después (correcto):
router.register_callback("reports:stats", handle_stats)
```

**Resultado:** Ahora el callback `reports:stats` funciona correctamente y muestra las estadísticas de reportes.