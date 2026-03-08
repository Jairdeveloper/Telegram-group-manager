# 03_OBJETIVO_DIA.md

## Fase 1: Alcance y contratos

**Fecha:** 2026-03-05
**Estado:** COMPLETADO

### Tareas

| Componente | Criterio OK |
|------------|-------------|
| API | `GET /health` retorna `{"status": "ok"}` |
| API | `POST /api/v1/chat?message=hola&session_id=test` retorna respuesta válida |
| Webhook | `GET /health` retorna `{"status": "ok"}` |
| Webhook | `POST /webhook/{token}` con payload válido retorna 200 |
| Telegram | `getWebhookInfo` sin errores recientes y `pending_update_count` estable |

### Comandos de Telegram (MVP)

| Comando | Descripción |
|---------|-------------|
| `/health` | Devuelve estado de API + Webhook |
| `/e2e` | Ejecuta secuencia completa |
| `/webhookinfo` | Devuelve resumen de `getWebhookInfo` |
| `/logs` | Devuelve últimos N eventos relevantes |

### Formato de reporte

```
🕐 Timestamp UTC: 2026-03-05T14:30:00Z

📊 Estado E2E:
  ✅ API Health: OK
  ✅ Webhook: OK
  ✅ Telegram: OK

🔗 Run ID: abc123
```

---

## Fase 2: Bot de Telegram (credenciales y seguridad)

**Fecha:** 2026-03-05
**Estado:** EN PROGRESO

### Tareas

1. **Crear bot con BotFather**
   - ✅ Ya existe: `TELEGRAM_BOT_TOKEN=8588716358:...` (en `.env`)

2. **Restringir quién puede ejecutar comandos**
   - [ ] Agregar `ADMIN_CHAT_IDS` o `ADMIN_USERNAMES` en `.env`
   - [ ] Implementar verificación en handlers

3. **Definir "canal" de reporte**
   - [ ] DM del admin o grupo privado
   - [ ] Configurar `ADMIN_CHAT_ID` en `.env`

4. **Manejo de secretos**
   - [ ] Nunca enviar tokens completos al chat
   - [ ] Enmascarar tokens: `123456...abcd`

### Variables de entorno requeridas

```bash
ADMIN_CHAT_IDS=123456789
ADMIN_USERNAMES=usuario1,usuario2
```

---

## Fase 3: E2E operable: run_id, check público (ngrok) y pistas accionables

**Estado:** ✅ COMPLETADO

### Objetivo

Hacer que `/e2e` sea realmente útil para diagnosticar problemas sin abrir consola.

### Estado actual

| Item | Estado |
|------|--------|
| `run_id` en `/e2e` | ✅ Implementado |
| Check público (ngrok) | ✅ Implementado |
| Pistas en errores | ✅ Implementado |

### Tareas pendientes

- [ ] Ninguna - Fase 3 completada

#### 3.1 - Mejorar pistas en errores

**Problema**: Los errores en `/e2e` no dan pistas accionables.

**Solución**: Extender mensajes de error en `app/ops/services.py` con sugerencias como:
- "Connection refused → ¿está uvicorn en 8001?"
- "403 Invalid token → revisa el token en la URL"
- "getWebhookInfo url vacía → ejecuta setWebhook"
- "Webhook 404 → verifica ngrok o dominio público"

**Estado**: ✅ COMPLETADO

#### 3.2 - Verificar check_webhook_public

**Estado**: Ya existe en `app/ops/checks.py`

**Implementado**:
- [x] Que `check_webhook_public()` funciona con ngrok
- [x] Documentar variable `NGROK_URL` si es necesaria

**Cambios**:
- Agregada variable `NGROK_URL` / `NGROK_HTTPS_URL` en settings
- `run_e2e_check()` ahora incluye check de webhook público si NGROK_URL está configurado

---

## Fase 4: Seguridad: separar WEBHOOK_TOKEN del TELEGRAM_BOT_TOKEN

**Estado:** ✅ COMPLETADO

### Objetivo

No exponer `TELEGRAM_BOT_TOKEN` en la URL pública del webhook.

### Tareas

#### 4.1 - Introducir WEBHOOK_TOKEN

**Settings** (`app/config/settings.py`):
- [x] Añadir `webhook_token: Optional[str]` a `WebhookSettings`
- [x] Regla: si existe, validar contra ese; si no, validar contra `telegram_bot_token` (legacy)

**Implementación** (`app/webhook/entrypoint.py`):
- [x] Ajustar para pasar el token esperado a `handle_webhook_impl`
- [x] Emitir evento `webhook.legacy_token_used` si llega el token legacy

**Scripts/Docs**:
- [x] `set_webhook_prod.py`
- [x] `scripts/sync_ngrok_webhook.ps1`
- [x] `ARRANQUE_DEV_PROD.md`
- [x] `estructura.md`

**Tests**:
- [x] Actualizar `tests/test_webhook_contract.py` para validar el nuevo token

#### 4.2 - Métricas async

**Tareas**:
- [x] Verificar métricas Prometheus actuales
- [x] Añadir contadores para `chat_api_error` y `telegram_send_error`

#### 4.3 - Runbooks finales

**Tareas**:
- [x] Consolidar documentación en `ARRANQUE_DEV_PROD.md`
- [ ] Checklist de release

---

## Definición de DONE (Semana 4)

- [ ] `/logs` devuelve eventos reales sin secretos
- [ ] `/e2e` identifica fallos típicos (API caída, webhook caído, ngrok roto, Telegram mal registrado)
- [ ] Webhook NO requiere exponer `TELEGRAM_BOT_TOKEN` en URL pública
- [ ] `pytest -q` en verde
- [ ] Docs actualizadas

---

## Referencias

- Documento original: `TELEGRAM_E2E_LOG_APP.md`
- API canónica: `app/api.entrypoint:app` (puerto 8000)
- Webhook canónico: `app/webhook.entrypoint:app` (puerto 8001)
- Redis: `REDIS_EN_PROYECTO.md`
- Runbook debug: `debug/11_debug.md`
- Arranque: `ARRANQUE_DEV_PROD.md`
