# Debug: Aplicación/Bot no responde

## Estado: ⏳ EN PROGRESO

### Archivos de debug por fase

| Fase | Archivo | Estado |
|------|---------|--------|
| Fase 0 | debug/00_debug.md | ✅ Completado |
| Fase 1 | debug/01_debug.md | ⏳ Pendiente ejecutar |

---

## Resumen de problemas identificados

### Problemas resueltos
| Problema | Solución |
|----------|----------|
| ADMIN_CHAT_IDS inválido | Cambiado a vacío (permite todos) |
| check_webhook_local() usaba WEBHOOK_TOKEN | Corregido a TELEGRAM_TOKEN |
| WEBHOOK_PORT=8443 | Corregido a 8001 |

---

## Ejecución de Debug

### Paso 1: Ejecutar comandos en Terminal

Los servicios deben estar corriendo. Ver `debug/01_debug.md` para detalles.

### Resumen de comandos:

```powershell
# Terminal 1: API
.\.venv\Scripts\python.exe -m uvicorn app.api.entrypoint:app --host 127.0.0.1 --port 8000

# Terminal 2: Webhook
.\.venv\Scripts\python.exe -m uvicorn app.webhook.entrypoint:app --host 127.0.0.1 --port 8001

# Terminal 3: Bot
.\.venv\Scripts\python.exe -m app.telegram_ops.entrypoint
```

### Paso 2: Verificar

```bash
curl http://127.0.0.1:8000/health  # Debe dar {"status":"ok"}
curl http://127.0.0.1:8001/health  # Debe dar {"status":"ok"}
```

---

## Tabla de tokens

| Variable | Valor |
|----------|-------|
| TELEGRAM_BOT_TOKEN | 8588716358:AAGw3RX94SyEeM1UxM-3sGPPs83n3IM2qJw |
| WEBHOOK_TOKEN | mysecretwebhooktoken |
| ADMIN_CHAT_IDS | (vacío = permite todos) |

---

## Si sigue sin funcionar

1. Verificar que el entorno virtual tiene las dependencias:
   ```bash
   .\.venv\Scripts\pip.exe install -r requirements.txt
   ```

2. Verificar que no hay errores en los logs de las terminales
