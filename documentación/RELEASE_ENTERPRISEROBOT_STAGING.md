# RELEASE_ENTERPRISEROBOT_STAGING
Fecha: 2026-03-10

## Objetivo
Guia practica para ejecutar y configurar el checklist de release en modo **Staging**.

## 1) Precondiciones
- Entorno de staging con variables de entorno aisladas.
- Webhook accesible desde internet o tunel (segun infraestructura).
- Base de datos de staging disponible (si aplica).

## 2) Configuracion base (.env)
Revisar/ajustar:
```
ENTERPRISE_ENABLED=true
ENTERPRISE_MODERATION_ENABLED=true
ENTERPRISE_OWNER_IDS=123456789

ENTERPRISE_FEATURE_FUN=true
ENTERPRISE_FEATURE_REACTIONS=true
ENTERPRISE_FEATURE_ANILIST=true
ENTERPRISE_FEATURE_WALLPAPER=true
ENTERPRISE_FEATURE_GETTIME=true

ENTERPRISE_DEFAULT_TIMEZONE=UTC
```

Integraciones externas:
```
ENTERPRISE_SPAMWATCH_URL=https://staging-spamwatch
ENTERPRISE_SPAMWATCH_TOKEN=token
ENTERPRISE_SIBYL_URL=https://staging-sibyl
ENTERPRISE_SIBYL_TOKEN=token
ENTERPRISE_ANILIST_URL=https://graphql.anilist.co
```

## 3) Migraciones de base de datos
```powershell
alembic upgrade head
```

## 4) Despliegue y arranque
API:
```powershell
uvicorn app.api.entrypoint:app --host 0.0.0.0 --port 8000
```

Webhook:
```powershell
uvicorn app.webhook.entrypoint:app --host 0.0.0.0 --port 9000
```

## 5) Registrar webhook en Telegram
```powershell
python set_telegram_webhook.py
```

## 6) Validaciones funcionales (staging)
- `/adminhelp` lista comandos esperados.
- `/whoami` devuelve rol correcto.
- Contenido: `/setrules`, `/setwelcome`, `/setnote`, `/filter`.
- Moderacion: `/antispam status`, `/blacklist add`, `/stickerblacklist add`, `/antichannel on`.
- Utilidades: `/fun`, `/reactions`, `/gettime`.

## 7) Observabilidad
- Revisar `/logs` y eventos `webhook.enterprise_moderation.blocked`.
- Verificar ausencia de errores en integraciones externas.

## 8) Checklist Staging (resumen)
- [ ] Variables de entorno revisadas.
- [ ] Migraciones aplicadas.
- [ ] Webhook registrado.
- [ ] Validaciones funcionales OK.
- [ ] Observabilidad sin errores.
