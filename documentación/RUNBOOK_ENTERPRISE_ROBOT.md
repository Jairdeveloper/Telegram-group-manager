# RUNBOOK_ENTERPRISE_ROBOT
Fecha: 2026-03-10

## Objetivo
Guia operativa para despliegue, verificacion, monitoreo y rollback de EnterpriseRobot.

## Alcance
- Runtime: webhook canonico y servicios enterprise.
- Modulos incluidos: permisos, contenido, moderacion avanzada, utilidades y entretenimiento.
- Persistencia: Postgres si `DATABASE_URL` valida, fallback in-memory si `no-db`.

## Pre-checklist
- `DATABASE_URL` configurada (o `no-db` para modo sin persistencia).
- `TELEGRAM_BOT_TOKEN` y `WEBHOOK_TOKEN` validos.
- `ENTERPRISE_ENABLED=true` para habilitar enterprise.
- `ENTERPRISE_MODERATION_ENABLED=true` si se requiere moderacion.
- `ENTERPRISE_FEATURE_*` segun rollout.
- `ENTERPRISE_OWNER_IDS` definido con al menos un id (para bootstrap de permisos).
- Validar que el webhook esta activo (`/webhookinfo` via OPS).

## Variables de entorno clave
Habilitacion global:
- `ENTERPRISE_ENABLED`
- `ENTERPRISE_MODERATION_ENABLED`

Feature flags por modulo:
- `ENTERPRISE_FEATURE_FUN`
- `ENTERPRISE_FEATURE_REACTIONS`
- `ENTERPRISE_FEATURE_ANILIST`
- `ENTERPRISE_FEATURE_WALLPAPER`
- `ENTERPRISE_FEATURE_GETTIME`

Integraciones externas:
- `ENTERPRISE_SPAMWATCH_URL`
- `ENTERPRISE_SPAMWATCH_TOKEN`
- `ENTERPRISE_SPAMWATCH_TIMEOUT`
- `ENTERPRISE_SIBYL_URL`
- `ENTERPRISE_SIBYL_TOKEN`
- `ENTERPRISE_SIBYL_TIMEOUT`
- `ENTERPRISE_ANILIST_URL`
- `ENTERPRISE_ANILIST_TIMEOUT`

Otros:
- `ENTERPRISE_DEFAULT_TIMEZONE`
- `ENTERPRISE_OWNER_IDS`
- `ENTERPRISE_SARDEGNA_IDS`

## Procedimiento de rollout
1. Desplegar con `ENTERPRISE_ENABLED=true` y `ENTERPRISE_MODERATION_ENABLED=false`.
2. Validar comandos basicos: `/adminhelp`, `/whoami`, `/fun`.
3. Activar utilidades por modulo con `ENTERPRISE_FEATURE_*`.
4. Habilitar moderacion con `ENTERPRISE_MODERATION_ENABLED=true`.
5. Activar antispam externo si corresponde (`spamwatch` / `sibyl`).

## Verificaciones funcionales
Permisos y admin:
- `/whoami` devuelve rol esperado.
- `/user list` lista usuarios enterprise.

Contenido:
- `/setrules <texto>` y `/rules` responden.
- `/setwelcome <texto>` y `/welcome` responden.
- `/setnote <nombre> <texto>` y `/note <nombre>` responden.

Moderacion:
- `/antispam status` muestra estado.
- `/blacklist add spam` seguido de mensaje con "spam" debe bloquear.
- `/stickerblacklist add <file_id>` seguido de sticker debe bloquear.
- `/antichannel on` bloquea mensajes de tipo channel.

Utilidades y entretenimiento:
- `/gettime UTC` retorna hora valida.
- `/fun` responde con texto.
- `/reactions hola` responde con reaccion.
- `/anilist <titulo>` responde (si URL configurada).

## Observabilidad y monitoreo
- Revisar `/logs` para eventos `webhook.enterprise_service.ok` y bloqueos.
- Buscar `webhook.enterprise_moderation.blocked` con `reason` y `source`.
- Usar metricas del webhook: `telegram_webhook_requests_total` (si Prometheus activo).

## Rollback rapido
Opcion A (total):
- `ENTERPRISE_ENABLED=false` (deshabilita comandos y moderacion enterprise).

Opcion B (solo moderacion):
- `ENTERPRISE_MODERATION_ENABLED=false` (mantiene comandos, deshabilita bloqueo).

Opcion C (modulo especifico):
- `ENTERPRISE_FEATURE_<MODULO>=false` (fun/reactions/anilist/wallpaper/gettime).

Opcion D (integraciones externas):
- Dejar `ENTERPRISE_SPAMWATCH_URL` o `ENTERPRISE_SIBYL_URL` vacio.

## Troubleshooting
Comandos no responden:
- Verificar `ENTERPRISE_ENABLED=true`.
- Verificar que el update se clasifica como `enterprise_command`.
- Revisar `app/webhook/handlers.py` y `/logs`.

Moderacion no bloquea:
- `ENTERPRISE_MODERATION_ENABLED=true`.
- Configuracion por chat (`/antispam on`, `/blacklist add`).
- Verificar que el actor no es `WHITELIST` o `SARDEGNA`.

AniList no responde:
- Verificar `ENTERPRISE_ANILIST_URL` y conectividad.
- Confirmar `ENTERPRISE_FEATURE_ANILIST=true`.

## Operacion y mantenimiento
- Reiniciar webhook runtime despues de cambios en env vars.
- Aplicar migraciones cuando se agrega persistencia.
- Registrar cambios de configuracion en auditoria.

## Notas
- Si `ENTERPRISE_ENABLED=false`, el dispatcher reconoce comandos pero responde "Enterprise deshabilitado".
- Modo `no-db` pierde configuracion al reiniciar.
