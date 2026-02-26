Roadmap técnico (fases, entregables y tiempos estimados)

MVP (0 - 2 semanas)
- Goal: Ejecutar bot en Telegram con el actor actual sin refactor completo.
- Tareas:
  - Añadir `telegram_adapter.py` que envíe updates al endpoint `/api/v1/chat` o invoque `Actor` directamente.
  - Crear `requirements.txt` y Dockerfile mínimo.
  - Documentar variables de entorno (`TELEGRAM_BOT_TOKEN`, `API_HOST`, `API_PORT`).
- Deliverable: Bot Telegram funcional en entorno local / Docker Compose.

Phase 1 — Modularización (2 - 6 semanas)
- Extraer `Actor`, `PatternEngine`, `EmbeddingService`, `LLMFallback` a módulos independientes.
- Reemplazar `SimpleConversationStorage` por Postgres + Alembic.
- Añadir Redis para caching y rate-limiting.
- Implementar background worker (Redis Streams) para embeddings y moderation.

Phase 2 — Production hardening (6 - 12 semanas)
- Add pgvector and migrate embeddings storage.
- Containerize and prepare k8s manifests + Helm.
- Observability (Prometheus/Grafana/Sentry/Loki).
- Auth & Multi-tenant support, DBA hardening.

Phase 3 — Scale & Agentization (3-6 months)
- Swap to dedicated VectorDB if needed (Milvus/Weaviate).
- Implement control loop + policy engine for autonomous agents (task planner, executor).
- Add paid features, tenancy billing, enterprise security.

Prioridades:
1. Telegram adapter + basic Docker (MVP) — highest priority.
2. Modularization of chat logic.
3. Persistent DB + vector storage.
4. Production infra + monitoring.
