Fecha: 2026-03-26
version: 1.0
referencia: 01_propuesta_robot_agenteia.md

Resumen de la implementacion

Este plan convierte las mejoras arquitectónicas recomendadas en una ejecución por fases. El foco es unificar comandos/menús/NL en un Action Registry, desacoplar permisos, agregar dry‑run y rollback, y centralizar plantillas de respuesta para una UX consistente. El resultado esperado es un núcleo de acciones reutilizable, seguro y auditable para la evolución a agente IA.

Arquitectura final:

- Action Registry (Single Source of Truth) para comandos/menús/NL.
- Capa de permisos desacoplada por acción/rol/tenant.
- Ejecutor de acciones con soporte de dry‑run y rollback.
- Plantillas de respuesta centralizadas para UX consistente.
- UI/UX sincronizada en tiempo real con el estado de acción.

Tabla de tareas:

Fase:
Fase 1 - Action Registry base
OBjetivo fase:
Definir el contrato de acciones y centralizar la ejecución desde un único registro.
Implementacion fase:
- Crear `app/agent/actions/registry.py` con modelos de acción (id, descripción, schema, permisos).
- Crear `app/agent/actions/executor.py` para ejecutar acciones registradas.
- Exponer interfaz de consulta de acciones para menús y NL.
- Migrar 2-3 acciones críticas (ej. antiflood, antispam, welcome) como piloto.

Fase:
Fase 2 - Permisos desacoplados
OBjetivo fase:
Separar la validación de permisos del flujo de ejecución.
Implementacion fase:
- Crear `app/agent/actions/permissions.py` con políticas por rol/tenant.
- Mapear roles existentes (admin/moderator/user) y reglas por acción.
- Integrar validación previa a la ejecución en el executor.
- Agregar mensajes de error estandarizados para permisos insuficientes.

Fase:
Fase 3 - Dry‑run y previsualización
OBjetivo fase:
Permitir simular cambios y mostrar impacto antes de confirmar.
Implementacion fase:
- Extender el contrato de acción con `dry_run(context, params)`.
- Implementar previsualización en 3 acciones piloto.
- Añadir UI de confirmación con resumen del cambio.
- Añadir flag `require_confirmation` según riesgo.

Fase:
Fase 4 - Rollback básico
OBjetivo fase:
Revertir acciones críticas cuando exista operación inversa segura.
Implementacion fase:
- Definir `undo(context, params, previous_state)` en acciones elegibles.
- Persistir `previous_state` en audit log.
- Habilitar rollback para acciones con cambios reversibles (ej. toggles).
- Documentar límites de rollback (no reversible en ciertas acciones).

Fase:
Fase 5 - Plantillas de respuesta centralizadas
OBjetivo fase:
Normalizar respuestas y estados de UI para todos los canales.
Implementacion fase:
- Crear `app/agent/actions/templates.py` con plantillas por acción.
- Normalizar mensajes de éxito/error/confirmación.
- Integrar respuestas de menús para reflejar estado post‑acción.
- Eliminar modales informativos redundantes cuando aplique.

Fase:
Fase 6 - Integración completa con NL y menús
OBjetivo fase:
Hacer que NL, comandos y menús disparen la misma acción.
Implementacion fase:
- Conectar `ActionParser` → Action Registry.
- Adaptar menús para usar `ActionStateProvider`.
- Añadir resolución de slots para parámetros faltantes.
- QA funcional con casos reales en grupos.
