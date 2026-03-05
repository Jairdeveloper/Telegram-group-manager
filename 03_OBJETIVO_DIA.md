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

## Estado del código existente

### API (`app/api/entrypoint.py`)
- ✅ `GET /health`
- ✅ `POST /api/v1/chat`
- ✅ `GET /api/v1/history/{session_id}`
- ✅ `GET /api/v1/stats`

### Webhook (`app/webhook/entrypoint.py`)
- ✅ `GET /health`
- ✅ `POST /webhook/{token}`
- ✅ `GET /metrics`

---

## Pendiente de implementar

- [ ] Fase 2: Configurar ADMIN_CHAT_IDS en .env
- [ ] Fase 2: Implementar verificación de acceso en handlers
- [ ] Fase 3: Crear servicio telegram_ops
- [ ] Fase 4: Implementar funciones de check
- [ ] Fase 5: Sistema de logs operativos
- [ ] Fase 6: Comandos Telegram
- [ ] Fase 7: Configurar ngrok

---

## Referencias

- Documento original: `TELEGRAM_E2E_LOG_APP.md`
- API canónica: `app/api.entrypoint:app` (puerto 8000)
- Webhook canónico: `app/webhook.entrypoint:app` (puerto 8001)
