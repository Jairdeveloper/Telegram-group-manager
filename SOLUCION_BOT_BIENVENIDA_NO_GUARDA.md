# Solución: Bot No Actualiza Mensaje de Bienvenida

## Problema

El usuario envía "cambiar mensaje de bienvenida" (en lenguaje natural, sin texto específico). El bot responde "Welcome actualizado" pero al consultar `/welcome` responde "(sin respuesta)".

## Causa Raíz

En `app/agent/actions/parser.py`, cuando el usuario dice "cambiar mensaje de bienvenida" sin especificar el texto:

1. **Antes del fix**: El parser rule-based retornaba `welcome.toggle` con `payload={"enabled": True}`
2. **Problema**: `welcome.toggle` solo activa/desactiva el flag `enabled` pero NO actualiza el texto
3. **Resultado**: El welcome se activa pero con texto vacío

## Flujo Incorrecto (Antes)

```
Usuario: "cambiar mensaje de bienvenida"
  ↓
ActionParser detecta "bienvenida" + "cambiar"
  ↓
No hay texto después de "bienvenida"
  ↓
Retorna: welcome.toggle {enabled: true}  ← INCORRECTO
  ↓
_welcome_toggle() ejecuta: solo cambia enabled=true
  ↓
welcome_text sigue vacío
  ↓
/welcome retorna "(sin respuesta)"
```

## Solución Aplicada

En `app/agent/actions/parser.py:92-106`, cambiar `welcome.toggle` por `welcome.set_creative_text`:

```python
# ANTES (incorrecto):
return ActionParseResult(
    action_id="welcome.toggle",
    payload={"enabled": True},
    confidence=0.6,
    reason="welcome_intent_no_text",
)

# DESPUÉS (correcto):
return ActionParseResult(
    action_id="welcome.set_creative_text",
    payload={},
    confidence=0.7,
    reason="welcome_intent_no_text_creative",
)
```

## Flujo Correcto (Ahora)

```
Usuario: "cambiar mensaje de bienvenida"
  ↓
ActionParser detecta "bienvenida" + "cambiar"
  ↓
No hay texto después de "bienvenida"
  ↓
Retorna: welcome.set_creative_text {}  ← CORRECTO
  ↓
_welcome_set_creative_text() ejecuta:
  - Genera mensaje creativo aleatorio
  - Guarda en welcome_text
  - enabled=true
  ↓
Mensaje: "✅ Mensaje de bienvenida configurado: ..."
  ↓
/welcome retorna el mensaje creativo
```

## Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `app/agent/actions/parser.py` | Línea 102: `welcome.toggle` → `welcome.set_creative_text` |

## Verificación

El fix asegura que cuando el usuario dice "cambiar mensaje de bienvenida" sin texto específico, el bot:
1. Genera un mensaje creativo automáticamente
2. Lo guarda en la base de datos
3. Responde con el mensaje generado
4. `/welcome` retorna el mensaje correcto