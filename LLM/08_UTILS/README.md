# Chatbot Evolution 🤖

Evolución profesional del chatbot ELIZA con arquitectura modular, NLP avanzado, persistencia y microservicios.

> **¡COMIENZA AQUÍ!** 👇
> 
> 🎓 **[START_HERE.py](START_HERE.py)** - Guía interactiva de inicio (RECOMENDADO)
> 🗂️ **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** - Índice maestro de documentación
> 🏗️ **[ARCHITECTURE_DIAGRAM.py](ARCHITECTURE_DIAGRAM.py)** - Visualiza la arquitectura ASCII
> 📊 **[PROJECT_STATUS_SUMMARY.py](PROJECT_STATUS_SUMMARY.py)** - Resumen completo del proyecto

---

## 🎯 Características

### Core
- ✅ **Modular**: Separación clara de responsabilidades
- ✅ **Tests**: Cobertura unitaria e integración (50+ tests)
- ✅ **NLP Motor**: Pattern matching avanzado + embeddings + tokenización

### Data & Persistence
- ✅ **Memoria**: Persistencia en SQLite/PostgreSQL
- ✅ **Embeddings**: Búsqueda semántica con Sentence Transformers
- ✅ **Conversación**: Historial persistente de interacciones

### Intelligence
- ✅ **40+ Patrones**: Saludos, emociones, preferencias, relaciones (x13 categorías)
- ✅ **Respuestas Empáticas**: Preguntas de seguimiento inteligentes
- ✅ **LLM Fallback**: Integración con OpenAI o Ollama local

### Web & Deploy
- ✅ **API REST**: FastAPI con Swagger docs auto-generados
- ✅ **Microservicios**: Docker + docker-compose listo para producción
- ✅ **CORS**: Soporte para múltiples orígenes

## 🚀 Quick Start

### Instalación

```bash
# Clone & setup
git clone <repo>
cd chatbot_evolution
python -m venv venv
source venv/bin/activate  # o `venv\Scripts\activate` en Windows
pip install -e .
```

### Ejecutar CLI

```bash
python -m src.main --mode cli

# Ejemplos de entrada:
# > hello
# > i like programming
# > alice loves python
# > help me
# > who are you
```

### Probar Patrones Mejorados

```bash
# Menú interactivo con ejemplos por categoría
python test_patterns.py

# Ver comparativa antes vs después
python test_patterns.py --compare

# Debug detallado del flujo
python debug_flow.py
```

### Ejecutar API

```bash
python -m src.main --mode api
# Swagger: http://localhost:8000/docs
```

### Con Docker

```bash
docker-compose up --build
```

## 📊 Estructura

```
src/
├── core/          # Config, logging, utils
├── nlp/           # Pattern matching, tokenización
├── brain/         # Actor, knowledge base
├── storage/       # SQLAlchemy ORM
├── embeddings/    # Sentence Transformers
├── llm/           # OpenAI/Ollama fallback
└── api/           # FastAPI routes
```

## 🧪 Tests

```bash
pytest tests/ -v --cov=src
```

## 📝 Roadmap Implementado

- [x] Modularizar código original
- [x] Tests unitarios
- [x] Motor NLP separado
- [x] Base de datos persistente
- [x] Embeddings semánticos
- [x] LLM fallback
- [x] API REST
- [ ] K8s deployment (next)

## 🔧 Configuración

Crear `.env`:

```env
DATABASE_URL=sqlite:///./chatbot.db
OPENAI_API_KEY=sk-...
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
USE_LLM_FALLBACK=true
LOG_LEVEL=INFO
```

## � Documentación

### Guías Principales
- [GETTING_STARTED.md](GETTING_STARTED.md) - Guía rápida de inicio
- [ARCHITECTURE.md](ARCHITECTURE.md) - Arquitectura técnica detallada
- **[IMPROVED_RULES.md](IMPROVED_RULES.md)** - ✨ Sistema de 40+ patrones mejorado
- [EVOLUTION_SUMMARY.md](EVOLUTION_SUMMARY.md) - Resumen del proceso de evolución

### Referencias Técnicas
- [STATUS.txt](STATUS.txt) - Métricas y estado del proyecto
- [PROJECT_MAP.txt](PROJECT_MAP.txt) - Mapa visual del proyecto
- [MANIFEST.md](MANIFEST.md) - Índice completo de archivos

### Ejemplos & Testing
- [example_usage.py](example_usage.py) - Ejemplos de uso
- [test_patterns.py](test_patterns.py) - ✨ Prueba interactiva de patrones
- [debug_flow.py](debug_flow.py) - Debug detallado del flujo

---

**Autor**: Manufacturing AI Team  
**Licencia**: MIT
