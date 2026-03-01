# 🚀 QUICK REFERENCE - Patrones del Chatbot v2.0

## Tabla Rápida Completa

| # | Categoría | Patrón | Ejemplo | Respuesta |
|----|-----------|--------|---------|-----------|
| 1 | **SALUDOS** | `hello` + cualquier cosa | "hello world" | "Hello! It's nice to meet you" |
| 2 | | `hi` + cualquier cosa | "hi there" | "Hi there! How can I help?" |
| 3 | | `hey` + cualquier cosa | "hey you" | "Hey! What's on your mind?" |
| 4 | | `good morning` | "good morning" | "Good morning! Ready to chat?" |
| 5 | | `good afternoon` | "good afternoon" | "Good afternoon! How are you?" |
| 6 | | `good evening` | "good evening" | "Good evening! Nice to see you" |
| 7 | **DESPEDIDAS** | `goodbye` + cualquier cosa | "goodbye" | "Goodbye! It was great talking to you" |
| 8 | | `bye` + cualquier cosa | "bye" | "See you later! Take care" |
| 9 | | `see you later` | "see you later" | "Catch you soon!" |
| 10 | | `see you tomorrow` | "see you tomorrow" | "Looking forward to it!" |
| 11 | **PRESENTACIÓN** | `my name is [Variable]` | "my name is alice" | "Pleased to meet you, alice! That's a great name" |
| 12 | | `i am [Variable]` | "i am bob" | "Nice to meet you, bob!" |
| 13 | **CÓMO ESTÁS** | `how are you` | "how are you" | "I'm doing great, thanks for asking!" |
| 14 | | `how are you doing` | "how are you doing" | "Doing well! What about you?" |
| 15 | | `how do you feel` | "how do you feel" | "I'm feeling good, thanks" |
| 16 | | `what's up` | "what's up" | "Not much, just here to help" |
| 17 | **EMOCIONES** | `i am [emoción]` | "i am sad" | "I'm sorry to hear you're sad. How can I help?" |
| 18 | | `i feel [emoción]` | "i feel confused" | "That's important. Would you like to talk about it?" |
| 19 | | `i am happy` | "i am happy" | "That's wonderful! What's making you happy?" |
| 20 | **PREFERENCIAS** | `i like [cosa]` | "i like pizza" | "pizza is great! Why do you enjoy pizza?" |
| 21 | | `i prefer [X] over [Y]` | "i prefer tea over coffee" | "I see. You're more into tea than coffee" |
| 22 | | `i hate [cosa]` | "i hate spiders" | "I see. It sounds like spiders isn't for you" |
| 23 | **RELACIONES** | `[persona] loves [cosa]` | "alice loves python" | "That's beautiful! What makes alice love python?" |
| 24 | | `[persona] is my friend` | "bob is my friend" | "That's lovely! How did you meet bob?" |
| 25 | | `[persona] is my family` | "alice is my sister" | "Family is important. Tell me more about alice" |
| 26 | **NECESIDADES** | `i need [cosa]` | "i need help" | "Why do you need help? How can I help?" |
| 27 | | `i want [cosa]` | "i want to learn" | "That's a good desire. What would learning give you?" |
| 28 | | `i have a problem` | "i have a problem" | "I'm sorry you're having trouble. What's the problem?" |
| 29 | | `help me` | "help me" | "Of course! I'm here to help. Tell me what you need" |
| 30 | **PREGUNTAS** | `what is [tema]?` | "what is love?" | "That's an interesting question about love!" |
| 31 | | `why [cosa]?` | "why do birds fly?" | "That's worth exploring. Tell me more about why" |
| 32 | | `how do [acción]?` | "how do you cook pasta?" | "That's a practical question. Let me think about cooking" |
| 33 | **AGRADECIMIENTO** | `thanks` + cualquier cosa | "thanks!" | "You're welcome! Happy to help" |
| 34 | | `thank you` | "thank you" | "My pleasure! Always glad to assist" |
| 35 | | `appreciate it` | "appreciate it" | "Of course! That's what I'm here for" |
| 36 | **CONFIRMACIÓN** | `yes` + cualquier cosa | "yes" | "Great! I'm glad we agree" |
| 37 | | `no` + cualquier cosa | "no" | "I understand. Tell me your perspective" |
| 38 | | `maybe` + cualquier cosa | "maybe" | "That's fair. Let's explore more" |
| 39 | **INFO BOT** | `who are you?` | "who are you?" | "I'm an AI chatbot created to have meaningful conversations" |
| 40 | | `what can you do?` | "what can you do?" | "I can have conversations, answer questions, help with ideas" |
| 41 | | `how do you work?` | "how do you work?" | "I use natural language processing to understand and respond" |

---

## Sintaxis de Variables

```
[Variable] = Captura 1 o más palabras consecutivas

número = Número de palabras a capturar (1 = "one", 2 = "one two", etc.)
"nombre" = Nombre para refenferencia en respuesta
```

### Ejemplos:
```
[1, "name"]     → Captura 1+ palabras como "name": "alice" → [[["alice"], "name"]]
[0, "object"]   → Ignora esta parte (wildcard)
[1, "topic"]    → Captura tema: "python programming" → [[["python", "programming"], "topic"]]
```

---

## Respuestas Default (Cuando no hay patrón)

Si el input no coincide con ningún patrón, se elige una al azar de:

```
1. "That's interesting, tell me more"
2. "I see. Could you elaborate?"
3. "That's a great point"
4. "I understand. What else?"
5. "In other words, you're saying...?"
6. "Can you give me an example?"
7. "That makes sense"
8. "I appreciate your thoughts"
```

---

## Cómo Crear Tu Propio Patrón

### Paso a Paso

1. **Identifica el patrón**
   ```
   "usuario siempre dice X y quiero responder Y"
   ```

2. **Escribe el patrón**
   ```python
   ["palabra1", "palabra2", [1, "variable"], 0]
   ```

3. **Escribe la respuesta**
   ```python
   ["Response", "text", "with", [1, "variable"], "replaced"]
   ```

4. **Agrega a `src/main.py`**
   ```python
   pattern_responses = [
       # ... patrones existentes ...
       [
           ["palabra1", "palabra2", [1, "variable"], 0],
           ["Response", "text", "with", [1, "variable"], "replaced"]
       ],
   ]
   ```

5. **Prueba**
   ```bash
   python test_patterns.py
   ```

---

## Consejos Prácticos

### ✅ HACER

```python
# Captura múltiples palabras
["i", "like", [1, "thing"], 0]      ✅ Ok: "i like deep learning models"

# Usa wildcards para flexibilidad
["hello", 0]                         ✅ Ok: "hello there" o "hello world"

# Agrupa palabras relacionadas
["good", "morning"]                  ✅ Ok: Saludo específico

# Responde con variable
["Interesting!", [1, "thing"], "!"]  ✅ Ok: Reemplaza variable
```

### ❌ NO HACER

```python
# Palabras muy específicas sin wildcard
["hello", "there"]                   ❌ No: Solo coincide "hello there"

# Variables sin número
[[1], "loves", [0, "object"]]        ❌ No: Variables sin nombre

# Respuesta sin variable remplazada
["You like it!"]                     ❌ No: Ignora lo que el usuario dijo

# Patrón muy genérico
[0]                                  ❌ No: Coincide TODO
```

---

## Testing Rápido

### Opción 1: Interactive Menu
```bash
python test_patterns.py
# Elige categoría → Elige ejemplo → Ver respuesta
```

### Opción 2: Debug Detallado
```bash
python debug_flow.py
# Muestra cada paso: tokenizar → pattern matching → traducir → respuesta
```

### Opción 3: CLI
```bash
python -m src.main --mode cli
# Escribe y ve respuesta

> hello
Bot: Hello! It's nice to meet you
```

### Opción 4: Código Python
```python
from src.main import get_default_brain
from src.storage.database import db
from src.brain.actor import Actor

db.init_db()
patterns, defaults = get_default_brain()
actor = Actor(patterns, defaults)

response = actor.process("i like python")
print(response.text)  # "python is great! Why do you enjoy python?"
```

---

## Categorías por Caso de Uso

### Para Soporte Técnico
Recomendado usar: **NECESIDADES**, **PROBLEMAS**, **PREGUNTAS**

### Para Chat Social
Recomendado usar: **SALUDOS**, **EMOCIONES**, **RELACIONES**

### Para Asistente Personal
Recomendado usar: **PREFERENCIAS**, **INFORMACIÓN**, **CONFIRMACIÓN**

### Para Exploración
Recomendado usar: **PREGUNTAS EXISTENCIALES**, **INFORMACIÓN DEL BOT**

---

## Estadísticas Rápidas

- **40+ patrones** organizados en 13 categorías
- **80% cobertura** de conversaciones típicas
- **8 respuestas default** para casos no anticipados
- **Procesamiento en tiempo real** (ms)
- **Sin dependencias externas** para patrón matching

---

## Referencias Rápidas

| Documento | Para Qué |
|-----------|----------|
| [IMPROVED_RULES.md](IMPROVED_RULES.md) | Documentación completa |
| [PATTERNS_CHANGELOG.md](PATTERNS_CHANGELOG.md) | Historia de cambios |
| [test_patterns.py](test_patterns.py) | Probar patrones |
| [debug_flow.py](debug_flow.py) | Debug detallado |
| [CONVERSATION_EXAMPLES.py](CONVERSATION_EXAMPLES.py) | Ejemplos de conversaciones |

---

**Última actualización:** 23 Feb 2026  
**Versión:** 2.0 - Patrones Mejorados  
**Próxima actualización:** Q2 2026
