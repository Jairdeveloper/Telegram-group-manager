# 🤖 Chatbot Monolith - README

## Descripción

**`chatbot_monolith.py`** es un archivo Python único y completamente autónomo que contiene TODO el código del chatbot.

Este archivo fue creado al fusionar los 7 módulos modulares en un solo archivo:
- ✅ Configuración (config.py)
- ✅ Logging (logger.py)
- ✅ NLP: Pattern Matching, Tokenización (pattern_engine.py, pronoun_translator.py)
- ✅ Orquestación (actor.py)
- ✅ Persistencia simple basada en JSON (reemplaza SQLAlchemy)
- ✅ Búsqueda semántica (embedder.py - opcional con Sentence Transformers)
- ✅ LLM Fallback (openai + ollama)
- ✅ CLI interactiva
- ✅ API REST con FastAPI (opcional)

**Tamaño:** ~1,200 líneas de código Python en UN solo archivo

---

## 📦 Requisitos

### Mínimos (CLI básico - sin dependencias externas)
```bash
python 3.10+
```

### Recomendados (Búsqueda semántica)
```bash
pip install sentence-transformers
```

### Opcionales (LLM Fallback)
```bash
pip install openai requests
```

### Todos (API REST + todo)
```bash
pip install fastapi uvicorn sentence-transformers openai requests
```

---

## 🚀 Uso Rápido

### Modo CLI (Interactivo)

```bash
python chatbot_monolith.py --mode cli
```

O simplemente:
```bash
python chatbot_monolith.py
```

Salida esperada:
```
======================================================================
ChatBot Evolution - Monolithic Mode (CLI)
======================================================================
Type 'quit' o '(quit)' to exit

> hello
Bot: Hello! It's nice to meet you
    [pattern] (confidence: 0.90)

> i like python
Bot: python is great! Why do you enjoy python?
    [pattern] (confidence: 0.90)

> quit
Bye!
```

### Modo API REST

```bash
python chatbot_monolith.py --mode api
```

Salida:
```
✅ API running at http://127.0.0.1:8000
📖 Swagger docs: http://127.0.0.1:8000/docs
```

Luego puedes acceder a:
- **API:** http://localhost:8000
- **Swagger docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

**Ejemplo de uso con curl:**
```bash
curl -X POST "http://localhost:8000/api/v1/chat?message=hello&session_id=user1"
```

Respuesta:
```json
{
  "session_id": "user1",
  "message": "hello",
  "response": "Hello! It's nice to meet you",
  "confidence": 0.9,
  "source": "pattern",
  "pattern_matched": true
}
```

---

## 📚 Endpoints de la API

### 1. Chat (POST)
```
POST /api/v1/chat?message=hello&session_id=user1
```

**Parámetros:**
- `message` (string, ejemplo): "hello"
- `session_id` (string, opcional): ID de sesión. Si no se proporciona, se genera uno.

**Respuesta:**
```json
{
  "session_id": "abc123",
  "message": "i like python",
  "response": "python is great! Why do you enjoy python?",
  "confidence": 0.9,
  "source": "pattern",
  "pattern_matched": true
}
```

### 2. Historial (GET)
```
GET /api/v1/history/abc123
```

**Respuesta:**
```json
{
  "session_id": "abc123",
  "history": [
    {
      "timestamp": "2026-02-24T10:30:45.123456",
      "user": "hello",
      "bot": "Hello! It's nice to meet you"
    },
    {
      "timestamp": "2026-02-24T10:31:10.654321",
      "user": "i like python",
      "bot": "python is great! Why do you enjoy python?"
    }
  ]
}
```

### 3. Estadísticas (GET)
```
GET /api/v1/stats
```

**Respuesta:**
```json
{
  "app_name": "ChatBot Evolution",
  "version": "2.1",
  "total_sessions": 5,
  "total_messages": 23
}
```

### 4. Health Check (GET)
```
GET /health
```

**Respuesta:**
```json
{
  "status": "ok",
  "version": "2.1"
}
```

---

## 🎯 Patrones NLP Incluidos (40+)

El chatbot reconoce 40+ patrones organizados en 13 categorías:

### 1. SALUDOS (6)
- `hello` → "Hello! It's nice to meet you"
- `hi` → "Hi there! How can I help?"
- `hey` → "Hey! What's on your mind?"
- `good morning` → "Good morning! Ready to chat?"
- `good afternoon` → "Good afternoon! How are you?"
- `good evening` → "Good evening! Nice to see you"

### 2. DESPEDIDAS (4)
- `goodbye` → "Goodbye! It was great talking to you"
- `bye` → "See you later! Take care"
- `see you later` → "Catch you soon!"
- `see you tomorrow` → "Looking forward to it!"

### 3. PRESENTACIÓN (2)
- `my name is [name]` → "Pleased to meet you, [name]!"
- `i am [name]` → "Nice to meet you, [name]!"

### 4. CÓMO ESTÁS (4)
- `how are you` → "I'm doing great, thanks for asking!"
- `how are you doing` → "Doing well! What about you?"
- `how do you feel` → "I'm feeling good, thanks"
- `what's up` → "Not much, just here to help"

### 5. EMOCIONES (3)
- `i am [feeling]` → "I'm sorry to hear you're [feeling]"
- `i feel [emotion]` → "That's important. Would you like to talk about it?"
- `i am happy` → "That's wonderful! What's making you happy?"

### 6. PREFERENCIAS (3)
- `i like [thing]` → "[thing] is great! Why do you enjoy [thing]?"
- `i prefer [A] over [B]` → "I see. So you're more into [A] than [B]"
- `i hate [thing]` → "I see. It sounds like [thing] isn't for you"

### 7. RELACIONES (3)
- `[subject] loves [object]` → "That's beautiful!"
- `[person] is my friend` → "That's lovely!"
- `[person] is my family` → "Family is important. Tell me more about [person]"

### 8. NECESIDADES (5)
- `i need [object]` → "Why do you need [object]?"
- `i want [object]` → "That's a good desire"
- `i have a problem` → "I'm sorry you're having trouble. What's the problem?"
- `help me` → "Of course! I'm here to help"

### 9. PREGUNTAS (3)
- `what is [topic]` → "That's an interesting question about [topic]"
- `why [question]` → "That's worth exploring"
- `how do [action]` → "That's a practical question"

### 10. AGRADECIMIENTO (3)
- `thanks` → "You're welcome! Happy to help"
- `thank you` → "My pleasure!"
- `appreciate it` → "Of course! That's what I'm here for"

### 11. CONFIRMACIÓN (3)
- `yes` → "Great! I'm glad we agree"
- `no` → "I understand. Tell me your perspective"
- `maybe` → "That's fair. Let's explore more"

### 12. INFO DEL BOT (3)
- `who are you` → "I'm an AI chatbot..."
- `what can you do` → "I can have conversations..."
- `how do you work` → "I use natural language processing..."

### 13. MISC (3)
- Preguntas terminadas en `?`
- Respuestas default variadas

---

## ⚙️ Configuración

Puedes configurar el chatbot a través de **variables de entorno** o modificando la clase `Settings` al inicio del archivo:

```python
# Variables de entorno
export DEBUG=False
export LOG_LEVEL=INFO
export API_HOST=127.0.0.1
export API_PORT=8000
export OPENAI_API_KEY=sk-...
export OLLAMA_BASE_URL=http://localhost:11434

# Luego ejecuta
python chatbot_monolith.py --mode api
```

**Configuración disponible:**
- `DEBUG` - Modo debug (default: False)
- `LOG_LEVEL` - Nivel de logging (default: INFO)
- `API_HOST` - Host de API (default: 127.0.0.1)
- `API_PORT` - Puerto de API (default: 8000)
- `OPENAI_API_KEY` - API key de OpenAI (opcional)
- `OLLAMA_BASE_URL` - URL de Ollama local (default: http://localhost:11434)
- `DATABASE_URL` - URL de base de datos (no usada en versión monolítica)

---

## 📁 Almacenamiento de Conversaciones

Por defecto, el chatbot guarda las conversaciones en un archivo **`conversations.json`**:

```json
{
  "abc123": [
    {
      "timestamp": "2026-02-24T10:30:45.123456",
      "user": "hello",
      "bot": "Hello! It's nice to meet you"
    },
    {
      "timestamp": "2026-02-24T10:31:10.654321",
      "user": "how are you",
      "bot": "I'm doing great, thanks for asking!"
    }
  ]
}
```

El archivo se crea automáticamente en el directorio de trabajo.

---

## 🔧 Estructura del Código

### Secciones principales:

```
PARTE 1: Configuración y Logging
  - Clase Settings (configuración centralizada)
  - Función get_logger() (logging factory)

PARTE 2: NLP - Pattern Matching
  - Clase PatternEngine (compilación y matching de patrones)
  - Clase Tokenizer (tokenización de texto)
  - Clase PronounTranslator (traducción de pronombres)

PARTE 3: Respuesta Estructurada
  - Dataclass Response (estructura estándar de respuesta)

PARTE 4: Actor Orquestador
  - Clase Actor (procesa entrada → genera respuesta)

PARTE 5: Persistencia (Simple JSON)
  - Clase SimpleConversationStorage (almacenamiento JSON)

PARTE 6: Búsqueda Semántica (Opcional)
  - Clase EmbeddingService (con Sentence Transformers)

PARTE 7: LLM Fallback (Opcional)
  - Clase LLMProvider (interfaz abstracta)
  - Clase OpenAIProvider (GPT-3.5-turbo)
  - Clase OllamaProvider (modelos locales)
  - Clase LLMFallback (gestor de fallback)

PARTE 8: CLI - Modo Interactivo
  - Función get_default_brain() (carga patrones)
  - Función run_cli() (CLI interactiva)

PARTE 9: API REST (Opcional - FastAPI)
  - Función run_api() (servidor REST)
  - 4 endpoints: /health, /chat, /history, /stats

PARTE 10: Main Entry Point
  - Función main() (punto de entrada)
```

---

## 📊 Comparativa: Monolítica vs Modular

| Aspecto | Monolítica | Modular |
|---------|-----------|---------|
| **Archivos** | 1 archivo | 13 archivos |
| **Líneas** | ~1,200 | ~2,500 |
| **Facilidad de uso** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Mantenibilidad** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Modularidad** | ⭐ | ⭐⭐⭐⭐⭐ |
| **Testabilidad** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Reutilización** | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Dependencias** | Mínimas | Organizadas |

---

## 🎓 Ejemplos de Uso

### Ejemplo 1: CLI básico
```bash
python chatbot_monolith.py

> hello
Bot: Hello! It's nice to meet you

> my name is alice
Bot: Pleased to meet you, alice!

> i like programming
Bot: programming is great! Why do you enjoy programming?

> bye
Bot: See you later! Take care
Bye!
```

### Ejemplo 2: API con Python
```python
import requests

# Chat
response = requests.post(
    "http://localhost:8000/api/v1/chat",
    params={"message": "hello", "session_id": "user123"}
)
print(response.json())

# Historial
response = requests.get(
    "http://localhost:8000/api/v1/history/user123"
)
print(response.json())

# Estadísticas
response = requests.get(
    "http://localhost:8000/api/v1/stats"
)
print(response.json())
```

### Ejemplo 3: API con JavaScript/Fetch
```javascript
// Chat
fetch('http://localhost:8000/api/v1/chat?message=hello&session_id=user1')
  .then(r => r.json())
  .then(data => console.log(data.response));

// Historial
fetch('http://localhost:8000/api/v1/history/user1')
  .then(r => r.json())
  .then(data => console.log(data.history));
```

---

## 🐛 Solución de Problemas

### Problema: "ModuleNotFoundError: No module named 'fastapi'"
**Solución:** Instala las dependencias necesarias:
```bash
pip install fastapi uvicorn
```

### Problema: "openai package not installed"
**Solución:** Instala el cliente de OpenAI:
```bash
pip install openai
```

### Problema: API escucha en 0.0.0.0
**Solución:** Cambia el `API_HOST` a 127.0.0.1 en la clase `Settings` o usa variable de entorno.

### Problema: Las conversaciones no se guardan
**Verifica:**
- El archivo `conversations.json` existe en el directorio de trabajo
- Tienes permisos de escritura en el directorio

---

## 📝 Notas

1. **Persistencia:** Esta versión usa almacenamiento simple en JSON. Para producción, usa la versión modular con SQLAlchemy + PostgreSQL.

2. **LLM Fallback:** Es totalmente opcional. El chatbot funciona perfectamente con solo pattern matching.

3. **Embeddings:** Requiere Sentence Transformers. Si no está instalado, la búsqueda semántica se deshabilita automáticamente.

4. **API:** Es completamente opcional. Puedes usar solo CLI.

5. **Logging:** Todos los módulos log automáticamente. Cambia `LOG_LEVEL` para más/menos verbosidad.

---

## ✅ Cheklist de Verificación

- [ ] Python 3.10+ instalado
- [ ] `chatbot_monolith.py` descargado
- [ ] Ejecutar CLI: `python chatbot_monolith.py`
- [ ] Probar patrones básicos (hello, how are you, bye)
- [ ] Opcional - Ejecutar API: `python chatbot_monolith.py --mode api`
- [ ] Opcional - Instalar FastAPI: `pip install fastapi uvicorn`
- [ ] Opcional - Probar endpoints con Swagger en http://localhost:8000/docs

---

**¡Disfruta usando Chatbot Evolution! 🚀**

---

**Última actualización:** 24 de Febrero 2026
**Versión:** 2.1 (Monolithic)
**Estado:** ✅ Production Ready
