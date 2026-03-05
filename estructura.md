# Estructura del Proyecto

## Vista General

```
manufacturing/robot/
├── app/                        # Código principal de la aplicación
│   ├── api/                    # Módulo API
│   ├── webhook/                # Módulo Webhook
│   ├── config/                 # Configuración centralizada
│   └── telegram_ops/          # Bot de Telegram para E2E checks
├── chat_service/               # Servicio de chat (lógica de negocio)
├── tests/                      # Pruebas unitarias e integración
├── scripts/                    # Scripts auxiliares
├── deploy/                     # Configuración Kubernetes
├── design/                     # Documentación de diseño
├── docs/                       # Documentación adicional
│
├── telegram_adapter.py         # Adapter de Telegram (polling)
├── telegram_ops/               # Módulo legacy de telegram_ops
├── worker.py                   # Worker para procesamiento async
├── webhook_tasks.py            # Tareas del worker
├── set_telegram_webhook.py     # Script para configurar webhook
├── set_webhook_prod.py         # Script para producción
│
├── .env                        # Variables de entorno
├── requirements.txt            # Dependencias Python
├── docker-compose.yml          # Orquestación Docker
├── Dockerfile                  # Imagen del contenedor
│
└── *.md                        # Documentación del proyecto
```

---

## Directorio `app/`

```
app/
├── __init__.py
├── api/
│   ├── __init__.py
│   ├── entrypoint.py           # Entry point canónico de API
│   ├── bootstrap.py             # Bootstrap de dependencias API
│   ├── factory.py              # Factory para crear app
│   └── routes.py               # Rutas de la API
│
├── webhook/
│   ├── __init__.py
│   ├── entrypoint.py           # Entry point canónico de Webhook
│   ├── bootstrap.py            # Bootstrap de dependencias Webhook
│   ├── handlers.py             # Lógica de negocio del webhook
│   ├── ports.py                # Interfaces/contratos
│   └── infrastructure.py       # Implementaciones de infraestructura
│
├── config/
│   ├── __init__.py
│   └── settings.py             # Configuración centralizada (Pydantic)
│
└    ├── __init__.py
    ├──── telegram_ops/
 entrypoint.py           # Bot de Telegram (comandos E2E)
    └── checks.py               # Funciones de verificación
```

### Descripción de archivos `app/api/`

| Archivo | Descripción |
|---------|-------------|
| `entrypoint.py` | Punto de entrada canónico `app.api.entrypoint:app` |
| `bootstrap.py` | Construye runtime (logger, agent, storage) |
| `factory.py` | Factory que crea la app FastAPI con rutas |
| `routes.py` | Rutas: `/chat`, `/history/{session_id}`, `/stats` |

### Descripción de archivos `app/webhook/`

| Archivo | Descripción |
|---------|-------------|
| `entrypoint.py` | Punto de entrada canónico `app.webhook.entrypoint:app` |
| `bootstrap.py` | Construye runtime (bot_token, api_client, dedup, queue) |
| `handlers.py` | Lógica: validación token, dedup, process_update |
| `ports.py` | Interfaces: ChatApiClient, DedupStore, TaskQueue, TelegramClient |
| `infrastructure.py` | Implementaciones: InMemoryDedupStore, RedisDedupStore, RequestsChatApiClient, RequestsTelegramClient, RqTaskQueue |

### Descripción de archivos `app/telegram_ops/`

| Archivo | Descripción |
|---------|-------------|
| `entrypoint.py` | Bot con comandos: /health, /e2e, /webhookinfo, /logs |
| `checks.py` | Funciones: check_api_health, check_webhook_health, get_webhook_info, run_e2e_check |

---

## Directorio `chat_service/`

```
chat_service/
├── __init__.py
├── agent.py              # Agente principal
├── brain.py              # Cerebro del agente
├── pattern_engine.py     # Motor de patrones
└── storage.py           # Almacenamiento en memoria
```

| Archivo | Descripción |
|---------|-------------|
| `agent.py` | Agente que procesa mensajes |
| `brain.py` | Lógica de procesamiento de lenguaje |
| `pattern_engine.py` | Motor de patrones/keywords |
| `storage.py` | Almacenamiento in-memory de conversaciones |

---

## Directorio `tests/`

```
tests/
├── __init__.py
├── conftest.py                    # Configuración pytest
├── test_api_contract.py           # Tests de contrato API
├── test_webhook_contract.py       # Tests de contrato Webhook
├── test_modular_entrypoints.py    # Tests de entrypoints
├── test_compose_regression.py     # Tests de regresión
├── test_ingress_regression.py     # Tests de ingress
├── test_agent_unit.py             # Tests unitarios del agente
├── test_pattern_engine_unit.py    # Tests del pattern engine
├── test_settings_unit.py          # Tests de configuración
├── test_bootstrap_unit.py         # Tests de bootstrap
└── test_webhook_handlers_unit.py  # Tests de handlers
```

---

## Directorio `scripts/`

```
scripts/
└── get_chat_id.py        # Script para obtener Chat ID
```

---

## Directorio `deploy/`

```
deploy/
├── webhook-deployment.yaml
├── worker-deployment.yaml
├── telegram-webhook-deploy.yaml
└── secret-telegram-bot.yaml
```

---

## Archivos de configuración raíz

| Archivo | Descripción |
|---------|-------------|
| `.env` | Variables de entorno |
| `requirements.txt` | Dependencias Python |
| `docker-compose.yml` | Orquestación Docker |
| `Dockerfile` | Imagen del contenedor |

---

## Flujo de datos

### Modo Polling (desarrollo)

```
Telegram ──► @cmb_robot ──► telegram_adapter.py
                                      │
                                      ▼
                              API (puerto 8000)
                              /api/v1/chat
                                      │
                                      ▼
                              chat_service/
                              (agent + brain + storage)
```

### Modo Webhook (producción)

```
Telegram ──► Internet ──► ngrok ──► Webhook (puerto 8001)
                                        │
                                        ▼
                                app/webhook/
                                (handlers + validation)
                                        │
                                        ▼
                                API (puerto 8000)
```

### Bot E2E (Telegram OPS)

```
Usuario ──► /e2e ──► app/telegram_ops/
                              │
                              ├── check_api_health()
                              ├── check_webhook_health()
                              ├── check_webhook_local()
                              └── get_webhook_info()
```

---

## Puertos

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| API | 8000 | API REST del chatbot |
| Webhook | 8001 | Endpoint de webhook |
| Redis | 6379 | Cola de tareas (opcional) |
| ngrok | 4040 | Interfaz de ngrok |

---

## Endpoints

### API (puerto 8000)

| Método | Path | Descripción |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/chat` | Procesar mensaje |
| GET | `/api/v1/history/{session_id}` | Historial de sesión |
| GET | `/api/v1/stats` | Estadísticas |
| GET | `/docs` | Documentación OpenAPI |

### Webhook (puerto 8001)

| Método | Path | Descripción |
|--------|------|-------------|
| POST | `/webhook/{token}` | Recibir updates de Telegram |
| GET | `/health` | Health check |
| GET | `/metrics` | Métricas Prometheus |

---

## Variables de entorno

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| TELEGRAM_BOT_TOKEN | Token del bot de Telegram | `123456:ABC...` |
| CHATBOT_API_URL | URL de la API | `http://127.0.0.1:8000/api/v1/chat` |
| REDIS_URL | URL de Redis | `redis://127.0.0.1:6379/0` |
| PROCESS_ASYNC | Modo async | `true`/`false` |
| DEDUP_TTL | TTL para dedup | `86400` |
| API_HOST | Host de API | `127.0.0.1` |
| API_PORT | Puerto de API | `8000` |
| WEBHOOK_PORT | Puerto de webhook | `8001` |
| WEBHOOK_TOKEN | Token del webhook | `mysecretwebhooktoken` |
| ADMIN_CHAT_IDS | IDs de admins | `123456789` |
| LOG_LEVEL | Nivel de logs | `INFO` |

---

## Bibliotecas principales

| Biblioteca | Uso |
|------------|-----|
| FastAPI | Framework web |
| python-telegram-bot | Bot de Telegram |
| httpx | Cliente HTTP async |
| pydantic | Validación de configuración |
| prometheus_client | Métricas |
| redis | Cola de tareas |
| python-dotenv | Carga de variables de entorno |
