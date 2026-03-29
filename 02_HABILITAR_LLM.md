# Análisis: Bot no entiende intención del usuario (Rule-Based vs LLM)

## Problema Reportado

El usuario envía: 
```
Quiero cambiar el mensaje de bienvenida personalizado utiliza tu creatividad y configura un nuevo mensaje de bienvenida
```

El bot extrae incorrectamente como mensaje de bienvenida:
```
"personalizado utiliza tu creatividad y configura un nuevo mensaje de bienvenida"
```

El bot está usando un sistema de **inferencia rule-based** (basado en reglas) que simplemente extrae texto después de "bienvenida", en lugar de entender la **intención** del usuario.

## Análisis del Problema

### Causa 1: Parser prioriza rule-based sobre LLM

El código original en `parser.py`:

```python
def parse(self, message: str) -> ActionParseResult:
    # 1. Siempre intenta rule-based primero
    rule_based = self._rule_based(message)
    if rule_based:
        return rule_based  # <-- Retorna inmediatamente

    # 2. Solo si rule-based falla, intenta LLM
    if self.llm_enabled:
        llm_result = self._llm_parse(message)
        ...
```

El parser siempre ejecutaba rule-based primero, sin dar oportunidad al LLM de entender la intención.

### Causa 2: Regex demasiado greedy

El patrón rule-based en línea 167-175 capturaba TODO texto después de "bienvenida" cuando la mensagem contenía palabras como "mensaje" o "texto":

```python
# PATRÓN PROBLEMÁTICO (ya eliminado)
if any(word in lowered for word in ("mensaje", "texto", "set", ...)):
    match = re.search(r"(?:welcome|bienvenida)[:\s]+(.+)", ...)
    # Capturaba todo lo que seguía como "texto de bienvenida"
```

### Causa 3: LLM no disponible

El LLM está fallando con errores de rate limit (429 Too Many Requests):
```
httpx.HTTPStatusError: Client error '429 Too Many Requests'
```

## Solución Implementada

### 1. Cambiar prioridad: LLM primero, luego rule-based

```python
def parse(self, message: str) -> ActionParseResult:
    # PRIORIDAD: LLM primero cuando está habilitado
    if self.llm_enabled:
        llm_result = self._llm_parse(message)
        if llm_result:
            return llm_result

    # Fallback a rule-based
    rule_based = self._rule_based(message)
    if rule_based:
        return rule_based
```

### 2. Agregar detección de intención en rule-based

Cuando el mensaje contiene palabras como "cambiar", "configurar", "establecer", "nuevo", etc., el parser ahora detecta que el usuario quiere **SETEAR** un mensaje (intención) en lugar de proporcionar el texto directamente:

```python
intent_words = ("cambiar", "configurar", "establecer", "nuevo", "crear", 
                "poner", "actualizar", "modificar", ...)

has_intent = any(word in lowered for word in intent_words)

if has_intent:
    # Retornar toggle en lugar de set_text
    return ActionParseResult(
        action_id="welcome.toggle",
        payload={"enabled": True},
        confidence=0.6,  # Lower confidence - es ambiguo
        reason="welcome_intent_no_text",
    )
```

### 3. Eliminar patrón greedy

Se eliminó el patrón que capturaba todo después de "bienvenida" + palabras clave.

## Resultados

| Mensaje | Antes (Rule-based) | Después |
|---------|-------------------|---------|
| "Quiero cambiar el mensaje de bienvenida..." | `set_text` con texto incorrecto | `toggle` (enable) |
| "bienvenida: Hola equipo" | `set_text` ✅ | `set_text` ✅ |
| "bienvenida con Hola" | `set_text` ✅ | `set_text` ✅ |
| "Activa bienvenida" | `toggle` ✅ | `toggle` ✅ |

## Limitaciones Actuales

1. **LLM no funciona**: Hay rate limits de OpenAI (429). Se necesita:
   - Implementar retry con backoff
   - Usar un provider alternativo
   - O mejorar las reglas rule-based

2. **Respuesta genérica**: Cuando el usuario dice "quiero cambiar" sin especificar el texto, el bot activa la bienvenida pero no pregunta qué texto quiere usar.

## Recomendaciones Futuras

1. **Mejorar integración LLM**: Implementar manejo de rate limits con retry exponencial
2. **Flujo conversacional**: Cuando el usuario expresa intención sin texto, preguntar "¿Qué mensaje de bienvenida quieres设置?"
3. **Mejores ejemplos en prompt LLM**: Agregar ejemplos de intención vs texto explícito
