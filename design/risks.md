Riesgos técnicos y mitigaciones

1) Latencia y coste de LLMs
- Riesgo: LLM cloud resulta caro / latente.
- Mitigación: Priorizar Ollama para baja latencia en infra propia; usar OpenAI como fallback; cachear respuestas y usar streaming.

2) Escalado de vectores
- Riesgo: pgvector en Postgres no escala indefinidamente.
- Mitigación: Empezar con pgvector; medir, y migrar a Milvus/Weaviate cuando sea necesario.

3) Consistencia del estado conversacional
- Riesgo: Monolito guarda estado en JSON local (pérdida/consistencia).
- Mitigación: Migrar a Postgres y Redis para sesiones y caché.

4) Seguridad y abuse cases en grupos Telegram
- Riesgo: Bot podría ser usado para spam o abusos.
- Mitigación: Rate limits, moderation pipeline, admin controls, ban lists.

5) Operacional y costos
- Riesgo: Costes inesperados de hosting/LLM.
- Mitigación: Controlar presupuesto con quotas, usar embeddings locales, planificación de escalado gradual.

6) Entrega y QA
- Riesgo: Comportamiento inesperado del motor de reglas + LLM.
- Mitigación: Tests automáticos para patrones, e2e tests con sandbox de Telegram.
