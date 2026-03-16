# RELEASE_ENTERPRISEROBOT_PROD
Fecha: 2026-03-10

## Objetivo
Guia practica para ejecutar y configurar el checklist de release en modo **Prod**.

## 1) Precondiciones
- Backups recientes verificados.
- Ventana de despliegue coordinada.
- Plan de rollback comunicado.

## 2) Configuracion base (produccion)
Revisar variables de entorno:
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
ENTERPRISE_SPAMWATCH_URL=https://prod-spamwatch
ENTERPRISE_SPAMWATCH_TOKEN=token
ENTERPRISE_SIBYL_URL=https://prod-sibyl
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

## 5) Validacion post-deploy
- `/adminhelp` lista comandos esperados.
- `/whoami` devuelve rol correcto.
- Moderacion: `/antispam status`, `/blacklist add`, `/antichannel on`.
- Utilidades: `/fun`, `/gettime`.
- Monitoreo de logs y errores por 30-60 min.

## 6) Rollback rapido
Opcion A:
```
ENTERPRISE_ENABLED=false
```

Opcion B:
```
ENTERPRISE_MODERATION_ENABLED=false
```

## 7) Checklist Prod (resumen)
- [ ] Backups verificados.
- [ ] Migraciones aplicadas.
- [ ] Servicios arriba (API/Webhook).
- [ ] Validaciones post-deploy OK.
- [ ] Observabilidad sin alertas.
