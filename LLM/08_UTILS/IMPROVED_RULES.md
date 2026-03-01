# 🚀 Chatbot - Sistema de Reglas Mejoradas

## Resumen de Mejoras

Se han mejorado significativamente los patrones de preguntas y respuestas del chatbot de **7 patrones básicos** a **40+ patrones organizados por categorías** temáticas.

---

## 📊 Comparativa Antes vs Después

### ANTES (7 patrones)
```
✅ hello → Hello there!
✅ hi → Hi there!
✅ my name is [name] → Pleased to meet you [name]
✅ how are you → I am fine thanks
✅ [subject] loves [object] → Interesting, why does...
✅ i need [object] → Why do you need...
✅ [question]? → What do you mean [question]?
```

**Limitaciones:**
- Pocas variaciones de saludos
- No maneja emociones
- No responde sobre preferencias
- Respuestas genéricas e impersonales
- Sin preguntas de seguimiento inteligentes

---

### DESPUÉS (40+ patrones)

#### 1️⃣ **SALUDOS** (6 patrones)
Cubre diferentes momentos del día:
```python
# Saludos básicos
hello → Hello! It's nice to meet you
hi → Hi there! How can I help?
hey → Hey! What's on your mind?

# Saludos por hora del día
good morning → Good morning! Ready to chat?
good afternoon → Good afternoon! How are you?
good evening → Good evening! Nice to see you
```

#### 2️⃣ **DESPEDIDAS** (4 patrones)
Respuestas amables al terminar:
```python
goodbye → Goodbye! It was great talking to you
bye → See you later! Take care
see you later → Catch you soon!
see you tomorrow → Looking forward to it!
```

#### 3️⃣ **PRESENTACIÓN** (2 patrones)
Introduce usuarios:
```python
my name is [name] → Pleased to meet you, [name]! That's a great name
i am [name] → Nice to meet you, [name]!
```

#### 4️⃣ **ESTADO DE ÁNIMO** (4 patrones)
Responde sobre cómo se siente:
```python
how are you → I'm doing great, thanks for asking!
how are you doing → Doing well! What about you?
how do you feel → I'm feeling good, thanks
what's up → Not much, just here to help
```

#### 5️⃣ **EMOCIONES DEL USUARIO** (3 patrones)
Muestra empatía:
```python
i am [feeling] → I'm sorry to hear you're [feeling]. How can I help?
i feel [emotion] → That's important. Would you like to talk about it?
i am happy → That's wonderful! What's making you happy?
```

#### 6️⃣ **PREFERENCIAS** (3 patrones)
Entiende gustos y aversiones:
```python
i like [thing] → [thing] is great! Why do you enjoy [thing]?
i prefer [option1] over [option2] → I see. You're more into [option1]
i hate [thing] → I see. It sounds like [thing] isn't for you
```

#### 7️⃣ **RELACIONES Y SENTIMIENTOS** (3 patrones)
Explora conexiones personales:
```python
[subject] loves [object] → That's beautiful! What makes [subject] love [object]?
[person] is my friend → That's lovely! How did you meet [person]?
[person] is my family → Family is important. Tell me more about [person]
```

#### 8️⃣ **NECESIDADES Y PROBLEMAS** (5 patrones)
Ayuda a resolver dificultades:
```python
i need [object] → Why do you need [object]? How can I help?
i want [object] → What would [object] give you?
i have a problem → I'm sorry you're having trouble. What's the problem?
help me → Of course! I'm here to help. Tell me what you need
```

#### 9️⃣ **PREGUNTAS SOBRE TEMAS** (3 patrones)
Responde preguntas abiertas:
```python
what is [topic]? → That's an interesting question about [topic]!
why [thing]? → That's worth exploring. Tell me more about why
how do [action]? → That's a practical question. Let me think about [action]
```

#### 🔟 **AGRADECIMIENTO** (3 patrones)
Responde positivamente:
```python
thanks → You're welcome! Happy to help
thank you → My pleasure! Always glad to assist
appreciate it → Of course! That's what I'm here for
```

#### 1️⃣1️⃣ **CONFIRMACIÓN / NEGACIÓN** (3 patrones)
Acepta respuestas sí/no:
```python
yes → Great! I'm glad we agree
no → I understand. Tell me your perspective
maybe → That's fair. Let's explore more
```

#### 1️⃣2️⃣ **INFORMACIÓN SOBRE EL BOT** (3 patrones)
Explica su propia naturaleza:
```python
who are you → I'm an AI chatbot created to have meaningful conversations
what can you do → I can have conversations, answer questions, help with ideas
how do you work → I use natural language processing to understand and respond
```

#### 1️⃣3️⃣ **PREGUNTAS EXISTENCIALES** (1 patrón)
Catch-all para preguntas complejas:
```python
[question]? → That's an interesting question. What made you ask that?
```

---

## 🎯 Respuestas Default Mejoradas

**ANTES (5 respuestas genéricas):**
```python
Is that right?
Interesting
Tell me more
I don't understand
Can you explain more?
```

**DESPUÉS (8 respuestas más naturales):**
```python
That's interesting, tell me more
I see. Could you elaborate?
That's a great point
I understand. What else?
In other words, you're saying...?
Can you give me an example?
That makes sense
I appreciate your thoughts
```

---

## 🔧 Cómo Funciona el Sistema de Patrones

### Sintaxis de Patrones

```python
pattern_responses = [
    [patrón, plantilla_respuesta],
    ...
]
```

### Tipos de Elementos

| Tipo | Sintaxis | Ejemplo | Explicación |
|------|----------|---------|-------------|
| **Palabra literal** | `"word"` | `"hello"` | Debe coincidir exactamente (sin importar mayúsculas) |
| **Wildcard** | `0` | `["hello", 0]` | Coincide con cualquier palabra (se ignora) |
| **Variable capturada** | `[num, "name"]` | `[1, "subject"]` | Captura 1+ palabras con ese nombre |
| **Lista anidada** | `[[...]]` | `[[1, "subject"], "loves", [0, "object"]]` | Patrón complejo con múltiples variables |

### Ejemplos de Funcionamiento

#### Ejemplo 1: Palabra Literal
```
Patrón:   ["hello", 0]
Entrada:  "hello world"
Tokens:   ["hello", "world"]
Resultado: ✅ MATCH - ignora "world" por el wildcard 0
Respuesta: "Hello! It's nice to meet you"
```

#### Ejemplo 2: Captura de Variable
```
Patrón:   ["i", "like", [1, "thing"], 0]
Entrada:  "i like pizza"
Resultado: ✅ MATCH - captura "pizza" como "thing"
Bindings: [[["pizza"], "thing"]]
Respuesta: "pizza is great! Why do you enjoy pizza?"
```

#### Ejemplo 3: Relaciones Complejas
```
Patrón:   [[1, "subject"], "loves", [0, "object"]]
Entrada:  "alice loves python"
Tokens:   ["alice", "loves", "python"]
Variables: subject="alice", object="python"
Respuesta: "That's beautiful! What makes alice love python?"
```

---

## 📝 Cómo Añadir Nuevos Patrones

### Paso 1: Identificar el Patrón
¿Qué entrada del usuario quieres reconocer?
```
Ejemplo: "i really enjoy X activity"
```

### Paso 2: Escribir el Patrón
```python
["i", "really", "enjoy", [1, "activity"], 0]
# 0 = wildcard para palabras finales opcionales
# [1, "activity"] = captura 1+ palabras como "activity"
```

### Paso 3: Escribir la Respuesta
```python
["That's", "awesome!", "What's", "the", "best", "part", "about", [1, "activity"], "?"]
# [1, "activity"] será reemplazado con lo capturado
```

### Paso 4: Añadir a `pattern_responses`
```python
pattern_responses = [
    # ... patrones existentes ...
    [
        ["i", "really", "enjoy", [1, "activity"], 0],
        ["That's", "awesome!", "What's", "the", "best", "part", "about", [1, "activity"], "?"]
    ],
]
```

---

## 🧠 Estrategia de Mejora Continua

### Fase 1: Sistema Base ✅ (COMPLETADO)
- 40+ patrones organizados por categoría
- Respuestas default de calidad
- Soporte para emociones y preferencias
- Preguntas de seguimiento inteligentes

### Fase 2: Personalización (PRÓXIMO)
```python
# Guardar patrones en base de datos
# Permitir que usuarios añadan patrones propios
# Ranking de patrones más usados
```

### Fase 3: Machine Learning (FUTURO)
```python
# Detectar patrones sin reglas explícitas
# Usar embeddings para similaridad semántica
# Aprender de interacciones exitosas
```

### Fase 4: Contexto (FUTURO)
```python
# Recordar conversaciones previas
# Adaptar respuestas según perfil del usuario
# Mantener coherencia multi-turno
```

---

## 🚀 Cómo Probar los Nuevos Patrones

### Opción 1: CLI Interactivo
```bash
python -m src.main --mode cli
```

Prueba estos inputs:
```
> hello
> i like programming
> alice loves python
> help me
> who are you
> goodbye
```

### Opción 2: Debug Script
```bash
python debug_flow.py
```

Introduce: `alice loves python`

### Opción 3: API REST
```bash
python -m src.main --mode api
# Accede a http://localhost:8000/docs
# POST /api/v1/chat con {"message": "hello"}
```

---

## 📈 Métricas de Mejora

| Métrica | Antes | Después | Mejora |
|---------|-------|---------|--------|
| Total Patrones | 7 | 40+ | **475% ↑** |
| Categorías | 1 | 13 | **1200% ↑** |
| Respuestas Default | 5 | 8 | **60% ↑** |
| Tipos de Interacción | 2 | 13 | **550% ↑** |
| Variaciones de Saludos | 2 | 6 | **200% ↑** |

---

## 💡 Ideas para Futuras Mejoras

- [ ] Patrones para bromas/humor
- [ ] Reconocimiento de sarcasmo
- [ ] Manejo de preguntas sin respuesta
- [ ] Sugerencias proactivas
- [ ] Personalización por usuario
- [ ] Integración con APIs externas
- [ ] Análisis de sentimientos avanzado
- [ ] Generación de respuestas con LLM
- [ ] Aprendizaje por refuerzo
- [ ] Soporte multi-idioma

---

## 📚 Referencias

- **PatternEngine**: [src/nlp/pattern_engine.py](src/nlp/pattern_engine.py)
- **Actor**: [src/brain/actor.py](src/brain/actor.py)
- **Tokeni

zador**: [src/nlp/pattern_engine.py#Tokenizer](src/nlp/pattern_engine.py)
- **Test Patterns**: [tests/test_pattern_engine.py](tests/test_pattern_engine.py)

---

**Última actualización:** 23 Feb 2026  
**Versión:** 2.0 - Sistema de Reglas Mejoradas
