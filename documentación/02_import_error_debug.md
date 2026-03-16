# Issue: Import Error - Relative Import with No Known Parent Package (Debug VS Code)

## Error

```
ImportError: attempted relative import with no known parent package
  File "...\app\webhook\handlers.py", line 24
    from .ports import ChatApiClient, DedupStore, TaskQueue, TelegramClient
```

## Causa

El error ocurre cuando se ejecuta el debug desde **VS Code con una configuración incorrecta**.

El problema es que estabas ejecutando el debug de manera que Python no reconocía el módulo como parte del paquete `app.webhook`. Esto pasa cuando:

1. VS Code ejecuta el archivo `handlers.py` directamente como script
2. O el `PYTHONPATH` no está configurado correctamente

## Solución

Se ha creado el archivo `.vscode/launch.json` con la configuración correcta.

### Configuración creada:

```json
{
    "name": "Python: Robot (Webhook)",
    "type": "debugpy",
    "request": "launch",
    "module": "uvicorn",
    "args": [
        "app.webhook.entrypoint:app",
        "--host", "0.0.0.0",
        "--port", "8000"
    ],
    "env": {
        "PYTHONPATH": "${workspaceFolder}",
        "BOT_TOKEN": "${env:BOT_TOKEN}",
        "WEBHOOK_TOKEN": "${env:WEBHOOK_TOKEN}",
        "CHATBOT_API_URL": "${env:CHATBOT_API_URL}",
        "DATABASE_URL": "${env:DATABASE_URL}",
        "REDIS_URL": "${env:REDIS_URL}",
        "ENVIRONMENT": "development"
    },
    "console": "integratedTerminal",
    "justMyCode": true,
    "subProcess": true
}
```

### Claves de la configuración:

| Propiedad | Valor | Propósito |
|-----------|-------|-----------|
| `module` | `"uvicorn"` | Ejecuta como módulo, no como archivo |
| `args` | `"app.webhook.entrypoint:app"` | Apunta al entrypoint正确 |
| `PYTHONPATH` | `"${workspaceFolder}"` | Asegura que `app` sea reconocible como paquete |
| `console` | `"integratedTerminal"` | Usa la terminal integrada de VS Code |

## Cómo usar

1. Ve a **Run and Debug** (Ctrl+Shift+D)
2. Selecciona **"Python: Robot (Webhook)"**
3. Presiona **F5** para iniciar el debug

## Puntos de Interrupción recomendados

Para hacer debug del flujo completo, usa estos breakpoints:

| Archivo | Línea | Función |
|---------|-------|---------|
| `app/webhook/entrypoint.py` | 108 | `webhook()` - Entry point del webhook |
| `app/webhook/handlers.py` | 252 | `handle_webhook_impl()` |
| `app/webhook/handlers.py` | 34 | `process_update_impl()` |
| `app/telegram/dispatcher.py` | 34 | `dispatch_telegram_update()` |
| `app/ops/services.py` | 242 | `handle_ops_command()` |

---

## Resumen

| Método de debug | Resultado |
|-----------------|-----------|
| `"Python: Robot (Webhook)"` con launch.json | ✅ Funciona |
| `"Python: Current File"` en handlers.py | ❌ ImportError |
| `python app/webhook/handlers.py` | ❌ ImportError |
| `robot` en terminal | ✅ Funciona (sin debug) |
