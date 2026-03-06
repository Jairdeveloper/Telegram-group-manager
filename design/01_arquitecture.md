# 01_arquitecture

## Objetivo

Definir la arquitectura objetivo del proyecto a partir del estado real del codigo y de los fallos observados en operacion:

- competencia entre runtimes con el mismo `TELEGRAM_BOT_TOKEN`
- mezcla de responsabilidades entre webhook conversacional y bot OPS
- coexistencia de flujos legacy y modulares
- intermitencia funcional segun que proceso reciba el update

La arquitectura propuesta prioriza:

1. una sola ruta de entrada por responsabilidad
2. un solo runtime por token de Telegram
3. contratos internos estables
4. modularidad antes de separar en microservicios fisicos

---

## Evaluacion del estado actual

### Lo que esta bien

- La API modular ya existe en `app/api`.
- El webhook modular ya existe en `app/webhook`.
- El dominio conversacional esta relativamente aislado en `chat_service`.
- Existen tests de contrato y unitarios para API y webhook.
- La configuracion base esta razonablemente centralizada en `app/config/settings.py`.

### Lo que hoy rompe la operacion

- Hay varios runtimes activos para Telegram:
  - `app/webhook`
  - `app/telegram_ops`
  - `telegram_adapter.py`
- No todos procesan el mismo tipo de update.
- Se reutiliza el mismo `TELEGRAM_BOT_TOKEN` para funciones distintas.
- El polling legacy y el webhook compiten por el control del bot.
- El bot OPS es un runtime separado, no integrado en el flujo canonico de entrada.

### Diagnostico arquitectonico

El proyecto no tiene un bug central de negocio.

El problema principal es de arquitectura operacional:

- demasiados entrypoints para un mismo canal
- separacion incompleta entre chatbot y operaciones
- responsabilidades cruzadas sobre el mismo bot

En resumen: el sistema esta modularizado, pero todavia no esta unificado.

---

## Decision arquitectonica

### Modelo elegido

Adoptar un modelo de **monolito modular con entrypoints canonicos y bounded contexts internos**, sin polling legacy en produccion.

Esto significa:

- un solo repositorio
- un solo dominio conversacional
- una sola API interna de chat
- un solo webhook canonico para mensajes conversacionales
- un canal OPS claramente separado

### Regla fundamental

**Un token de Telegram no puede ser atendido por mas de un runtime.**

---

## Arquitectura objetivo

## 1. Bounded contexts

### A. Chat Application

Responsabilidad:

- exponer la API de conversacion
- orquestar el dominio de chat
- persistir historial

Modulos:

- `app/api`
- `chat_service`

Contrato principal:

- `POST /api/v1/chat`

### B. Telegram Ingress

Responsabilidad:

- recibir updates de Telegram
- validar token y deduplicar
- clasificar el update
- despachar al flujo correcto

Modulos:

- `app/webhook`

Regla:

- este es el unico punto canonico de entrada desde Telegram para produccion

### C. Operations / Diagnostics

Responsabilidad:

- health checks
- e2e
- logs
- diagnostico operativo

Modulos:

- `app/ops`
- `app/telegram_ops/checks.py`

Regla:

- la logica OPS no debe vivir como bot aparte si comparte token con el chatbot
- debe exponerse como servicios internos reutilizables

### D. Worker / Async Processing

Responsabilidad:

- procesamiento diferido
- colas
- reintentos internos

Modulos:

- `worker.py`
- `webhook_tasks.py`

Regla:

- es un detalle de infraestructura, no un segundo punto de entrada

---

## 2. Entry points canonicos

### Canonicos

- `app.api.entrypoint:app`
- `app.webhook.entrypoint:app`
- `worker.py`

### A deprecar

- `telegram_adapter.py`
- cualquier runtime polling para el mismo token de produccion
- cualquier modulo legacy duplicado bajo `telegram_ops/` raiz si no es el canonico

---

## 3. Modelo de flujo de datos objetivo

### Flujo conversacional

```text
Telegram
  -> Webhook canonico
  -> Telegram ingress dispatcher
  -> Chat application service
  -> Agent / Brain / Storage
  -> Telegram sendMessage
```

### Flujo OPS

```text
Telegram comando /health /logs /e2e
  -> Webhook canonico
  -> Telegram ingress dispatcher
  -> Ops application service
  -> checks / event store / diagnostics
  -> Telegram sendMessage
```

### Flujo async

```text
Webhook canonico
  -> enqueue opcional
  -> worker
  -> chat service
  -> Telegram sendMessage
```

---

## 4. Dispatcher de Telegram

La pieza que falta hoy es un dispatcher explicito dentro del webhook.

### Responsabilidad del dispatcher

Dado un update Telegram:

1. validar token
2. deduplicar
3. extraer `chat_id`, `text`, `update_id`
4. clasificar:
   - comando OPS
   - mensaje conversacional
   - update no soportado
5. despachar al handler correcto

### Clasificacion minima

- si `text` empieza por `/` y pertenece a:
  - `/health`
  - `/logs`
  - `/e2e`
  - `/webhookinfo`
  entonces va a OPS

- si `text` no empieza por `/`, va a chat

- si el update no contiene texto, se ignora o se registra

### Regla clave

Los comandos no se ignoran.
Los comandos se despachan.

El filtro actual que solo ignora `/...` corrige el bug inmediato, pero no resuelve la arquitectura final.

---

## 5. Contratos internos objetivo

## Telegram ingress service

Interfaz propuesta:

```python
dispatch_telegram_update(update: dict) -> DispatchResult
```

Donde `DispatchResult` debe indicar:

- tipo de flujo ejecutado
- status
- respuesta generada
- metadata operativa

## Chat application service

Interfaz propuesta:

```python
handle_chat_message(chat_id: int, text: str) -> ChatResponse
```

Responsabilidades:

- construir `session_id`
- llamar a `agent.process`
- persistir historial
- devolver respuesta estructurada

## Ops application service

Interfaz propuesta:

```python
handle_ops_command(chat_id: int, command: str, args: list[str]) -> OpsResponse
```

Responsabilidades:

- auth de admin
- rate limiting
- ejecutar checks
- consultar logs
- construir respuesta

---

## 6. Estructura objetivo del codigo

```text
app/
  api/
  config/
  ops/
    services.py
    events.py
    checks.py
  telegram/
    dispatcher.py
    models.py
    services.py
  webhook/
    entrypoint.py
    bootstrap.py
    handlers.py
    infrastructure.py
    ports.py
chat_service/
  agent.py
  brain.py
  pattern_engine.py
  storage.py
```

### Ajustes sobre el estado actual

- mover la logica de `app/telegram_ops/checks.py` hacia `app/ops/checks.py`
- eliminar el bot OPS como runtime independiente si comparte token
- convertir `app/telegram_ops/entrypoint.py` en logica reutilizable o retirarlo
- introducir `app/telegram/dispatcher.py` como punto unico de clasificacion

---

## 7. Politica de tokens

Hay dos opciones validas.

### Opcion A. Un solo bot

Uso:

- un unico token
- un unico webhook
- dispatcher interno que separa chat y comandos

Ventajas:

- operacion simple
- una sola URL webhook
- una sola identidad de bot

Desventajas:

- mezcla funcional en el mismo bot

### Opcion B. Dos bots separados

Uso:

- bot conversacional con su token
- bot OPS con otro token

Ventajas:

- aislamiento total
- menos riesgo de colision de responsabilidades

Desventajas:

- mas configuracion
- dos identidades en Telegram

### Decision recomendada

Para este proyecto, la opcion recomendada es:

**dos bots separados en mediano plazo**.

Mientras tanto, en corto plazo:

**un solo webhook canonico con dispatcher interno**.

---

## 8. Reglas de evolucion

1. Ningun nuevo flujo Telegram debe nacer fuera del webhook canonico.
2. Ningun comando OPS debe depender de polling si el sistema opera por webhook.
3. Ningun modulo de dominio debe llamar directamente a `requests` o `httpx` sin pasar por un adapter.
4. Los contratos HTTP y de modulo deben mantenerse versionados por tests.
5. Todo comportamiento nuevo de Telegram debe quedar observable en `ops_events`.

---

## 9. Roadmap de implementacion

### Fase A. Estabilizacion

- mantener `app.webhook.entrypoint` como unica entrada Telegram
- retirar `telegram_adapter.py` del flujo operativo
- evitar usar `app.telegram_ops.entrypoint` en paralelo con webhook

### Fase B. Unificacion de comando y chat

- crear `app/telegram/dispatcher.py`
- mover comandos OPS a servicios internos
- despachar `/health`, `/logs`, `/e2e`, `/webhookinfo` desde webhook

### Fase C. Limpieza estructural

- deprecar runtime `app/telegram_ops/entrypoint.py`
- mover checks OPS a `app/ops`
- documentar nuevos contratos

### Fase D. Separacion opcional

- si la operacion lo exige, separar bot conversacional y bot OPS en tokens distintos

---

## 10. Decision final

La arquitectura que usaremos sera:

**monolito modular con un webhook canonico, dispatcher de Telegram interno, servicios de chat y OPS separados por contexto, y sin runtimes competidores para un mismo token**.

Esto resuelve el problema real del sistema:

- elimina la intermitencia causada por multiples entrypoints
- mantiene modularidad y simplicidad operativa
- permite evolucionar a dos bots o a servicios mas separados sin rehacer el dominio

---

## 11. Estado deseado de operacion

En estado estable, el sistema debe comportarse asi:

- mensajes normales -> respuesta conversacional
- `/health` -> estado operativo
- `/logs` -> eventos recientes
- `/e2e` -> checks estructurados
- todo entrando por el mismo webhook canonico
- sin necesidad de `telegram_adapter.py`
- sin necesidad de arrancar un bot OPS paralelo para el mismo token
