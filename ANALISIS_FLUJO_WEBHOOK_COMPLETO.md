# ANÁLISIS EXHAUSTIVO: FLUJO DE MENSAJE TELEGRAM DESDE WEBHOOK

## MAPA GENERAL DEL FLUJO
```
POST /webhook/{token}
    ↓
handle_webhook_impl() [entrypoint.py líneas 809-918]
    ↓
Token validation + JSON parsing
    ↓
dedup_update() - Deduplicación  [handlers.py líneas 73-80]
    ↓
process_async ? enqueue : process_update_impl()
    ↓
process_update_impl() [handlers.py líneas 82-777]
    ↓
Route dispatch → handle_chat_message_fn()
    ↓
telegram_client.send_message()
```

---

## 1️⃣ ENTRYPOINT WEBHOOK: `handle_webhook_impl()`

**Ubicación:** `app/webhook/handlers.py` líneas 809-918

### 1.1 Validación del Token

```python
# Líneas 819-830
if webhook_token is not None:
    if token != webhook_token:
        requests_metric.labels(status="forbidden").inc()
        record_event(component="webhook", event="webhook.forbidden", ...)
        raise HTTPException(status_code=403, detail="Invalid token")
else:
    if token != bot_token:
        requests_metric.labels(status="forbidden").inc()
        record_event(component="webhook", event="webhook.forbidden", ...)
        raise HTTPException(status_code=403, detail="Invalid token")
```

**🔴 PROBLEMAS IDENTIFICADOS:**
- ✅ Los 403 están correctamente lanzados
- ✅ El logging está presente
- ✅ La métrica se incrementa

### 1.2 Parsing del JSON

```python
# Líneas 832-864
update = None
body = None
if hasattr(request, "body"):
    try:
        body = await request.body()
    except Exception:
        body = None

if body is not None:
    # Intenta PTB handler primero
    if ptb_webhook_handler is not None and hasattr(ptb_webhook_handler, "to_internal"):
        update = ptb_webhook_handler.to_internal(body)
    
    if not update:
        try:
            update = json.loads(body)
        except Exception:
            logger.exception("webhook.invalid_json")
            requests_metric.labels(status="invalid").inc()
            return {"ok": True}  # ✅ Retorno seguro
else:
    try:
        update = await request.json()
    except Exception:
        logger.exception("webhook.invalid_json")
        requests_metric.labels(status="invalid").inc()
        return {"ok": True}  # ✅ Retorno seguro
```

**🟢 ESTADO:** Correcto. Si JSON es inválido, retorna `{"ok": True}` a Telegram

---

## 2️⃣ ROUTING INICIAL: Deduplicación y Enqueue

**Ubicación:** `app/webhook/handlers.py` líneas 865-913

### 2.1 Deduplicación

```python
# Líneas 865-873
update_id = update.get("update_id")
payload = extract_chat_payload(update)
chat_id = payload[0] if payload else None

record_event(
    component="webhook",
    event="webhook.received",
    update_id=update_id,
    chat_id=chat_id,
    process_async=process_async,
)

if update_id is not None and not dedup_update(update_id):
    logger.info("webhook.duplicate_update", extra=log_ctx)
    record_event(component="webhook", event="webhook.dedup.duplicate", ...)
    requests_metric.labels(status="duplicate").inc()
    return {"ok": True}  # ✅ Dedup correcto
```

**🟢 ESTADO:** Correcto. Duplicados se rechazan sin procesar.

### 2.2 Async vs Sync Processing

```python
# Líneas 876-913
try:
    async def _run_processor() -> None:
        result = process_update_sync(update)
        if inspect.isawaitable(result):
            await result

    if process_async and task_queue is not None:
        try:
            job_id = task_queue.enqueue_process_update(update=update)
            logger.info("webhook.enqueued_update", extra={**log_ctx, "job_id": job_id})
            record_event(..., job_id=job_id)
        except Exception:
            # 🟢 FALLBACK A SYNC SI REDIS/QUEUE FALLA
            logger.exception("webhook.enqueue_failed", extra=log_ctx)
            logger.warning("webhook.fallback_sync_after_enqueue_failure", extra=log_ctx)
            await _run_processor()
    elif process_async and task_queue is None:
        logger.warning("webhook.async_queue_unavailable", extra=log_ctx)
        logger.warning("webhook.fallback_sync_after_queue_unavailable", extra=log_ctx)
        await _run_processor()  # ✅ FALLBACK TIENE SENTIDO
        await _run_processor()  # 🔴 BUG: DOBLE LLAMADA A _run_processor()
    else:
        await _run_processor()
```

**🔴 CRÍTICO BUG ENCONTRADO:**
```python
# Línea 909-910
await _run_processor()  # Primera llamada
await _run_processor()  # SEGUNDA LLAMADA - BUG
```

**EFECTO**: Si `process_async=True` pero `task_queue=None`, el update se procesa **DOS VECES**. Esto causaría dos respuestas enviadas.

### 2.3 Try/Except Principal

```python
# Líneas 876-918
try:
    # ... procesamiento ...
    requests_metric.labels(status="ok").inc()
    return {"ok": True}
except Exception:
    logger.exception("webhook.handle_error", extra=log_ctx)
    record_event(component="webhook", event="webhook.handle_error", ...)
    requests_metric.labels(status="error").inc()
    return {"ok": True}  # ✅ Siempre retorna OK a Telegram
```

**🟢 ESTADO:** El try/except está bien, pero es DEMASIADO AMPLIO. Oculta errores completos.

---

## 3️⃣ PROCESS UPDATE IMPL: El Corazón del Flujo

**Ubicación:** `app/webhook/handlers.py` líneas 82-777

### 3.1 Inicialización de Variables

```python
# Línealículas 82-177
async def process_update_impl(
    update: Dict[str, Any],
    *,
    telegram_client: TelegramClient,
    logger,
    process_time_metric=None,
    chat_api_error_metric=None,
    telegram_send_error_metric=None,
    handle_chat_message_fn: Callable[..., Dict[str, Any]] = handle_chat_message,
    handle_ops_command_fn: Callable[..., Any] = handle_ops_command,
    handle_enterprise_command_fn: Callable[..., Any] = handle_enterprise_command,
    handle_enterprise_moderation_fn: Callable[..., Any] = handle_enterprise_moderation,
    is_admin_fn: Callable[[int], bool] = is_admin,
    rate_limit_check: Callable[[int], Any] = check_rate_limit,
) -> None:
    """Process update by dispatching chat and OPS commands via application services."""
    start = time.time()
    
    # Parsing del update
    if update.get("callback_query"):
        dispatch = dispatch_telegram_update(update)
    else:
        router = _get_manager_bot_router()
        dispatch = router.route_update(update).to_legacy_dispatch()
    
    update_id = dispatch.update_id
    chat_id = dispatch.chat_id
    log_ctx = {"update_id": update_id, "chat_id": chat_id}
    menu_to_show: Optional[str] = None
    reply: Optional[str] = None  # ✅ INICIALIZADO AQUÍ - CRÍTICO
```

**🟢 ESTADO:** `reply` IS INICIALIZADO a `None` en línea 106. Esto previene `NameError`.

### 3.2 Dispatch Handling: Early Returns

```python
# Líneas 108-135
if dispatch.kind == "unsupported":
    logger.info("webhook.unsupported_update", extra=log_ctx)
    record_event(...)
    return  # ✅ Early return - no envía nada
```

**🟢 ESTADO:** Para unsupported updates, retorna sin enviar mensaje.

### 3.3 Callback Query Handling

```python
# Líneas 193-239
if dispatch.kind == "callback_query":
    menu_engine = get_menu_engine()
    rate_limiter = get_rate_limiter()
    
    # Rate limit check
    if rate_limiter and not rate_limiter.is_allowed(user_id, "callback"):
        # ... answer callback and return
        return  # ✅ Sin set de reply
    
    if menu_engine and callback_data:
        await menu_engine.handle_callback_query_raw(...)
    else:
        # ... answer callback
    
    record_event(...)
    return  # ✅ Early return - no continúa a section chat_message
```

**🟢 ESTADO:** Callback queries tienen su propio flujo y return antes de llegar a la sección de chat_message. No interfiere.

### 3.4 Chat Message / Agent Task Main Logic

```python
# Línea 241: Inicio del bloque principal
if dispatch.kind in ("chat_message", "agent_task"):
    # AQUÍ OCURRE LA MAGIA...
```

---

## 4️⃣ HANDLE_CHAT_MESSAGE_FN: Donde se Genera la Respuesta

**Ubicación:** `app/ops/services.py` líneas 25-70

### 4.1 Estructura de la Función

```python
def handle_chat_message(chat_id: int, text: str, *, agent=None, storage=None) -> Dict[str, Any]:
    """Process a chat message using the chatbot domain service."""
    try:
        runtime = None
        if agent is None or storage is None:
            runtime = _get_default_api_runtime()
        agent = agent or runtime.agent
        storage = storage or runtime.storage

        session_id = str(chat_id)
        response = agent.process(text)
        
        # 🟢 VALIDACIÓN AGREGADA: Verifica si response es None
        if response is None:
            logger.error(f"Agent returned None for text: {text}")
            return {
                "chat_id": chat_id,
                "session_id": str(chat_id),
                "message": text,
                "response": "No se pudo procesar el mensaje.",  # ✅ Fallback
                "confidence": 0.0,
                "source": "error",
                "pattern_matched": False,
            }
        
        storage.save(session_id, text, response.text)

        return {
            "chat_id": chat_id,
            "session_id": session_id,
            "message": text,
            "response": response.text,
            "confidence": response.confidence,
            "source": response.source,
            "pattern_matched": response.pattern_matched,
        }
    except Exception as e:
        import traceback
        logger.error(f"🔴 CRITICAL ERROR in handle_chat_message: {type(e).__name__}: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        logger.error(f"Chat ID: {chat_id}, Text: {text}")
        return {
            "chat_id": chat_id,
            "session_id": str(chat_id),
            "message": text,
            "response": "Ocurrió un error procesando tu mensaje. Por favor intenta de nuevo.",
            "confidence": 0.0,
            "source": "error",
            "pattern_matched": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }
```

**🟢 ESTADO:** 
- ✅ `response` is validado (no None)
- ✅ Exception handling con fallback
- ✅ Siempre retorna Dict con key `"response"`

### 4.2 Cómo se Usa en handlers.py

```python
# Línea 640-654 (Fallback cuando NLP falla)
result = handle_chat_message_fn(chat_id, text)
if result and isinstance(result, dict):
    reply = result.get("response", "(no response)")
else:
    reply = "(no response)"
    logger.warning(f"Invalid result from handle_chat_message_fn: {result}")
```

**🟢 ESTADO:** 
- ✅ Valida que result es dict
- ✅ Usa `.get("response", ...)` con fallback
- ✅ Registra si result es inválido

---

## 5️⃣ TELEGRAM.SEND_MESSAGE(): Envío de la Respuesta

**Ubicación 1:** `app/webhook/handlers.py` líneas 759-770
**Ubicación 2:** `app/webhook/infrastructure.py` líneas 29-35

### 5.1 Dónde Se Llama

```python
# Línea 759-770 [handlers.py]
logger.info(f"About to send reply: {reply!r}")
try:
    await _maybe_await(telegram_client.send_message(chat_id=chat_id, text=reply))
    record_event(
        component="webhook",
        event="webhook.telegram_send.ok",
        update_id=update_id,
        chat_id=chat_id,
    )
except Exception:
    logger.exception("webhook.telegram_send_error", extra=log_ctx)
    record_event(
        component="webhook",
        event="webhook.telegram_send.error",
        level="ERROR",
        update_id=update_id,
        chat_id=chat_id,
    )
    if telegram_send_error_metric is not None:
        telegram_send_error_metric.inc()
```

**🟡 PROBLEMA IDENTIFICADO:**
- Si `send_message()` lanza exception, se registra pero NO se relanza
- Telegram nunca sabe que hubo un problema (webhook ya retornó {"ok": True})

### 5.2 Implementación de send_message()

```python
# app/webhook/infrastructure.py líneas 29-35
def send_message(self, *, chat_id: int, text: str, reply_markup: Optional[Dict] = None) -> Dict[str, Any]:
    url = f"https://api.telegram.org/bot{self._bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    response = self._requests.post(url, json=payload, timeout=self._timeout)
    return {"status_code": response.status_code, "text": response.text}  # ✅ Siempre retorna algo
```

**🟢 ESTADO:** No lanza exception, siempre retorna dict con status_code.

**🔴 PROBLEMA:** Status code no se valida. Si request.post() retorna 401 (bot token inválido), sigue devolviendo `{"status_code": 401, ...}` sin error.

---

## 6️⃣ LOGGING: Análisis de Cobertura

### Puntos con Logging ✅
- ✅ Línea 75: `logger.exception("Dedup check failed")`
- ✅ Línea 812: `logger.exception("webhook.invalid_json")`
- ✅ Línea 876: `logger.info("webhook.duplicate_update", ...)`
- ✅ Línea 490: `logger.info(f"ActionParser: text={text!r}, result={parse_result.action_id}")`
- ✅ Línea 759: `logger.info(f"About to send reply: {reply!r}")`
- ✅ Línea 766: `logger.exception("webhook.telegram_send_error", extra=log_ctx)`

### Puntos SIN Logging o Logging Insuficiente 🔴
1. **Línea 104-106:** Parsing de dispatch - NO HAY LOGGING SI NO PUEDE EXTRAER update_id - ¡CRÍTICO!
   ```python
   dispatch = router.route_update(update).to_legacy_dispatch()
   update_id = dispatch.update_id
   chat_id = dispatch.chat_id
   # ¿Qué pasa si dispatch.to_legacy_dispatch() retorna None? ¿Si update_id es None?
   ```

2. **Línea 241-242:** Desde aqui a línea 480 hay MÚLTIPLES if/elif sin logging de cuál rama se ejecuta:
   ```python
   if dispatch.kind in ("chat_message", "agent_task"):
       # ... 240 líneas de lógica ...
       # FALTA LOGGING: "dispatch.kind=chat_message, procesando flujo chat_message"
   ```

3. **Línea 550-610:** Bloque NLP try/except:
   ```python
   try:
       from app.nlp.integration import get_nlp_integration
       nlp_integration = get_nlp_integration()
       # ... varias líneas ...
   except Exception as e:
       logger.error(f"🔴 CRITICAL NLP PROCESSING ERROR: {type(e).__name__}: {e}")
       # ✅ Este está bien logueado
   ```

4. **Línea 636-677:** Fallback handling - FALTA LOGGING más clara:
   ```python
   result = handle_chat_message_fn(chat_id, text)
   if result and isinstance(result, dict):
       reply = result.get("response", "(no response)")
   else:
       reply = "(no response)"
       logger.warning(f"Invalid result from handle_chat_message_fn: {result}")
       # 🟡 Esto está bien, pero debería ser ERROR no WARNING
   ```

---

## 7️⃣ VARIABLES NO INICIALIZADAS: Búsqueda de "reply ="

### Dónde se asigna `reply`

1. **Línea 106:** `reply: Optional[str] = None` - ✅ INICIALIZACIÓN
2. **Línea 210:** `reply = f"Mensaje de bienvenida..."`
3. **Línea 231:** `reply = "Envia una foto..."`
4. **...** (20+ más asignaciones)
5. **Línea 528:** `reply = action_reply` (dentro de if action_executed)
6. **Línea 759:** `await telegram_client.send_message(chat_id=chat_id, text=reply)`

### Análisis de Rutas

La variable `reply` se inicializa como `None` en línea 106, por lo que **NO hay NameError posible**.

**PERO**: Hay un escenario donde `reply` podría permanecer `None`:

```python
# Línea 241-480: if dispatch.kind in ("chat_message", "agent_task"):
if dispatch.kind in ("chat_message", "agent_task"):
    # ... 240 líneas de if/elif
    if state and state.get("state") == "waiting_welcome_text":
        reply = "..."
    elif state and state.get("state") == "waiting_welcome_media":
        reply = "..."
    # ... más elif ...
    else:
        # Línea 475: Inicio del bloque principal sin estado
        # Aquí se ejecuta ActionParser, NLP, agent_task, etc.
```

**El Código está mucho mejor ahora**, pero veamos los else clauses en el árbol:

```python
# Línea 676-691: else clause por defecto
else:
    moderation = handle_enterprise_moderation_fn(...)
    if moderation.get("status") == "blocked":
        reply = moderation.get("response_text", "Mensaje bloqueado.")
    else:
        result = handle_chat_message_fn(chat_id, dispatch.text)
        reply = result.get("response", "(no response)")
```

**🟢 ESTADO:** En TOUS los caminos, `reply` recibe un valor antes de `send_message()`.

---

## 8️⃣ ASYNC/SYNC MISMATCH y PROCESS_ASYNC

**Ubicación:** `app/webhook/handlers.py` líneas 883-912

### 8.1 Configuración

```python
# bootstrap.py línea 74
process_async = settings.process_async
```

Este valor viene de variable de entorno: `PROCESS_ASYNC` (true/false)

### 8.2 La Lógica

```python
if process_async and task_queue is not None:
    # Intenta enqueue a Redis/RQ
    try:
        job_id = task_queue.enqueue_process_update(update=update)
        # ✅ Correcto: job enqueued, webhook retorna inmediatamente
    except Exception:
        # 🟢 FALLBACK: Si Redis falla, procesar en sync
        logger.warning("webhook.fallback_sync_after_enqueue_failure", extra=log_ctx)
        await _run_processor()

elif process_async and task_queue is None:
    # 🔴 CRÍTICO: process_async=True pero Redis no configurado
    logger.warning("webhook.async_queue_unavailable", extra=log_ctx)
    await _run_processor()  # Primera ejecución
    await _run_processor()  # 🔴 BUG: SEGUNDA EJECUCIÓN
    # Mensaje se procesa DOS VECES

else:
    # process_async=False - procesar sincronamente
    await _run_processor()
```

### 8.3 Escenario Error: process_async=True sin Redis

**Configuración:**
```
PROCESS_ASYNC=true
REDIS_URL=""  # No configurado
```

**Resultado:**
1. `process_async=True`, pero `task_queue=None` (no hay Redis)
2. Se ejecuta la rama `elif process_async and task_queue is None`
3. **Se llama `_run_processor()` DOS VECES**

**Impacto:**
- Mensaje se procesa dos veces
- Usuario recibe DOS respuestas idénticas de Telegram
- Dedup NO previene esto porque es dentro de `_run_processor()`

---

## 🔴 LISTA DE BUGS CRÍTICOS ENCONTRADOS

### BUG #1: Double Processing en Async-sin-Queue
**Ubicación:** `handlers.py` línea 909-910
```python
elif process_async and task_queue is None:
    logger.warning("webhook.async_queue_unavailable", extra=log_ctx)
    logger.warning("webhook.fallback_sync_after_queue_unavailable", extra=log_ctx)
    await _run_processor()  # Primera ejecución
    await _run_processor()  # SEGUNDA - BUG
```
**Severidad:** 🔴 CRÍTICA - Causa doble respuesta
**Solución:** Remover la segunda `await _run_processor()`

### BUG #2: send_message() No Valida Estatus HTTP
**Ubicación:** `infrastructure.py` línea 35
```python
response = self._requests.post(url, json=payload, timeout=self._timeout)
return {"status_code": response.status_code, "text": response.text}
```
**Severidad:** 🟡 MEDIA - Si bot token es inválido, no genera error
**Síntoma:** HTTP 401 se retorna sin exception
**Solución:** Validar `response.status_code >= 400` y lanzar exception

### BUG #3: Dispatch.to_legacy_dispatch() Sin Validación
**Ubicación:** `handlers.py` línea 104
```python
dispatch = router.route_update(update).to_legacy_dispatch()
update_id = dispatch.update_id  # ¿Qué si dispatch es None?
```
**Severidad:** 🟡 MEDIA - Podría lanzar AttributeError
**Solución:** Validar `dispatch is not None` antes de acceder a propiedades

### BUG #4: Try/Except Demasiado Amplio
**Ubicación:** `handlers.py` línea 720-758
```python
try:
    # ... 38 líneas de lógica ...
except Exception:
    logger.exception("webhook.service_error", extra=log_ctx)
    reply = "(internal error)"
```
**Severidad:** 🟡 MEDIA - Oculta errores reales
**Solución:** Ser más específico con las exceptions

### BUG #5: Logging Insuficiente en Routing
**Ubicación:** `handlers.py` líneas 241-480
**Severidad:** 🟡 MEDIA - Dificulta debugging
**Síntoma:** No se sabe qué rama del if/elif se ejecutó
**Solución:** Agregar logging al inicio de cada rama importante

---

## 📋 TABLA DE FLUJOS: Todos los Caminos Posibles

```
UPDATE RECIBIDO
├─ Token inválido?
│  └─ ❌ HTTP 403 (no procesa)
├─ JSON inválido?
│  └─ ✅ {"ok": True} (no procesa)
├─ Duplicado?
│  └─ ✅ {"ok": True} (no procesa)
├─ dispatch.kind == "unsupported"?
│  └─ ✅ return (no se envía mensaje)
├─ dispatch.kind == "callback_query"?
│  └─ ✅ menu_engine.handle_callback_query_raw()
│     └─ ✅ return (no se envía mensaje de texto)
├─ dispatch.kind in ("chat_message", "agent_task")?
│  ├─ ¿Hay estado de conversación?
│  │  ├─ waiting_welcome_text → reply = "Guardado"
│  │  ├─ waiting_welcome_media → reply = "Guardado"
│  │  ├─ waiting_*_duration/exceptions → reply = "Guardado" o Validación
│  │  └─ ... (10+ estados más)
│  └─ Más else: ActionParser → NLP → agent → chat_service
│     ├─ ActionParser ejecutó OK? → reply = action_result.message
│     ├─ ActionParser ejecutó ERROR? → reply = action_result.response_text
│     ├─ ActionParser no ejecutó?
│     │  ├─ Moderation bloqueó? → reply = moderation.response_text
│     │  ├─ dispatch.kind == "agent_task"? → reply = agent_core.process_async() (agent_result.response)
│     │  ├─ NLP habilitada y confiada?
│     │  │  ├─ Ejecutó acción? → reply = "✓ Accion: ..."
│     │  │  └─ No ejecutó acción? → reply = handle_chat_message_fn()
│     │  └─ NLP NO confiada? → reply = handle_chat_message_fn()
├─ dispatch.kind == "ops_command"?
│  └─ reply = handle_ops_command_fn()
├─ dispatch.kind == "enterprise_command"?
│  ├─ return "menu"? → menu_engine.send_menu_message() y return (no se envía respuesta de texto)
│  └─ return "ok"? → reply = result.get("response_text")
└─ Else (otros tipos)?
   ├─ Moderation bloqueó? → reply = "Mensaje bloqueado"
   └─ Else? → reply = handle_chat_message_fn()

ENVÍO DE RESPUESTA
├─ try: send_message(chat_id, reply)
├─ except: logging (no relanzar, webhook ya retornó OK)
├─ menu_to_show? → menu_engine.send_menu_message()
└─ Retornar {"ok": True}
```

---

## 🔧 ARREGLOS RECOMENDADOS

### Arreglo #1: Remover Doble Llamada (CRÍTICA)
**Archivo:** `app/webhook/handlers.py` línea 909-910
```python
# ANTES
elif process_async and task_queue is None:
    logger.warning("webhook.async_queue_unavailable", extra=log_ctx)
    logger.warning("webhook.fallback_sync_after_queue_unavailable", extra=log_ctx)
    await _run_processor()
    await _run_processor()  # ELIMINAR ESTA LÍNEA

# DESPUÉS
elif process_async and task_queue is None:
    logger.warning("webhook.async_queue_unavailable", extra=log_ctx)
    logger.warning("webhook.fallback_sync_after_queue_unavailable", extra=log_ctx)
    await _run_processor()
```

### Arreglo #2: Validar Send Message Status Code
**Archivo:** `app/webhook/infrastructure.py` líneas 29-35
```python
# ANTES
def send_message(self, *, chat_id: int, text: str, reply_markup: Optional[Dict] = None) -> Dict[str, Any]:
    url = f"https://api.telegram.org/bot{self._bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    response = self._requests.post(url, json=payload, timeout=self._timeout)
    return {"status_code": response.status_code, "text": response.text}

# DESPUÉS
def send_message(self, *, chat_id: int, text: str, reply_markup: Optional[Dict] = None) -> Dict[str, Any]:
    url = f"https://api.telegram.org/bot{self._bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    response = self._requests.post(url, json=payload, timeout=self._timeout)
    
    # Validar status code
    if response.status_code >= 400:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Telegram API error: {response.status_code} - {response.text}")
        raise Exception(f"Telegram API returned {response.status_code}: {response.text}")
    
    return {"status_code": response.status_code, "text": response.text}
```

### Arreglo #3: Agregar Logging de Routing
**Archivo:** `app/webhook/handlers.py` línea 241 (inicio del bloque if dispatch.kind in ...)
```python
# AGREGAR LOGGING AL INICIO
if dispatch.kind in ("chat_message", "agent_task"):
    from app.manager_bot._menu_service import get_conversation_state
    logger.info(f"Processing {dispatch.kind}: user_id={dispatch.user_id}, text={dispatch.text[:50]!r}...")  # AGREGAR
    conversation = get_conversation_state()
    # ... resto del código
```

### Arreglo #4: Validar dispatch Antes de Usarlos
**Archivo:** `app/webhook/handlers.py` línea 104-107
```python
# ANTES
dispatch = router.route_update(update).to_legacy_dispatch()
update_id = dispatch.update_id
chat_id = dispatch.chat_id

# DESPUÉS
legacy_dispatch = router.route_update(update)
if legacy_dispatch is None:
    logger.error("route_update returned None")
    record_event(component="webhook", event="webhook.routing_error", update_id=update.get("update_id"))
    return

dispatch = legacy_dispatch.to_legacy_dispatch()
if dispatch is None:
    logger.error("to_legacy_dispatch returned None")
    record_event(component="webhook", event="webhook.dispatch_error", update_id=update.get("update_id"))
    return

update_id = dispatch.update_id
chat_id = dispatch.chat_id
```

### Arreglo #5: Cambiar WARNING a ERROR en Logging
**Archivo:** `app/webhook/handlers.py` línea 641
```python
# ANTES
logger.warning(f"Invalid result from handle_chat_message_fn: {result}")

# DESPUÉS
logger.error(f"Invalid result from handle_chat_message_fn: {result}")
```

---

## 📊 RESUMEN DE ESTADO

| Punto | Estado | Severidad | Acción |
|-------|--------|-----------|--------|
| Token validation | ✅ OK | - | - |
| JSON parsing | ✅ OK | - | - |
| Deduplication | ✅ OK | - | - |
| Double processing en async | 🔴 BUG | CRÍTICA | Remover línea 910 |
| send_message status validation | 🔴 BUG | MEDIA | Validar status >= 400 |
| dispatch.to_legacy_dispatch | 🔴 BUG | MEDIA | Validar no es None |
| reply initialization | ✅ OK | - | - |
| handle_chat_message validation | ✅ OK | - | - |
| Logging coverage | 🟡 INCOMPLETO | MEDIA | Agregar en routing |
| Exception handling | 🟡 DEMASIADO AMPLIO | MEDIA | Ser más específico |
| Async/sync fallback | ✅ OK (excepto doble) | - | Remover doble llamada |

