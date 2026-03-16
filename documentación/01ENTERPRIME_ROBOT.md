# 01ENTERPRIME_ROBOT - Implementacion adaptada al proyecto actual

## 1. Objetivo
Definir una implementacion tipo EnterpriseBot adaptada al estado real de este repositorio (`manufacturing/robot`), aprovechando lo ya construido: API modular, webhook modular, settings centralizados y desacople por puertos/adaptadores en webhook.

La meta no es reescribir todo desde cero, sino conectar y evolucionar el sistema actual con un flujo de codificacion seguro, incremental y testeable.

## 2. Estado actual del proyecto (base de partida)
Arquitectura vigente (hibrida modular + legacy wrappers):
- API:
  - `app/api/factory.py`
  - `app/api/routes.py`
  - `chatbot_monolith.py` (entrypoint y compatibilidad)
- Webhook Telegram:
  - `telegram_webhook_prod.py` (composition root)
  - `app/webhook/handlers.py` (logica de negocio)
  - `app/webhook/ports.py` (interfaces)
  - `app/webhook/infrastructure.py` (adaptadores Requests/Redis/RQ)
  - `webhook_tasks.py` (worker path)
- Worker async:
  - `worker.py`
- Config:
  - `app/config/settings.py`

Punto clave: el webhook ya esta desacoplado de librerias externas a nivel de logica, y eso se convierte en el patron de referencia para el resto del sistema.

## 3. Arquitectura objetivo adaptada (para este repo)
Se recomienda arquitectura en 4 capas sin romper el deploy actual.

### 3.1 Capa Transport
Responsable de entrada/salida HTTP o Telegram.
- API FastAPI (`/api/v1/*`)
- Webhook FastAPI (`/webhook/{token}`)
- Futuros adapters (CLI, pruebas e2e, panel admin)

### 3.2 Capa Application
Casos de uso orquestados y testeables.
- `process_update` (ya existe como servicio compartido en webhook)
- Futuros casos: `send_alert`, `escalate_incident`, `summarize_shift`, `maintenance_recommendation`

### 3.3 Capa Domain
Reglas puras de negocio del bot manufactura.
- Politicas de respuesta
- Reglas de priorizacion de incidentes
- Clasificacion de mensajes operativos

### 3.4 Capa Infrastructure
Implementaciones concretas de puertos.
- Telegram API client
- Chat API client
- Dedup store (Redis/InMemory)
- Queue (RQ)
- Storage futuro (PostgreSQL)

## 4. Stack tecnico recomendado para este proyecto
Stack realista y compatible con lo que ya tienes:
- Lenguaje/runtime: Python 3.11+
- API/webhook: FastAPI + Uvicorn
- Config: `pydantic-settings` (ya en uso)
- Cola/cache: Redis + RQ (ya integrado)
- Transporte HTTP saliente: `requests` (actual); migrable a `httpx` async si se decide
- Observabilidad: `prometheus-client` en webhook + logging estructurado progresivo
- Calidad: `pytest` + tests de contrato y unitarios (ya presentes)
- Entorno: Docker Compose para ejecución completa local

## 5. Flujo de trabajo detallado para conectarlo con el proyecto actual (codificacion)
Este flujo esta diseñado para implementar sin romper contratos existentes (`/api/v1/chat`, `/webhook/{token}`).

### Paso 1: Congelar contratos y baseline
1. Ejecutar:
```bash
pytest -q
```
2. Confirmar inmutables:
- `POST /api/v1/chat` mantiene payload y codigos
- `POST /webhook/{token}` mantiene `403`, `500`, y `200 {"ok": true}`

### Paso 2: Definir un nuevo caso de uso en Application
1. Crear modulo de caso de uso en `app/application/` (nueva carpeta).
2. Mover logica de decision de respuesta fuera de transport cuando aplique.
3. Inyectar dependencias por interfaz (no imports directos de `requests`, `redis`, `rq`).

Regla de codificacion:
- Transport llama caso de uso
- Caso de uso usa puertos
- Infrastructure implementa puertos

### Paso 3: Extender puertos y adaptadores
1. Si el caso de uso necesita nueva dependencia externa:
- Agregar interfaz en `app/webhook/ports.py` (o modulo de puertos comun)
- Implementar adaptador en `app/webhook/infrastructure.py` (o infraestructura comun)
2. Mantener implementacion fallback para test/local cuando sea posible.

### Paso 4: Composition root explicito
1. En `telegram_webhook_prod.py` y futuros entrypoints:
- Instanciar adaptadores concretos
- Conectar use-case + handlers
- Evitar logica de negocio inline
2. `webhook_tasks.py` debe reutilizar el mismo servicio de dominio/use-case (sin duplicar reglas).

### Paso 5: Integrar con API actual
1. Si el comportamiento nuevo impacta respuesta de chat:
- Integrar desde `app/api/routes.py` mediante servicios inyectados
2. Evitar meter logica nueva directamente en `chatbot_monolith.py`; usarlo como wrapper de compatibilidad.

### Paso 6: Estrategia async/sync operativa
- Modo sync (debug rapido):
  - `.env` con `PROCESS_ASYNC=false`
- Modo async (produccion recomendada):
  - `.env` con `PROCESS_ASYNC=true`
  - Redis arriba
  - `worker.py` corriendo

### Paso 7: Pruebas obligatorias por cambio
1. Unit tests del caso de uso (sin red real, sin Redis real).
2. Contract tests webhook/API (status y payload).
3. Pruebas negativas:
- timeout Chat API
- no-200 Chat API
- fallo envio Telegram
- BOT token ausente
- fallo enqueue async

### Paso 8: Observabilidad minima
1. Mantener metricas Prometheus de webhook.
2. Agregar logs con contexto (`chat_id`, `update_id`, `job_id`).
3. Verificar `getWebhookInfo` en Telegram durante pruebas externas.

### Paso 9: Rollout seguro
1. Feature flag por variable de entorno para funcionalidades nuevas.
2. Activacion gradual en entorno dev/staging.
3. Checklist de rollback:
- volver a flujo anterior sin cambio de contrato
- desactivar flag

## 6. Flujo operacional end-to-end (mensaje Telegram)
1. Telegram envia update al endpoint publico HTTPS `/webhook/{token}`.
2. `telegram_webhook_prod.py` valida token y delega a `handle_webhook_impl`.
3. Se ejecuta deduplicacion (`DedupStore` Redis o memoria).
4. Si `PROCESS_ASYNC=true` y hay cola:
- se encola tarea en RQ
- `worker.py` procesa con `webhook_tasks.py`
5. Si `PROCESS_ASYNC=false`:
- procesa en el request actual
6. `process_update_impl`:
- extrae `chat_id/text`
- llama `ChatApiClient`
- envia respuesta con `TelegramClient`
7. webhook responde `200 {"ok": true}`.

## 7. Convenciones de codificacion para este repositorio
- No usar `os.getenv` fuera de `app/config/settings.py`.
- No acoplar handlers a librerias externas.
- No duplicar logica entre webhook y worker.
- Mantener contratos HTTP existentes durante refactor.
- Cualquier cambio de contrato debe ser explicitamente versionado.

## 8. Plan de implementacion sugerido (3 iteraciones)
### Iteracion A (estabilizacion)
- Consolidar puertos/adaptadores actuales en webhook.
- Cubrir pruebas negativas faltantes.
- Asegurar `pytest -q` estable independiente del `.env` local.

### Iteracion B (application layer)
- Crear `app/application` y mover casos de uso reutilizables.
- Reusar mismos casos de uso desde API y worker cuando aplique.

### Iteracion C (retiro de legacy)
- Convertir `chatbot_monolith.py` y `telegram_webhook_prod.py` en wrappers finos.
- Definir entrypoints canonicos en `app/api` y `app/webhook`.
- Ajustar compose/deploy para usar solo ruta modular.

## 9. Resultado esperado
Con este enfoque, el bot queda:
- Mas facil de mantener y testear.
- Menos sensible a fallos de infraestructura.
- Listo para evolucionar a arquitectura enterprise real sin ruptura funcional.
- Alineado con tu proyecto actual y su estado real, no con un rediseño teorico desconectado.
