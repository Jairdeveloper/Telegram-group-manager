# Estabilizacion ngrok - Pasos 4 y 6

Fecha: 2026-03-03

Este documento resume lo implementado para estabilizar el tunel ngrok y reducir errores intermitentes en webhook Telegram.

## Paso 4 aplicado: keepalive y timeouts

Se ajusto el runtime de `uvicorn` del webhook para conexiones mas estables:
- `--timeout-keep-alive 30`
- `--timeout-graceful-shutdown 30`

Archivos actualizados:
- `docker-compose.yml`
- `deploy/webhook-deployment.yaml`
- `deploy/telegram-webhook-deploy.yaml`
- `ARRANQUE_DEV_PROD.md` (comando local actualizado)

Objetivo:
- Reducir cierres prematuros de conexion y mejorar estabilidad frente a latencias temporales.

## Paso 6 aplicado: auto-sync de webhook cuando cambia URL ngrok

Se agrego script:
- `scripts/sync_ngrok_webhook.ps1`

Que hace:
1. Obtiene `TELEGRAM_BOT_TOKEN` desde variable de entorno o `.env`.
2. Lee la URL HTTPS activa de ngrok via `http://127.0.0.1:4040/api/tunnels`.
3. Construye la URL final: `https://<ngrok>/webhook/<TOKEN>`.
4. Ejecuta `setWebhook`.
5. Verifica `getWebhookInfo`.

## Uso operativo

1. Arranca API y webhook:
```powershell
python chatbot_monolith.py --mode api
uvicorn app.webhook.entrypoint:app --host 0.0.0.0 --port 80 --timeout-keep-alive 30 --timeout-graceful-shutdown 30
```

2. Arranca ngrok (en otra terminal):
```powershell
ngrok http 8001
```

3. Sincroniza webhook automaticamente:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/sync_ngrok_webhook.ps1
```

## Validacion recomendada

```powershell
curl http://127.0.0.1:8001/health
curl "https://api.telegram.org/bot$env:TELEGRAM_BOT_TOKEN/getWebhookInfo"
```

Revisar:
- `result.url` con token en path.
- `last_error_message` vacio o sin errores recientes.
- `pending_update_count` estable.

## Nota de operacion

Si ngrok cambia la URL (comun en plan free), debes re-ejecutar `scripts/sync_ngrok_webhook.ps1`.

Usa ngrok con subdominio reservado (plan de pago) para URL fija.
Sin URL fija, cada reinicio rompe webhook.

Mantén ngrok como servicio, no en terminal manual.
En Windows puedes usar nssm/Task Scheduler para autoarranque y autorestart.

Fija región cercana y baja latencia:

ngrok http --region=eu 8001
Configura keepalive y timeouts en tu app/proxy (ya tienes endpoint liviano, bien).
Evita que el webhook tarde demasiado antes de responder 200.

Monitorea salud continuamente:

GET /health local y público.
getWebhookInfo (last_error_message, pending_update_count).
Auto-reconfigura webhook cuando cambie URL ngrok (si usas free).
Script al arrancar ngrok:

lee URL del API local de ngrok (http://127.0.0.1:4040/api/tunnels)
ejecuta set_webhook_prod.py set <url>/webhook/<token>.
Para producción real, evita ngrok y usa dominio propio + reverse proxy (Nginx/Caddy) + TLS estable.
Es la forma más confiable para Telegram webhooks.