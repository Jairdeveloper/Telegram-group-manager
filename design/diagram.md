Diagrama conceptual (texto)

Telegram Users
  ↓ (updates)
Telegram Adapter (aiogram)
  ↓ HTTP/gRPC
API Gateway (FastAPI)
  ├─ Auth / Rate limits (Redis)
  ├─ Chat Service (Actor)
  │    ├─ Pattern Engine (rules)
  │    ├─ Embedding Service (pgvector/Postgres)
  │    └─ LLM Orchestrator (Ollama -> OpenAI fallback)
  ├─ Background Worker (Redis Streams) -> embeddings, moderation
  └─ Storage (Postgres)

Observability: Logs → Loki; Metrics → Prometheus → Grafana
Security: Ingress TLS, JWT for admin, per-tenant quotas in Redis

Notes:
- Use webhooks in production; long-polling allowed for dev.
- Keep Actor stateless; session state in Postgres/Redis.
