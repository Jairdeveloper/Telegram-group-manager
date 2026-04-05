# 📑 ÍNDICE DE ANÁLISIS - NAVEGACIÓN RÁPIDA

Fecha: 1 Abril 2026
Análisis: Arquitectura del bot y problemas de integración NLP

---

## 📚 DOCUMENTOS GENERADOS EN ESTA SESIÓN

### 🚀 EMPEZAR AQUÍ

1. **[RESUMEN_EJECUTIVO_1PAGINA.md](RESUMEN_EJECUTIVO_1PAGINA.md)** (⏱️ 2 min lectura)
   - Visión rápida de qué está mal
   - 3 problemas principales
   - Orden de fixes
   - ✅ **LEER PRIMERO si quieres respuestas rápidas**

### 📊 ANÁLISIS TÉCNICO COMPLETO

2. **[ANALISIS_FLUJO_WEBHOOK_NLP.md](ANALISIS_FLUJO_WEBHOOK_NLP.md)** (⏱️ 10 min lectura)
   - Flujo completo del webhook paso a paso
   - Donde está roto el NLP
   - Dónde vs flujo actual toma decisiones
   - Root causes identificadas
   - ✅ **LEER si quieres entender la arquitectura**

3. **[DIAGRAMA_VISUAL_FLUJO.md](DIAGRAMA_VISUAL_FLUJO.md)** (⏱️ 5 min lectura)
   - Diagramas ASCII del flujo actual (roto) vs esperado
   - Visualización de dónde falla cada parte
   - Dónde buscar problemas en logs
   - ✅ **LEER si eres visual o necesitas ver el flujo gráficamente**

### 🔧 DETALLES TÉCNICOS

4. **[DETALLES_ERRORES_Y_SOLUCIONES.md](DETALLES_ERRORES_Y_SOLUCIONES.md)** (⏱️ 15 min lectura)
   - Código actual INCORRECTO line-by-line
   - Código correcto esperado
   - Explicación de por qué cada línea está mal
   - Soluciones específicas
   - ✅ **LEER si necesitas ver el código exacto a cambiar**

5. **[CONCLUSIONES_ANALISIS_FINAL.md](CONCLUSIONES_ANALISIS_FINAL.md)** (⏱️ 20 min lectura)
   - Pregunta: "Qué hace el bot?" - Respuesta paso a paso
   - Pregunta: "Dónde falla?" - Análisis profundo
   - Pregunta: "Hay imports rotos?" - Lista completa
   - Score de diagnóstico
   - Pasos para arreglar
   - ✅ **LEER si quieres análisis exhaustivo**

---

## 🎯 RESPUESTAS A TUS PREGUNTAS

### P1: ¿Cuál es el punto de entrada principal?
**Respuesta rápida:** `app/webhook/entrypoint.py:handle_webhook()`

Detalles en:
- [RESUMEN_EJECUTIVO_1PAGINA.md#qué-pasa-cuando-recibes-un-mensaje](RESUMEN_EJECUTIVO_1PAGINA.md)
- [ANALISIS_FLUJO_WEBHOOK_NLP.md#1-punto-de-entrada-appwebhookentrypointpy](ANALISIS_FLUJO_WEBHOOK_NLP.md)

### P2: ¿Dónde se procesa el mensaje del usuario?
**Respuesta rápida:** `app/webhook/handlers.py:process_update_impl()` (línea 80)

Detalles en:
- [DIAGRAMA_VISUAL_FLUJO.md#-flujo-actual-roto](DIAGRAMA_VISUAL_FLUJO.md)
- [ANALISIS_FLUJO_WEBHOOK_NLP.md#4-manejo-de-chat-message](ANALISIS_FLUJO_WEBHOOK_NLP.md)

### P3: ¿Dónde se integra NLP/intent classifier?
**Respuesta rápida:** NO se integra. Debería estar en `handlers.py` pero no está.

Detalles en:
- [ANALISIS_FLUJO_WEBHOOK_NLP.md#el-code-de-nlp-existe-pero-nunca-se-ejecuta](ANALISIS_FLUJO_WEBHOOK_NLP.md)
- [CONCLUSIONES_ANALISIS_FINAL.md#problema-2-nlp-desconectado](CONCLUSIONES_ANALISIS_FINAL.md)

### P4: ¿Cómo se llama al action_mapper?
**Respuesta rápida:** Nunca se llama. Existe en `app/nlp/action_mapper.py` pero no se usa.

Detalles en:
- [DETALLES_ERRORES_Y_SOLUCIONES.md#problema-3-nlp-no-integrado-en-el-flujo-de-webhook](DETALLES_ERRORES_Y_SOLUCIONES.md)

### P5: ¿Hay errores de importación/inicialización?
**Respuesta rápida:** 
- ✅ NO hay imports en handlers.py que causen error
- ❌ PERO integration.py tiene SyntaxError que impide importarlo
- ❌ PERO handlers.py NO importa NLP, entonces nunca se ejecuta

Detalles en:
- [RESUMEN_EJECUTIVO_1PAGINA.md#imports-rotos](RESUMEN_EJECUTIVO_1PAGINA.md)
- [CONCLUSIONES_ANALISIS_FINAL.md#3-hay-imports-rotos](CONCLUSIONES_ANALISIS_FINAL.md)

---

## 📍 ARCHIVOS CLAVE DEL BOT (REFERENCIA)

```
app/
├── webhook/
│   ├── entrypoint.py         ← Punto entrada HTTP
│   ├── handlers.py           ← process_update_impl() aquí (LÍNEA 80)
│   │                           PROBLEMA: No integra NLP
│   └── bootstrap.py
├── telegram/
│   ├── dispatcher.py         ← dispatch_telegram_update() aquí
│   │                           OK: Clasifica bien
│   └── services.py
├── ops/
│   └── services.py           ← handle_chat_message() aquí (LÍNEA 22)
│                              PROBLEMA: Ignora NLP completamente
├── nlp/
│   ├── integration.py        ← ❌ ROTO: Indentación línea 31-78
│   │                           PROBLEMA: SyntaxError
│   ├── pipeline.py           ← Existe pero nunca se usa
│   ├── action_mapper.py      ← Existe pero nunca se llama
│   ├── intent_classifier.py  ← Existe pero desconectado
│   ├── ner.py                ← EntityExtractor aquí
│   ├── classifiers/
│   │   ├── ensemble_classifier.py   ← EnsembleIntentClassifier aquí
│   │   └── ml_classifier.py
│   └── ...
└── agent/
    └── core.py               ← agent.process() aquí
                               Usado al final por handle_chat_message()
```

---

## 🔴 PROBLEMAS IDENTIFICADOS

### CRÍTICA (Bloquea todo)

| # | Problema | Archivo | Línea | Impacto |
|---|----------|---------|-------|---------|
| 0 | SyntaxError indentación | `integration.py` | 31-78 | No se puede importar módulo |
| 1 | NLP no integrado | `handlers.py` | ~170-320 | NLP nunca se ejecuta |
| 2 | handle_chat_message ignora NLP | `services.py` | 22-40 | Agent único path |

### MEDIA

| # | Problema | Archivo | Línea | Impacto |
|---|----------|---------|-------|---------|
| 3 | IntentClassifier viejo | `integration.py` | 35-40 | Accuracy 50% en lugar de 81% |
| 4 | spaCy no instalado | `ner.py` | 36 | EntityExtractor debilitado |

---

## 📊 MATRIZ DE DECISIÓN

¿Cuál documento leer primero?

```
¿Tienes 2 min?
  → RESUMEN_EJECUTIVO_1PAGINA.md

¿Tienes 5 min?
  → + DIAGRAMA_VISUAL_FLUJO.md

¿Tienes 15 min?
  → + DETALLES_ERRORES_Y_SOLUCIONES.md

¿Tienes 30+ min?
  → Lee todos:
     1. RESUMEN_EJECUTIVO_1PAGINA.md (2 min)
     2. ANALISIS_FLUJO_WEBHOOK_NLP.md (10 min)
     3. DIAGRAMA_VISUAL_FLUJO.md (5 min)
     4. DETALLES_ERRORES_Y_SOLUCIONES.md (15 min)
     5. CONCLUSIONES_ANALISIS_FINAL.md (20 min)
```

---

## 🎓 CONTEXTO PREVIO

### Sesión anterior (fase2_diagnostico.md):
- NLP FASE 2 está 100% implementado
- Pero 0% integrado en el bot
- Problema: EnsembleIntentClassifier no se usa

### Esta sesión agrega:
- Análisis completo de por qué NLP está desconectado
- Error sintáctico en integration.py que impide importarlo
- Flujo completo paso a paso desde webhook
- Dónde debería integrase NLP pero no lo está
- Soluciones específicas

---

## ✅ VERIFICACIÓN

Para confirmar el análisis es correcto, corre:

```bash
# 1. Intenta importar integration
python -c "from app.nlp.integration import get_nlp_integration"
# Esperado: SyntaxError/IndentationError

# 2. Verifica que handlers NO importa NLP
grep -c "from app.nlp" app/webhook/handlers.py
# Esperado: 0

# 3. Verifica que services NO usa NLP
grep -c "nlp\|NLP\|integration" app/ops/services.py
# Esperado: 0
```

---

## 📞 PRÓXIMOS PASOS

1. **Lee el documento que corresponda a tu tiempo disponible**
2. **Identifica qué problemas afectan tu caso**
3. **Aplica los fixes en orden de prioridad**
4. **Prueba con tests**

Orden recomendado:
1. FIX #0: Fijar indentación integration.py (5 min)
2. FIX #1: Integrar NLP en handlers.py (30 min)
3. FIX #2: Cambiar a EnsembleClassifier (45 min)
4. FIX #3: Instalar spaCy (10 min)

**Tiempo total: ~90 minutos para solucionarlo completamente.**

---

## 📝 NOTAS

- Todos los documentos están en el root del proyecto
- Usa `CTRL+F` para buscar por palabra clave
- Los diagramas ASCII son directamente copiables
- Los códigos "correcto"/"incorrecto" son listos para copy-paste

