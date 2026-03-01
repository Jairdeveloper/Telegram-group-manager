# Webhooks — Qué son, por qué y cómo los usamos en Chat Manager Group Bot

Este documento explica en detalle qué son los webhooks, por qué los usamos en este proyecto y cómo los implementamos y desplegamos de forma segura y operable.

---

## 1) ¿Qué es un webhook?

- Un webhook es un mecanismo para que un servicio (proveedor) notifique a otro (cliente) sobre eventos empujando una petición HTTP a una URL configurada en el cliente.
- A diferencia del polling (donde el cliente consulta periódicamente al proveedor si hay novedades), con webhooks el proveedor envía la actualización inmediatamente cuando ocurre el evento.
- En términos prácticos: Telegram envía un POST a tu endpoint cada vez que hay un nuevo mensaje, actualización o evento relevante para el bot.

## 2) Polling vs Webhooks — diferencias importantes

- Polling:
  - Cliente consulta al API del proveedor repetidamente (frecuencia fija).
  - Simplicidad (útil en desarrollo), pero mayor latencia y uso de recursos.
- Webhooks:
  - Proveedor empuja updates al servidor del cliente en tiempo real.
  - Baja latencia, menos llamadas innecesarias, mejor escalabilidad para producción.

Por eso: en producción preferimos webhooks; para desarrollo y pruebas rápidas, long-polling (ya incluido como `telegram_adapter.py`) es aceptable.

## 3) ¿Por qué usamos webhooks en este proyecto?

- Latencia y UX: Respuestas más rápidas en grupos grandes (Telegram entrega update inmediatamente).
- Eficiencia: Evitamos ciclos inútiles de consulta y reducimos consumo de API (y costes si aplica).
- Escalabilidad: Con webhooks podemos integrar ingress, balanceadores y escalar el servicio receptor (stateless + cola).
- Seguridad operativa: Permite centralizar TLS/ingress con certificados gestionados (Let's Encrypt / cert-manager).

## 4) Cómo los usamos aquí (arquitectura y flujo)

1. Telegram envía un POST a `https://<your-domain>/webhook/<BOT_TOKEN>` configurado mediante `setWebhook`.
2. `telegram_webhook.py` (FastAPI) recibe la petición y valida el token en la ruta (y opcionalmente cabeceras o firma).
3. El adapter extrae `chat_id` y `text` y reenvía la entrada al Chat API interno (`/api/v1/chat`) para procesamiento por el `Agent`.
4. Para respuestas rápidas, el adapter puede:
   - Llamar a `/api/v1/chat` y, cuando obtenga la respuesta, invocar `sendMessage` de la API de Telegram para publicar la respuesta.
   - O bien, almacenar la petición en una cola (Redis/RabbitMQ) y devolver HTTP 200 inmediatamente; un worker consumirá la cola y usará `sendMessage`.

Diagram (simplificado):

Telegram -> Ingress (HTTPS) -> `telegram_webhook` (FastAPI) -> Chat API (`/api/v1/chat`) -> Agent -> Reply -> Telegram API (sendMessage)

## 5) Seguridad y validación

Recomendaciones concretas para producción:

- Endpoint secreto: usar path que incluya el `BOT_TOKEN` o un token secreto adicional para dificultar peticiones no autorizadas.
  - Ejemplo: `/webhook/<BOT_TOKEN>` o `/webhook/<BOT_TOKEN>?secret=<HMAC>`.
- TLS obligatorio: el endpoint debe estar expuesto solo en HTTPS; gestionar certificados con cert-manager/Let's Encrypt via Ingress.
- Validación de remitente: opcionalmente filtrar por rangos de IPs de Telegram (no siempre fiable) o validar cabeceras cuando el proveedor lo soporte.
- Rate limiting: proteger el endpoint con límites en el Ingress o proxys (NGINX, cloud LB) para evitar abuse.
- Idempotencia y deduplicación: procesar `update_id` de Telegram para evitar efectos por reenvíos y garantizar no procesar dos veces la misma update.

## 6) Consideraciones operativas

- Responder rápido: Telegram espera un 200 OK; si el procesamiento es pesado (LLM, embeddings), se recomienda responder 200 rápidamente y procesar en background.
- Retries: Si Telegram no recibe 200, reintentará la entrega; diseñar handlers idempotentes.
- Concurrency: usar una cola (Redis/RabbitMQ) para desacoplar recepción de updates y procesamiento LLM.
- Escalado: mantener `telegram_webhook` stateless; el estado de sesión reside en Postgres/Redis.

## 7) Local testing y desarrollo

- ngrok: exponer localmente tu API con `ngrok http 8000` y establecer el webhook a la URL pública devuelta por ngrok.
- set_telegram_webhook.py: en este repo hay `set_telegram_webhook.py` para registrar la URL pública con Telegram.
  - Ejemplo: `python set_telegram_webhook.py https://<your-ngrok>.ngrok.io/webhook/<BOT_TOKEN>`
- Alternativa: long-polling para desarrollo (`telegram_adapter.py`).

## 8) Implementación recomendada para este proyecto

1. En contenedores: desplegar `telegram_webhook.py` (FastAPI) detrás de un Ingress con TLS y autenticar la ruta con el `BOT_TOKEN`.
2. Ingress + cert-manager: ejemplo de anotaciones para cert-manager (NGINX ingress):

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: telegram-webhook-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
    - hosts:
        - chat.example.com
      secretName: telegram-tls
  rules:
    - host: chat.example.com
      http:
        paths:
          - path: /webhook/
            pathType: Prefix
            backend:
              service:
                name: telegram-webhook-svc
                port:
                  number: 80
```

Nota: configura la ruta final `/webhook/<BOT_TOKEN>` con la misma configuración al aplicar `setWebhook`.

## 9) Buenas prácticas de desarrollo/producción

- No bloquear la ruta: si el `Agent` realiza llamadas LLM largas, procesarlas en background y retornar 200 early.
- Monitoreo y trazabilidad: añadir logs correlacionados por `update_id` o `chat_id`, y métricas (latencia, rate, errores).
- Seguridad extra: usar HMAC en la URL o cabeceras con un secreto compartido si quieres más protección que solo el token en la ruta.
- Escucha de errores: instrumentar Sentry/Prometheus para alertas.

## 10) Cómo usar las utilidades del repo

- `telegram_webhook.py`: adaptador webhook (FastAPI). Desplegar este servicio accesible por HTTPS.
- `set_telegram_webhook.py`: script para hacer `setWebhook` con la URL pública.
- `telegram_adapter.py`: implementación de long-polling para desarrollo — no usar en producción.

Ejemplo rápido de registro del webhook (local con ngrok):

1. Inicia API y webhook service localmente:
```powershell
# terminal A
python chatbot_monolith.py --mode api

# terminal B
uvicorn telegram_webhook:app --host 0.0.0.0 --port 8001
```
2. Exponer con ngrok:
```bash
ngrok http 8001
```
3. Registrar webhook:
```bash
set TELEGRAM_BOT_TOKEN=123:ABC
python set_telegram_webhook.py https://<ngrok-id>.ngrok.io/webhook/123:ABC
```

## 11) Troubleshooting común

- No llegan updates: verificar que `setWebhook` devolvió `ok: true` y que la URL es accesible desde Internet.
- 401/403 en webhook: revisar token en la ruta y que `BOT_TOKEN` coincide.
- Retries constantes: tu endpoint retorna error o tarda demasiado; devolver 200 rápido y procesar asíncronamente.
- Mensajes duplicados: implementar deduplicación por `update_id`.

---

Si quieres, genero también:
- Un ejemplo de `Ingress` y `Deployment` completo (Helm-friendly) para Kubernetes con cert-manager.
- Un `docker-compose.yml` para simular HTTPS local con `ngrok` o Traefik + Let's Encrypt staging.

¿Cuál prefieres que añada ahora?

## 12) Manifiesto de Kubernetes de ejemplo (Deployment, Service, Ingress)

Adjunto en `deploy/telegram-webhook-deploy.yaml` encontrarás un manifiesto de ejemplo con:

- `Deployment` (réplicas = 2) con variable de entorno `TELEGRAM_BOT_TOKEN` consumida desde un `Secret`.
- `Service` (ClusterIP) que expone el puerto 80.
- `Ingress` configurado para `nginx-ingress` y `cert-manager` con anotaciones para ACME (Let's Encrypt).

Puntos clave del Ingress de ejemplo:

- Usa `nginx.ingress.kubernetes.io/use-regex: "true"` y `nginx.ingress.kubernetes.io/rewrite-target: /$2` para mapear
  rutas como `/webhook/<BOT_TOKEN>` hacia el servicio interno. La ruta definida es `/webhook/(.*)`.
- Define TLS via `spec.tls` y `secretName` (ej. `telegram-tls`) para que cert-manager gestione certificados.

Flujo de despliegue rápido:

1. Crea un Secret con el token del bot:
```bash
kubectl create secret generic telegram-bot-secret --from-literal=bot_token="123:ABC"
```
2. Ajusta `deploy/telegram-webhook-deploy.yaml` (imagen, dominio `chat.example.com`) y aplica:
```bash
kubectl apply -f deploy/telegram-webhook-deploy.yaml
```
3. Verifica que cert-manager obtuvo el certificado y que el `Secret` `telegram-tls` existe.
4. Registra el webhook en Telegram:
```bash
curl -X POST "https://api.telegram.org/bot123:ABC/setWebhook" -d "url=https://chat.example.com/webhook/123:ABC"
```

Notas ACME / Let's Encrypt:

- Instala `cert-manager` siguiendo la documentación oficial: https://cert-manager.io/docs/installation/
- Crea un `ClusterIssuer` para Let's Encrypt staging en pruebas y luego un issuer de producción:

  ```yaml
  apiVersion: cert-manager.io/v1
  kind: ClusterIssuer
  metadata:
    name: letsencrypt-staging
  spec:
    acme:
      server: https://acme-staging-v02.api.letsencrypt.org/directory
      email: your-email@example.com
      privateKeySecretRef:
        name: letsencrypt-staging
      solvers:
      - http01:
          ingress:
            class: nginx
  ```

- Reemplaza `server` por `https://acme-v02.api.letsencrypt.org/directory` para production (`letsencrypt-prod`).

Seguridad adicional y buenas prácticas:

- Validar `BOT_TOKEN` en la ruta del webhook y/o añadir HMAC en cabeceras para mayor seguridad.
- Implementar deduplicación por `update_id` y devolver 200 early si se procesa en background.
- Usar `NetworkPolicy` para limitar acceso interno al servicio webhook y exponer solo vía Ingress.
