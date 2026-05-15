# Solución al Bug: Doble Respuesta al Enviar Comandos

## Problema

Cuando el usuario envía un comando al bot (ej: `/confog` o cualquier comando), el bot responde correctamente al comando pero también envía simultáneamente un mensaje "(sin respuesta)".

## Causa Raíz

El problema tiene dos orígenes:

### 1. Menu sin respuesta (en `app/webhook/processors/command.py`)

Cuando un comando enterprise retorna `status="menu"`, el código muestra el menú pero retorna `ProcessorResult()` sin `reply`:

```python
# Líena 113
return ProcessorResult()  # reply=None por defecto
```

