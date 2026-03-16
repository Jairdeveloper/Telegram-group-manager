# Telegram E2E Log App (Runbook por Fases)

Objetivo: tener un bot de Telegram que ejecute checks E2E (API + webhook + tunel) y reporte logs/estado de forma confiable en el chat para acelerar debugging y operacion.

Premisas del proyecto actual:
- API canonica: `app.api.entrypoint:app` (puerto local sugerido: `8000`)
- Webhook canonico: `app.webhook.entrypoint:app` (puerto local sugerido: `8001`)
- Webhook path: `POST /webhook/{token}` (token en `.env`)
- Ngrok local expone `8001` y se sincroniza con `scripts/sync_ngrok_webhook.ps1`

Nota operativa vigente:
- `app.webhook.entrypoint:app` es el unico ingress canonico de Telegram.
- `telegram_adapter.py` queda como runtime legacy.
- `app.telegram_ops.entrypoint.py` queda como runtime transitorio.
- No se deben ejecutar en paralelo para el mismo `TELEGRAM_BOT_TOKEN`.

---

## Fase 1: Alcance y contratos

Tareas:
1. Definir que significa "E2E OK":
   - API: `GET /health` OK y `POST /api/v1/chat` OK.
   - Webhook: `GET /health` OK y `POST /webhook/{token}` OK.
   - Telegram: `getWebhookInfo` sin errores recientes y `pending_update_count` estable.
2. Definir comandos de Telegram:
   - `/health`
   - `/e2e`
   - `/webhookinfo`
   - `/logs`
3. Definir formato de reporte:
   - timestamp UTC
   - resultado por etapa `OK/FAIL`
   - error corto y pista de revision

---

## Fase 2: Bot de Telegram (credenciales y seguridad)

Tareas:
1. Crear bot con BotFather y guardar token en `.env`.
2. Restringir quien puede ejecutar comandos.
3. Definir canal de reporte.
4. No exponer secretos completos en el chat.

---

## Fase 3: Punto de ejecucion

Historico:
- existio una opcion separada `telegram_ops` por polling.

Estado actual recomendado:
- la arquitectura objetivo ya no recomienda un proceso OPS paralelo si comparte token.
- el destino es integrar el despacho OPS dentro del webhook canonico.

Opciones:
1. Integrado en webhook/API existentes.
2. Servicio separado solo si usa otro token distinto.

---

## Fase 4: Implementar checks

Tareas:
1. `check_api_health()`
2. `check_api_chat()`
3. `check_webhook_health()`
4. `check_webhook_local(token)`
5. `check_webhook_public(ngrok_url, token)`
6. `get_webhook_info(token)`
7. Definir timeouts agresivos para debug.

Notas:
- Los checks deben devolver objetos estructurados.
- Cada check debe capturar excepcion y retornar `FAIL` con detalle.

---

## Fase 5: Captura de logs operativos

Objetivo: que el bot pueda responder "que paso" sin abrir consola.

Eventos minimos:
- `webhook.received`
- `webhook.dedup.duplicate`
- `webhook.chat_api.ok|error`
- `webhook.telegram_send.ok|error`
- `webhook.enqueue.ok|error`

Backend minimo:
- archivo rotado o store simple consultable

---

## Fase 6: Ejecucion desde Telegram

Tareas:
1. Implementar parser de comandos:
   - `/health`
   - `/e2e`
   - `/webhookinfo`
   - `/logs 50`
2. Implementar ack rapido para `/e2e`.
3. Implementar rate limiting.
4. Implementar correlacion por `run_id`.

---

## Fase 7: Tunel y registro de webhook

Tareas:
1. Levantar webhook local en `8001`.
2. Levantar ngrok: `ngrok http 8001`.
3. Sincronizar webhook:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\sync_ngrok_webhook.ps1
```

4. Verificar `getWebhookInfo`.

---

## Fase 8: Modo async (opcional)

Tareas:
1. Levantar Redis local o Docker.
2. Levantar worker:

```powershell
python worker.py
```

3. Validar cola.
4. Mantener fallback sync si Redis cae.

---

## Fase 9: Runbook E2E

Local (PowerShell):

```powershell
# API
.\.venv\Scripts\python -m uvicorn app.api.entrypoint:app --host 127.0.0.1 --port 8000

# Webhook
.\.venv\Scripts\python -m uvicorn app.webhook.entrypoint:app --host 127.0.0.1 --port 8001 --timeout-keep-alive 30 --timeout-graceful-shutdown 30

# Ngrok
ngrok http 8001

# Sync webhook
powershell -ExecutionPolicy Bypass -File .\scripts\sync_ngrok_webhook.ps1
```

Checks manuales:

```powershell
curl.exe http://127.0.0.1:8000/health
curl.exe http://127.0.0.1:8001/health
```

---

## Fase 10: Criterios de salida

1. `/health` devuelve estado de API y webhook en menos de 3 segundos.
2. `/e2e` detecta:
   - API caida
   - webhook caido
   - ngrok no levantado
   - webhook mal registrado
3. `/logs` devuelve eventos recientes sin exponer secretos.

---

## Regla final de operacion

Mientras no exista separacion real por tokens:
- usar un solo runtime Telegram por token
- preferir siempre `app.webhook.entrypoint:app`
- no operar con `telegram_adapter.py` y `app.telegram_ops.entrypoint.py` en paralelo
