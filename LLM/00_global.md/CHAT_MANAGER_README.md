# Chat Manager Group Bot — README

Resumen
- Nombre: Chat Manager (Telegram Group Bot)
- Propósito: Gestionar conversaciones y moderación en grupos de Telegram usando un motor híbrido reglas + LLM (local u OpenAI) basado en el código existente `chatbot_monolith.py`.
- Estado actual: MVP funcional en modo monolítico con API REST (`--mode api`) y un adapter de Telegram (`telegram_adapter.py`). La clase `Actor` fue renombrada a `Agent`.

Contenido del repositorio relevante
- `chatbot_monolith.py` — Motor principal (Agent, PatternEngine, Embeddings opcionales, LLM fallback, storage JSON, API FastAPI).
- `telegram_adapter.py` — Adapter mínimo (long-polling) que envía mensajes al endpoint `/api/v1/chat`.
- `requirements.txt` — Dependencias para ejecutar el MVP.
- `design/` — Documentación de arquitectura, stack, roadmap, riesgos y decisiones.

Requisitos
- Python 3.10+ (recomendado 3.11)
- Pip

Variables de entorno principales
- `TELEGRAM_BOT_TOKEN` — Token del bot de Telegram (obligatorio para `telegram_adapter.py`).
- `CHATBOT_API_URL` — URL del endpoint de chat (default: `http://127.0.0.1:8000/api/v1/chat`).
- `OPENAI_API_KEY` — (opcional) para usar OpenAI como fallback.
- `OLLAMA_BASE_URL` — (opcional) URL de Ollama local (default `http://localhost:11434`).
- `API_HOST` / `API_PORT` — Host y puerto para la API (configurables en `Settings`).

Instalación rápida
```bash
python -m venv .venv
.\.venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

Ejecución MVP (local)
1) Levantar la API (chat engine) usando entrypoint canonico
```bash
uvicorn app.api.entrypoint:app --host 0.0.0.0 --port 8000
```
2) En otra terminal, iniciar el adapter de Telegram (long-polling)
```bash
set TELEGRAM_BOT_TOKEN=xxxx:yyyyy
python telegram_adapter.py
```
Nota: `telegram_adapter.py` por defecto hace POST a `CHATBOT_API_URL` con `message` como parámetro.

Uso rápido
- Invita al bot al grupo o chatea en privado. El adapter enviará cada mensaje al endpoint y replicará la respuesta.
- Patrones soportados: saludos (`hello`, `hi`), presentaciones (`my name is ...`), preguntas simples, agradecimientos, confirmaciones y respuestas por defecto. Consulta `chatbot_monolith.py -> get_default_brain()` para la lista completa.

Ejemplo curl (directo a la API)
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/chat?message=hello&session_id=group1"
```

Consideraciones para desplegar en producción
- Reemplazar `telegram_adapter.py` long-polling por Webhooks con `aiogram`/FastAPI o usar una instancia con Webhook en HTTPS.
- Sustituir `SimpleConversationStorage` (JSON) por Postgres + `pgvector` para embeddings y SQLAlchemy/Alembic para migraciones.
- Añadir Redis para caché, rate-limits y colas de background (embeddings, moderation).
- Contenerizar (Docker) y orquestar (Kubernetes) para escalabilidad.
- Observabilidad: métricas (Prometheus), logs estructurados y Sentry para errores.

Commit / Naming notes
- Se renombró `Actor` → `Agent` en `chatbot_monolith.py`. Actualiza referencias si existen en otros módulos.

Roadmap corto (siguientes pasos técnicos)
- 1) Validar flujo local: API + adapter + pruebas en un grupo de Telegram (MVP).
- 2) Implementar Webhook adapter y HTTPS (let's encrypt / ingress).
- 3) Extraer `Agent` y `PatternEngine` a un paquete `chat_service` para facilitar tests y reuso.
- 4) Migrar almacenamiento a Postgres + pgvector; añadir Redis.

Archivos creados/actualizados por el equipo aquí
- `telegram_adapter.py` (scaffold long-polling)
- `design/*` (arquitectura, roadmap, riesgos, etc.)

Contacto y propietario
- Rol: CTO / Lead Dev — tú (asumido)

¿Quieres que cree también un `Dockerfile` y `docker-compose.yml` mínimo para probar el MVP con un único comando?
