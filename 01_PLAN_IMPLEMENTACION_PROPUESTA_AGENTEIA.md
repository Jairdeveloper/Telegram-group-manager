Fecha: 2026-03-26
version: 1.0
referencia: 01_propuesta_robot_agenteia.md

Resumen de la migracion:
El sistema actual cuenta con Agent Core, Intent Router, memoria, RAG, herramientas reales y métricas. La migración consiste en transformar el bot en un agente IA de administración de grupos mediante una capa de acciones estructuradas y un NLU/Planner que traduzca lenguaje natural a acciones con validación, permisos y confirmaciones. Se unificarán los flujos de menú/comandos con acciones, manteniendo seguridad, trazabilidad y reutilizando funcionalidades existentes del ManagerBot.

Arquitectura final:
El sistema tendrá una capa de Action Registry como fuente única de verdad, donde menús, comandos y lenguaje natural disparan acciones registradas. Un Action Parser basado en LLM traducirá texto libre a acciones estructuradas, con validación de schemas y fallback rule-based. Un SlotResolver gestionará entradas incompletas mediante flujos conversacionales. La capa de permisos estará desacoplada, con políticas de confirmación según riesgo (ban, kick, borrar mensajes masivo) y auditoría completa. Los menús se construirán dinámicamente consultando el estado real de cada feature.

Tabla de tareas:

Fase: 1
Objetivo fase: Catálogo de acciones y capa unificada de ejecución
Implementacion fase:
- Crear `app/agent/actions/` con Action Registry (id, descripción, inputs, permisos, efectos)
- Cada acción expone schema de parámetros (pydantic), validate(context) para permisos admin/moderador y contexto grupo, execute(context, params) reutilizando lógica de ManagerBot
- Extraer lógica de handlers/menus a servicios reutilizables en `app/manager_bot/services/`
- Resultado: Menús y NL usan el mismo backend de acciones

Fase: 2
Objetivo fase: NLU → Action (parser estructurado)
Implementacion fase:
- Añadir ActionParser que use LLM para producir JSON con action_id y params
- Validar JSON con schema de la acción; si falla, pedir aclaración
- Añadir confidence y fallback rule-based
- Resultado: El bot entiende texto libre y lo convierte en acción concreta

Fase: 3
Objetivo fase: Flujos conversacionales guiados (slots)
Implementacion fase:
- Guardar pending_action en memoria de conversación
- Crear SlotResolver para preguntar por parámetros faltantes
- Integrar con UI: mostrar botones rápidos para completar slots
- Resultado: UX fluida y coherente con menús inline

Fase: 4
Objetivo fase: Confirmaciones, auditoría y seguridad
Implementacion fase:
- Política de confirmación según riesgo (ban, kick, borrar mensajes masivo)
- Registro de cambios (quién, qué, cuándo) en audit_log
- Políticas por tenant (allow/deny actions, límites por rol)
- Resultado: Acciones seguras y auditables

Fase: 5
Objetivo fase: Sincronización UI/UX con estado real
Implementacion fase:
- Estado de cada feature consultable desde Action Registry
- Menús construidos dinámicamente con ActionStateProvider
- Eliminar modales informativos y actualizar descripción inline
- Resultado: UI coherente con el estado real del grupo

Fase: 6
Objetivo fase: Evaluación, QA y dataset de intents
Implementacion fase:
- Dataset interno de frases → acción esperada
- Tests automáticos de ActionParser y SlotResolver
- Métricas de precisión y tasa de confirmación/cancelación
- Resultado: Evolución controlada y medible