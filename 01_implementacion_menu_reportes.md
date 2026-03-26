Fecha: 24/03/2026
Version: 1.1
Referencia: reportes.md

---

## Resumen de la implementacion

Se implementará una nueva característica al sistema de reportes existente que permitirá configurar el destinatario de los reportes generados. Esta funcionalidad se integrará con el módulo `ReportsFeature` ya implementado, añadiendo una capa de configuración de distribución de reportes.

El sistema soportará tres opciones de envío:
- **Ninguno**: No se envía el reporte a nadie
- **Fundador**: Enviar al fundador del grupo
- **Grupo Staff**: Enviar al grupo de staff

Esta característica extiende la funcionalidad existente documentada en `implementacion_menu_reports.md`, específicamente en la Fase 3 (Callbacks y UI) y Fase 4 (Acciones Automáticas), añadiendo configuración de destinatarios.

---

## Arquitectura final

```
┌─────────────────────────────────────────────────────────────────┐
│                     Menú de Configuración                        │
│         (reports:config:destinatario - Nueva característica)    │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ReportsFeature Module                        │
│  create_report() / get_reports() / resolve_report()           │
│  get_stats() / dismiss_report() + nuevo: get/set_destination()  │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│              ConfigStorage (Extensión)                          │
│  - destination: str (ninguno|fundador|grupo_staff)              │
│  - destination_config: dict                                     │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Sistema de Envío                               │
│  - Notificaciones a destinatario configurado                   │
│  - Lógica condicional según selección                           │
└─────────────────────────────────────────────────────────────────┘
```

**Componentes a añadir:**
- `DestinationConfig` - Modelo de configuración de destinatario
- `ReportsConfigService` - Servicio de gestión de configuración
- Extensión de `reports_menu.py` - Menú de configuración de destinatario
- Integración con sistema de notificaciones existente

---

## Tabla de tareas

| ID  | Tarea                                           | Prioridad | Estado      |
|-----|-------------------------------------------------|-----------|-------------|
| 01  | Extender `GroupConfig` con campo destinatario   | Alta      | Pendiente   |
| 02  | Crear `DestinationConfig` modelo de datos       | Alta      | Pendiente   |
| 03  | Implementar `ReportsConfigService`             | Alta      | Pendiente   |
| 04  | Añadir opción en `reports_menu.py`             | Alta      | Pendiente   |
| 05  | Crear callback handlers para configuración      | Alta      | Pendiente   |
| 06  | Integrar con sistema de notificaciones          | Alta      | Pendiente   |
| 07  | Modificar `ReportsFeature` para usar destino   | Alta      | Pendiente   |
| 08  | Persistir configuración por grupo               | Media     | Pendiente   |
| 09  | Pruebas unitarias                               | Alta      | Pendiente   |
| 10  | Documentación técnica                           | Baja      | Pendiente   |

---

## Fase 1: Configuración de Datos

**Objetivo fase:**
Extender el modelo de datos existente para soportar la configuración de destinatarios.

**Implementacion fase:**
1. Añadir campo `report_destination` a `GroupConfig`:
   - Tipo: string/enum
   - Valores: `ninguno`, `fundador`, `grupo_staff`

2. Crear `DestinationConfig` dataclass:
   - `destination_type`: EnumDestinationType
   - `custom_recipients`: list[int] (opcional)
   - `enabled`: bool

3. Integrar con `ConfigStorage` existente

4. Ejecutar migración de datos si es necesario

---

## Fase 2: Servicio de Configuración

**Objetivo fase:**
Implementar lógica de negocio para gestionar la configuración de destinatarios.

**Implementacion fase:**
1. Crear `ReportsConfigService`:
   - `get_destination(chat_id)` - Obtener configuración actual
   - `set_destination(chat_id, destination_type)` - Guardar configuración
   - `get_destination_recipients(chat_id)` - Resolver lista de destinatarios

2. Implementar resolución de destinatarios:
   - `NINGUNO`: Retornar lista vacía
   - `FUNDADOR`: Obtener ID de fundador del grupo
   - `GRUPO_STAFF`: Obtener lista de IDs del grupo staff

3. Integrar con sistema de permisos existente

---

## Fase 3: Interfaz de Usuario y Callbacks

**Objetivo fase:**
Añadir opciones de menú y handlers para que administradores configuren el destinatario.

**Implementacion fase:**
1. Extender `reports_menu.py`:
   - Añadir opción "Configurar Destinatario" al menú principal
   - Crear submenú de selección (Ninguno/Fundador/Grupo Staff)

2. Crear callback handlers:
   - `reports:config:dest` - Mostrar menú de configuración
   - `reports:config:set:{type}` - Procesar selección

3. Añadir validación de permisos (solo administradores)

4. Mostrar estado actual de configuración en UI

---

## Fase 4: Integración con Sistema de Envío

**Objetivo fase:**
Conectar la configuración con el flujo de creación y notificación de reportes.

**Implementacion fase:**
1. Modificar `ReportsFeature.create_report()`:
   - Llamar a `ReportsConfigService.get_destination_recipients()`
   - Incluir lista de destinatarios en el objeto reporte

2. Extender sistema de notificaciones:
   - Usar lista de destinatarios configurada
   - Manejar caso "NINGUNO" (no enviar notificación)

3. Integrar con lógica existente de notificaciones a admins

4. Añadir logs de auditoría por cada envío

---

## Fase 5: Persistencia y Pruebas

**Objetivo fase:**
Garantizar persistencia de configuración y correcto funcionamiento del sistema.

**Implementacion fase:**
1. Verificar que `ConfigStorage` persista la configuración por chat

2. Crear pruebas unitarias:
   - Cambios de configuración
   - Resolución de destinatarios
   - Integración con notifications

3. Pruebas de integración con flujo completo

4. Documentar casos de uso y ejemplos