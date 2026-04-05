# 📊 DIAGRAMA VISUAL DEL FLUJO DEL BOT

## 🔴 FLUJO ACTUAL (ROTO)

```
┌─────────────────────────────────────────────────────────────────┐
│                    TELEGRAM WEBHOOK REQUEST                      │
│  POST /webhook/abc123                                            │
│  Body: {"update_id": 123, "message": {"text": "cambiar..."}}    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              app/webhook/entrypoint.py                           │
│  handle_webhook(token, request)                                 │
│  - Valida token                                                 │
│  - Llama handle_webhook_impl()                                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              app/webhook/handlers.py                             │
│  handle_webhook_impl(token, request, ...)                       │
│  - Valida webhook token                                         │
│  - Deduplica update                                             │
│  - Encolado O procesa sync: process_update_sync(update)         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              app/webhook/handlers.py:80                          │
│  process_update_impl(update, ...)                               │
│  - Llama dispatch_telegram_update(update)                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│          app/telegram/dispatcher.py:dispatch_telegram_update()  │
│  - Extrae callback_query, chat_id, text, user_id               │
│  - Clasifica tipo de update:                                    │
│    * callback_query → kind="callback_query"                     │
│    * /comando → kind="ops_command"                              │
│    * @empresa → kind="enterprise_command"                       │
│    * Texto normal → kind="chat_message"  ← NUESTRO CASO         │
│  - Retorna DispatchResult                                       │
└─────────────────────────────────────────────────────────────────┘
           kind="chat_message", text="cambiar..."
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  app/webhook/handlers.py:process_update_impl() [líneas 170-300] │
│                                                                  │
│  if dispatch.kind == "chat_message":                            │
│      # Maneja estado conversacional (welcome_text, etc.)        │
│      # ... lógica especial ...                                  │
│      # Línea ~250: Llama                                        │
│      result = handle_chat_message(chat_id, text)               │
└─────────────────────────────────────────────────────────────────┘
              text="cambiar mensaje de bienvenida..."
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│        app/ops/services.py:handle_chat_message()  [línea 22]   │
│                                                                  │
│  def handle_chat_message(chat_id, text, *, agent=None, ...):   │
│      agent = agent or runtime.agent                            │
│      response = agent.process(text)  ← ❌ AQUÍ ESTÁ EL PROBLEMA│
│      storage.save(session_id, text, response.text)             │
│      return {...}                                               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│         app/agent/core.py (o similar) - ChatBot Agent           │
│                                                                  │
│  agent.process("cambiar mensaje de bienvenida...")             │
│  - Busca patrones:                                              │
│    * "^/comando" → No encontrado                                │
│    * "palabra: valor" → No encontrado                           │
│    * Patrones regex genéricos → Parcialmente matching           │
│  - Devuelve respuesta genérica de chat                          │
│  - NO ejecuta acción específica (set_welcome, etc.)             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    TELEGRAM RESPONSE                             │
│  text: "No entiendo el comando"  ← ❌ FALLA DEL USUARIO        │
└─────────────────────────────────────────────────────────────────┘


❌ PROBLEMA: NLP NUNCA SE EJECUTA
• app/nlp/integration.py está disponible pero NO SE IMPORTA
• get_nlp_integration() NUNCA es llamado
• action_mapper NUNCA es usado
• El bot ignora completamente el sistema NLP
```

---

## ✅ FLUJO ESPERADO (Lo que debería pasar)

```
┌─────────────────────────────────────────────────────────────────┐
│                    TELEGRAM WEBHOOK REQUEST                      │
│  POST /webhook/abc123                                            │
│  Body: {"update_id": 123, "message": {"text": "cambiar..."}}    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
         [IGUAL QUE ANTES hasta process_update_impl]
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  app/webhook/handlers.py:process_update_impl() [MODIFICADO]     │
│                                                                  │
│  if dispatch.kind == "chat_message":                            │
│      text = dispatch.text                                       │
│      chat_id = dispatch.chat_id                                 │
│      user_id = dispatch.user_id                                 │
│                                                                  │
│      # 1️⃣ INTENTAR NLP PRIMERO ← NUEVO                          │
│      from app.nlp.integration import get_nlp_integration        │
│      nlp_integration = get_nlp_integration()                    │
│      action_result = nlp_integration.get_action_for_message(text)
│                                                                  │
│      if action_result and action_result.action_id:             │
│          # ✅ NLP reconoció una acción                          │
│          await execute_action(action_result)                    │
│          return  # ← NO llamar a handle_chat_message           │
│      #                                                           │
│      # 2️⃣ FALLBACK: Si NLP falla, usar agent                   │
│      result = handle_chat_message(chat_id, text)               │
└─────────────────────────────────────────────────────────────────┘
              text="cambiar mensaje de bienvenida..."
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│     app/nlp/integration.py:get_action_for_message()             │
│                                                                  │
│  nlp_integration.get_action_for_message(text):                 │
│  1. Llama process_message(text)                                 │
│  2. Llama pipeline.process(text)                                │
│     → Normaliza: "cambiar mensaje de [...] → "cambiar..."       │
│     → Tokeniza: ["cambiar", "mensaje", "de", ...]              │
│     → Clasifica intent: IntentClassifier().classify()           │
│        • Usa regex patterns                                     │
│        • Detecta: intent="set_welcome", confidence=0.87         │
│     → Extrae entities: NER["cambiar..."]={"action": "welcome"}  │
│     → Mapea acción: ActionMapper.map() → action_id="welcome..."│
│  3. Retorna ActionParseResult(                                  │
│       action_id="welcome.set_text",                             │
│       payload={"text": "La nueva bienvenida"},                  │
│       confidence=0.87                                           │
│     )                                                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│        EJECUTAR ACCIÓN: execute_action()                        │
│                                                                  │
│  action_id = "welcome.set_text"                                 │
│  payload = {"text": "La nueva bienvenida"}                      │
│                                                                  │
│  - Busca handler para "welcome.set_text" en el registry         │
│  - Ejecuta: WelcomeHandler.set_text(chat_id, text)             │
│  - Actualiza config del group                                   │
│  - Retorna: "Mensaje de bienvenida actualizado"                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    TELEGRAM RESPONSE                             │
│  text: "Mensaje de bienvenida actualizado" ← ✅ ÉXITO          │
└─────────────────────────────────────────────────────────────────┘


✅ RESULTADO: NLP FUNCIONA
• action_mapper reconoce intención
• Se ejecuta la acción correcta
• Usuario obtiene respuesta esperada
```

---

## 🔴 ESTADO ACTUAL vs ✅ ESTADO ESPERADO

```
COMPONENTE                  ACTUAL              ESPERADO         STATUS
──────────────────────────────────────────────────────────────────────
NLPBotIntegration       Existe               Existe              ❌ Pero con error sintáctico
EnsembleClassifier      Existe               Importado           ❌ No importado en handlers
ActionMapper            Existe               Llamado             ❌ Nunca se llama
action_mapper.map()     Existe               En flujo            ❌ Nunca se ejecuta
handle_chat_message()   Siempre agent        Fallback después NLP ❌ Ignora NLP
Flujo webhook           Sin NLP              Con NLP primero     ❌ NLP desconectado
Resultado               Falla en comandos naturales              ❌ Bot no responde

SCORE: 0% NLP integrado
```

---

## 🔍 DÓNDE BUSCAR PROBLEMAS

```
┌─ ¿El webhook recibe el mensaje?
│  → Ver logs de app/webhook/entrypoint.py
│
├─ ¿Se clasifica correctamente como "chat_message"?
│  → Ver app/telegram/dispatcher.py:dispatch_telegram_update()
│  → Buscar "dispatch.kind" en logs
│
├─ ¿Se llama a handle_chat_message()?
│  → Ver logs de app/ops/services.py:handle_chat_message()
│
├─ ¿Por qué el agent.process() no reconoce el comando?
│  → Agent espera patrones rígidos: "/cmd", "palabra:", ":[valor]"
│  → Texto natural no coincide → agent devuelve genérico
│
└─ ¿POR QUÉ NLP NO SE LLAMA?
   → get_nlp_integration() NO se importa en handlers.py
   → NO existe en el flujo de process_update_impl()
   → intentar importar fallaría por error sintáctico en integration.py
      (la propiedad classifier está FUERA de la clase)
```

---

## 📌 ARCHIVOS CRÍTICOS

```
app/
├── webhook/
│   ├── entrypoint.py         ← POST /webhook/{token} aquí
│   ├── handlers.py           ← process_update_impl() aquí (línea 80)
│   │                           ← AQUÍ VA EL FIX #1 (integrar NLP)
│   └── ports.py
├── telegram/
│   ├── dispatcher.py         ← dispatch_telegram_update() aquí
│   │                           ← Clasifica updates
│   └── services.py
├── ops/
│   ├── services.py           ← handle_chat_message() aquí (línea 22)
│   │                           ← AQUÍ VA EL FIX #2 (si se decide)
│   └── ...
├── nlp/
│   ├── integration.py        ← ❌ ROTO: línea 31-78 (indentación)
│   │                           ← AQUÍ VA EL FIX #0 (fix sintáctico)
│   ├── pipeline.py           ← Existe pero nunca se usa
│   ├── action_mapper.py      ← Existe pero nunca se llama
│   ├── intent_classifier.py  ← Existe pero no integrado
│   ├── ner.py               ← spaCy opcional, fallback ok
│   └── classifiers/          ← EnsembleIntentClassifier aquí
└── ...
```

