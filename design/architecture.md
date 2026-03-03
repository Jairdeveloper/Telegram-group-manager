Arquitectura actual (as-is): monolito en transicion a modular API/Webhook

Resumen de evaluacion
- El proyecto ya no es un monolito puro: existe extraccion modular en `app/api` y `app/webhook`.
- La ejecucion sigue en modo "compatibilidad": entrypoints legacy (`chatbot_monolith.py`, `telegram_webhook_prod.py`) exponen runtime y delegan parte de la logica a modulos nuevos.
- No hay separacion real en microservicios independientes aun (no hay bounded contexts desplegados por separado con contratos versionados entre servicios).

Topologia actual
- Capa API:
  - `app/api/factory.py`: crea FastAPI app y middleware CORS.
  - `app/api/routes.py`: contratos HTTP de chat, history y stats.
  - `chatbot_monolith.py`: wrapper/entrypoint que construye actor/storage y delega en `app/api`.
- Capa Webhook:
  - `telegram_webhook_prod.py`: adapter FastAPI + wiring de env, Redis/RQ, metrics.
  - `app/webhook/handlers.py`: logica de negocio de token, dedup, procesamiento sync y encolado.
  - `app/webhook/entrypoint.py`: wrapper para exponer app desde modulo nuevo.
- Capa dominio conversacional:
  - `chat_service/agent.py` y `chat_service/pattern_engine.py`.
  - `chatbot_monolith.py` mantiene logica adicional historica (LLM fallback y storage simple JSON).
- Infraestructura operativa:
  - Redis/RQ opcional para procesamiento async de webhook.
  - `worker.py` para RQ worker.
  - Prometheus metrics en webhook (`/metrics`).

Estado de madurez por componente
- API modular: funcional y testeada por contrato.
- Webhook modular: funcional, con handlers extraidos y contratos cubiertos.
- Configuracion: aun distribuida en varios archivos via `os.getenv`.
- Infra interfaces: acoplamiento directo a `requests`, `redis`, `rq` en adapters actuales.
- Legacy retirement: pendiente, aun hay entrypoints legacy activos.

Desviaciones entre arquitectura objetivo y arquitectura real
- Objetivo documento previo: microservicios API-first completos.
- Real hoy:
  - Modularizacion interna dentro de un mismo runtime/repositorio.
  - Sin servicio de embeddings desacoplado.
  - Sin storage principal Postgres en flujo productivo actual (se usa JSON simple en parte del flujo).
  - LLM orchestrator existe conceptualmente en monolito, no como servicio/modulo estable independiente.

Decision arquitectonica vigente
- Mantener estrategia "modular first" antes de separar microservicios.
- Consolidar contratos y capas internas (config + puertos/adaptadores) como prerequisito para futura separacion fisica de servicios.

Riesgos actuales
- Config dispersa: mayor probabilidad de drift de variables y defaults.
- Acoplamiento a infraestructura: tests mas friccionados y menor reemplazo de proveedores.
- Duplicidad/arrastre legacy: riesgo de divergencia de comportamiento entre rutas viejas y nuevas.

Plan de evolucion recomendado (corto plazo)
1. Centralizar settings en `app/config`.
2. Introducir puertos/adaptadores para `requests`/`redis`/`rq`.
3. Completar pruebas negativas de webhook.
4. Definir y ejecutar deprecacion por fases de entrypoints legacy.
