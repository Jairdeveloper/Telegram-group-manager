# Debug - Fase 6: Conflicto de Polling y Estado Operativo

## Estado: ⚠️ PARCIALMENTE RESUELTO Y DOCUMENTADO (2026-03-06)

---

## Error reportado

- `telegram.error.Conflict: Conflict: terminated by other getUpdates request; make sure that only one bot instance is running`
- El bot no responde al comando `/e2e` en mi entorno

---

## Diagnostico

La incidencia actual mezcla dos problemas distintos:

1. Problema operativo del bot:
   - habia multiples instancias consumiendo `getUpdates`
   - eso provoca `409 Conflict` y deja al bot sin responder a comandos como `/e2e`

2. Problema operativo de la API:
   - la API en `127.0.0.1:8000` no estaba respondiendo durante la verificacion
   - aunque el bot reciba `/e2e`, el check falla porque `api_health` y `api_chat` dependen de esa API

3. Limitacion del entorno de verificacion:
   - `telegram_webhook_info` falla dentro del sandbox por falta de salida de red
   - no debe interpretarse por si solo como fallo de configuracion del proyecto

---

## Verificaciones ejecutadas

| Verificacion | Resultado |
|-------------|-----------|
| `GET http://127.0.0.1:8000/health` | FAIL |
| `GET http://127.0.0.1:8001/health` | OK |
| `POST /webhook/<TELEGRAM_BOT_TOKEN>` | OK |
| `get_recent_events(limit=8)` | OK |
| `run_e2e_check()` | FAIL |
| `close` contra Telegram | OK |
| `deleteWebhook` contra Telegram | OK |

---

## Solucion aplicada en codigo

Se modifico `app/telegram_ops/entrypoint.py` para endurecer el arranque del bot en modo polling:

1. Se añade un lock local en `logs/telegram_ops.pid`
   - impide arrancar multiples instancias locales del bot de forma silenciosa
   - si ya hay otra instancia viva, el proceso termina con un mensaje explicito

2. Se captura `telegram.error.Conflict`
   - el conflicto deja de quedar solo en logs ruidosos
   - ahora se convierte en salida controlada del proceso

3. Se usa `drop_pending_updates=True` en `run_polling()`
   - reduce ruido por backlog pendiente al reiniciar el bot

---

## Evidencia tecnica

Archivo modificado:

- `app/telegram_ops/entrypoint.py`

Elementos añadidos:

- `acquire_polling_lock()`
- `release_polling_lock()`
- manejo explicito de `Conflict`
- `app.run_polling(drop_pending_updates=True)`

Verificacion del cambio:

```bash
.\.venv\Scripts\python.exe -m py_compile app\telegram_ops\entrypoint.py
```

Resultado: OK

Prueba de lock:

```bash
.\.venv\Scripts\python.exe -c "from app.telegram_ops.entrypoint import acquire_polling_lock, release_polling_lock; pid = acquire_polling_lock(); print(pid); release_polling_lock(pid)"
```

Resultado: OK

---

## Estado despues de la correccion

| Componente | Estado |
|-----------|--------|
| Webhook | ✅ Operativo |
| Persistencia de eventos (`FileEventStore`) | ✅ Operativa |
| Bot polling local | ✅ Protegido contra doble arranque local |
| Conflicto remoto/external polling | ⚠️ Aun posible si otra instancia usa el mismo token |
| API | ❌ Sigue sin responder en `8000` |
| `/e2e` end-to-end | ⚠️ Bloqueado mientras API siga caida |

---

## Procedimiento recomendado

1. Levantar la API:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.api.entrypoint:app --host 127.0.0.1 --port 8000
```

2. Levantar el webhook:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.webhook.entrypoint:app --host 127.0.0.1 --port 8001
```

3. Levantar una unica instancia del bot:

```powershell
.\.venv\Scripts\python.exe -m app.telegram_ops.entrypoint
```

4. Si vuelve a aparecer `409 Conflict`, ejecutar:

```bash
curl "https://api.telegram.org/bot<TOKEN>/close"
curl "https://api.telegram.org/bot<TOKEN>/deleteWebhook"
```

5. Repetir:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8001/health
```

Y luego desde Telegram:

```text
/health
/e2e
/logs
```

---

## Conclusiones

- El error de polling del bot ya no queda sin control en el arranque local.
- El problema principal que sigue impidiendo un `/e2e` completamente exitoso es que la API no esta levantada en `127.0.0.1:8000`.
- Si existe otra instancia del bot fuera de este entorno usando el mismo token, el conflicto puede reaparecer y debera cerrarse operativamente con `close` y `deleteWebhook`.
