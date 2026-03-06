# ARQUITECTURA_OBJETIVO

## Proposito

Convertir la arquitectura propuesta en [01_arquitecture.md](c:\Users\1973b\zpa\Projects\manufacturing\robot\design\01_arquitecture.md) en un plan de implementacion ejecutable, con fases, entregables, riesgos, pruebas y criterio de salida.

El objetivo operativo es eliminar la intermitencia actual del bot y dejar una unica arquitectura canonica para Telegram:

- un solo runtime por token
- un solo punto de entrada para updates
- separacion clara entre chat y operaciones
- contratos internos estables y testeables

---

## Resultado esperado

Al terminar este plan, el sistema debe operar asi:

- mensajes normales de Telegram -> flujo conversacional
- comandos `/health`, `/logs`, `/e2e`, `/webhookinfo` -> flujo OPS
- ambos flujos entrando por `app.webhook.entrypoint:app`
- sin dependencia operativa de `telegram_adapter.py`
- sin necesidad de correr `app.telegram_ops.entrypoint` en paralelo

---

## Principios de implementacion

1. No introducir un nuevo runtime Telegram fuera del webhook canonico.
2. No romper los contratos HTTP existentes sin tests de contrato.
3. No mover logica de dominio a los entrypoints.
4. Todo cambio de comportamiento en Telegram debe quedar trazado en `ops_events`.
5. Las decisiones de corto plazo deben permitir la opcion futura de dos bots separados.

---

## Estado actual resumido

Hoy existen tres piezas relevantes:

- `app/webhook`: flujo conversacional por webhook
- `app/telegram_ops`: comandos OPS por polling
- `telegram_adapter.py`: flujo legacy conversacional por polling

Problema central:

- el mismo `TELEGRAM_BOT_TOKEN` puede terminar siendo usado por mas de un runtime
- dependiendo de quien reciba el update, el sistema responde mensajes o comandos, pero no ambos de forma consistente

---

## Plan de implementacion

## Fase 0. Congelacion de arquitectura operativa

### Objetivo

Estabilizar el punto de entrada mientras se hace la migracion.

### Cambios

- Declarar `app.webhook.entrypoint:app` como unico ingress canonico de Telegram.
- Marcar `telegram_adapter.py` como legacy/no operativo.
- Marcar `app.telegram_ops.entrypoint.py` como runtime transitorio solo para migracion.
- Documentar que no deben correr en paralelo para el mismo token.

### Entregables

- actualizacion de documentacion operativa
- checklist de arranque canonico

### Riesgos

- seguir arrancando procesos legacy por costumbre

### Pruebas

- verificacion manual de que solo el webhook queda expuesto al bot

### Criterio de salida

- existe una sola ruta de entrada Telegram en operacion

---

## Fase 1. Introducir dispatcher de Telegram

### Objetivo

Mover la clasificacion de updates al webhook y eliminar la dependencia de runtimes paralelos.

### Cambios

Crear:

- `app/telegram/dispatcher.py`
- `app/telegram/models.py`
- `app/telegram/services.py`

Responsabilidades del dispatcher:

1. extraer `chat_id`, `text`, `update_id`
2. clasificar update en:
   - `ops_command`
   - `chat_message`
   - `unsupported`
3. devolver un `DispatchResult`

### Reglas de clasificacion

- `/health`, `/logs`, `/e2e`, `/webhookinfo` -> `ops_command`
- texto normal -> `chat_message`
- updates sin texto -> `unsupported`

### Modulos a tocar

- `app/webhook/handlers.py`
- `app/webhook/entrypoint.py`

### Entregables

- dispatcher reutilizable
- webhook consumiendo dispatcher en vez de decidir inline

### Riesgos

- duplicar logica temporal entre webhook y telegram_ops

### Pruebas

- test unitario del dispatcher
- test del webhook con comando OPS
- test del webhook con mensaje normal
- test con update no soportado

### Criterio de salida

- el webhook ya distingue comandos de mensajes sin usar filtros ad hoc

---

## Fase 2. Extraer servicios de aplicacion

### Objetivo

Separar la logica de chat y de operaciones del transporte Telegram.

### Cambios

Crear:

- `app/ops/checks.py`
- `app/ops/services.py`

Definir servicios:

- `handle_chat_message(chat_id: int, text: str) -> ChatResponse`
- `handle_ops_command(chat_id: int, command: str, args: list[str]) -> OpsResponse`

### Origen de la logica

- mover la logica reusable de `app/telegram_ops/checks.py` a `app/ops/checks.py`
- mover el comportamiento de `/health`, `/logs`, `/e2e`, `/webhookinfo` a `app/ops/services.py`
- dejar `app/telegram_ops/entrypoint.py` como thin wrapper temporal o deprecarlo despues

### Modulos a tocar

- `app/telegram_ops/checks.py`
- `app/telegram_ops/entrypoint.py`
- `app/webhook/handlers.py`
- `app/api/routes.py` si se decide compartir servicios de chat mas explicitamente

### Entregables

- servicio OPS independiente del polling
- servicio de chat reusable desde Telegram ingress

### Riesgos

- dejar comportamiento duplicado entre wrapper viejo y servicio nuevo

### Pruebas

- tests unitarios de `handle_ops_command`
- tests unitarios de `handle_chat_message`
- tests de regresion para `/e2e` y `/logs`

### Criterio de salida

- el webhook puede ejecutar comandos OPS sin depender de `app.telegram_ops.entrypoint.py`

---

## Fase 3. Integrar el dispatcher con los servicios

### Objetivo

Completar el flujo final:

- webhook -> dispatcher -> servicio correcto -> respuesta Telegram

### Cambios

Refactorizar `app/webhook/handlers.py` para que:

- deje de llamar directamente al chat API para toda clase de texto
- invoque el dispatcher primero
- use `handle_chat_message` para mensajes conversacionales
- use `handle_ops_command` para comandos OPS

### Decision tecnica

El webhook debe seguir siendo el adaptador de entrada.
No debe convertirse en un lugar de negocio.

### Entregables

- `process_update_impl` simplificado
- despacho unificado de comandos y mensajes

### Riesgos

- romper los contratos actuales del webhook al cambiar demasiado de una vez

### Pruebas

- `POST /webhook/{token}` con texto normal -> respuesta conversacional
- `POST /webhook/{token}` con `/logs` -> respuesta OPS
- `POST /webhook/{token}` con `/e2e` -> respuesta OPS
- `POST /webhook/{token}` con update repetido -> dedup mantiene contrato

### Criterio de salida

- un mismo runtime webhook responde tanto chat como OPS

---

## Fase 4. Deprecar runtimes legacy

### Objetivo

Eliminar competencia de procesos y reducir ambiguedad operacional.

### Cambios

- deprecar `telegram_adapter.py`
- retirar `app/telegram_ops/entrypoint.py` del flujo normal
- actualizar runbooks, scripts y docs
- limpiar referencias en documentos que promuevan polling como camino principal

### Entregables

- inventario de componentes legacy
- runbook actualizado

### Riesgos

- dejar scripts o docs apuntando al camino viejo

### Pruebas

- smoke test de arranque usando solo:
  - API
  - webhook
  - worker opcional

### Criterio de salida

- no queda ningun flujo operativo recomendado que dependa de polling legacy

---

## Fase 5. Endurecimiento de contratos y observabilidad

### Objetivo

Cerrar la arquitectura con observabilidad y contratos estables.

### Cambios

- consolidar contratos en tests de contrato
- agregar eventos operativos para:
  - `telegram.dispatch.chat`
  - `telegram.dispatch.ops`
  - `telegram.dispatch.unsupported`
  - `ops.command.completed`
  - `ops.command.failed`
- revisar `app/config/settings.py` para evitar settings dispersos restantes

### Entregables

- suite de tests mas completa
- trazabilidad completa del flujo Telegram

### Riesgos

- dejar huecos de observabilidad en los nuevos caminos

### Pruebas

- tests de contrato webhook
- tests de regresion de eventos `ops_events`
- tests de fallo de API/chat/telegram send

### Criterio de salida

- cualquier fallo funcional puede rastrearse desde logs operativos

---

## Fase 6. Separacion opcional en dos bots

### Objetivo

Dejar preparada la evolucion a dos tokens si la operacion lo requiere.

### Cambios

- introducir soporte explicito para:
  - `TELEGRAM_CHATBOT_TOKEN`
  - `TELEGRAM_OPS_TOKEN`
- aislar configuracion y handlers por bot
- decidir si el bot OPS sigue en el mismo webhook o pasa a otro ingress

### Regla

Esta fase no es obligatoria para estabilizar el sistema.
Es una optimizacion de aislamiento operativo.

### Entregables

- decision documentada
- configuracion preparada

### Criterio de salida

- el sistema puede operar con uno o dos bots sin rediseñar dominio

---

## Orden recomendado de ejecucion

1. Fase 0
2. Fase 1
3. Fase 2
4. Fase 3
5. Fase 4
6. Fase 5
7. Fase 6

Motivo:

- primero se estabiliza el ingress
- luego se introduce el dispatcher
- despues se desacopla la logica
- recien al final se elimina lo legacy

---

## Backlog tecnico por archivo

### Crear

- `app/telegram/dispatcher.py`
- `app/telegram/models.py`
- `app/telegram/services.py`
- `app/ops/checks.py`
- `app/ops/services.py`

### Refactorizar

- `app/webhook/handlers.py`
- `app/webhook/entrypoint.py`
- `app/telegram_ops/checks.py`
- `app/telegram_ops/entrypoint.py`
- `app/config/settings.py`

### Deprecar

- `telegram_adapter.py`

### Documentacion a actualizar

- `estructura.md`
- `TELEGRAM_E2E_LOG_APP.md`
- `design/architecture.md`
- `design/contratos.md`

---

## Suite minima de pruebas por fase

### Unitarias

- dispatcher clasifica bien comandos y mensajes
- servicio OPS responde segun comando
- servicio chat devuelve respuesta estructurada

### Contrato

- webhook token valido
- webhook token invalido
- webhook dedup
- webhook comando OPS
- webhook mensaje normal

### Integracion local

- mensaje normal desde Telegram -> respuesta chat
- `/logs` -> respuesta operativa
- `/e2e` -> ejecucion completa

### Regresion

- ningun comando se responde con el `brain`
- ningun mensaje normal se pierde por dispatcher
- no aparecen runtimes competidores usando el mismo token

---

## Definition of Done

La arquitectura objetivo se considera implementada cuando:

1. `app.webhook.entrypoint:app` es el unico ingress Telegram en uso.
2. El webhook ejecuta chat y OPS desde el mismo runtime.
3. `telegram_adapter.py` deja de ser necesario para operar.
4. `app.telegram_ops.entrypoint.py` deja de ser necesario como proceso paralelo.
5. Existen tests de contrato y unitarios para ambos flujos.
6. La documentacion operativa y de arquitectura refleja el estado real del sistema.

---

## Recomendacion de inicio

El primer bloque a implementar debe ser:

- Fase 1
- Fase 2
- Fase 3

Porque ese bloque ya elimina el problema estructural principal sin esperar a una separacion futura de bots.
