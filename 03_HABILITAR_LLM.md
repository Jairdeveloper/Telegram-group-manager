# Análisis: Bot activa welcome pero no setea mensaje

## Problema

El usuario envía: 
```
Quiero cambiar el mensaje de bienvenida personalizado utiliza tu creatividad y configura un nuevo mensaje de bienvenida
```

El bot responde "Welcome actualizado" pero cuando consulta `/welcome` el mensaje está vacío.

## Logs Analizados

```
2026-03-28 10:55:30,729 INFO ActionParser: text='...', result=welcome.toggle, conf=0.6
2026-03-28 10:55:30,730 INFO ActionParser: using roles=['admin']
2026-03-28 10:55:30,736 INFO ActionExecutor.execute: action_id=welcome.toggle, payload={'enabled': True}
2026-03-28 10:55:30,776 INFO ActionParser: action_result status=ok, message=Welcome actualizado

# Luego al consultar /welcome:
welcome_text='', enabled=True
```

## Causa del Problema

1. **Rule-based parser**: Retorna `welcome.toggle` (activar) porque detecta palabras de intención como "cambiar", "configurar" pero no hay texto explícito después de "bienvenida"

2. **Fallback a LLM**: El LLM (Ollama) retorna `welcome.toggle` en lugar de entender que el usuario quiere GENERAR un mensaje creativo

3. **El resultado**: Se ejecuta `welcome.toggle` que solo activa la funcionalidad pero no setea ningún texto

## Solución Implementada

### 1. Nueva acción: `welcome.set_creative_text`

Se agregó una nueva acción que genera automáticamente un mensaje de bienvenida creativo:

```python
CREATIVE_WELCOME_MESSAGES = [
    "¡Bienvenido/a! 🎉 Nos alegra tenerte aquí...",
    "¡Hola! 👋 Bienvenido/a a nuestro grupo...",
    "¡Bienvenido/a! 🚀 Este es un lugar...",
    # ... más opciones
]

async def _welcome_set_creative_text(ctx, params):
    # Selecciona un mensaje aleatorio de la lista
    creative_message = random.choice(CREATIVE_WELCOME_MESSAGES)
    # Guarda en repositorio
    welcome = EnterpriseWelcome(..., welcome_text=creative_message, enabled=True)
    ...
    return ActionResult(status="ok", message=f"✅ Mensaje de bienvenida configurado:\n\n{creative_message}")
```

### 2. Mejorado prompt del LLM

Se agregó guía para que el LLM retorne `welcome.set_creative_text` cuando el usuario quiere generar un mensaje:

```python
examples = """...
- "Quiero cambiar el mensaje de bienvenida" -> {"action_id": "welcome.set_creative_text", "payload": {}}
- "Cambia la bienvenida usa tu creatividad" -> {"action_id": "welcome.set_creative_text", "payload": {}}
- "Pon un mensaje de bienvenida creativo" -> {"action_id": "welcome.set_creative_text", "payload": {}}"""

prompt = """...
Si el usuario quiere cambiar/configurar la bienvenida pero NO especifica el texto, 
usa welcome.set_creative_text para generar un mensaje automáticamente."""
```

### 3. Mejorada detección de intención en rule-based

Cuando el usuario usa palabras como "creatividad", "crear", "generar", ahora retorna `welcome.toggle` (activar) en lugar de intentar extraer texto.

## Flujo Esperado

| Paso | Descripción |
|------|-------------|
| 1 | Usuario: "Quiero cambiar el mensaje de bienvenida..." |
| 2 | LLM parsea → `welcome.set_creative_text` |
| 3 | Sistema genera mensaje creativo |
| 4 | Sistema guarda y responde con el mensaje generado |

## Limitaciones Actuales

1. **LLM no funciona bien**: El LLM (Ollama) sigue retornando `welcome.toggle` - necesita más ejemplos o mejor modelo
2. **Lista de mensajes limitada**: Solo 5 mensajes predefinidos, podría mejorarse con generación dinámica

## Recomendaciones

1. **Mejorar prompt LLM**: Añadir más ejemplos de conversaciones donde el usuario pide "crear" o "generar"
2. **Usar LLM para generar**: En lugar de mensajes predefinidos, usar el LLM para generar un mensaje personalizado basado en el contexto del grupo
3. **Flujo conversacional**: Cuando hay ambigüedad, preguntar "¿Qué mensaje de bienvenida quieres?" en lugar de asumir
