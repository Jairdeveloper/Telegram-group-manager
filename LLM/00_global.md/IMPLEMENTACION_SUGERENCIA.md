Voy a ejecutar esto en dos frentes: 1) implementar ahora mismo la base de pruebas real con pytest (unitarias + API + contrato webhook), y 2) dejar una dirección arquitectónica única para evolución SaaS/agente autónomo, con roadmap ejecutable. Primero reviso el estado de testing y luego edito archivos.

***veriica que Tengas contexto suficiente para ejecutar el Plan de implementación:***

**Crear suite pytest con 3 capas:**
Unit: chat_service (PatternEngine, Agent).
API: endpoint /api/v1/chat del monolito con TestClient.
Webhook contract: validación de token, deduplicación y ruta ingress (/webhook/{token}).
Corregir inconsistencias que hoy rompen calidad:
Import inválido en test_monolith.py.
Configuración de ingress (rewrite-target) y agregar test de regresión para esa regla.
Dejar base de ejecución de pruebas:
pytest.ini, tests/, fixtures y monkeypatch para evitar red externa.
Mantener scripts demo opcionales, pero removerlos del camino de validación principal.
Empiezo a editar archivos ahora.

Voy a introducir pytest y refactor mínimo del monolito para exponer una app testeable sin levantar uvicorn; así cubrimos unit, API y contrato webhook de forma automatizada.

Estoy añadiendo ahora tests de contrato para webhook y una regresión explícita para el manifiesto Ingress, para bloquear el bug de rewrite-target en CI antes de desplegar.

Voy a corregir también el import roto del script legado test_monolith.py para que no quede deuda visible en el repo, aunque la validación oficial ya quedará en pytest.

Estoy ejecutando la suite para validar que los cambios realmente cierran el objetivo (unit + API + webhook + regresión ingress) y ajustar cualquier fallo residual.

La suite ya pasa completa (10 tests). Voy a cerrar con resumen ejecutable: cambios concretos, dirección arquitectónica única y roadmap técnico con foco SaaS/agente autónomo, sin ambigüedad.

Implementé el aspecto de calidad y pruebas completo, y fijé una dirección técnica única.

Cambios ejecutados

Suite pytest real creada (10 tests) con cobertura por capas:
Unitarias de motor híbrido: tests/test_agent_unit.py, tests/test_pattern_engine_unit.py
Contrato API /api/v1/chat: tests/test_api_contract.py
Contrato webhook (token, dedup, procesamiento): tests/test_webhook_contract.py
Regresión Ingress (rewrite-target): tests/test_ingress_regression.py
Refactor mínimo para testear API sin levantar servidor:
Nueva fábrica de app: chatbot_monolith.py:535
run_api() ahora consume la fábrica: chatbot_monolith.py:603
Correcciones de regresión:
Ingress corregido a /$1: deploy/webhook-deployment.yaml:77, deploy/telegram-webhook-deploy.yaml:67
Import roto del script demo corregido: test_monolith.py:19
Base de ejecución de pruebas:
Config pytest: pytest.ini
Bootstrap de imports de proyecto: tests/conftest.py
Dependencia agregada: requirements.txt:16
Resultado verificado
pytest -q ejecutado con éxito: 10 passed.

Arquitectura final elegida (decisión única)
Adoptar una arquitectura modular API-first con núcleo conversacional como librería (chat_service), borde de entrada webhook stateless, procesamiento asíncrono por cola, persistencia en Postgres+Redis y orquestación LLM desacoplada para evolución a agente autónomo.

Stack técnico

Backend: Python 3.11, FastAPI, Uvicorn.
Núcleo IA: motor reglas (PatternEngine/Agent) + orquestador LLM (OpenAI/Ollama).
Asíncrono: Redis + RQ (migrable a Celery/Kafka según escala).
Datos: Postgres (histórico/tenant), Redis (estado corto, dedup, rate limits).
Infra: Docker, Kubernetes, NGINX Ingress, cert-manager.
Calidad: pytest, CI (lint+tests+contract tests).
Diagrama conceptual (texto)
Telegram -> Ingress HTTPS -> Webhook FastAPI -> Queue(Redis/RQ) -> Worker -> Chat Service (Reglas + LLM Orchestrator) -> Postgres/Redis -> Telegram sendMessage

**Roadmap técnico**

Semana 1: consolidar test suite en CI, bloquear merge sin green tests.
Semana 2-3: extraer API y webhook a paquetes app/api, app/webhook; eliminar acoplamiento monolítico.
Semana 4-5: migrar storage JSON a Postgres + repositorio por tenant.
Semana 6-8: policy engine + planner básico (tool routing, guardrails, budgets).
Semana 9-12: multi-tenant enterprise (auth, quotas, auditoría, observabilidad completa).
Riesgos técnicos

Deriva de complejidad por mantener monolito+modular en paralelo.
Coste LLM sin gobernanza por tenant.
Duplicación de eventos si falla deduplicación distribuida.
Latencia de respuesta en picos sin backpressure.
Ventajas competitivas

Respuestas robustas y controlables por enfoque híbrido reglas+LLM.
Coste predecible por degradación elegante a reglas/local LLM.
Camino claro a agente autónomo sin reescritura total.
Capacidad enterprise (auditoría, seguridad, multi-tenant) desde diseño.
Coste estimado

MVP productivo: bajo-medio.
Escala startup (primeros clientes): medio.
Enterprise multi-tenant con SLO fuertes: medio-alto.
La curva de coste queda controlable al priorizar reglas/local inference y colas asíncronas.
Escalabilidad
Escala horizontal en webhook/worker; estado fuera del proceso; particionamiento por tenant; evolución progresiva de RQ a bus de eventos cuando se requiera.

Nivel de complejidad
Medio al inicio, alto al entrar en modo enterprise. Complejidad justificada por retorno en resiliencia, diferenciación y velocidad de iteración.

Conclusión única final
La estrategia óptima es consolidar ya la base de calidad con pruebas de contrato obligatorias (ya implementada), y ejecutar una migración controlada hacia arquitectura modular API-first con núcleo híbrido reusable y procesamiento asíncrono state-externalized; esta ruta maximiza escalabilidad, diferenciación y evolución a agente autónomo con el menor riesgo de reescritura futura.

Siguiente paso inmediato: integro CI para ejecutar esta suite en cada PR y bloquear merges sin pytest en verde.