# RELEASE_ENTERPRISEROBOT_DEV
Fecha: 2026-03-10

## Objetivo
Guia practica para ejecutar y configurar el checklist de release en modo **Dev**.

## 1) Alcance y modulos
- Confirmar los modulos a incluir y sus comandos:
  - Permisos/usuarios: `/adminhelp`, `/whoami`, `/user`, `/ban`.
  - Contenido: `/setrules`, `/rules`, `/setwelcome`, `/welcome`, `/setnote`, `/note`, `/filter`.
  - Moderacion: `/antispam`, `/blacklist`, `/stickerblacklist`, `/antichannel`.
  - Utilidades: `/fun`, `/reactions`, `/anilist`, `/wallpaper`, `/gettime`.

## 2) Configuracion base (.env)
Crear/editar `.env`:
```
TELEGRAM_BOT_TOKEN=TU_TOKEN
WEBHOOK_TOKEN=TU_WEBHOOK_TOKEN
CHATBOT_API_URL=http://127.0.0.1:8000/api/v1/chat
DATABASE_URL=postgresql://user:pass@localhost:5432/robot

ENTERPRISE_ENABLED=true
ENTERPRISE_MODERATION_ENABLED=false
ENTERPRISE_OWNER_IDS=123456789

ENTERPRISE_FEATURE_FUN=true
ENTERPRISE_FEATURE_REACTIONS=true
ENTERPRISE_FEATURE_ANILIST=false
ENTERPRISE_FEATURE_WALLPAPER=true
ENTERPRISE_FEATURE_GETTIME=true

ENTERPRISE_DEFAULT_TIMEZONE=UTC
```

Si usas integraciones externas (opcional):
```
ENTERPRISE_SPAMWATCH_URL=https://tu-spamwatch
ENTERPRISE_SPAMWATCH_TOKEN=token
ENTERPRISE_SIBYL_URL=https://tu-sibyl
ENTERPRISE_SIBYL_TOKEN=token
ENTERPRISE_ANILIST_URL=https://graphql.anilist.co
```

## 3) Migraciones de base de datos
Aplicar migraciones:
```powershell
alembic upgrade head
```

Verificar tablas enterprise en Postgres:
- `enterprise_users`
- `enterprise_bans`
- `enterprise_rules`
- `enterprise_welcome`
- `enterprise_notes`
- `enterprise_filters`
- `enterprise_antispam`
- `enterprise_blacklist`
- `enterprise_sticker_blacklist`
- `enterprise_antichannel`

## 4) Ejecutar tests Dev
```powershell
pytest -q
```

Debe pasar:
- Unit tests por caso de uso.
- Contract tests de comandos.
- E2E webhook -> response.
- Regresion permisos y bans.

## 5) Levantar runtimes
API:
```powershell
uvicorn app.api.entrypoint:app --host 127.0.0.1 --port 8000
```

Webhook:
```powershell
uvicorn app.webhook.entrypoint:app --host 127.0.0.1 --port 9000
```

## 6) Registrar webhook en Telegram
```powershell
python set_telegram_webhook.py
```

## 7) Verificaciones rapidas
En Telegram:
- `/adminhelp`
- `/whoami`
- `/fun`
- `/gettime UTC`

## 8) Activar moderacion en Dev (opcional)
Editar `.env`:
```
ENTERPRISE_MODERATION_ENABLED=true
```
Reiniciar webhook y probar:
- `/blacklist add spam`
- Enviar texto con "spam" (debe bloquear)

## 9) Checklist Dev (resumen)
- [ ] Modulos y comandos validados.
- [ ] Dependencias externas confirmadas (si aplica).
- [ ] Feature flags definidos.
- [ ] `ENTERPRISE_ENABLED` y `ENTERPRISE_OWNER_IDS` configurados.
- [ ] Migraciones aplicadas.
- [ ] Tests Dev ejecutados.
