Fecha: 2026-03-26
version: 1.0
referencia: PLAN_IMPLEMENTACION_EVOLUCION_ROBOT.md

Resumen de la implementacion

Se completo la Fase 1 integrando un proveedor LLM real y dejando listo el cableado para respuestas generativas. Se agrego el modulo chat_service/llm con proveedores OpenAI y Ollama, se actualizo el Agent para usar LLM como fallback cuando no hay match de patrones (controlado por feature flag), se reemplazo el placeholder del tool LLM por una llamada real y se incluyo configuracion en settings y .env.example.

Arquitectura final (Fase 1)

- chat_service/llm/*: capa de integracion LLM (config, factory, providers)
- chat_service/agent.py: fallback a LLM si no hay match
- app/tools/builtins.py: tool LLM real con control por flag
- app/config/settings.py: variables LLM
- .env.example: ejemplo de configuracion

Fase: 1
OBjetivo fase:
Integrar un LLM real como proveedor de respuestas generativas, habilitando el primer paso del agente.

Implementacion fase:
- Se crearon los modulos:
- chat_service/llm/base.py (LLMConfig, BaseLLMProvider, DummyProvider)
- chat_service/llm/factory.py (LLMFactory y config_from_settings)
- chat_service/llm/chat.py (helper de generacion)
- chat_service/llm/providers/openai.py
- chat_service/llm/providers/ollama.py
- Se actualizo chat_service/agent.py para usar LLM como fallback cuando no hay match (feature flag LLM_ENABLED).
- Se actualizo app/tools/builtins.py para que el tool `llm` ejecute un proveedor real.
- Se agrego configuracion LLM en app/config/settings.py y ejemplo en .env.example.
- Se ajusto app/api/bootstrap.py para inyectar configuracion LLM al Agent.

Archivos modificados/creados:
- chat_service/llm/__init__.py
- chat_service/llm/base.py
- chat_service/llm/factory.py
- chat_service/llm/chat.py
- chat_service/llm/providers/__init__.py
- chat_service/llm/providers/openai.py
- chat_service/llm/providers/ollama.py
- chat_service/agent.py
- app/tools/builtins.py
- app/config/settings.py
- app/api/bootstrap.py
- .env.example

Validacion:
- No se ejecutaron pruebas automatizadas ni llamadas reales a LLM en este paso.
- Para validar manualmente: setear LLM_ENABLED=true y configurar LLM_PROVIDER/OPENAI_API_KEY u OLLAMA_BASE_URL.

Fase: 2
OBjetivo fase:
Introducir Intent Router y un Agent Flow basico que enrute entre chat, ops y tareas de agente.

Implementacion fase:
- Se creo app/agent/intent_router.py con clasificacion rule-based y opcion de clasificacion LLM.
- Se creo app/agent/core.py como skeleton de Agent Core con fallback a ChatService.
- Se creo app/agent/__init__.py para exportar componentes del agente.
- Se actualizo app/telegram/dispatcher.py para usar Intent Router y emitir kind agent_task.
- Se actualizo app/telegram/models.py para incluir el nuevo tipo agent_task.
- Se actualizo app/webhook/handlers.py para procesar agent_task y enrutar al Agent Core manteniendo la logica de estados conversacionales.

Archivos modificados/creados (Fase 2):
- app/agent/__init__.py
- app/agent/intent_router.py
- app/agent/core.py
- app/telegram/dispatcher.py
- app/telegram/models.py
- app/webhook/handlers.py

Validacion:
- No se ejecutaron pruebas automatizadas en este paso.
- Para validacion manual: enviar un mensaje con palabras clave (ej: "buscar clima") y verificar que el evento sea webhook.agent_flow.ok.

Fase: 3
OBjetivo fase:
Habilitar memoria conversacional de corto y largo plazo.

Implementacion fase:
- Se creo app/agent/memory.py con buffer en memoria y persistencia via ConversationRepository.
- Se creo app/agent/context.py con ContextBuilder para construir ventana de contexto.
- Se actualizo app/agent/core.py para usar MemorySystem y ContextBuilder, y guardar cada intercambio.
- Se actualizaron exports en app/agent/__init__.py.

Archivos modificados/creados (Fase 3):
- app/agent/memory.py
- app/agent/context.py
- app/agent/core.py
- app/agent/__init__.py

Validacion:
- No se ejecutaron pruebas automatizadas en este paso.
- Para validacion manual: activar LLM y verificar que el system_prompt contenga historial y que conversations.json (o PostgreSQL) reciba nuevos mensajes.

Fase: 4
OBjetivo fase:
Incorporar RAG para busqueda semantica en documentacion tecnica.

Implementacion fase:
- Se creo app/agent/embeddings.py con SentenceTransformer para embeddings.
- Se creo app/agent/rag.py con busqueda y generacion con contexto.
- Se creo app/knowledge/indexer.py, loader.py y chunks.py para indexar documentos.
- Se creo app/knowledge/vector_store.py con InMemory y PostgresVectorStore.
- Se agrego modelo KnowledgeDocument en app/database/models.py.
- Se actualizo app/config/settings.py y .env.example con configuracion RAG.
- Se integro RAG en app/agent/core.py usando rag_enabled.
- Se actualizaron exports en app/agent/__init__.py y app/knowledge/__init__.py.

Archivos modificados/creados (Fase 4):
- app/agent/embeddings.py
- app/agent/rag.py
- app/knowledge/__init__.py
- app/knowledge/chunks.py
- app/knowledge/loader.py
- app/knowledge/indexer.py
- app/knowledge/vector_store.py
- app/database/models.py
- app/config/settings.py
- .env.example
- app/agent/core.py
- app/agent/__init__.py

Validacion:
- No se ejecutaron pruebas automatizadas ni indexaciones reales.
- Para validacion manual: crear un indice con KnowledgeIndexer y luego enviar una pregunta con RAG_ENABLED=true.

Fase: 5
OBjetivo fase:
Completar Agent Core con loop ReAct y planificador multi-step.

Implementacion fase:
- Se creo app/agent/reasoning.py con un reasoner basico y decision plan/respond.
- Se creo app/agent/planner.py como wrapper del Planner existente.
- Se creo app/agent/tool_executor.py como executor simple.
- Se actualizo app/agent/core.py para ejecutar un loop ReAct (decision -> plan -> respuesta) cuando AGENT_REACT_ENABLED=true.
- Se agrego configuracion AGENT_REACT_ENABLED y AGENT_MAX_ITERATIONS en settings y .env.example.
- Se actualizaron exports en app/agent/__init__.py.

Archivos modificados/creados (Fase 5):
- app/agent/reasoning.py
- app/agent/planner.py
- app/agent/tool_executor.py
- app/agent/core.py
- app/agent/__init__.py
- app/config/settings.py
- .env.example

Validacion:
- No se ejecutaron pruebas automatizadas en este paso.
- Para validacion manual: activar AGENT_REACT_ENABLED=true y enviar un mensaje con herramientas (ej: "calcula 2+2").

Fase: 6
OBjetivo fase:
Reemplazar tools simuladas por tools reales y seguras.

Implementacion fase:
- Se actualizaron tools en app/tools/builtins.py para usar APIs reales y agregar guardrails.
- Search: DuckDuckGo API configurable via SEARCH_API_URL/SEARCH_PROVIDER.
- Weather: OpenWeatherMap via WEATHER_API_KEY/WEATHER_API_URL.
- Database: consultas SELECT con limite via DATABASE_URL y DATABASE_MAX_ROWS.
- HTTP: GET con allowlist via HTTP_ALLOWED_HOSTS y limite de bytes.
- Se agregaron parametros de configuracion en app/config/settings.py y .env.example.

Archivos modificados/creados (Fase 6):
- app/tools/builtins.py
- app/tools/router.py
- app/config/settings.py
- .env.example

Validacion:
- No se ejecutaron pruebas automatizadas en este paso.
- Para validacion manual: configurar SEARCH_API_URL, WEATHER_API_KEY o HTTP_ALLOWED_HOSTS y probar tools via mensajes.

Fase: 7
OBjetivo fase:
Observabilidad completa y hardening operativo.

Implementacion fase:
- Se creo app/monitoring/agent_metrics.py con metricas Prometheus para agente, RAG, tools y LLM.
- Se integraron metricas en Agent Core (thoughts, actions, tokens), RAG (latency, tokens) y ToolRouter (duracion).
- Se exportaron metricas y helpers en app/monitoring/__init__.py.

Archivos modificados/creados (Fase 7):
- app/monitoring/agent_metrics.py
- app/monitoring/__init__.py
- app/agent/core.py
- app/agent/rag.py
- app/tools/router.py

Validacion:
- No se ejecutaron pruebas automatizadas en este paso.
- Para validacion manual: activar Prometheus y verificar nuevas metricas en /metrics.

Fase: 8
OBjetivo fase:
Crear pruebas para validar las nuevas capacidades del agente (LLM, intent routing, memoria, RAG, tools, ReAct, metricas).

Implementacion fase:
- Se crearon suites de tests unitarios en tests/agent/, tests/tools/ y tests/monitoring/.
- Se cubrieron rutas principales: intent_router, memory/context, rag, react y tools reales con mocks.
- Se agregaron checks basicos de metricas (agent_metrics) sin depender de Prometheus real.

Tests creados:
- tests/agent/test_intent_router_unit.py
- tests/agent/test_memory_context_unit.py
- tests/agent/test_rag_unit.py
- tests/agent/test_react_unit.py
- tests/tools/test_builtins_real_unit.py
- tests/monitoring/test_agent_metrics_unit.py

Validacion:
- No se ejecutaron pruebas en este paso.
- Sugerencia: pytest tests/agent tests/tools tests/monitoring
