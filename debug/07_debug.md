# Debug - Fase 7: Red Telegram y Arranque del Bot

## Estado: ⚠️ DEBUG COMPLETADO CON CAUSA RAIZ IDENTIFICADA (2026-03-06)

## BUG: 
mensaje de consola: telegram.error.Conflict: Conflict: terminated by other getUpdates request; make sure that only one bot instance is running

---

## Error descrito

- El bot no responde al comando `/e2e`
- `telegram.error.Conflict: Conflict: terminated by other getUpdates request`
- Se descarta falla de red ya que el bot responde a otros comandos como /logs (verificar)
- Dar pasos para hacer test a la red y aislar bug de comando /e2e
---

## Resultado del proceso de debug

La situacion ya no es la misma que en fases anteriores. En esta verificacion se confirmo lo siguiente:

1. La API ya responde correctamente:
   - `GET http://127.0.0.1:8000/health` -> `{"status":"ok","version":"2.1"}`

2. El webhook responde correctamente:
   - `GET http://127.0.0.1:8001/health` -> `{"status":"ok"}`

3. El chequeo E2E local ya no falla por API ni por webhook:
   - `api_health`: OK
   - `api_chat`: OK
   - `webhook_health`: OK
   - `webhook_local`: OK

4. El fallo restante del bot en este entorno Windows es de red hacia Telegram:
   - al arrancar el bot, falla en `get_me()` con `telegram.error.NetworkError: httpx.ConnectError: All connection attempts failed`
   - por tanto el bot no llega a quedar operativo para recibir `/e2e`

5. El `409 Conflict` sigue siendo un riesgo operativo real, pero en esta pasada el error reproducido localmente fue de conectividad a Telegram, no de lógica del proyecto.

---

## Verificaciones ejecutadas

| Verificacion | Resultado |
|-------------|-----------|
| `GET http://127.0.0.1:8000/health` | ✅ OK |
| `GET http://127.0.0.1:8001/health` | ✅ OK |
| `run_e2e_check()` | ⚠️ `overall=FAIL` solo por `telegram_webhook_info` |
| Arranque del bot con `python -m app.telegram_ops.entrypoint` | ❌ FAIL por red a Telegram |
| Lock local `logs/telegram_ops.pid` | ✅ OK |
| `py_compile` de archivos modificados | ✅ OK |

---

## Salida observada de `run_e2e_check()`

```json
{
  "checks": {
    "api_health": { "status": "OK" },
    "api_chat": { "status": "OK" },
    "webhook_health": { "status": "OK" },
    "webhook_local": { "status": "OK" },
    "telegram_webhook_info": {
      "status": "FAIL",
      "error": "All connection attempts failed"
    }
  },
  "overall": "FAIL"
}
```

Interpretacion:
- el sistema local del proyecto esta funcional
- el check que falla depende de salida de red a Telegram

---

## Causa raiz identificada

La causa raiz actual de que el bot no responda en este entorno es:

- falta de conectividad saliente hacia `api.telegram.org`

Evidencia:

```text
telegram.error.NetworkError: httpx.ConnectError: All connection attempts failed
ERROR:__main__:Telegram network bootstrap failed. Verify outbound connectivity to api.telegram.org: httpx.ConnectError: All connection attempts failed
```

Esto ocurre durante la inicializacion del bot, antes de empezar el polling real.

---

## Correcciones aplicadas

### 1. `app/telegram_ops/entrypoint.py`

Se reforzo el arranque del bot:

- lock local para evitar dobles instancias en `logs/telegram_ops.pid`
- captura explicita de `Conflict`
- captura explicita de `NetworkError`
- mensaje de error claro si no hay conectividad a Telegram
- `drop_pending_updates=True` en `run_polling()`

### 2. `app/telegram_ops/__init__.py`

Se elimino la importacion eager de `app.telegram_ops.entrypoint`.

Motivo:
- evitaba warning por doble importacion al ejecutar `python -m app.telegram_ops.entrypoint`
- reducia inicializaciones duplicadas del bot

---

## Evidencia tecnica

### Validacion de sintaxis

```bash
.\.venv\Scripts\python.exe -m py_compile app\telegram_ops\entrypoint.py app\telegram_ops\__init__.py
```

Resultado: OK

### Arranque del bot tras correccion

Comando:

```powershell
.\.venv\Scripts\python.exe -m app.telegram_ops.entrypoint
```

Resultado:
- el proceso termina
- no queda lock stale en `logs/telegram_ops.pid`
- el error queda clasificado como problema de red

---

## Conclusiones

1. El problema de API caida ya no aplica en esta fase.
2. El proyecto local responde correctamente en API y webhook.
3. El bot sigue sin responder a `/e2e` en este entorno porque no puede conectarse a Telegram durante el bootstrap.
4. El codigo del bot ahora falla de forma explicita y diagnosticable en lugar de quedar ambiguo.

---

## Accion operativa requerida

1. Verificar conectividad saliente a `api.telegram.org` desde la maquina donde corre el bot.
2. Si existe proxy, firewall o VPN, permitir HTTPS hacia Telegram.
3. Una vez restaurada la red, arrancar:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.api.entrypoint:app --host 127.0.0.1 --port 8000
.\.venv\Scripts\python.exe -m uvicorn app.webhook.entrypoint:app --host 127.0.0.1 --port 8001
.\.venv\Scripts\python.exe -m app.telegram_ops.entrypoint
```

4. Si reaparece `409 Conflict`, ejecutar:

```bash
curl "https://api.telegram.org/bot<TOKEN>/close"
curl "https://api.telegram.org/bot<TOKEN>/deleteWebhook"
```

5. Reintentar desde Telegram:

```text
/health
/e2e
/logs
```
