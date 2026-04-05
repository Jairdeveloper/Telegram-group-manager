# DIAGRAMA VISUAL DEL FLUJO DE MENSAJE TELEGRAM

## 🗺️ FLUJO COMPLETO LÍNEA POR LÍNEA

```
┌─────────────────────────────────────────────────────┐
│  1. POST /webhook/{token}                           │
│  📍 entrypoint.py línea 123                          │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  2. handle_webhook_impl()                           │
│  📍 handlers.py línea 809                            │
└────────────────┬────────────────────────────────────┘
                 │
         ┌───────┴───────┐
         ▼               ▼
    🔐 Token       🔐 JSON
    Validation     Parsing
      │               │
  Línea 819-830   Línea 832-864
  ✅ OK                │
                       ▼
                   ✅ OK (valida)
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│  3. Deduplication Check                             │
│  📍 handlers.py línea 865-873                        │
│  dedup_update(update_id)                            │
└────────────────┬────────────────────────────────────┘
                 │
         ┌───────┴───────┐
         ▼               ▼
     ✅ NEW          ❌ DUPLICATE
   Procesar        Return {"ok": True}
         │
         ▼
┌─────────────────────────────────────────────────────┐
│  4. Async Decision                                  │
│  📍 handlers.py línea 876-912                        │
└────────────────┬────────────────────────────────────┘
         │
     ┌───┴───┬─────────┬──────────┐
     ▼       ▼         ▼          ▼
  ASYNC  ASYNC_AND  ASYNC_AND   SYNC
  ✅OK  QUEUE_FAIL  NO_QUEUE  (Normal)
  Enqueue Try→    🔴 BUG    Process
    │      Sync   Double     Sync
    │      OK     Process    │
    │      │         │       │
    └──────┴─────────┴───────┘
            │
            ▼ await _run_processor()
┌─────────────────────────────────────────────────────┐
│  5. process_update_impl()                           │
│  📍 handlers.py línea 82-777                         │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
        📊 Parse Dispatch
        Línea 92-106
                 │
         ┌───────┴────────┬─────────┐
         ▼                ▼         ▼
     "UNSUPPORTED"  "callback"  OTHER
     │              │           │
  Return      Return (menu)  Continue
  No reply    No reply       │
                            ▼
┌─────────────────────────────────────────────────────┐
│  6. CHAT MESSAGE Handler                            │
│  📍 handlers.py línea 241-720                        │
│  if dispatch.kind in ("chat_message", "agent_task")│
└────────────────┬────────────────────────────────────┘
                 │
         ┌───────┴────────────┐
         ▼                    ▼
   ¿HAS STATE?            NO STATE
   (Conversación)         │
   Estados:               ▼
   waiting_welcome_text   PRIORIDAD 1: ActionParser
   waiting_media          ├─ Parse natural language
   waiting_duration       ├─ IF confidence >= 0.5
   waiting_antispan       │  └─ Ejecutar action
   etc.                   │     ├─ OK → reply = action.result
   │                      │     └─ ERROR → reply = error.msg
   ▼                      │
   Set reply             PRIORIDAD 2: NLP (si no ActionParser)
   & menu                ├─ should_use_nlp(text)?
   (Línea 210-475)       │  └─ process_message()
                         │     └─ IF action_id
                         │        └─ reply = "✓ Accion"
                         │        └─ ELSE → chat_service
                         │
                         PRIORIDAD 3: Agent
                         ├─ IF dispatch.kind == "agent_task"
                         │  └─ agent_core.process_async(text)
                         │
                         PRIORIDAD 4: Chat Service
                         └─ handle_chat_message_fn(chat_id, text)
                            └─ reply = result.get("response")
                            
┌─────────────────────────────────────────────────────┐
│  7. handle_chat_message() - Chatbot Core             │
│  📍 app/ops/services.py línea 25-70                  │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
            🤖 Agent
        runtime.agent.process(text)
            │
    ┌───────┴──────┐
    ▼              ▼
  ✅ response   ❌ None
  │              │
  ├─ Validación │ Set default reply:
  │ return dict │ "No se pudo procesar"
  │             │
  └─────┬───────┘
        │
        ▼ (Siempre retorna Dict)
    RETORNA:
    {
      "response": "...",
      "confidence": 0.5,
      "source": "...",
      "pattern_matched": true/false
    }
┌─────────────────────────────────────────────────────┐
│  8. Extract reply                                   │
│  📍 handlers.py línea 640-660                        │
│  reply = result.get("response", "(no response)")   │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
        ✅ reply está definido
           (NUNCA ES None)
        
┌─────────────────────────────────────────────────────┐
│  9. TRY/EXCEPT Principal                            │
│  📍 handlers.py línea 720-758                        │
│  Captura cualquier exception de los pasos anteriores│
└────────────────┬────────────────────────────────────┘
     ┌───────────┴──────────┐
     ▼                      ▼
  ✅ OK                  ❌ Exception
  reply es               reply = "(internal error)"
  válido                 
     │                      │
     └──────────┬───────────┘
                │
                ▼
┌─────────────────────────────────────────────────────┐
│  10. ENVÍO DE RESPUESTA                             │
│  📍 handlers.py línea 759-770                        │
│  telegram_client.send_message(chat_id, text=reply) │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
     try: _maybe_await(send_message(...))
         │
     ┌───┴──────────────────┐
     ▼                      ▼
  🟢 OK               🔴 Exception
  record_event.ok    logger.exception()
     │               record_event.error
     │                      │
     └──────────┬───────────┘
                │
                ▼
        (Exception NO se relanza)
        (Webhook ya retornó {"ok": True})
        
┌─────────────────────────────────────────────────────┐
│  11. MENU (Si aplica)                               │
│  📍 handlers.py línea 771-780                        │
│  if menu_to_show:                                  │
│    menu_engine.send_menu_message(...)              │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
        return {"ok": True}
        (Webhook termina)
```

---

## 🔴 PUNTOS CRÍTICOS CON BUGS

### 1️⃣ DOUBLE PROCESSING (Línea 909-910)
```
Escenario: PROCESS_ASYNC=true, REDIS_URL=""
                │
         ┌──────┴──────┐
         ▼             ▼
    process_update_impl()  process_update_impl()
    (PRIMERA EJECUCIÓN)   (SEGUNDA EJECUCIÓN - BUG)
         │                │
         ▼                ▼
    send_message()   send_message()
    Respuesta 1     Respuesta 2
    
Usuario recibe DOS mensajes idénticos 🔴
```

### 2️⃣ SEND_MESSAGE STATUS NO VALIDADO (Línea 35)
```
HTTP Response: 401 (Invalid token)
                │
                ▼
    return {"status_code": 401, "text": "..."}
                │
                ▼ (NO LANZA EXCEPTION)
    
webhook retorna {"ok": True}
Usuario NUNCA se enterra que falló 🔴
```

### 3️⃣ DISPATCH.TO_LEGACY_DISPATCH() SIN VALIDACIÓN (Línea 104)
```
router.route_update(update)
    │
    ▼
    .to_legacy_dispatch()  ← ¿Retorna None?
    │
    ▼
dispatch.update_id  ← AttributeError si None
```

---

## 📊 TABLA: Variables Críticas por Punto

| Línea | Variable | Inicializado | Riesgo | Estado |
|-------|----------|--------------|--------|--------|
| 106 | `reply` | `None` | ✅ NO hay NameError | SAFE |
| 106 | `menu_to_show` | `None` | ✅ NO hay NameError | SAFE |
| 104 | `dispatch` | ❓ | 🔴 Si router falla | UNSAFE |
| 105 | `update_id` | ✅ extracted | ✅ OK | SAFE |
| 195 | `chat_id` | ✅ extracted | ✅ OK | SAFE |

---

## 🔧 FIX APLICADO (ANTES vs DESPUÉS)

### FIX #1: Double Processing

```diff
  elif process_async and task_queue is None:
      logger.warning("webhook.async_queue_unavailable", extra=log_ctx)
      logger.warning("webhook.fallback_sync_after_queue_unavailable", extra=log_ctx)
      await _run_processor()
-     await _run_processor()
```

### FIX #2: Status Code Validation

```diff
  def send_message(self, *, chat_id: int, text: str, reply_markup: Optional[Dict] = None):
      response = self._requests.post(url, json=payload, timeout=self._timeout)
+     if response.status_code >= 400:
+         raise Exception(f"Telegram API error {response.status_code}")
      return {"status_code": response.status_code, "text": response.text}
```

### FIX #3: Dispatch Validation

```diff
  route_result = router.route_update(update)
+ if route_result is None:
+     logger.error("Router returned None")
+     return
  dispatch = route_result.to_legacy_dispatch()
+ if dispatch is None:
+     logger.error("to_legacy_dispatch returned None")
+     return
  update_id = dispatch.update_id
```

---

## 📈 IMPACTO DE LOS BUGS

| Bug | Impacto | Probabilidad | Severidad |
|-----|---------|--------------|-----------|
| Double Processing | Usuario recibe DOS respuestas | ALTA (si PROCESS_ASYNC=true sin Redis) | 🔴 CRÍTICA |
| Status Code No Validado | Bot falla silentalmente si token inválido | MEDIA (token puede ser inválido) | 🔴 CRÍTICA |
| Dispatch Sin Validación | AttributeError si router falla | BAJA (router raras veces falla) | 🟡 MEDIA |

---

## ✅ RESUMEN: QÚERE ARREGLAR

1. **DEBE HACERSE HOY:** Remover doble `await _run_processor()` en línea 910
2. **DEBE HACERSE HOY:** Validar status code en `send_message()`
3. **DEBERÍA HACERSE:** Validar dispatch no es None
4. **NICE TO HAVE:** Mejorar logging de routing

