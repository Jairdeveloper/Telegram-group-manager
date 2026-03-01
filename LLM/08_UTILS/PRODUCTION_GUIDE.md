# Guía Completa: Llevar a Producción (Pasos 1, 2, 3)

## PASO 1: Recomendación de Plataformas y Arquitectura

### Recomendación Principal: Supabase + Render
- **Base de Datos**: Supabase (Postgres + pgvector para embeddings vectoriales)
- **Aplicación**: Render (contenedor Docker con FastAPI)
- **CI/CD**: GitHub Actions (tests automáticos + push de imagen a GHCR)

### Alternativas Recomendadas (en orden):
1. **Railway**: Setup rápido para prototipos, incluye Postgres y despliegue sencillo
2. **Fly.io**: Excelente para micro-servicios globales con bajo overhead
3. **AWS (App Runner)**: Para cargas empresariales con máximo control
4. **Serverless (AWS Lambda)**: Solo si ejecutas funciones cortas (no aplica para FastAPI long-running)

### Vector Databases Alternativas (si necesitas escala):
- **Pinecone**: Mejor para búsqueda vectorial de millones de embeddings
- **Weaviate**: Self-hosted o managed; open-source
- **Milvus**: Open-source, escala bien para data science

---

## PASO 2: Preparar Despliegue (Supabase + Render)

### 2.1 Crear Proyecto Supabase
```bash
# Accede a https://app.supabase.com
# 1. New project → Eligir nombre y región
# 2. Database > Extensions → Habilitar "pgvector"
# 3. Settings > Database → Copiar DATABASE_URL (postgres://...)
# 4. Settings > API → Copiar SUPABASE_URL y SERVICE_ROLE_KEY
```

### 2.2 Configurar tu Repo Localmente
```bash
# Clonar o usar tu repo
cd c:\Users\1973b\zpa\Projects\manufacturing\chatbot_evolution

# Crear .env con tus credenciales de Supabase
echo "DATABASE_URL=postgres://usuario:pass@host/db" > .env.production
echo "SUPABASE_URL=https://xxx.supabase.co" >> .env.production
echo "SUPABASE_KEY=eyJxx..." >> .env.production
echo "OPENAI_API_KEY=sk-xxx" >> .env.production
echo "DEBUG=false" >> .env.production
```

### 2.3 Crear Repositorio Git (GitHub)
```bash
# Si aún no está en GitHub:
git init
git add .
git commit -m "Initial commit: chatbot evolution production ready"
git branch -M main
git remote add origin https://github.com/tu-usuario/chatbot-evolution.git
git push -u origin main
```

### 2.4 Crear Web Service en Render
1. Acceder a https://dashboard.render.com
2. **New** → **Web Service**
3. **Connect Repository** → Selecciona `chatbot-evolution`
4. **Configurar**:
   - **Name**: `chatbot-evolution`
   - **Environment**: `Docker`
   - **Build Command**: `(usar default o `docker build ...`)`
   - **Start Command**: `alembic upgrade head && python -m src.main --mode api`
   - **Plan**: Starter (FREE si es para testing)

5. **Environment Variables** (agregar cada una):
   ```
   DATABASE_URL → (copiar de Supabase)
   SUPABASE_URL → (de Supabase)
   SUPABASE_KEY → (service role key)
   OPENAI_API_KEY → (tu key)
   DEBUG → false
   API_HOST → 0.0.0.0
   API_PORT → 8000
   ```

6. **Health Check Path**: `/api/v1/health`
7. **Crear servicio** → Render construirá y desplegará automáticamente

### 2.5 Crear Tablas en Supabase (si no existen)
Ejecuta en el SQL Editor de Supabase:
```sql
-- Extensión pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Tabla ejemplo para documentos/embeddings
CREATE TABLE IF NOT EXISTS documents (
  id BIGSERIAL PRIMARY KEY,
  content TEXT NOT NULL,
  embedding vector(384),  -- 384 dims si usas sentence-transformers/all-MiniLM-L6-v2
  created_at TIMESTAMP DEFAULT NOW()
);

-- Índice para búsqueda vecorial rápida
CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

---

## PASO 3: Tests Locales y Verificación

### 3.1 Pruebas en tu Máquina Antes de Desplegar
```bash
# Instalar dependencias
pip install -r requirements.txt
pip install -e .

# Ejecutar tests
pytest -q

# Resultado esperado: ≥ 40 tests pasados
```

### 3.2 Probar Localmente con Docker
```bash
# Build de la imagen
docker build -t chatbot-evolution:latest .

# Ejecutar contenedor (con variables de entorno locales)
docker run -e DATABASE_URL="postgres://localhost:5432/chatbot" \
           -e SUPABASE_URL="https://xxx.supabase.co" \
           -e SUPABASE_KEY="eyJ..." \
           -e OPENAI_API_KEY="sk-..." \
           -p 8000:8000 \
           chatbot-evolution:latest

# Verificar health check
curl http://localhost:8000/api/v1/health
# Debe devolver: {"status": "ok"}
```

### 3.3 Probar API Localmente (sin Docker)
```bash
# Terminal 1: Iniciar API
DEBUG=false python -m src.main --mode api

# Terminal 2: Test endpoint
curl http://localhost:8000/api/v1/health

# Test chat endpoint (si existe)
curl -X POST http://localhost:8000/api/v1/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "hello"}'
```

### 3.4 Verificar Despliegue en Render
```bash
# Una vez desplegado, probar desde la URL de Render
RENDER_URL="https://chatbot-evolution.onrender.com"

curl $RENDER_URL/api/v1/health
# Resultado: {"status": "ok", ...}

# Probar un endpoint
curl -X POST $RENDER_URL/api/v1/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "test"}'
```

### 3.5 Monitoreo Posterior al Despliegue
1. En Render → **Logs** → verificar errors y warnings
2. En Supabase → **Database > Logs** → revisar queries lentas
3. Configurar alertas (opcional) en Render para CPU/Memory

---

## Checklist Final Antes de Producción

- [ ] Tests locales pasan (41+ tests ✓)
- [ ] `.env.production` con credenciales de Supabase guardado de forma segura
- [ ] Supabase bgvector habilitado
- [ ] Tablas creadas en Supabase (si necesarias)
- [ ] GitHub Actions (`.github/workflows/ci.yml`) configurado
- [ ] Render servicio creado y variables de entorno agregadas
- [ ] Health check accesible desde Render
- [ ] Pruebas de CI/CD: push a main triggea build automático
- [ ] Logs de Render sin errores críticos
- [ ] Base de datos Supabase respondiendo correctamente

---

## Resumen de Archivos Creados

1. **DEPLOY_SUPABASE_RENDER.md** → Guía detallada Supabase + Render
2. **DEPLOY_SUPABASE_ONLY.md** → Por qué no usar "solo Supabase"
3. **.github/workflows/ci.yml** → GitHub Actions: tests + build + push
4. **render.yaml** → Configuración ejemplo para Render (opcional)
5. **fly.toml** → Configuración ejemplo para Fly.io (alternativa)
6. **.env** → Variables por defecto para dev local

---

## Próximos Pasos Opcionales

1. **Monitoring**: Agregar tracing con Datadog/NewRelic
2. **Auto-scaling**: En Render configurar min/max instances
3. **Load testing**: Usar `locust` o `k6` para verificar capacidad
4. **Custom domain**: Apuntar `chatbot.tudominio.com` a Render
5. **Backup automático**: Configurar snapshots de Supabase diarios

---

¡Listo para producción! 🚀
