Arquitectura elegida: Microservicios modulares (API-first) + Adapter de Telegram

Decisión única:
- Adoptar una arquitectura modular basada en microservicios desplegables en contenedores (Docker) y orquestables con Kubernetes. API-first con un Adapter de Telegram (async) que conecta a la capa de conversación.

Componentes principales:
- Adapter Telegram (aiogram) — maneja updates y webhooks/long-polling.
- API Gateway (FastAPI) — endpoint REST/GRPC para chat y administración.
- Chat Service (Actor) — motor híbrido reglas + LLM, separado en paquete reutilizable.
- Embedding Service — abstracción sobre `pgvector` o Milvus; inicialmente `pgvector` en Postgres para acelerar salida al mercado.
- LLM Orchestrator — switch entre Ollama (on-prem) y OpenAI (cloud) con circuito de fallback.
- Storage — Postgres (principal), Redis (caching, rate limiting), object store para archivos si es necesario.
- Queue (Redis Streams o RabbitMQ) — para tareas asíncronas (batch-embeddings, moderation, generation streaming).
- Observability — Prometheus + Grafana, logs estructurados y Sentry.

Por qué descarto alternativas:
- Monolito persistente: rápido para prototipar, pero bloquea escalado y evolución a agente autónomo.
- Serverless pura (funciones por request): sube latencia en LLM/hardware pesado; complica estado/embeddings.
- VectorDB gestionado desde el inicio (Weaviate/Milvus gestionado): coste y complejidad excesivos en MVP; preferir `pgvector` en Postgres para MVP.

Consecuencias estratégicas:
- Permite multi-tenant futuro (SaaS) con límites por tenant en Redis/queue.
- Facilita migración a agente autónomo encapsulando comportamiento y política en Chat Service.
