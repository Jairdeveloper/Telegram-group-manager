Fecha: 2026-03-26
version: 1.0
referencia: PLAN_IMPLEMENTACION_EVOLUCION_AGENTE_COMPLETADO.md

Resumen de la propuesta

El sistema ya cuenta con un Agent Core, Intent Router, memoria, RAG, herramientas reales y métricas. El siguiente salto para convertirlo en un **agente IA de administración de grupos** es unificar los flujos de menú/comandos con una **capa de acciones estructuradas** y un **NLU/Planner** que traduzca lenguaje natural a esas acciones con validación, permisos y confirmaciones. La propuesta prioriza seguridad, trazabilidad y reutilización de funcionalidades existentes del ManagerBot.

Contexto actual (según código y última actualización)

- `app/agent/core.py` ya orquesta LLM, RAG, memoria y un loop ReAct.
- `app/agent/intent_router.py` enruta intents (rule-based y opción LLM).
- `app/tools/*` expone herramientas reales con guardrails.
- ManagerBot ya implementa operaciones de administración vía menús inline.
- Existen métricas y tests base, pero faltan flows de confirmación, acciones estructuradas y un esquema único de permisos.

Objetivo funcional

Permitir que un admin diga en lenguaje natural:
- “Activa antiflood con 10 mensajes en 5 segundos y borra mensajes”
- “Silencia 30m a los que envíen enlaces de Telegram”
Y el bot:
- Interprete la intención → genere una acción estructurada
- Valide permisos → solicite confirmación si aplica
- Ejecute la misma lógica que hoy se ejecuta desde menú/comando
- Responda con el resultado y refleje el estado en el menú

Propuesta de próximos pasos (por fases)

Fase 1: Catálogo de acciones y capa unificada de ejecución
Objetivo: Tener un “Action Registry” único que represente todas las operaciones de administración.
Implementación:
- Crear `app/agent/actions/` con un registro de acciones (id, descripción, inputs, permisos, efectos).
- Cada acción expone:
  - `schema` de parámetros (pydantic)
  - `validate(context)` (permiso admin/moderador, contexto grupo)
  - `execute(context, params)` (reusa la lógica de ManagerBot)
- Extraer la lógica que hoy vive en handlers/menus a servicios reutilizables (`app/manager_bot/services/`).
Resultado:
- Menús y NL usan el mismo backend de acciones.

Fase 2: NLU → Action (parser estructurado)
Objetivo: Traducir lenguaje natural a una acción validada y explícita.
Implementación:
- Añadir un `ActionParser` que use LLM para producir JSON con `action_id` y `params`.
- Validar el JSON con el schema de la acción; si falla, pedir aclaración.
- Añadir `confidence` y fallback rule-based.
Resultado:
- El bot entiende texto libre y lo convierte en acción concreta.

Fase 3: Flujos conversacionales guiados (slots)
Objetivo: Manejar entradas incompletas (“pon antiflood” → pedir cantidad/tiempo).
Implementación:
- Guardar `pending_action` en memoria de conversación.
- Crear un `SlotResolver` para preguntar por parámetros faltantes.
- Integrar con UI: mostrar botones rápidos para completar slots.
Resultado:
- UX fluida y coherente con menús inline.

Fase 4: Confirmaciones, auditoría y seguridad
Objetivo: Evitar cambios peligrosos y tener trazabilidad.
Implementación:
- Política de confirmación según riesgo (ban, kick, borrar mensajes masivo).
- Registro de cambios (quién, qué, cuándo) en `audit_log`.
- Políticas por tenant (allow/deny actions, límites por rol).
Resultado:
- Acciones seguras y auditables.

Fase 5: Sincronización UI/UX con estado real
Objetivo: Que el menú refleje siempre el estado actual.
Implementación:
- Estado de cada feature consultable desde `Action Registry`.
- Menús construidos dinámicamente con `ActionStateProvider`.
- Eliminar modales informativos y actualizar descripción inline.
Resultado:
- UI coherente con el estado real del grupo.

Fase 6: Evaluación, QA y dataset de intents
Objetivo: Medir calidad y reducir errores de interpretación.
Implementación:
- Dataset interno de frases → acción esperada.
- Tests automáticos de `ActionParser` y `SlotResolver`.
- Métricas de precisión y tasa de confirmación/cancelación.
Resultado:
- Evolución controlada y medible.

Mejoras arquitectónicas recomendadas

- **Action Registry como Single Source of Truth**: todo comando/menú/NL dispara acciones registradas.
- **Layer de permisos** desacoplado: validar roles por acción antes de ejecutar.
- **Dry‑run** para mostrar previsualización del cambio antes de confirmar.
- **Rollback básico** (cuando sea posible) para revertir cambios críticos.
- **Plantillas de respuesta** centralizadas para consistencia de UX.

Riesgos y mitigaciones

- Ambigüedad de lenguaje natural → usar confirmaciones y preguntas de clarificación.
- Acciones peligrosas → requerir confirmación y doble check de permisos.
- Divergencia entre menú y NL → unificar ejecución en `Action Registry`.

Resultados esperados

- Menos dependencia de comandos fijos.
- Mayor accesibilidad para admins no técnicos.
- Escalabilidad: nuevas funciones se agregan como acciones reutilizables.
