# LOCALIZACIÓN EXACTA DE LOS BUGS EN EL CÓDIGO

## 🔴 BUG #1: DOUBLE PROCESSING (CRÍTICA)

**Archivo:** `app/webhook/handlers.py`
**Líneas:** 903-913
**Función:** `handle_webhook_impl()`

```python
903:	    try:
904:	        async def _run_processor() -> None:
905:	            result = process_update_sync(update)
906:	            if inspect.isawaitable(result):
907:	                await result
908:	
909:	        if process_async and task_queue is not None:
910:	            try:
911:	                job_id = task_queue.enqueue_process_update(update=update)
912:	                logger.info(
913:	                    "webhook.enqueued_update", extra={**log_ctx, "job_id": job_id}
914:	                )
915:	                record_event(
916:	                    component="webhook",
917:	                    event="webhook.enqueue.ok",
918:	                    update_id=update_id,
919:	                    chat_id=chat_id,
920:	                    job_id=job_id,
921:	                )
922:	            except Exception:
923:	                # If the queue is misconfigured or Redis is down, fall back to
924:	                # sync processing so Telegram still gets a timely response.
925:	                logger.exception("webhook.enqueue_failed", extra=log_ctx)
926:	                logger.warning("webhook.fallback_sync_after_enqueue_failure", extra=log_ctx)
927:	                record_event(
928:	                    component="webhook",
929:	                    event="webhook.enqueue.error",
930:	                    level="ERROR",
931:	                    update_id=update_id,
932:	                    chat_id=chat_id,
933:	                )
934:	                await _run_processor()
935:	        elif process_async and task_queue is None:
936:	            logger.warning("webhook.async_queue_unavailable", extra=log_ctx)
937:	            logger.warning("webhook.fallback_sync_after_queue_unavailable", extra=log_ctx)
938:	            record_event(
939:	                component="webhook",
940:	                event="webhook.enqueue.unavailable",
941:	                level="WARN",
942:	                update_id=update_id,
943:	                chat_id=chat_id,
944:	            )
945:	            await _run_processor()  # ← PRIMERA EJECUCIÓN
946:	            await _run_processor()  # ← 🔴 SEGUNDA EJECUCIÓN (ELIMINAR ESTA LÍNEA)
947:	        else:
948:	            await _run_processor()
949:
950:	        requests_metric.labels(status="ok").inc()
951:	        return {"ok": True}
```

**EL PROBLEMA:**
- **Línea 945-946:** Cuando `process_async=True` pero `task_queue=None` (Redis no disponible)
- Se ejecuta `_run_processor()` DOS veces
- Esto causa que el mensaje se procese y se envíe dos respuestas

**LA SOLUCIÓN:**
Eliminar la línea 946: `await _run_processor()`

---

## 🔴 BUG #2: SEND_MESSAGE NO VALIDA STATUS CODE

**Archivo:** `app/webhook/infrastructure.py`
**Líneas:** 27-35
**Clase:** `_LegacyRequestsTelegramClient`
**Método:** `send_message()`

```python
  27:	    def send_message(self, *, chat_id: int, text: str, reply_markup: Optional[Dict] = None) -> Dict[str, Any]:
  28:	        url = f"https://api.telegram.org/bot{self._bot_token}/sendMessage"
  29:	        payload = {"chat_id": chat_id, "text": text}
  30:	        if reply_markup:
  31:	            payload["reply_markup"] = reply_markup
  32:	        response = self._requests.post(url, json=payload, timeout=self._timeout)
  33:	        return {"status_code": response.status_code, "text": response.text}
```

**EL PROBLEMA:**
- **Línea 32-33:** Se hace POST al API de Telegram
- Si Telegram retorna 401 (Bad token), 400 (Bad request), etc.
- El método simplemente retorna `{"status_code": 401, ...}` SIN lanzar exception
- El webhook continúa normalmente retornando `{"ok": True}`
- El usuario NUNCA se entera de que el mensaje no se envió

**LA SOLUCIÓN:**
Agregar validación después de línea 32:

```python
    response = self._requests.post(url, json=payload, timeout=self._timeout)
    
    # NEW: Validar que la respuesta fue exitosa
    if response.status_code >= 400:
        error_msg = f"Telegram API error {response.status_code}: {response.text[:200]}"
        raise Exception(error_msg)
    
    return {"status_code": response.status_code, "text": response.text}
```

---

## 🟡 BUG #3: DISPATCH.TO_LEGACY_DISPATCH() SIN VALIDACIÓN

**Archivo:** `app/webhook/handlers.py`
**Líneas:** 100-107
**Función:** `process_update_impl()`

```python
 82:	async def process_update_impl(
 83:	    update: Dict[str, Any],
 ...
100:	    start = time.time()
101:	    if update.get("callback_query"):
102:	        dispatch = dispatch_telegram_update(update)
103:	    else:
104:	        router = _get_manager_bot_router()
105:	        dispatch = router.route_update(update).to_legacy_dispatch()  # ← POSIBLE None
106:	    update_id = dispatch.update_id  # ← AttributeError si dispatch es None
107:	    chat_id = dispatch.chat_id
```

**EL PROBLEMA:**
- **Línea 105:** `router.route_update(update)` retorna un objeto
- Ese objeto tiene método `.to_legacy_dispatch()` que PODRÍA retornar `None`
- **Línea 106:** Acceso a `dispatch.update_id` causa `AttributeError` si dispatch es None

**LA SOLUCIÓN:**
Agregar validaciones:

```python
    start = time.time()
    if update.get("callback_query"):
        dispatch = dispatch_telegram_update(update)
    else:
        router = _get_manager_bot_router()
        route_result = router.route_update(update)
        
        # NEW: Validar que route_result no es None
        if route_result is None:
            logger.error("Router.route_update returned None")
            record_event(
                component="webhook",
                event="webhook.router_error",
                update_id=update.get("update_id"),
            )
            return
        
        dispatch = route_result.to_legacy_dispatch()
        
        # NEW: Validar que dispatch no es None
        if dispatch is None:
            logger.error("to_legacy_dispatch() returned None")
            record_event(
                component="webhook",
                event="webhook.dispatch_error",
                update_id=update.get("update_id"),
            )
            return
    
    update_id = dispatch.update_id
    chat_id = dispatch.chat_id
```

---

## 🟡 BUG #4: FALTA LOGGING + EXCEPCIÓN MUY AMPLIA

**Archivo:** `app/webhook/handlers.py`
**Líneas:** 720-758
**Bloque:** `try/except` principal en `process_update_impl()`

```python
720:	    except Exception:
721:	        logger.exception("webhook.service_error", extra=log_ctx)
722:	        record_event(
723:	            component="webhook",
724:	            event="webhook.service.error",
725:	            level="ERROR",
726:	            update_id=update_id,
727:	            chat_id=chat_id,
728:	        )
729:	        if chat_api_error_metric is not None:
730:	            chat_api_error_metric.inc()
731:	        reply = "(internal error)"
```

**EL PROBLEMA:**
- **Línea 720:** `except Exception:` es DEM SIADA AMPLIO
- Captura TODAS las excepciones (incluso las que no debería)
- Oculta bugs del código
- El mensaje "Error interno" es muy genérico

**IMPACTO:**
Si hay un bug en línea 500 (por ejemplo, variable no inicializada), el try/except lo oculta y simplemente retorna "(internal error)"

**MEJOR PRÁCTICA:**
Ser más específico:

```python
    except ValueError as e:
        logger.error(f"Invalid value in processing: {e}", exc_info=True)
        reply = "Parámetro inválido"
    except ConnectionError as e:
        logger.error(f"Connection error: {e}", exc_info=True)
        reply = "Error de conexión"
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        reply = "Error inesperado"
```

---

## 🟡 BUG #5: FALTA LOGGING DE DISPATCH.KIND

**Archivo:** `app/webhook/handlers.py`
**Línea:** 241
**Bloque:** Inicio del procesamiento de chat_message

```python
241:	        if dispatch.kind in ("chat_message", "agent_task"):
242:	            from app.manager_bot._menu_service import get_conversation_state
243:	            conversation = get_conversation_state()
```

**EL PROBLEMA:**
- Cuando se entra a este bloque, NO hay logging indicando que se va a procesar
- Si hay un error más adelante, es difícil saber si fue en este bloque o en otro
- Especialmente cuando hay múltiples `elif` para diferentes `dispatch.kind`

**SOLUCIÓN:**
Agregar logging al inicio:

```python
        if dispatch.kind in ("chat_message", "agent_task"):
            logger.info(
                f"Processing {dispatch.kind}",
                extra={
                    "user_id": dispatch.user_id,
                    "text_len": len(dispatch.text or ""),
                    "has_state": conversation.get_state(dispatch.user_id, dispatch.chat_id) is not None,
                }
            )
            from app.manager_bot._menu_service import get_conversation_state
            conversation = get_conversation_state()
```

---

## 📊 RESUMEN: BUGS POR SEVERIDAD

| Bug | Archivo | Línea | Severidad | Causa |
|-----|---------|-------|-----------|-------|
| Double Processing | handlers.py | 945-946 | 🔴 CRÍTICA | Doble await |
| Status Code No Validado | infrastructure.py | 33 | 🔴 CRÍTICA | No valida HTTP 4xx |
| Dispatch Sin Validación | handlers.py | 105-106 | 🟡 MEDIA | Posible None |
| Try/Except Demasiado Amplio | handlers.py | 720 | 🟡 MEDIA | Oculta errores |
| Falta Logging | handlers.py | 241 | 🟡 MEDIA | Dificulta debug |

---

## ✅ CHECKLIST DE ARREGLOS

- [ ] Eliminar línea 946 en `handlers.py` (DOBLE AWAIT)
- [ ] Agregar validación de status_code en `infrastructure.py` línea 33
- [ ] Agregar validación de dispatch None en `handlers.py` línea 105-106
- [ ] Mejorar try/except en `handlers.py` línea 720 (OPCIONAL)
- [ ] Agregar logging de dispatch.kind en `handlers.py` línea 241 (OPCIONAL)

---

## 🧪 CÓMO TESTEAR LOS BUGS

### Test para Bug #1 (Double Processing)

```bash
# Configuración:
PROCESS_ASYNC=true
REDIS_URL=""  # Vacío - no hay Redis

# Acción:
Enviar un mensaje al bot

# Resultado ESPERADO (après fix):
Una respuesta

# Resultado ACTUAL (antes fix):
DOS respuestas idénticas
```

### Test para Bug #2 (Status Code)

```bash
# Configuración:
BOT_TOKEN="123:ABC-INVALID_TOKEN"  # Token inválido

# Acción:
Enviar un mensaje al bot

# Resultado ESPERADO (après fix):
Error en logs: "Telegram API error 401"

# Resultado ACTUAL (antes fix):
Silencio - webhook retorna OK aunque fallo
```

### Test para Bug #3 (Dispatch None)

```bash
# Difícil de reproducir - ocurre si router tiene bug

# Resultado ESPERADO (après fix):
Error loguedo: "to_legacy_dispatch() returned None"

# Resultado ACTUAL (antes fix):
AttributeError 'NoneType' object has no attribute 'update_id'
```

