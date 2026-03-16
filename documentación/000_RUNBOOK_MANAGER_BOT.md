# RUNBOOK_MANAGER_BOT.md

> **Fecha**: 2026-03-11
> **Versión**: 1.0.0

---

## Descripción

ManagerBot es el dispatcher unificado del chatbot de manufactura. Maneja tres tipos de módulos:
- **OPS**: Comandos operativos (/health, /e2e, /webhookinfo, /logs)
- **Enterprise**: Comandos de gestión (/user, /ban, /rules, etc.)
- **Agent**: Agente autónomo con LLM (desactivado por defecto)

---

## Arquitectura

```
Telegram ──► Webhook ──► ManagerBot
                            │
                     ┌──────┴──────┐
                     ▼             ▼
                   OPS       Enterprise
                     │             │
                     └──────┬──────┘
                            ▼
                    chat_service (original)
                    
                    (optional) Agent Gateway
```

---

## Despliegue

### Requisitos

- Python 3.11+
- PostgreSQL
- Redis (opcional)
- Telegram Bot Token

### Variables de Entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Token del bot de Telegram | - |
| `WEBHOOK_TOKEN` | Token para validación de webhook | - |
| `MANAGER_ENABLE_OPS` | Habilitar módulo OPS | `true` |
| `MANAGER_ENABLE_ENTERPRISE` | Habilitar módulo Enterprise | `true` |
| `MANAGER_ENABLE_AGENT` | Habilitar agente autónomo | `false` |
| `AGENT_SERVICE_URL` | URL del servicio de agente | `http://localhost:8001` |

### Producción

```bash
# Build
docker build -t manager-bot:latest .

# Run
docker run -d \
  --name manager-bot \
  -e TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN \
  -e WEBHOOK_TOKEN=$WEBHOOK_TOKEN \
  -p 8080:8080 \
  manager-bot:latest

# Configurar webhook
curl -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setWebhook" \
  -d "url=https://tu-dominio.com/webhook/${WEBHOOK_TOKEN}"
```

### Desarrollo

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables
cp .env.example .env
# Editar .env con tus valores

# Ejecutar
uvicorn app.webhook.entrypoint:app --reload --port 8080

# Configurar webhook para desarrollo
python set_telegram_webhook.py
```

---

## Comandos Disponibles

### OPS (Administrativos)

| Comando | Descripción | Permiso |
|---------|-------------|---------|
| `/health` | Estado de API y Webhook | admin |
| `/e2e` | Ejecutar checks E2E | admin |
| `/webhookinfo` | Información del webhook | admin |
| `/logs` | Últimos eventos | admin |

### Enterprise (Gestión)

| Comando | Descripción | Permiso |
|---------|-------------|---------|
| `/adminhelp` | Lista de comandos admin | admin |
| `/user add <id> <rol>` | Agregar usuario | admin |
| `/user list` | Listar usuarios | admin |
| `/ban <id> [reason]` | Banear usuario | admin |
| `/unban <id>` | Desbanear usuario | admin |
| `/rules` | Ver reglas | user |
| `/setrules <texto>` | Establecer reglas | admin |
| `/welcome` | Ver mensaje de bienvenida | user |
| `/setwelcome <texto>` | Establecer bienvenida | admin |
| `/note <nombre>` | Ver nota | user |
| `/notes` | Listar notas | user |
| `/setnote <nombre> <texto>` | Establecer nota | admin |
| `/filter add <patron>` | Agregar filtro | admin |
| `/filter list` | Listar filtros | admin |
| `/antispam <on/off/status>` | Configurar antispam | admin |
| `/blacklist add <patron>` | Agregar a blacklist | admin |
| `/whoami` | Ver mi rol | user |
| `/fun` | Toggle modo fun | user |
| `/reactions <texto>` | Reacciones automáticas | user |
| `/anilist <titulo>` | Buscar anime | user |
| `/wallpaper [tema]` | Obtener wallpaper | user |
| `/gettime [zona]` | Obtener hora | user |

---

## Endpoints

### Health

```bash
curl https://bot.example.com/health
```

Respuesta:
```json
{"status": "ok"}
```

### Manager Health

```bash
curl https://bot.example.com/manager/health
```

Respuesta:
```json
{
  "status": "ok",
  "modules": {
    "ops": {"status": "ok", "module": "ops"},
    "enterprise": {"status": "ok", "module": "enterprise"},
    "agent": {"status": "ok", "module": "agent"}
  },
  "enabled_modules": ["ops", "enterprise"]
}
```

### Webhook

```
POST /webhook/{token}
```

### Metrics

```bash
curl https://bot.example.com/metrics
```

---

## Troubleshooting

### El bot no responde

1. **Verificar webhook configurado**:
   ```bash
   curl "https://api.telegram.org/bot${TOKEN}/getWebhookInfo"
   ```

2. **Verificar logs**:
   ```bash
   docker logs manager-bot
   ```

3. **Verificar token**:
   ```bash
   echo $TELEGRAM_BOT_TOKEN
   ```

4. **Ejecutar comando de diagnóstico**:
   Envía `/health` al bot

### Error 403 Forbidden

- El token de webhook es incorrecto
- Verificar que `WEBHOOK_TOKEN` coincida con el path

### Error de conexión a base de datos

1. Verificar variables de entorno de DB
2. Revisar logs de PostgreSQL
3. Verificar conectividad: `pg_isready -h <host> -p 5432`

### Módulo Enterprise deshabilitado

Verificar que `MANAGER_ENABLE_ENTERPRISE=true` está configurado.

### Agent no funciona

1. Verificar que `MANAGER_ENABLE_AGENT=true`
2. Verificar que `AGENT_SERVICE_URL` es accesible
3. Revisar logs del servicio de agente

---

## Feature Flags

Los feature flags permiten controlar qué módulos están activos sin re-desplegar.

| Flag | Módulo | Default | Descripción |
|------|--------|---------|-------------|
| `MANAGER_ENABLE_OPS` | OPS | `true` | Comandos operativos |
| `MANAGER_ENABLE_ENTERPRISE` | Enterprise | `true` | Funcionalidad Enterprise |
| `MANAGER_ENABLE_AGENT` | Agent | `false` | Agente autónomo (LLM) |

---

## Migración desde Legacy

### Entry points obsoletos

Los siguientes entry points están **deprecated** y no deben ejecutarse en paralelo:

- `telegram_adapter.py` - Legacy adapter
- `app/telegram_ops/entrypoint.py` - OPS polling (migrado a webhook)

### Nuevo flujo

1. Usar solo `app.webhook.entrypoint:app` como entrypoint
2. Configurar webhook de Telegram hacia ese endpoint
3. Los comandos OPS y Enterprise se manejan vía webhook

---

## Métricas

### Prometheus

El endpoint `/metrics` expone métricas de Prometheus:

- `requests_total` - Total de requests
- `process_time_seconds` - Tiempo de procesamiento
- `chat_api_errors_total` - Errores de API
- `telegram_send_errors_total` - Errores de envío a Telegram

---

## Contacto

Para soporte, contactar al equipo de desarrollo.
