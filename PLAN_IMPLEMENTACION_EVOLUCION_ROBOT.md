Fecha: 2026-03-26
version: 1.0
referencia: PROPUESTA_EVOLUCION_AGENTE.md; ARQUITECTURA_PROYECTO_ROBOT.md; arquitectura.png

Resumen de la implementacion

Evolucionar el proyecto Robot desde un chatbot rule-based a un agente IA con razonamiento, memoria de corto y largo plazo, RAG y ejecucion de tools reales, manteniendo el monolito modular actual. El plan prioriza integrar LLM real, memoria conversacional, RAG sobre PostgreSQL + pgvector, y un Agent Core con loop ReAct (identify/plan/execute), conectando herramientas reales y observabilidad completa. La integracion se hace dentro del flujo actual (webhook -> dispatcher) reemplazando el flujo de chat por un Intent Router que derive a Agent Flow o a flujos OPS/Enterprise existentes.

Arquitectura final:

- Entrada: app.webhook.entrypoint -> app.webhook.handlers
- Clasificacion: app.telegram.dispatcher -> Intent Router (nuevo)
- Agent Flow:
  - Agent Core (Reason + Planner + Executor)
  - Memory System (short + long term)
  - RAG Service (pgvector)
  - Tool Executor (tools reales)
- Soporte: Guardrails + Policies + Observabilidad (Prometheus + tracing)
- Infra: PostgreSQL + pgvector, Redis (colas y cache), LLM provider (Ollama/OpenAI)

Tabla de tareas:

| Fase | Objetivo | Entregables clave | Dependencias |
|------|----------|------------------|--------------|
| 1 | Integrar LLM real | chat_service/llm/*, factory, provider Ollama/OpenAI, wiring en chat_service/agent.py | Ninguna |
| 2 | Intent Router + Agent Flow basico | app/agent/intent_router.py, app/agent/core.py (skeleton), wiring en dispatcher | Fase 1 |
| 3 | Memory System | app/agent/memory.py, app/agent/context.py, schema conversations | Fase 1 |
| 4 | RAG / Knowledge Base | app/agent/rag.py, app/knowledge/indexer.py, embeddings, pgvector | Fase 1-3 |
| 5 | Agent Core ReAct + Planner | app/agent/core.py completo, planner, reasoning, tool executor | Fase 2-4 |
| 6 | Tools reales | app/tools/builtins.py + nuevos adapters (search, weather, db, http) | Fase 1-5 |
| 7 | Observabilidad y hardening | metricas detalladas, tracing, dashboards, politicas de costos | Fase 1-6 |

Fase: 1
OBjetivo fase:
Integrar un LLM real como proveedor de respuestas generativas, habilitando el primer paso del agente.
Implementacion fase:
- Crear chat_service/llm/base.py, factory.py, chat.py y providers/ollama.py, providers/openai.py.
- Reemplazar el placeholder en app/tools/builtins.py por invocacion a LLM real.
- Integrar LLM en chat_service/agent.py para mensajes tipo chat.
- Agregar configuracion en app/config/settings.py para modelos, endpoints y API keys.
- Validar con prueba manual de una conversacion simple.

Fase: 2
OBjetivo fase:
Introducir Intent Router y un Agent Flow basico que enrute entre chat, ops y tareas de agente.
Implementacion fase:
- Crear app/agent/intent_router.py con reglas de comandos y clasificacion LLM.
- Agregar app/agent/core.py (skeleton) con interfaz process().
- Modificar app/telegram/dispatcher.py para derivar a Intent Router en flujo chat.
- Mantener compatibilidad con OPS y Enterprise en paralelo.

Fase: 3
OBjetivo fase:
Habilitar memoria conversacional de corto y largo plazo.
Implementacion fase:
- Implementar app/agent/memory.py con buffer por chat_id y politicas de truncado.
- Implementar app/agent/context.py para construir ventana de contexto.
- Agregar tablas conversations/messages via migration.
- Guardar mensajes entrantes y respuestas del agente.

Fase: 4
OBjetivo fase:
Incorporar RAG para busqueda semantica en documentacion tecnica.
Implementacion fase:
- Implementar app/agent/rag.py y app/agent/embeddings.py.
- Crear app/knowledge/indexer.py + loader/chunks.
- Configurar pgvector y pipeline de indexacion.
- Integrar RAG en Agent Core para queries con necesidades de conocimiento.

Fase: 5
OBjetivo fase:
Completar Agent Core con loop ReAct y planificador multi-step.
Implementacion fase:
- Completar app/agent/core.py con Reason/Plan/Execute/Observe.
- Implementar app/agent/planner.py y app/agent/reasoning.py.
- Crear app/agent/tool_executor.py con ejecucion de tools y retries.
- Definir criterios de salida y limites de iteracion.

Fase: 6
OBjetivo fase:
Reemplazar tools simuladas por tools reales y seguras.
Implementacion fase:
- Implementar app/tools/* reales (search, weather, database, http).
- Validar ACL/quotas en app/policies/engine.py.
- Añadir sanitizacion y guardrails por tool.

Fase: 7
OBjetivo fase:
Observabilidad completa y hardening operativo.
Implementacion fase:
- Agregar metricas de latencia, tokens, tools y RAG.
- Integrar tracing y dashboards.
- Añadir caching y politicas de costos (rate limits por chat).
- Documentar y entrenar runbooks.
