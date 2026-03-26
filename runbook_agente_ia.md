# Runbook de Uso - Agente IA del Chatbot (Flujo Canonico)

Fecha: 2026-03-26
Version: 1.1

## Objetivo
Este runbook describe los pasos para activar y usar la nueva funcionalidad de Agente IA (LLM, memoria, RAG y tools reales) **siguiendo el flujo de despliegue canonico del proyecto**.

## Flujo de despliegue canonico (resumen)
- **Entrada unica:** `app.webhook.entrypoint:app` (monolito modular)
- **No usar runtimes legacy:** `telegram_adapter.py` y `app.telegram_ops.entrypoint.py` (deprecated)
- **Worker** solo si `PROCESS_ASYNC=true` y hay Redis

## 0) Requisitos previos
- Python 3.10+
- Dependencias instaladas (`pip install -r requirements.txt` o `pip install -e .`)
- Acceso a un proveedor LLM (Ollama local o OpenAI)
- (Opcional) PostgreSQL si se usara memoria/RAG persistente

## 1) Configuracion (.env)
Crear/actualizar `.env` con variables **del runtime canonico**:

### Webhook/Telegram
- `TELEGRAM_BOT_TOKEN=...`
- `WEBHOOK_TOKEN=...` (recomendado)
- `PROCESS_ASYNC=false` (o `true` si usas Redis + worker)
- `DEDUP_TTL=86400`
- `HOST=0.0.0.0`
- `PORT=8000`

### Redis (si async)
- `REDIS_URL=redis://localhost:6379/0`

### LLM (elige un proveedor)
**Ollama (local)**
- `LLM_ENABLED=true`
- `LLM_PROVIDER=ollama`
- `LLM_MODEL=llama3` (o el modelo disponible)
- `OLLAMA_BASE_URL=http://localhost:11434`

**OpenAI**
- `LLM_ENABLED=true`
- `LLM_PROVIDER=openai`
- `LLM_MODEL=gpt-4o-mini` (o el modelo deseado)
- `OPENAI_API_KEY=...`
- `OPENAI_BASE_URL=https://api.openai.com/v1`

### Agente IA (Intent + ReAct)
- `AGENT_REACT_ENABLED=true`
- `AGENT_MAX_ITERATIONS=3`

### RAG (opcional)
- `RAG_ENABLED=true`
- `RAG_EMBEDDING_MODEL=all-MiniLM-L6-v2`
- `RAG_TOP_K=5`
- `RAG_MIN_SCORE=0.2`
- (Opcional) `RAG_USE_POSTGRES=true` si usas vector store en PostgreSQL

### Tools reales (opcional)
- Search (DuckDuckGo):
  - `SEARCH_API_URL=https://api.duckduckgo.com/`
  - `SEARCH_PROVIDER=duckduckgo`
- Weather (OpenWeatherMap):
  - `WEATHER_API_KEY=...`
- HTTP allowlist:
  - `HTTP_ALLOWED_HOSTS=example.com,api.myservice.com`

## 2) Indexar documentacion para RAG (opcional)
Ejemplo basico en consola Python:

```python
from app.knowledge.indexer import KnowledgeIndexer
from pathlib import Path

indexer = KnowledgeIndexer()
count = indexer.index_path(Path("./BASE_DE_CONOCIMIENTO"))
print("Chunks indexados:", count)
```

## 3) Arranque canonico
### 3.1 Webhook (entrada unica)
```bash
python -m app.webhook.entrypoint
```

O usando CLI (si instalaste el paquete):
```bash
robot
```

### 3.2 Worker (solo si PROCESS_ASYNC=true)
```bash
python worker.py
```

O usando CLI:
```bash
robot-worker
```

## 4) Registrar webhook de Telegram
Exponer el puerto `PORT` (ej: 8000) con ngrok/ingress y registrar el webhook:

- URL esperada:
  - `https://<PUBLIC_URL>/webhook/<WEBHOOK_TOKEN>`
  - Si no usas `WEBHOOK_TOKEN`, usar `TELEGRAM_BOT_TOKEN`.

Scripts disponibles en el repo:
- `set_webhook.py`
- `set_webhook_prod.py`
- `set_telegram_webhook.py`

## 5) Validacion manual (mensajes de ejemplo)
Enviar mensajes al bot:
- `buscar clima madrid`
- `calcula 2+2`
- `convierte 10 km a mi`

Esperado:
- Respuesta del agente sin necesidad de patrones.
- En logs, evento `webhook.agent_flow.ok`.
- Historial guardado en `conversations.json` (o PostgreSQL si esta configurado).

## 6) Verificacion de historial
- JSON (fallback): revisar `conversations.json`.
- PostgreSQL: consultar tabla `conversations`.

## 7) Verificacion de metricas
Abrir `/metrics` y buscar:
- `agent_thoughts_total`
- `agent_actions_total`
- `rag_retrieval_latency_seconds`
- `tool_execution_duration_seconds`
- `llm_tokens_used_total`

## 8) Troubleshooting
- No responde con LLM:
  - Verificar `LLM_ENABLED=true`.
  - Revisar conectividad a Ollama/OpenAI.
- RAG no devuelve contexto:
  - Verificar que se indexo la documentacion.
  - Verificar `RAG_ENABLED=true`.
- Tools fallan:
  - Configurar API keys (Weather).
  - Definir allowlist para HTTP.
- Webhook no recibe updates:
  - Verificar URL registrada y token correcto.
  - Confirmar que el puerto esta expuesto publicamente.

## 9) Rollback rapido
- Desactivar agente IA:
  - `AGENT_REACT_ENABLED=false`
  - `LLM_ENABLED=false`
- Desactivar RAG:
  - `RAG_ENABLED=false`
- Volver a comportamiento anterior (pattern matching + planner basic).

## 10) Nota sobre entrypoints legacy
- NO usar `telegram_adapter.py` ni `app.telegram_ops.entrypoint.py`.
- El entrypoint canonico es `app.webhook.entrypoint:app`.
