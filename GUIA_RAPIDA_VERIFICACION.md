# 🔍 GUÍA RÁPIDA DE VERIFICACIÓN - FLUJO TELEGRAM

## ¿ESTÁ MI BOT ENVIANDO DOS RESPUESTAS A UN MENSAJE?

### Paso 1: Verifica tu configuración
```bash
# ¿Qué valor tiene en tu .env?
PROCESS_ASYNC=true      # ← Peligro
REDIS_URL=""            # ← Peligro
```

Si ambas son así, **TIENES EL BUG #1 ACTIVO AHORA MISMO**.

### Paso 2: Confirmación rápida
- Envía un mensaje simple: "hola"
- ¿Recibes una respuesta o DOS?
  - **Una respuesta** = Bug no está activo (quizás PROCESS_ASYNC=false)
  - **DOS respuestas** = Bug CONFIRMA (línea 945-946 es el culpable)

### Paso 3: Fix Inmediato
```python
# Archivo: app/webhook/handlers.py
# Línea: 945-946
# ELIMINAR ESTA LÍNEA:
await _run_processor()  # ← SEGUNDA LLAMADA
```

---

## ¿MI BOT FALLA SILENCIOSAMENTE CON BOT TOKEN INVÁLIDO?

### Paso 1: Verifica el token
```bash
# En tu .env:
BOT_TOKEN="123:ABC-XYZ..."  # ¿Es correcto?
```

### Paso 2: Confirmación rápida
- Cambia el token a algo inválido: `BOT_TOKEN="0:FAKE"`
- Reinicia el webhook
- Envía un mensaje
- ¿Qué pasa?
  - **Respuesta normal** = Bug PRESENTE (no valida status 401)
  - **Error en logs** = Bug NO presente (valida correctamente)

### Paso 3: Fix Inmediato
```python
# Archivo: app/webhook/infrastructure.py
# Línea: 32-33
# AGREGAR DESPUÉS DE response = self._requests.post(...):
if response.status_code >= 400:
    raise Exception(f"Telegram API error {response.status_code}")
```

---

## ¿QUIERO SABER EXACTAMENTE QUÉ ESTÁ PASANDO EN CADA STEP?

### Sigue los Logs
Busca en los logs durante el procesamiento:

```
[1] Token validation
    └─ Busca: "webhook.received"

[2] Deduplication
    └─ Busca: "webhook.duplicate_update" o "webhook.dedup.ok"

[3] Async/Sync decision
    └─ Busca: "webhook.enqueued_update" (async OK)
              "webhook.enqueue_failed" (async fallback to sync)
              "webhook.async_queue_unavailable" (async sin Redis)

[4] Dispatch routing
    └─ Busca: "webhook.dispatch.chat_message"
              "webhook.dispatch.callback_query"
              "webhook.dispatch.ops_command"
              "webhook.dispatch.enterprise_command"
              "webhook.unsupported_update"

[5] Message processing
    └─ Busca: "webhook.action_parser.executed"
              "webhook.nlp_flow.ok"
              "webhook.agent_flow.ok"
              "webhook.chat_service.ok"
              "webhook.enterprise_moderation.blocked"

[6] Response sending
    └─ Busca: "About to send reply:"  (línea 759)
              "webhook.telegram_send.ok"
              "webhook.telegram_send_error"

[7] Menu display (si aplica)
    └─ Busca: "webhook.menu.display"
              "webhook.menu.send_error"
```

---

## TABLA RÁPIDA DE DIAGNÓSTICO

| Síntoma | Causa Probable | Archivo | Línea | Fix |
|---------|----------------|---------|-------|-----|
| DOS respuestas a un mensaje | PROCESS_ASYNC=true, sin Redis | handlers.py | 945-946 | Eliminar línea 946 |
| Bot falla con token inválido | API status no validado | infrastructure.py | 33 | Agregar validación |
| Usuario recibe "(internal error)" | Exception en procesamiento | handlers.py | 720 | Verificar logs detallados |
| Mensaje enviado pero sin respuesta | Chat service error | services.py | 25-70 | Verificar agent.process() |
| Menú no aparece | Menu engine error | handlers.py | 771-780 | Verificar menu_engine existence |

---

## 🧪 TEST RÁPIDO: ¿ESTÁ FUNCIONANDO CORRECTAMENTE?

### Test 1: Token Inválido
```bash
# Configuración:
BOT_TOKEN="0:FAKE"

# Esperado: Error en logs con HTTP status
# Si ves: Silencio o respuesta normal → Bug presente
```

### Test 2: Double Processing
```bash
# Configuración:
PROCESS_ASYNC=true
REDIS_URL=""

# Envía: Un mensaje
# Esperado: Una respuesta
# Si ves: DOS respuestas → Bug presente
```

### Test 3: Text Empty
```bash
# Envía: Un mensaje vacío o "    " (solo espacios)
# Esperado: Respuesta fallida o mensaje genérico
# Si ves: Crash o "(internal error)" → Posible bug
```

### Test 4: Dispatch Unknown
```bash
# Envía: Un update inválido (si logras hackear uno)
# Esperado: Logging claro de "unsupported_update"
# Si ves: Crash o silencio → Bug en dispatch
```

---

## 📊 MATRIZ DE FLUJOS: ¿POR CUÁL CAMINO PASIÓN?

```
Tipo de Update          | Handler               | Resultado Esperado
------------------------|-----------------------|-------------------
Mensaje de texto        | handle_chat_message   | Respuesta de texto
Comando /start          | enterprise_command    | Menú o bienvenida
Botón callback          | menu_engine           | Edit message o alert
Comando /ops admin      | handle_ops_command    | Respuesta admin
Mensaje con foto/video  | handle_chat_message   | Respuesta normal (ignore media)
Update desconocido      | (unsupported)         | Nada (no responde)
```

### ¿Cómo sé por cuál camino pasó?

Busca en logs el valor de `dispatch.kind`:

```
💬 CHAT_MESSAGE: Usuario envió texto normal
   → Pasa por: ActionParser → NLP → agent → chat_service
   
🔘 CALLBACK_QUERY: Usuario clickeó un botón
   → Pasa por: menu_engine
   
❌ UNSUPPORTED: Update que no reconocemos
   → Pasa por: (retorna sin hacer nada)
   
🛠️ ENTERPRISE_COMMAND: Comando /start /help etc
   → Pasa por: handle_enterprise_command
   
⚙️ OPS_COMMAND: Comando admin
   → Pasa por: handle_ops_command
```

---

## 🚨 ERROR CRÍTICO: "Cannot find Telegram client"

**Causa probable:** `BOT_TOKEN` no está configurado
```bash
# En tu .env:
BOT_TOKEN=""  # ← Vacío
```

**Fix:** Asegúrate que está en `.env` con valor válido
```bash
BOT_TOKEN="123456789:ABCDEFGHijklmnopq"
```

---

## 🚨 ERROR CRÍTICO: "Async queue unavailable"

**Causa:** `PROCESS_ASYNC=true` pero Redis no existe o está desconectado

**Fix Inmediato:** 
- Opción 1: Configura Redis
  ```bash
  REDIS_URL="redis://localhost:6379"
  ```
- Opción 2: Desactiva async
  ```bash
  PROCESS_ASYNC=false
  ```

**IMPORTANTE:** PERO si PROCESS_ASYNC=true sin REDIS, tienes el BUG #1 (doble processing) ACTIVO. Arregla la línea 946 YA.

---

## 📞 PREGUNTAS FRECUENTES

### P: ¿Por qué recibo dos respuestas?
**R:** Probablemente BUG #1. Checks:
1. ¿SON IDÉNTICAS las dos respuestas?
   - Sí → BUG #1 (#945-946)
   - No → Algo diferente está pasando
2. ¿`PROCESS_ASYNC=true` en tu .env?
   - Sí y `REDIS_URL=""` → SEGURO que es BUG #1
   - No → Podría ser otra cosa (ej: menú enviado después de texto)

### P: ¿Por qué no recibo respuesta?
**R:** Posibles causas:
1. **BOT_TOKEN inválido** (BUG #2) → Checkea logs
2. **Chat service error** → Busca "webhook.chat_service" en logs
3. **Timeout** → ¿Tarda >30 seg en procesar?
4. **Telegram API caída** → ¿Puedes enviar mensajes desde otro bot?

### P: ¿Por qué recibo "internal error"?
**R:** Hay una exception en línea 475-720. Checkea logs detallados.
```
Logger.exception()  se llama en línea 721, así que debe haber stacktrace.
```

### P: ¿Cómo sé que el menú se envió?
**R:** Busca en logs:
```
"webhook.menu.display" → Menú se envió correctamente
"webhook.menu.send_error" → Error al enviar menú
```

---

## 🔧 CÓMO LIMPIAR Y RESETEAR

Si algo está mal, intenta:

```bash
# 1. Limpar caché de Python
rm -rf __pycache__
rm -rf .pytest_cache

# 2. Resetear dedup store si es in-memory
# (Requiere reiniciar la aplicación)

# 3. Verificar que Redis está limpio
redis-cli FLUSHALL

# 4. Enviar un mensaje de prueba
# (Debería procesarse normalmente)
```

---

## 📋 CHECKLIST: ¿TODO ESTÁ CORRECTO?

- [ ] Token validation retorna 403 para tokens inválidos
- [ ] JSON parsing invalido retorna {"ok": True} sin procesar
- [ ] Duplicates se descartan sin procesar
- [ ] NO recibo dos respuestas (arreglaste línea 946)
- [ ] Bot token inválido genera error en logs (arreglaste status validation)
- [ ] Envío un mensaje y recibo UNA respuesta
- [ ] Logs muestran el flujo claramente (dispatch.kind, chat_service, etc)
- [ ] Botones del menú funcionan (callback_query)
- [ ] Comandos /start /help responden correctamente

Si marcase ✅ en todo, **tu webhook está funcionando correctamente**.

