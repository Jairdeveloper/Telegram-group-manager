Stack técnico (decisión concreta y justificativa)

Core language & runtime
- Python 3.11: ecosistema, async support, maturity.

Web/API
- FastAPI: async, production-ready, docs auto, easy to containerize.
- Uvicorn/Gunicorn: asgi workers for production.

Telegram Adapter
- `aiogram` (preferred): async, robust, good webhook support. Alternative: `python-telegram-bot` (sync/async hybrid).

Database & Vector
- Postgres + `pgvector` (MVP): ACID, familiar, pgvector simple de operar.
- Migrate to Milvus/Weaviate when vector scale demands it.

Caching/Queue
- Redis: caching, rate-limiting, pub/sub, Streams for background work.

Embeddings & LLM
- Embeddings: `sentence-transformers` local for privacy and cost control; optionally OpenAI embeddings for quality/scale.
- LLM: Ollama for on-prem inference (low-latency) + OpenAI as fallback for reliability.

ORM & Config
- SQLAlchemy + Alembic (migrations).
- pydantic-settings for config management.

Infra & CI
- Docker for local/dev; Kubernetes (AKS/EKS/GKE) for production.
- GitHub Actions for CI/CD; Helm charts for deployments.

Monitoring & Security
- Prometheus + Grafana, Loki for logs, Sentry for errors.
- TLS termination at ingress; OAuth2/JWT for admin API.

Why this stack:
- Minimizes initial ops cost (Postgres/pgvector), keeps path to scale with mature components.
- Python + FastAPI leverages existing codebase quickly.
