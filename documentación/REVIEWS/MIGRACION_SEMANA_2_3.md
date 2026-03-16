# MIGRACION_SEMANA_2_3 - Retiro progresivo de legacy

## Fuente canonica vigente
- API: `app/api/*`
- Webhook: `app/webhook/*`

## Legacy temporal (compatibilidad)
Legacy eliminado. Los entrypoints canonicos son:
- API: `app/api/entrypoint.py`
- Webhook: `app/webhook/entrypoint.py`

## Plan de deprecacion en 3 pasos
### Paso A - Wrappers solamente
- Objetivo: dejar legacy como puentes de import/ejecucion.
- Estado esperado:
  - Wrappers legacy delegan a `app.webhook.entrypoint`.
  - Deploys nuevos apuntan a `app.webhook.entrypoint:app`.
  - API de despliegue apunta a `app.api.entrypoint:app`.

Estado de ejecucion (2026-03-04):
- [x] Deploys/documentacion operativa apuntan a entrypoints canonicos.

### Paso B - Migrar despliegues al entrypoint modular
- Objetivo: operacion unificada en una ruta.
- Cambios:
  - `docker-compose.yml` usa `app.webhook.entrypoint:app` y `app.api.entrypoint:app`.
  - Manifests `deploy/*webhook*.yaml` usan comando `uvicorn app.webhook.entrypoint:app ...`.
- Validacion:
  - `GET /health` webhook y API en verde.
  - `POST /webhook/{token}` funcional en sync y async.

### Paso C - Eliminacion de legacy
- Objetivo: remover deuda tecnica cuando haya estabilidad.
- Criterio de retiro:
  - 2 releases consecutivas estables sobre entrypoints modulares.
  - Sin referencias en despliegue/CI a archivos legacy.
  - Documentacion actualizada solo con rutas canonicas.

Estado de ejecucion (2026-03-04):
- [x] Eliminados entrypoints legacy del repositorio.
- [x] Documentacion operativa actualizada para usar entrypoints canonicos.

## Checklist de salida de legacy
- [x] CI ejecuta tests contra entrypoints modulares.
- [x] Runbooks documentan `app.webhook.entrypoint:app` y `app.api.entrypoint:app`.
- [ ] Tareas RQ siguen operativas (`worker.py` + `webhook_tasks.py`).
- [ ] Monitoreo (`/metrics`) y healthchecks validados en modular.

## Riesgos y mitigaciones
- Riesgo: drift entre wrapper legacy y modular.
  - Mitigacion: prohibir logica nueva en wrappers y cubrir contrato en tests.
- Riesgo: configuracion de entorno inconsistente.
  - Mitigacion: validar `.env` y tipado fuerte en `app/config/settings.py`.
- Riesgo: error silencioso en entrega Telegram.
  - Mitigacion: revisar `getWebhookInfo`, metricas y logs de webhook/worker.
Nota (2026-03-04):
- El Paso C se ejecuto antes de completar los criterios originales (2 releases consecutivas estables). Si quieres mantener ese guardrail, reintroduce el criterio como \"bloqueador\" antes de futuros retiros similares.

