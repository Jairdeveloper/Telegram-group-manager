# 04 - Objetivo por Fase: Telegram E2E Log App

---

## Fase 1: Alcance y contratos

**Objetivo:** Definir qué significa "E2E OK", los comandos del bot y el formato de reporte.

**Operaciones:**
1. Definir criterios "E2E OK":
   - API: `GET /health` OK y `POST /api/v1/chat` OK
   - Webhook: `GET /health` OK, `POST /webhook/{token}` OK
   - Telegram: `getWebhookInfo` sin errores y `pending_update_count` estable
2. Definir comandos MVP:
   - `/health`: estado de API + Webhook
   - `/e2e`: secuencia completa (API → Webhook local → Webhook público → Telegram)
   - `/webhookinfo`: resumen de `getWebhookInfo`
   - `/logs`: últimos N eventos relevantes
3. Definir formato de reporte: timestamp UTC, resultado por etapa (OK/FAIL), error corto + pista

---

## Fase 2: Bot de Telegram (credenciales y seguridad)

**Objetivo:** Crear bot y configurar seguridad.

**Operaciones:**
1. Crear bot con BotFather y guardar token en `.env` como `TELEGRAM_BOT_TOKEN`
2. Configurar restricciones de acceso: `ADMIN_CHAT_IDS` o `ADMIN_USERNAMES` en `.env`
3. Definir canal de reporte (DM admin o grupo privado)
4. Configurar manejo de secretos: nunca enviar tokens completos, enmascarar en reportes

---

## Fase 3: Punto de ejecución

**Objetivo:** Definir dónde vive "la app" del bot.

**Operaciones:**
- **Opción A (recomendada):** Crear servicio separado `telegram_ops`
  - Crear pequeño servicio (FastAPI/script) que reciba comandos, ejecute checks y publique resultados
  - Ejecutar con el mismo `.venv` del repo
- **Opción B:** Integrado en webhook/API existentes
  - Añadir router "ops" en API/webhook
  - Mantener detrás de auth (admin chat ids) y/o header interno

---

## Fase 4: Implementar "checks" (funciones puras)

**Objetivo:** Implementar funciones de verificación.

**Operaciones:**
1. `check_api_health()`: `GET http://127.0.0.1:8000/health`
2. `check_api_chat()`: `POST http://127.0.0.1:8000/api/v1/chat?message=hola&session_id=e2e`
3. `check_webhook_health()`: `GET http://127.0.0.1:8001/health`
4. `check_webhook_local(token)`: `POST http://127.0.0.1:8001/webhook/{token}` con payload simulado
5. `check_webhook_public(ngrok_url, token)`: `POST https://<ngrok>/webhook/{token}` con payload simulado
6. `get_webhook_info(token)`: `GET https://api.telegram.org/bot<TOKEN>/getWebhookInfo`
7. Definir timeouts agresivos: 2-5s para health y checks rápidos
8. Retornar objetos estructurados (no strings) con captura de excepciones

---

## Fase 5: Captura de logs "operativos"

**Objetivo:** Poder responder "qué pasó" sin abrir consola.

**Operaciones:**
1. Definir eventos mínimos a registrar:
   - `webhook.received` (update_id, chat_id)
   - `webhook.dedup.duplicate`
   - `webhook.chat_api.ok|error`
   - `webhook.telegram_send.ok|error`
   - `webhook.enqueue.ok|error` (si async)
2. Elegir backend de logs:
   - MVP: archivo rotado (`logs/ops.log`) o ring buffer
   - Producción: stdout + agregador (ELK/Loki)
3. Implementar endpoint/función para tail: `get_recent_events(limit=50)` filtrable

---

## Fase 6: Ejecución desde Telegram (comandos)

**Objetivo:** Procesar comandos del usuario.

**Operaciones:**
1. Implementar parser de comandos: `/health`, `/e2e`, `/webhookinfo`, `/logs 50`
2. Implementar "ack rápido": responder inmediatamente al recibir `/e2e` y luego editar/enviar resultado
3. Implementar rate limiting: evitar spam de `/e2e` (ej: 1 cada 30s por chat)
4. Implementar correlación: asignar `run_id` y devolverlo en cada respuesta

---

## Fase 7: Tunel y registro de webhook (ngrok)

**Objetivo:** Configurar ngrok y sincronizar webhook con Telegram.

**Operaciones:**
1. Levantar webhook local en puerto `8001`
2. Levantar ngrok: `ngrok http 8001`
3. Sincronizar webhook en Telegram: `powershell -ExecutionPolicy Bypass -File .\scripts\sync_ngrok_webhook.ps1`
4. Verificar entrega: confirmar `getWebhookInfo.last_error_message` vacío o sin errores

---

## Fase 8: Modo async (opcional)

**Objetivo:** Habilitar procesamiento asíncrono con Redis.

**Operaciones:**
1. Levantar Redis local o vía Docker (puerto `6379`)
2. Levantar worker: `python worker.py`
3. Validar cola: enviar `/e2e` y confirmar que webhook encola y worker procesa
4. Definir fallback: si Redis cae, webhook debe seguir respondiendo (sync)

---

## Fase 9: Runbook E2E (comandos exactos)

**Objetivo:** Documentar comandos para ejecución local.

**Operaciones:**
- **API:** `.\.venv\Scripts\python -m uvicorn app.api.entrypoint:app --host 127.0.0.1 --port 8000`
- **Webhook:** `.\.venv\Scripts\python -m uvicorn app.webhook.entrypoint:app --host 127.0.0.1 --port 8001 --timeout-keep-alive 30 --timeout-graceful-shutdown 30`
- **Ngrok:** `ngrok http 8001`
- **Sync webhook:** `powershell -ExecutionPolicy Bypass -File .\scripts\sync_ngrok_webhook.ps1`
- **Checks manuales:** `curl.exe http://127.0.0.1:8000/health` y `curl.exe http://127.0.0.1:8001/health`

---

## Fase 10: Criterios de salida (listo para usar)

**Objetivo:** Verificar que el sistema funciona correctamente.

**Operaciones:**
1. `/health` devuelve OK/FAIL para API+Webhook en <3s
2. `/e2e` detecta:
   - API caída
   - Webhook caído
   - Ngrok no levantado
   - Webhook mal registrado (404/502 en Telegram)
3. `/logs` devuelve eventos recientes sin exponer secretos
