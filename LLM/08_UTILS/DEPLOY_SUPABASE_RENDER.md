# Despliegue: Supabase (Postgres + pgvector) + Render (FastAPI)

Guía paso a paso para desplegar la aplicación usando Supabase como capa de datos (Postgres + pgvector) y Render para ejecutar el contenedor Docker de FastAPI.

1) Preparar Supabase
   - Crear un proyecto en https://app.supabase.com
   - En `Database > Extensions` habilitar `pgvector` (si no está disponible, crear extensión en SQL: `CREATE EXTENSION IF NOT EXISTS vector;`).
   - Guardar `SUPABASE_URL` y `SUPABASE_SERVICE_ROLE_KEY` (usar `SERVICE_ROLE` para operaciones back-end).
   - Crear las tablas necesarias para tu aplicación (ej. `documents` con columna vector `embedding vector(1536)` o según tamaño de embeddings).

2) Preparar la app
   - Variables de entorno necesarias (ejemplos):
     - `DATABASE_URL` (cadena Postgres proporcionada por Supabase)
     - `SUPABASE_URL`, `SUPABASE_KEY` (service role)
     - `OPENAI_API_KEY` (si usas OpenAI)
     - `REDIS_URL` (opcional)
     - `API_HOST`, `API_PORT`, `DEBUG`

   - Configura `src/core/config.py` para leer `DATABASE_URL`/`SUPABASE` si no está ya.
   - Asegura migraciones con `alembic` (definir `alembic.ini` y scripts de migración). Al desplegar, ejecutar `alembic upgrade head`.

3) Docker image
   - El `Dockerfile` en el repo crea una imagen que arranca la app con `python -m src.main --mode api`.
   - Construir localmente para pruebas:
     ```bash
     docker build -t chatbot-evolution:latest .
     docker run -e DATABASE_URL="postgres://..." -p 8000:8000 chatbot-evolution:latest
     ```

4) Crear servicio en Render
   - En https://dashboard.render.com crear un nuevo `Web Service` y seleccionar `Docker` (conectar repo o subir Dockerfile).
   - Establecer `Dockerfile` path: `./Dockerfile`.
   - Añadir variables de entorno necesarias en el panel de Render: `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_KEY`, `OPENAI_API_KEY`, etc.
   - Start command (opcional) para ejecutar migraciones antes de arrancar:
     ```bash
     alembic upgrade head && python -m src.main --mode api
     ```
   - Health check: `http://<service>.onrender.com/api/v1/health`.

5) CI/CD
   - Agregar un GitHub Action que ejecute tests, build de la imagen y publicación (ejemplo: `.github/workflows/ci.yml` incluido en este repo).
   - En Render puedes configurar despliegues automáticos desde `main` branch.

6) Verificación
   - Comprobar `/api/v1/health` y endpoints de la API.
   - Insertar un embedding y ejecutar una consulta de similitud en `pgvector` para validar index y performance.

Notas
 - Para volúmenes grandes de embeddings considerar un vector DB dedicado (Pinecone, Weaviate, Milvus).
 - Guardar todas las claves en el panel de Render y Supabase (no en el repositorio).

Referencias
 - Supabase: https://supabase.com
 - Render Docker docs: https://render.com/docs/deploy-docker
