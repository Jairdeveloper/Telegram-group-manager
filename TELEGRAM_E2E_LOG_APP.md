# Telegram E2E Log App (Runbook por Fases)

Objetivo: tener un bot de Telegram que ejecute checks E2E (API + Webhook + tunel) y reporte logs/estado de forma confiable en el chat, para acelerar debugging y operación.

Premisas del proyecto actual:
- API canónica: `app.api.entrypoint:app` (puerto local sugerido: `8000`)
- Webhook canónico: `app.webhook.entrypoint:app` (puerto local sugerido: `8001`)
- Webhook path: `POST /webhook/{token}` (token en `.env`)
- Ngrok (local): expone `8001` y se sincroniza con `scripts/sync_ngrok_webhook.ps1`

---

## Fase: Alcance y contratos

Tareas:
1. Definir qué significa “E2E OK”:
   - API: `GET /health` OK y `POST /api/v1/chat` OK.
   - Webhook: `GET /health` OK, `POST /webhook/{token}` OK.
   - Telegram: `getWebhookInfo` sin errores recientes y `pending_update_count` estable.
2. Definir comandos de Telegram (MVP):
   - `/health`: devuelve estado de API + Webhook.
   - `/e2e`: ejecuta secuencia completa (API -> Webhook local -> Webhook público -> Telegram).
   - `/webhookinfo`: devuelve resumen de `getWebhookInfo` (url + last_error_message + pending_update_count).
   - `/logs`: devuelve últimos N eventos relevantes (mínimo: webhook recibido, chat api ok/error, sendMessage ok/error).
3. Definir formato de reporte (para que sea legible en Telegram):
   - Timestamp UTC
   - Resultado por etapa: `OK/FAIL`
   - Error corto + “pista” (qué revisar)

---

## Fase: Bot de Telegram (credenciales y seguridad)

Tareas:
1. Crear bot con BotFather y guardar token en `.env`:
   - `TELEGRAM_BOT_TOKEN=...`
2. Restringir quién puede ejecutar comandos:
   - Lista de `ADMIN_CHAT_IDS` o `ADMIN_USERNAMES` en `.env`.
3. Definir “canal” de reporte:
   - DM del admin, o un grupo privado.
4. Decidir manejo de secretos:
   - Nunca enviar tokens completos al chat.
   - En reportes, enmascarar token: `123456...abcd`.

---

## Fase: Punto de ejecución (dónde vive “la app”)

Opción A (recomendada): servicio separado `telegram_ops` (proceso/servicio aparte).
Tareas:
1. Crear un pequeño servicio (FastAPI o script) que:
   - Recibe comandos del bot (polling o webhook).
   - Ejecuta checks contra tu API/Webhook.
   - Publica resultados al chat.
2. Ejecutarlo con el mismo `.venv` del repo.

Opción B: integrado en el webhook/API existentes.
Tareas:
1. Añadir un router “ops” en la API o webhook.
2. Mantenerlo detrás de auth (admin chat ids) y/o header interno.

---

## Fase: Implementar “checks” (funciones puras)

Tareas:
1. Implementar `check_api_health()`:
   - `GET http://127.0.0.1:8000/health`
2. Implementar `check_api_chat()`:
   - `POST http://127.0.0.1:8000/api/v1/chat?message=hola&session_id=e2e`
3. Implementar `check_webhook_health()`:
   - `GET http://127.0.0.1:8001/health`
4. Implementar `check_webhook_local(token)`:
   - `POST http://127.0.0.1:8001/webhook/{token}` con payload Telegram simulado.
5. Implementar `check_webhook_public(ngrok_url, token)`:
   - `POST https://<ngrok>/webhook/{token}` con payload Telegram simulado.
6. Implementar `get_webhook_info(token)`:
   - `GET https://api.telegram.org/bot<TOKEN>/getWebhookInfo`
7. Definir timeouts agresivos para debug:
   - 2-5s para health y checks rápidos.

Notas:
- Los checks deben devolver objetos estructurados (no strings) para poder serializar a Telegram sin ambigüedad.
- Cada check debe capturar excepción y retornar `FAIL` con `error_type` + `message`.

---

## Fase: Captura de logs “operativos” dentro del repo

Objetivo: que el bot pueda responder “qué pasó” sin abrir consola.

Tareas:
1. Definir eventos mínimos a registrar (en webhook y en ops runner):
   - `webhook.received` (update_id, chat_id)
   - `webhook.dedup.duplicate`
   - `webhook.chat_api.ok|error`
   - `webhook.telegram_send.ok|error`
   - `webhook.enqueue.ok|error` (si async)
2. Elegir backend de logs para consulta rápida:
   - MVP: archivo rotado (`logs/ops.log`) o memoria con límite (ring buffer).
   - Producción: stdout + agregador (ELK/Grafana Loki).
3. Implementar endpoint/función para “tail”:
   - `get_recent_events(limit=50)` filtrable por `chat_id` o `update_id`.

---

## Fase: Ejecución desde Telegram (comandos)

Tareas:
1. Implementar parser de comandos:
   - `/health`
   - `/e2e`
   - `/webhookinfo`
   - `/logs 50`
2. Implementar “ack rápido”:
   - Al recibir `/e2e`, responder inmediatamente “E2E iniciado…” y luego editar/enviar resultado.
3. Implementar rate limiting:
   - Evitar spam de `/e2e` (ej: 1 cada 30s por chat).
4. Implementar correlación:
   - Asignar un `run_id` y devolverlo en cada respuesta.

---

## Fase: Tunel y registro de webhook (ngrok)

Tareas:
1. Estándar local:
   - Levantar webhook local en `8001`.
   - Levantar ngrok: `ngrok http 8001`.
2. Sincronizar webhook en Telegram:
   - Ejecutar: `powershell -ExecutionPolicy Bypass -File .\\scripts\\sync_ngrok_webhook.ps1`
3. Verificar que Telegram entrega:
   - Confirmar `getWebhookInfo.last_error_message` vacío o sin errores recientes.

---

## Fase: Modo async (opcional, cuando quieras volver a `PROCESS_ASYNC=true`)

Tareas:
1. Levantar Redis local o vía Docker:
   - Puerto `6379` escuchando.
2. Levantar worker:
   - `python worker.py`
3. Validar cola:
   - Enviar `/e2e` y confirmar que la etapa webhook encola y el worker procesa.
4. Definir fallback:
   - Si Redis cae, el webhook debe seguir respondiendo (fallback sync).

---

## Fase: Runbook E2E (comandos exactos)

Local (PowerShell):
```powershell
# API
.\.venv\Scripts\python -m uvicorn app.api.entrypoint:app --host 127.0.0.1 --port 8000

# Webhook
.\.venv\Scripts\python -m uvicorn app.webhook.entrypoint:app --host 127.0.0.1 --port 8001 --timeout-keep-alive 30 --timeout-graceful-shutdown 30

# Ngrok (en otra terminal)
ngrok http 8001

# Sync webhook URL (cuando cambia ngrok)
powershell -ExecutionPolicy Bypass -File .\scripts\sync_ngrok_webhook.ps1
```

Checks manuales:
```powershell
curl.exe http://127.0.0.1:8000/health
curl.exe http://127.0.0.1:8001/health
```

---

## Fase: Criterios de salida (listo para usar)

Tareas:
1. `/health` devuelve OK/FAIL para API+Webhook en <3s.
2. `/e2e` detecta:
   - API caída
   - Webhook caído
   - Ngrok no levantado
   - Webhook mal registrado (404/502 en Telegram)
3. `/logs` devuelve eventos recientes sin exponer secretos.

