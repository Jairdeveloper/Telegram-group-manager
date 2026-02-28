Objetivo del día

Cerrar Semana 1: CI con pytest obligatorio y bloqueo de merge en rojo.
Avanzar Semana 2: iniciar extracción modular app/api y app/webhook sin romper contrato actual.
Asunción clave
En tu documento, “Semana 2” viene como “Semana 2-3” (extracción modular). Hoy atacamos la parte crítica de esa extracción.

Plan de ejecución (hoy, en bloques)
Bloque 1 (60-90 min): Baseline y seguridad

Verificar que local está verde: pytest -q.
Congelar estado actual: branch dedicada refactor/week1-week2.
Definir DoD de hoy:
CI corre tests en PR.
Merge bloqueado si falla.
app/api y app/webhook creados con rutas operativas o wrappers.
Bloque 2 (90 min): Semana 1 - CI obligatorio

Crear workflow CI (GitHub Actions o tu CI actual) con:
Python setup
install deps
pytest -q
Activar protección de rama:
Required status checks: job de tests
Require PR para merge
Entregable: PR que falle si rompes un test.
Bloque 3 (120 min): Semana 2 - extracción mínima API/Webhook

Crear estructura:
app/api/... (router /api/v1/chat)
app/webhook/... (ingress /webhook/{token})
Mover lógica por capas sin cambiar comportamiento:
monolito llama a módulos nuevos (adapter/facade)
Mantener compatibilidad de contratos existentes (tests actuales).
Bloque 4 (60 min): Pruebas de no regresión

Ejecutar pytest -q.
Añadir tests puntuales si falta cobertura en módulos nuevos.
Validar dedup/token webhook y contrato /api/v1/chat.
Bloque 5 (45 min): Cierre técnico

Documentar en README:
cómo correr tests
cómo corre CI
nueva estructura modular
Abrir PR con checklist DoD y riesgos pendientes.
Criterio de “terminado hoy”
CI obligatorio activo y bloqueando merge si tests fallan.
API/Webhook ya desacoplados a app/api y app/webhook (aunque sea primer corte).
Suite pytest en verde local + CI.
Documento corto de migración y siguientes pasos de Semana 2-3.
Si quieres, en el siguiente paso te preparo el checklist exacto de PRs (PR1 CI, PR2 refactor modular) con archivos esperados por cada PR.