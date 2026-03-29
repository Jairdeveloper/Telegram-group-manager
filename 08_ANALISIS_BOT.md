Fecha: 2026-03-27
version: 1.0
referencia: 07_ANALISIS_BOT.md

---

# Análisis: El mensaje se guarda pero no se lee

## Logs actuales

```
Enterprise result: {'status': 'ok', 'response_text': ''}
About to send reply: ''
```

**El problema está claro:**
- El sistema ActionParser guarda el mensaje en el repositorio
- El sistema Enterprise lee del repositorio, pero retorna vacío
- Esto significa que los datos NO se están persistiendo correctamente

---

## Causa raíz

El sistema tiene **dos sistemas de almacenamiento diferentes** que no están sincronizados:

1. **ActionParser** guarda usando `get_welcome_repo()` (puede ser en memoria)
2. **Enterprise** lee usando `content_service.get_welcome()` (puede ser PostgreSQL)

Si PostgreSQL está habilitado, los datos se guardan ahí. Pero si está deshabilitado, se usa memoria y los datos se pierden cuando el servidor se reinicia.

---

## Solución implementada

Agregar logs de debug para ver exactamente qué está pasando:

**En pilot_actions.py:**
```python
logger.info(f"Welcome saved: {saved.welcome_text if saved else 'NONE'}")
```

**En handlers.py de Enterprise:**
```python
logger.info(f"/welcome: welcome={welcome}")
```

---

## Próximo paso

Por favor:
1. Envía "bienvenida: Hola equipo"
2. Envía "/welcome"

Y envíame los logs actualizados para ver:
- Si el mensaje se está guardando correctamente
- Si se está leyendo correctamente
