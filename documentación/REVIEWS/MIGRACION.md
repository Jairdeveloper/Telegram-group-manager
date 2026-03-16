# Migracion Semana 2-3 (primer corte)

## Objetivo

Desacoplar API y Webhook por capas, sin cambiar contratos ni comportamiento observable.

## Estado actual

- API modular activa en `app/api`:
  - `factory.py` crea la app FastAPI.
  - `routes.py` define `/api/v1/chat`, `/api/v1/history/{session_id}`, `/api/v1/stats`.
- Webhook modular activo en `app/webhook`:
  - `handlers.py` contiene logica de negocio (token/dedup/procesamiento).
  - `entrypoint.py` expone app compatible para runtime actual.
- Entrypoints legacy preservados:
  - `chatbot_monolith.py` delega construccion de API a `app/api`.
  - `telegram_webhook_prod.py` delega flujo webhook a `app/webhook/handlers.py`.

## Contratos preservados

- API: `POST /api/v1/chat` mantiene estructura de respuesta.
- Webhook: `POST /webhook/{token}` mantiene validacion de token, deduplicacion por `update_id`, y respuesta `{"ok": true}`.

## Riesgos pendientes

- Branch protection aun depende de configuracion manual en GitHub UI (`Require PR` + `Required check: pytest`).
- Fallback de dedup en memoria (sin Redis) no es distribuido entre replicas.
- Warning tecnico pendiente: `datetime.utcnow()` deprecado en Python reciente.

## Siguientes pasos recomendados (Semana 2-3)

1. Extraer y estabilizar capa de configuracion (`settings`) para API/Webhook en modulos dedicados.
2. Aislar interfaces de infraestructura (requests/redis/rq) para mejorar testeo y reemplazo de proveedores.
3. Agregar pruebas negativas adicionales de webhook (errores de Chat API y de envio Telegram).
4. Definir plan de retirada progresiva de codigo legacy cuando los entrypoints modulares sean canonicos.
