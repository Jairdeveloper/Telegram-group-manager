# 03_OBJETIVO_DIA.md

## Fase: Alcance y contratos

**Fecha:** 2026-03-05
**Estado:** EN PROGRESO

---

## Tareas a ejecutar

### 1. Definir qué significa "E2E OK"

| Componente | Criterio OK |
|------------|-------------|
| API | `GET /health` retorna `{"status": "ok"}` |
| API | `POST /api/v1/chat?message=hola&session_id=test` retorna respuesta válida |
| Webhook | `GET /health` retorna `{"status": "ok"}` |
| Webhook | `POST /webhook/{token}` con payload válido retorna 200 |
| Telegram | `getWebhookInfo` sin errores recientes y `pending_update_count` estable |

### 2. Definir comandos de Telegram (MVP)

| Comando | Descripción |
|---------|-------------|
| `/health` | Devuelve estado de API + Webhook |
| `/e2e` | Ejecuta secuencia completa (API -> Webhook local -> Webhook público -> Telegram) |
| `/webhookinfo` | Devuelve resumen de `getWebhookInfo` (url + last_error_message + pending_update_count) |
| `/logs` | Devuelve últimos N eventos relevantes (webhook recibido, chat api ok/error, sendMessage ok/error) |

### 3. Definir formato de reporte

```
🕐 Timestamp UTC: 2026-03-05T14:30:00Z

📊 Estado E2E:
  ✅ API Health: OK
  ✅ API Chat: OK
  ✅ Webhook Health: OK
  ✅ Webhook Local: OK
  ✅ Webhook Público: OK
  ✅ Telegram: OK

🔗 Run ID: abc123
```

**Formato por etapa:**
- Timestamp UTC
- Resultado por etapa: `OK/FAIL`
- Error corto + "pista" (qué revisar)

---

## Estado del código existente

### API (`app/api/entrypoint.py`)
- ✅ `GET /health` - Implementado
- ✅ `POST /api/v1/chat` - Implementado
- ✅ `GET /api/v1/history/{session_id}` - Implementado
- ✅ `GET /api/v1/stats` - Implementado

### Webhook (`app/webhook/entrypoint.py`)
- ✅ `GET /health` - Implementado
- ✅ `POST /webhook/{token}` - Implementado
- ✅ `GET /metrics` - Implementado (Prometheus)

---

## Pendiente de implementar

- [ ] Bot de Telegram con comandos `/health`, `/e2e`, `/webhookinfo`, `/logs`
- [ ] Implementar funciones de check (check_api_health, check_api_chat, etc.)
- [ ] Sistema de logs operativos
- [ ] Formato de reporte estructurado

---

## Referencias

- Documento original: `TELEGRAM_E2E_LOG_APP.md`
- API canónica: `app/api.entrypoint:app` (puerto 8000)
- Webhook canónico: `app/webhook.entrypoint:app` (puerto 8001)
