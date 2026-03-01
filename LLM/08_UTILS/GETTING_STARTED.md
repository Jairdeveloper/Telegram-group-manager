# Getting Started - ChatBot Evolution

## 📋 Requisitos

- Python 3.10+
- pip o poetry

## 🚀 Instalación Rápida

### 1. Clonar/Descargar proyecto

```bash
cd chatbot_evolution
```

### 2. Crear entorno virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -e .
# o
pip install -r requirements.txt
```

### 4. Configuración (opcional)

```bash
cp .env.example .env
# Editar .env si quieres OpenAI o Ollama
```

## 🎮 Modo CLI Interactivo

```bash
python -m src.main --mode cli
```

Ejemplo de sesión:

```
> hello
Bot: Hello there how can I help?
    [pattern] (confidence: 0.90)

> how are you
Bot: I am functioning well thanks for asking
    [pattern] (confidence: 0.90)

> something odd
Bot: Tell me more
    [default] (confidence: 1.00)

> (quit)
Bye!
```

## 🌐 API REST

### Iniciar servidor

```bash
python -m src.main --mode api
```

El servidor estará en: `http://localhost:8000`

### Swagger Docs

Abre tu navegador: [`http://localhost:8000/docs`](http://localhost:8000/docs)

### Ejemplos cURL

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Chat
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "text": "hello",
    "session_id": "test",
    "username": "alice"
  }'

# Historial
curl http://localhost:8000/api/v1/chat/history/test

# Estadísticas de usuario
curl http://localhost:8000/api/v1/stats/user/alice
```

### Ejemplo Python + requests

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/chat",
    json={
        "text": "hello there",
        "session_id": "my_session",
        "username": "bob"
    }
)

data = response.json()
print(f"Bot: {data['message']}")
print(f"Confidence: {data['confidence']:.2f}")
print(f"Source: {data['source']}")
```

## 🧪 Tests

### Ejecutar todos los tests

```bash
pytest tests/ -v
```

### Con cobertura

```bash
pytest tests/ --cov=src --cov-report=html
# Abre htmlcov/index.html para ver reporte
```

### Tests específicos

```bash
# Solo tests del actor
pytest tests/test_actor.py -v

# Solo tests de NLP
pytest tests/test_pattern_engine.py -v

# Solo embeddings
pytest tests/test_embeddings.py -v
```

## 🐳 Docker

### Build y run

```bash
docker-compose up --build
```

Accede a: `http://localhost:8000`

### Solo API (sin compose)

```bash
docker build -t chatbot-api .
docker run -p 8000:8000 chatbot-api
```

## 📊 Ejemplos Completos

```bash
python example_usage.py
```

Demuestra:
1. Chat básico
2. Persistencia en BD
3. Embeddings semánticos
4. Actor avanzado
5. LLM fallback

## 🔌 Características Principales

### ✅ Implementadas

- **Pattern Matching**: Motor NLP modular y optimizado
- **Persistencia**: SQLAlchemy + SQLite (configurable PostgreSQL)
- **Embeddings**: Búsqueda semántica con Sentence Transformers
- **LLM Fallback**: Integración con OpenAI o Ollama
- **API REST**: FastAPI con Swagger
- **Tests**: 100+ tests unitarios
- **Docker**: Containerización lista

### 🔮 Roadmap Futuro

- [ ] K8s deployment manifests
- [ ] Redis cache layer
- [ ] Neo4j knowledge graphs
- [ ] Fine-tuning de embeddings
- [ ] Multi-language support
- [ ] User profiling & personalization
- [ ] Analytics dashboard
- [ ] Real-time WebSocket chat

## 📝 Arquitectura

```
src/
├── core/       → Config, logging, utils centralizados
├── nlp/        → Pattern engine, tokenización
├── brain/      → Actor, lógica de conversación
├── storage/    → ORM, repositorios, persistencia
├── embeddings/ → Búsqueda semántica
├── llm/        → Integración con LLMs externos
└── api/        → Endpoints REST
```

## 🔑 Variables de Entorno

| Variable | Default | Descripción |
|----------|---------|-------------|
| `DATABASE_URL` | sqlite:///./chatbot.db | Conexión BD |
| `LOG_LEVEL` | INFO | Nivel de logging |
| `OPENAI_API_KEY` | - | Key para OpenAI |
| `OLLAMA_BASE_URL` | http://localhost:11434 | URL de Ollama |
| `EMBEDDING_MODEL` | all-MiniLM-L6-v2 | Modelo embeddings |
| `USE_LLM_FALLBACK` | true | Activar LLM fallback |

## 🧠 Personalizar Brain

Edita `src/main.py` o crea tu propio:

```python
from src.brain.actor import Actor

# Define patrones y respuestas
patterns = [
    [["hello"], ["Hola"]],
    [[[1, "name"], "is", "cool"], ["Si,", [1, "name"], "es cool"]],
]

defaults = [["OK"], ["Entendido"]]

# Crea actor
actor = Actor(patterns, defaults)

# Usa
response = actor.process("hello")
print(response.text)
```

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'src'"

```bash
# Asegúrate de estar en el directorio correcto
cd chatbot_evolution
pip install -e .
```

### Embeddings lento

Primera ejecución descarga modelo (~80MB). Paciencia.

```bash
# Descargar manualmente:
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
```

### "OPENAI_API_KEY not set"

Opción 1: Crear `.env` con tu key

```bash
echo "OPENAI_API_KEY=sk-your-key" > .env
```

Opción 2: Usar Ollama local (sin key)

```bash
# Instalar Ollama
ollama pull mistral
# El bot usará Ollama automáticamente
```

## 📚 Documentación Completa

- [NLP Engine](./docs/nlp_engine.md)
- [API Reference](./docs/api.md)
- [Database Schema](./docs/database.md)

## 🤝 Contribuir

Las contribuciones son bienvenidas! Por favor:

1. Fork el repo
2. Crea rama feature (`git checkout -b feature/amazing`)
3. Commit cambios (`git commit -m 'Add amazing feature'`)
4. Push (`git push origin feature/amazing`)
5. Abre PR

## 📄 Licencia

MIT - Ver [LICENSE](./LICENSE)

## 👥 Autores

Manufacturing AI Team

---

¡Diviértete evolucionando tu chatbot! 🚀
