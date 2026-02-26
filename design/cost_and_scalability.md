Coste estimado y escalabilidad

MVP (local / small cloud)
- Infra mínima (1 small VM, Postgres managed, Redis): $50 - $200 / mes.
- LLM: Ollama local => infra cost only. OpenAI fallback adds consumption cost (est. $0.002 - $0.02 per 1k tokens depending model).

Production (SaaS, small cluster)
- K8s cluster 2-3 nodes + managed Postgres + Redis + monitoring: $300 - $1,500 / mes.
- Vector DB managed: add $200 - $800 / mes.
- LLM API usage: can be dominant cost depending on usage pattern.

Scalability plan:
- Start: single Postgres + pgvector; scale reads via replicas and Redis caching.
- Medium: migrate vector indices to dedicated VectorDB, scale LLMs horizontally (Ollama inference nodes or cloud API).
- Large: autoscaling k8s, sharded vector DB, autoscaling inference fleet.

Nivel de complejidad: Medio → Alto (creciente con agent features).
