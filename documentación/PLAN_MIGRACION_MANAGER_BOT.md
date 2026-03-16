# PLAN_MIGRACION_MANAGER_BOT.md

> **Fecha**: 2026-03-11
> **Proyecto**: Chatbot Manufacturing
> **Objetivo**: Unificar el bot bajo ManagerBot y separar la proyección del agente autónomo

---

## Resumen Ejecutivo

El proyecto actualmente tiene dos entrypoints separados (`app/webhook/entrypoint.py` y `app/telegram_ops/entrypoint.py`) con funcionalidad mezclada. El plan propone crear un `ManagerBot` unificado como dispatcher central y aislar el agente autónomo como servicio independiente.

---

## FASE 0: Baseline y Router Unificado

### Objetivo
Crear la estructura base del ManagerBot con un router único que delegue a los módulos existentes sin romper funcionalidad.

### Steps

#### 0.1 Crear estructura de ManagerBot

```python
app/manager_bot/
├── __init__.py
├── core.py           # ManagerBot principal
├── registry.py       # Registro de módulos
├── settings.py       # Configuración
└── transport/
    └── telegram/
        ├── __init__.py
        └── router.py # Router unificado
```

#### 0.2 Implementar core.py

- Crear clase `ManagerBot` que inicialice:
  - Configuración desde `app.config.settings`
  - Registry de módulos
  - Router de Telegram
- Exponer método `register_module(module: Module)` 
- Exponer método `get_router()` que devuelve el router FastAPI

#### 0.3 Implementar registry.py

```python
class ModuleRegistry:
    """Registro central de módulos"""
    
    def __init__(self):
        self._modules: Dict[str, Module] = {}
    
    def register(self, module: Module) -> None:
        """Registrar módulo con su feature flag"""
        self._modules[module.name] = module
    
    def get_module(self, name: str) -> Optional[Module]:
        return self._modules.get(name)
    
    def is_enabled(self, name: str) -> bool:
        module = self._modules.get(name)
        return module.is_enabled() if module else False
    
    def list_routes(self) -> List[Route]:
        """Listar todas las rutas registradas"""
        routes = []
        for module in self._modules.values():
            if module.is_enabled():
                routes.extend(module.get_routes())
        return routes
```

#### 0.4 Definir contrato de Module

```python
from dataclasses import dataclass
from typing import List, Callable, Dict, Any
from pydantic import BaseModel

class ModuleContract(BaseModel):
    name: str
    version: str
    feature_flag: str  # e.g., "MANAGER_ENABLE_OPS"
    routes: List[str]
    permissions: List[str]

class Module:
    """Interfaz que deben implementar todos los módulos"""
    
    @property
    def contract(self) -> ModuleContract:
        raise NotImplementedError
    
    def is_enabled(self) -> bool:
        """Verificar feature flag"""
        import os
        return os.getenv(self.contract.feature_flag, "false").lower() == "true"
    
    def get_handlers(self) -> Dict[str, Callable]:
        """Devolver handlers del módulo"""
        raise NotImplementedError
    
    def health_check(self) -> Dict[str, Any]:
        """Opcional: health check del módulo"""
        return {"status": "ok"}
```

#### 0.5 Crear transport/telegram/router.py

- Mover lógica de routing de `app/webhook/handlers.py`
- Implementar `route_update(update: Dict)` que:
  1. Clasifique el tipo de mensaje (ops_command, enterprise_command, chat)
  2. Busque el módulo correspondiente en el registry
  3. Delegue al handler apropiado
- Mantener compatibilidad con el flujo actual

#### 0.6 Actualizar entrypoint principal

Modificar `app/webhook/entrypoint.py`:

```python
from app.manager_bot.core import ManagerBot

# Crear ManagerBot
manager = ManagerBot()

# Registrar módulos existentes (se implementarán en fases siguientes)
# Por ahora, solo registrar el router

app = manager.get_app()  # FastAPI app

# Rutas existentes
app.include_router(manager.get_router())
```

#### 0.7 Validación

- [ ] Un solo ingress operativo: `app.webhook.entrypoint:app`
- [ ] Sin runtimes paralelos para el mismo token
- [ ] Tests pasan con la nueva estructura
- [ ] Feature flags configurados en `.env`

---

## FASE 1: Migrar OPS como Módulo Registrado

### Objetivo
Mover comandos OPS (`/health`, `/e2e`, `/webhookinfo`, `/logs`) al módulo `ops` dentro del ManagerBot.

### Steps

#### 1.1 Crear módulo OPS

```python
app/manager_bot/application/
└── ops/
    ├── __init__.py
    ├── commands.py      # Definición de comandos
    └── services.py     # Lógica de negocio (reutilizar app/ops/services.py)
```

#### 1.2 Definir comandos OPS

```python
# app/manager_bot/application/ops/commands.py
from dataclasses import dataclass
from typing import List

@dataclass
class OpsCommand:
    name: str
    handler: Callable
    description: str
    admin_only: bool = True

OPS_COMMANDS = [
    OpsCommand("/health", health_command, "Estado de API y Webhook"),
    OpsCommand("/e2e", e2e_command, "Ejecutar checks E2E"),
    OpsCommand("/webhookinfo", webhookinfo_command, "Info de webhook"),
    OpsCommand("/logs", logs_command, "Últimos eventos"),
]
```

#### 1.3 Implementar OpsModule

```python
# app/manager_bot/application/ops/__init__.py
from app.manager_bot.core import Module, ModuleContract

class OpsModule(Module):
    @property
    def contract(self) -> ModuleContract:
        return ModuleContract(
            name="ops",
            version="1.0.0",
            feature_flag="MANAGER_ENABLE_OPS",
            routes=["/health", "/e2e", "/webhookinfo", "/logs"],
            permissions=["admin"]
        )
    
    def get_handlers(self) -> Dict[str, Callable]:
        return {cmd.name: cmd.handler for cmd in OPS_COMMANDS}
    
    def is_enabled(self) -> bool:
        import os
        return os.getenv("MANAGER_ENABLE_OPS", "true").lower() == "true"
```

#### 1.4 Migrar lógica de servicios

- Reutilizar `app/ops/services.py` existente
- Crear thin wrappers en `app/manager_bot/application/ops/services.py`
- Mantener compatibilidad de contratos

#### 1.5 Registrar OPS en ManagerBot

```python
# En app/manager_bot/core.py
from app.manager_bot.application.ops import OpsModule

class ManagerBot:
    def __init__(self):
        self.registry = ModuleRegistry()
        self._register_default_modules()
    
    def _register_default_modules(self):
        # OPS siempre habilitado por defecto
        self.registry.register(OpsModule())
```

#### 1.6 Eliminar app/telegram_ops/entrypoint.py

Una vez migrado y validado:
- Eliminar el entrypoint de polling separado
- Eliminar `logs/telegram_ops.pid` y locks relacionados
- Actualizar documentación de despliegue

#### 1.7 Validación

- [ ] Comandos `/health`, `/e2e`, `/webhookinfo`, `/logs` funcionan via webhook
- [ ] Mismo comportamiento que `telegram_ops/entrypoint.py`
- [ ] Feature flag `MANAGER_ENABLE_OPS` funciona
- [ ] Sin conflictos de tokens

---

## FASE 2: Migrar Enterprise como Módulo Registrado

### Objetivo
Envolver handlers Enterprise existentes como casos de uso registrados en el ManagerBot.

### Steps

#### 2.1 Analizar comandos Enterprise

Listar comandos existentes y sus handlers:
- `/start` - Mensaje de bienvenida
- `/help` - Ayuda
- `/admin` - Panel de admin
- Comandos de billing, users, etc.

#### 2.2 Crear módulo Enterprise

```python
app/manager_bot/application/
└── enterprise/
    ├── __init__.py
    ├── commands.py      # Definición de comandos
    └── services.py     # Reutilizar app/enterprise/services.py
```

#### 2.3 Definir contratos de permisos

```python
# app/manager_bot/application/enterprise/commands.py
from dataclasses import dataclass
from typing import List

@dataclass
class EnterpriseCommand:
    name: str
    handler: Callable
    description: str
    required_permissions: List[str]

ENTERPRISE_COMMANDS = [
    EnterpriseCommand("/start", start_command, "Bienvenida", []),
    EnterpriseCommand("/admin", admin_command, "Panel admin", ["admin"]),
    # ... otros comandos
]
```

#### 2.4 Implementar EnterpriseModule

```python
# app/manager_bot/application/enterprise/__init__.py
from app.manager_bot.core import Module, ModuleContract

class EnterpriseModule(Module):
    @property
    def contract(self) -> ModuleContract:
        return ModuleContract(
            name="enterprise",
            version="1.0.0",
            feature_flag="MANAGER_ENABLE_ENTERPRISE",
            routes=["/start", "/help", "/admin", ...],
            permissions=["user", "admin"]
        )
```

#### 2.5 Centralizar Policy Checks

- Mover verificaciones de permisos a `app/manager_bot/policies/`
- Crear middleware de authorization:
```python
# app/manager_bot/policies/authorization.py
async def authorize(module: Module, user_id: int, command: str) -> bool:
    """Verificar permisos antes de ejecutar comando"""
    permissions = get_user_permissions(user_id)
    required = module.get_required_permissions(command)
    return has_permissions(permissions, required)
```

#### 2.6 Actualizar handlers existentes

- Wrappers para mantener compatibilidad
- Middleware de logging unificado
- Manejo de errores consistente

#### 2.7 Registrar en ManagerBot

```python
self.registry.register(EnterpriseModule())
```

#### 2.8 Validación

- [ ] Comandos Enterprise funcionan vía webhook
- [ ] Permisos centralizados
- [ ] Policy checks antes de ejecución
- [ ] Feature flag `MANAGER_ENABLE_ENTERPRISE` funciona

---

## FASE 3: Aislamiento del Agente Autónomo

### Objetivo
Separar la proyección del agente autónomo (LLM + memoria + RAG) como servicio independiente.

### Decisión Arquitectónica

**Opción recomendada**: Servicio separado con API REST/gRPC.

### Steps

#### 3.1 Crear servicio de agente (nuevo)

```
agent_service/
├── app/
│   ├── agent/
│   │   ├── core.py          # Agent ReAct
│   │   ├── intent_router.py # Clasificación
│   │   ├── memory.py       # Sistema de memoria
│   │   └── rag.py          # RAG service
│   ├── api/
│   │   └── routes.py       # Endpoints REST
│   └── config/
│       └── settings.py
├── chat_service/
│   └── llm/               # Integración LLM
├── docker-compose.yml
└── requirements.txt
```

#### 3.2 Definir contrato de API

```python
# agent_service/app/api/routes.py
from fastapi import FastAPI
from pydantic import BaseModel

class AgentRequest(BaseModel):
    message: str
    session_id: str
    context: dict = {}

class AgentResponse(BaseModel):
    response: str
    confidence: float
    sources: list = []

app = FastAPI()

@app.post("/chat", response_model=AgentResponse)
async def chat(request: AgentRequest):
    # Procesar con Agent Core
    pass

@app.get("/health")
async def health():
    return {"status": "ok", "agent": "ready"}
```

#### 3.3 Crear AgentGateway en ManagerBot

```python
# app/manager_bot/application/agent_gateway.py
import httpx
from typing import Optional

class AgentGateway:
    """Gateway para comunicarse con el servicio de agente"""
    
    def __init__(self, agent_url: str = None):
        import os
        self.agent_url = agent_url or os.getenv("AGENT_SERVICE_URL", "http://localhost:8001")
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def chat(self, message: str, session_id: str, context: dict = None) -> dict:
        """Enviar mensaje al agente"""
        response = await self.client.post(
            f"{self.agent_url}/chat",
            json={"message": message, "session_id": session_id, "context": context or {}}
        )
        response.raise_for_status()
        return response.json()
    
    async def health_check(self) -> bool:
        """Verificar si el servicio de agente está disponible"""
        try:
            response = await self.client.get(f"{self.agent_url}/health")
            return response.status_code == 200
        except Exception:
            return False
    
    async def close(self):
        await self.client.aclose()
```

#### 3.4 Crear AgentModule (stub)

```python
# app/manager_bot/application/agent/__init__.py
from app.manager_bot.core import Module, ModuleContract

class AgentModule(Module):
    """Módulo stub que delega al servicio externo"""
    
    def __init__(self, gateway: AgentGateway):
        self.gateway = gateway
    
    @property
    def contract(self) -> ModuleContract:
        return ModuleContract(
            name="agent",
            version="1.0.0",
            feature_flag="MANAGER_ENABLE_AGENT",
            routes=["/agent/chat"],
            permissions=["user"]
        )
    
    def is_enabled(self) -> bool:
        import os
        return os.getenv("MANAGER_ENABLE_AGENT", "false").lower() == "true"
```

#### 3.5 Integrar en flujo de chat

Modificar `process_update_impl` en `app/webhook/handlers.py`:

```python
# Cuando dispatch.kind == "chat" y MANAGER_ENABLE_AGENT=true
if dispatch.kind == "chat":
    if agent_module.is_enabled():
        # Usar AgentGateway
        result = await agent_gateway.chat(
            message=dispatch.text,
            session_id=str(chat_id),
            context={"user_id": dispatch.user_id}
        )
        reply = result["response"]
    else:
        # Usar chat_service actual
        result = handle_chat_message_fn(chat_id, dispatch.text)
        reply = result.get("response", "(no response)")
```

#### 3.6 Feature Flags

```bash
# .env
MANAGER_ENABLE_AGENT=false  # Por defecto desactivado
AGENT_SERVICE_URL=http://agent-service:8001
```

#### 3.7 Validación

- [ ] AgentGateway se conecta al servicio externo
- [ ] Feature flag controla activación
- [ ] Fallback a chat_service si agente no disponible
- [ ] Sin dependencias directas del bot hacia core del agente

---

## FASE 4: Limpieza y Documentación

### Objetivo
Eliminar código legacy y unificar runbook de operación.

### Steps

#### 4.1 Deprecar entrypoints legacy

- Eliminar `telegram_adapter.py` si ya no se usa
- Eliminar referencias a entrypoints antiguos
- Limpiar imports obsoletos

#### 4.2 Unificar logging

- Consolidar en `app/manager_bot/telemetry/`
- Métricas comunes para todos los módulos

#### 4.3 Documentar runbook

Crear `RUNBOOK_MANAGER_BOT.md`:

```markdown
# Runbook ManagerBot

## Despliegue

### Producción
```bash
# Build y deploy
docker build -t manager-bot:latest .
docker push registry/manager-bot:latest

# Desplegar
kubectl apply -f deploy/production/
```

### Configuración

| Variable | Descripción | Default |
|----------|-------------|---------|
| MANAGER_ENABLE_OPS | Habilitar módulo OPS | true |
| MANAGER_ENABLE_ENTERPRISE | Habilitar módulo Enterprise | true |
| MANAGER_ENABLE_AGENT | Habilitar agente autónomo | false |
| AGENT_SERVICE_URL | URL del servicio de agente | http://localhost:8001 |

## Comandos

### Health
curl https://bot.example.com/health

### Metrics
curl https://bot.example.com/metrics

## Troubleshooting

### El bot no responde
1. Verificar webhook: `/webhookinfo`
2. Revisar logs: `kubectl logs -f manager-bot`
3. Verificar token: `echo $TELEGRAM_BOT_TOKEN`
```

#### 4.4 Validación

- [ ] Un solo ingress operativo
- [ ] ManagerBot es único dispatcher
- [ ] OPS y Enterprise funcionan con mismo token
- [ ] Agente aislado/desactivado por defecto
- [ ] Runbook único

---

## FASE 5: Testing de Casos de Uso

### Objetivo
Crear suite de tests completa para validar cada módulo y caso de uso del ManagerBot.

### Estructura de Tests

```
tests/
├── manager_bot/
│   ├── test_registry.py
│   ├── test_module_contract.py
│   ├── test_transport/
│   │   ├── test_router.py
│   │   └── test_dispatcher.py
│   ├── test_application/
│   │   ├── ops/
│   │   │   ├── test_ops_commands.py
│   │   │   ├── test_ops_module.py
│   │   │   └── test_ops_services.py
│   │   ├── enterprise/
│   │   │   ├── test_enterprise_commands.py
│   │   │   ├── test_enterprise_module.py
│   │   │   └── test_enterprise_permissions.py
│   │   └── agent/
│   │       ├── test_agent_gateway.py
│   │       └── test_agent_module.py
│   └── test_integration/
│       ├── test_manager_bot_end_to_end.py
│       └── test_module_discovery.py
```

### Tests por Fase

#### Tests FASE 0 - Baseline

##### test_registry.py

```python
# tests/manager_bot/test_registry.py
import pytest
from unittest.mock import Mock, patch
from app.manager_bot.registry import ModuleRegistry, Module

class FakeModule(Module):
    """Módulo de prueba"""
    
    def __init__(self, name: str = "test", enabled: bool = True):
        self._name = name
        self._enabled = enabled
        self._contract = Mock()
        self._contract.name = name
        self._contract.feature_flag = "TEST_ENABLED"
    
    @property
    def contract(self):
        return self._contract
    
    def is_enabled(self) -> bool:
        return self._enabled
    
    def get_handlers(self) -> dict:
        return {"test_handler": lambda x: x}

class TestModuleRegistry:
    
    def test_register_module(self):
        registry = ModuleRegistry()
        module = FakeModule("test_module")
        
        registry.register(module)
        
        assert registry.get_module("test_module") == module
    
    def test_get_module_not_found(self):
        registry = ModuleRegistry()
        
        assert registry.get_module("nonexistent") is None
    
    def test_is_enabled_when_module_exists(self):
        registry = ModuleRegistry()
        module = FakeModule("test", enabled=True)
        registry.register(module)
        
        assert registry.is_enabled("test") is True
    
    def test_is_enabled_when_module_not_exists(self):
        registry = ModuleRegistry()
        
        assert registry.is_enabled("nonexistent") is False
    
    def test_list_routes_returns_only_enabled_modules(self):
        registry = ModuleRegistry()
        registry.register(FakeModule("enabled_module", enabled=True))
        registry.register(FakeModule("disabled_module", enabled=False))
        
        routes = registry.list_routes()
        
        assert len(routes) == 1
```

##### test_module_contract.py

```python
# tests/manager_bot/test_module_contract.py
import pytest
from pydantic import ValidationError
from app.manager_bot.core import ModuleContract

class TestModuleContract:
    
    def test_valid_contract(self):
        contract = ModuleContract(
            name="ops",
            version="1.0.0",
            feature_flag="MANAGER_ENABLE_OPS",
            routes=["/health", "/e2e"],
            permissions=["admin"]
        )
        
        assert contract.name == "ops"
        assert contract.version == "1.0.0"
    
    def test_invalid_contract_missing_name(self):
        with pytest.raises(ValidationError):
            ModuleContract(
                version="1.0.0",
                feature_flag="MANAGER_ENABLE_TEST",
                routes=[],
                permissions=[]
            )
```

##### test_transport/test_router.py

```python
# tests/manager_bot/test_transport/test_router.py
import pytest
from unittest.mock import Mock, AsyncMock
from app.manager_bot.transport.telegram.router import TelegramRouter

class TestTelegramRouter:
    
    @pytest.fixture
    def mock_registry(self):
        registry = Mock()
        registry.get_module.return_value = Mock(
            get_handlers=Mock(return_value={"test_cmd": Mock()})
        )
        return registry
    
    def test_route_update_classifies_ops_command(self, mock_registry):
        router = TelegramRouter(mock_registry)
        
        update = {
            "message": {
                "chat": {"id": 123},
                "text": "/health"
            }
        }
        
        result = router.route_update(update)
        
        assert result.kind == "ops_command"
        assert result.command == "/health"
    
    def test_route_update_classifies_enterprise_command(self, mock_registry):
        router = TelegramRouter(mock_registry)
        
        update = {
            "message": {
                "chat": {"id": 123},
                "text": "/start"
            }
        }
        
        result = router.route_update(update)
        
        assert result.kind == "enterprise_command"
    
    def test_route_update_classifies_chat(self, mock_registry):
        router = TelegramRouter(mock_registry)
        
        update = {
            "message": {
                "chat": {"id": 123},
                "text": "Hola bot"
            }
        }
        
        result = router.route_update(update)
        
        assert result.kind == "chat"
    
    def test_route_update_unsupported_message_type(self, mock_registry):
        router = TelegramRouter(mock_registry)
        
        update = {"inline_query": {"id": "123", "query": "test"}}
        
        result = router.route_update(update)
        
        assert result.kind == "unsupported"
```

#### Tests FASE 1 - OPS Module

##### test_ops_module.py

```python
# tests/manager_bot/test_application/ops/test_ops_module.py
import pytest
from unittest.mock import patch, Mock
from app.manager_bot.application.ops import OpsModule

class TestOpsModule:
    
    @patch.dict("os.environ", {"MANAGER_ENABLE_OPS": "true"})
    def test_ops_module_enabled(self):
        module = OpsModule()
        
        assert module.is_enabled() is True
    
    @patch.dict("os.environ", {"MANAGER_ENABLE_OPS": "false"})
    def test_ops_module_disabled(self):
        module = OpsModule()
        
        assert module.is_enabled() is False
    
    def test_ops_module_contract(self):
        module = OpsModule()
        contract = module.contract
        
        assert contract.name == "ops"
        assert "/health" in contract.routes
        assert "/e2e" in contract.routes
        assert "/webhookinfo" in contract.routes
        assert "/logs" in contract.routes
    
    def test_ops_module_has_handlers(self):
        module = OpsModule()
        handlers = module.get_handlers()
        
        assert "/health" in handlers
        assert "/e2e" in handlers
        assert handlers["/health"] is not None
    
    def test_ops_module_health_check(self):
        module = OpsModule()
        health = module.health_check()
        
        assert health["status"] == "ok"
```

##### test_ops_commands.py

```python
# tests/manager_bot/test_application/ops/test_ops_commands.py
import pytest
from unittest.mock import AsyncMock, Mock, patch
from app.manager_bot.application.ops.commands import OpsCommand, OPS_COMMANDS

class TestOpsCommands:
    
    def test_ops_command_dataclass(self):
        handler = Mock()
        cmd = OpsCommand(
            name="/test",
            handler=handler,
            description="Test command",
            admin_only=True
        )
        
        assert cmd.name == "/test"
        assert cmd.handler == handler
        assert cmd.description == "Test command"
        assert cmd.admin_only is True
    
    def test_ops_commands_list_contains_all_commands(self):
        command_names = [cmd.name for cmd in OPS_COMMANDS]
        
        assert "/health" in command_names
        assert "/e2e" in command_names
        assert "/webhookinfo" in command_names
        assert "/logs" in command_names
    
    def test_all_ops_commands_have_handlers(self):
        for cmd in OPS_COMMANDS:
            assert cmd.handler is not None, f"Command {cmd.name} has no handler"

@pytest.mark.asyncio
class TestOpsCommandExecution:
    
    @pytest.mark.asyncio
    async def test_health_command_returns_status(self):
        # Test que el comando /health devuelve estado
        pass
    
    @pytest.mark.asyncio
    async def test_e2e_command_execution(self):
        # Test que el comando /e2e ejecuta los checks
        pass
    
    @pytest.mark.asyncio
    async def test_logs_command_returns_events(self):
        # Test que el comando /logs devuelve eventos
        pass
```

##### test_ops_services.py

```python
# tests/manager_bot/test_application/ops/test_ops_services.py
import pytest
from unittest.mock import AsyncMock, Mock, patch

class TestOpsServices:
    
    @pytest.mark.asyncio
    async def test_handle_health_returns_api_and_webhook_status(self):
        from app.manager_bot.application.ops.services import handle_health
        
        result = await handle_health(
            check_api_health_fn=AsyncMock(return_value={"status": "ok"}),
            check_webhook_health_fn=AsyncMock(return_value={"status": "ok"})
        )
        
        assert "api" in result.lower()
        assert "webhook" in result.lower()
    
    @pytest.mark.asyncio
    async def test_handle_e2e_runs_all_checks(self):
        from app.manager_bot.application.ops.services import handle_e2e
        
        mock_check = AsyncMock(return_value={"passed": True, "failed": 0})
        
        result = await handle_e2e(run_e2e_check_fn=mock_check)
        
        mock_check.assert_called_once()
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_handle_logs_returns_event_list(self):
        from app.manager_bot.application.ops.services import handle_logs
        
        mock_events = [
            {"event": "test", "timestamp": "2026-01-01"},
            {"event": "test2", "timestamp": "2026-01-02"}
        ]
        
        result = await handle_logs(
            get_event_store_fn=Mock(return_value=mock_events)
        )
        
        assert len(result) > 0
```

#### Tests FASE 2 - Enterprise Module

##### test_enterprise_module.py

```python
# tests/manager_bot/test_application/enterprise/test_enterprise_module.py
import pytest
from unittest.mock import patch, Mock
from app.manager_bot.application.enterprise import EnterpriseModule

class TestEnterpriseModule:
    
    @patch.dict("os.environ", {"MANAGER_ENABLE_ENTERPRISE": "true"})
    def test_enterprise_module_enabled(self):
        module = EnterpriseModule()
        
        assert module.is_enabled() is True
    
    @patch.dict("os.environ", {"MANAGER_ENABLE_ENTERPROFILE": "false"})
    def test_enterprise_module_disabled(self):
        module = EnterpriseModule()
        
        assert module.is_enabled() is False
    
    def test_enterprise_module_contract(self):
        module = EnterpriseModule()
        contract = module.contract
        
        assert contract.name == "enterprise"
        assert "/start" in contract.routes
        assert "/admin" in contract.routes
    
    def test_enterprise_module_has_handlers(self):
        module = EnterpriseModule()
        handlers = module.get_handlers()
        
        assert "/start" in handlers
        assert handlers["/start"] is not None
```

##### test_enterprise_permissions.py

```python
# tests/manager_bot/test_application/enterprise/test_enterprise_permissions.py
import pytest
from unittest.mock import Mock, AsyncMock
from app.manager_bot.policies.authorization import authorize

class TestAuthorization:
    
    @pytest.mark.asyncio
    async def test_authorize_admin_has_access(self):
        mock_module = Mock()
        mock_module.get_required_permissions.return_value = ["admin"]
        
        # User with admin permission
        result = await authorize(
            module=mock_module,
            user_id=123,
            command="/admin"
        )
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_authorize_user_no_admin_permission(self):
        mock_module = Mock()
        mock_module.get_required_permissions.return_value = ["admin"]
        
        # Regular user without admin
        result = await authorize(
            module=mock_module,
            user_id=456,
            command="/admin"
        )
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_authorize_public_command_no_permission_required(self):
        mock_module = Mock()
        mock_module.get_required_permissions.return_value = []
        
        result = await authorize(
            module=mock_module,
            user_id=456,
            command="/start"
        )
        
        assert result is True
    
    def test_has_permissions_utility(self):
        from app.manager_bot.policies.authorization import has_permissions
        
        user_perms = ["user", "read"]
        required = ["user"]
        
        assert has_permissions(user_perms, required) is True
        
        required_admin = ["admin"]
        assert has_permissions(user_perms, required_admin) is False
```

#### Tests FASE 3 - Agent Gateway

##### test_agent_gateway.py

```python
# tests/manager_bot/test_application/agent/test_agent_gateway.py
import pytest
from unittest.mock import AsyncMock, patch, Mock
import httpx

class TestAgentGateway:
    
    @pytest.fixture
    def mock_env(self):
        with patch.dict("os.environ", {"AGENT_SERVICE_URL": "http://test:8001"}):
            yield
    
    @pytest.mark.asyncio
    async def test_agent_gateway_chat_success(self, mock_env):
        from app.manager_bot.application.agent_gateway import AgentGateway
        
        gateway = AgentGateway()
        
        with patch.object(gateway, 'client') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = {
                "response": "Test response",
                "confidence": 0.9,
                "sources": []
            }
            mock_response.raise_for_status = Mock()
            mock_client.post = AsyncMock(return_value=mock_response)
            
            result = await gateway.chat("Hello", "session123")
            
            assert result["response"] == "Test response"
            assert result["confidence"] == 0.9
    
    @pytest.mark.asyncio
    async def test_agent_gateway_health_check_success(self, mock_env):
        from app.manager_bot.application.agent_gateway import AgentGateway
        
        gateway = AgentGateway()
        
        with patch.object(gateway, 'client') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value={"status": "ok"})
            mock_client.get = AsyncMock(return_value=mock_response)
            
            result = await gateway.health_check()
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_agent_gateway_health_check_failure(self, mock_env):
        from app.manager_bot.application.agent_gateway import AgentGateway
        
        gateway = AgentGateway()
        
        with patch.object(gateway, 'client') as mock_client:
            mock_client.get = AsyncMock(side_effect=httpx.ConnectError())
            
            result = await gateway.health_check()
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_agent_gateway_chat_with_context(self, mock_env):
        from app.manager_bot.application.agent_gateway import AgentGateway
        
        gateway = AgentGateway()
        
        with patch.object(gateway, 'client') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = {"response": "Response", "confidence": 0.8, "sources": []}
            mock_response.raise_for_status = Mock()
            mock_client.post = AsyncMock(return_value=mock_response)
            
            context = {"user_id": 123, "chat_id": 456}
            await gateway.chat("Message", "session123", context=context)
            
            call_args = mock_client.post.call_args
            assert "context" in call_args.kwargs["json"]
            assert call_args.kwargs["json"]["context"] == context
    
    @pytest.mark.asyncio
    async def test_agent_gateway_timeout(self, mock_env):
        from app.manager_bot.application.agent_gateway import AgentGateway
        
        gateway = AgentGateway()
        
        with patch.object(gateway, 'client') as mock_client:
            mock_client.post = AsyncMock(side_effect=httpx.TimeoutException())
            
            with pytest.raises(httpx.TimeoutException):
                await gateway.chat("Hello", "session123")
```

##### test_agent_module.py

```python
# tests/manager_bot/test_application/agent/test_agent_module.py
import pytest
from unittest.mock import patch, Mock, AsyncMock
from app.manager_bot.application.agent import AgentModule

class TestAgentModule:
    
    @patch.dict("os.environ", {"MANAGER_ENABLE_AGENT": "true"})
    def test_agent_module_enabled(self):
        mock_gateway = Mock()
        module = AgentModule(mock_gateway)
        
        assert module.is_enabled() is True
    
    @patch.dict("os.environ", {"MANAGER_ENABLE_AGENT": "false"})
    def test_agent_module_disabled(self):
        mock_gateway = Mock()
        module = AgentModule(mock_gateway)
        
        assert module.is_enabled() is False
    
    def test_agent_module_contract(self):
        mock_gateway = Mock()
        module = AgentModule(mock_gateway)
        contract = module.contract
        
        assert contract.name == "agent"
        assert contract.feature_flag == "MANAGER_ENABLE_AGENT"
    
    @pytest.mark.asyncio
    async def test_agent_module_chat_delegates_to_gateway(self):
        mock_gateway = Mock()
        mock_gateway.chat = AsyncMock(return_value={"response": "Test"})
        
        module = AgentModule(mock_gateway)
        
        result = await module.chat("Hello", "session123")
        
        mock_gateway.chat.assert_called_once_with("Hello", "session123", None)
        assert result["response"] == "Test"
    
    def test_agent_module_requires_user_permission(self):
        mock_gateway = Mock()
        module = AgentModule(mock_gateway)
        
        assert "user" in module.contract.permissions
```

#### Tests de Integración

##### test_manager_bot_end_to_end.py

```python
# tests/manager_bot/test_integration/test_manager_bot_end_to_end.py
import pytest
from unittest.mock import patch, Mock, AsyncMock
from fastapi.testclient import TestClient
from app.manager_bot.core import ManagerBot
from app.manager_bot.application.ops import OpsModule
from app.manager_bot.application.enterprise import EnterpriseModule

class TestManagerBotEndToEnd:
    
    @pytest.fixture
    def manager_bot(self):
        with patch("app.manager_bot.core.ModuleRegistry"):
            with patch.dict("os.environ", {
                "MANAGER_ENABLE_OPS": "true",
                "MANAGER_ENABLE_ENTERPRISE": "true",
                "MANAGER_ENABLE_AGENT": "false"
            }):
                return ManagerBot()
    
    def test_manager_bot_initialization(self, manager_bot):
        assert manager_bot is not None
        assert manager_bot.registry is not None
    
    def test_manager_bot_registers_ops_module(self, manager_bot):
        ops_module = manager_bot.registry.get_module("ops")
        assert ops_module is not None
    
    def test_manager_bot_registers_enterprise_module(self, manager_bot):
        enterprise_module = manager_bot.registry.get_module("enterprise")
        assert enterprise_module is not None
    
    def test_manager_bot_get_router(self, manager_bot):
        router = manager_bot.get_router()
        assert router is not None
    
    def test_manager_bot_get_app(self, manager_bot):
        app = manager_bot.get_app()
        assert app is not None
    
    @pytest.mark.asyncio
    async def test_manager_bot_process_ops_command(self, manager_bot):
        # Simular mensaje OPS
        update = {
            "message": {
                "chat": {"id": 123},
                "text": "/health"
            }
        }
        
        # El router debe clasificar como ops_command
        router = manager_bot.get_router()
        result = router.route_update(update)
        
        assert result.kind == "ops_command"
        assert result.command == "/health"
    
    @pytest.mark.asyncio
    async def test_manager_bot_process_enterprise_command(self, manager_bot):
        update = {
            "message": {
                "chat": {"id": 123},
                "text": "/start"
            }
        }
        
        router = manager_bot.get_router()
        result = router.route_update(update)
        
        assert result.kind == "enterprise_command"
    
    @pytest.mark.asyncio
    async def test_manager_bot_process_chat_message(self, manager_bot):
        update = {
            "message": {
                "chat": {"id": 123},
                "text": "Hola bot"
            }
        }
        
        router = manager_bot.get_router()
        result = router.route_update(update)
        
        assert result.kind == "chat"

class TestFeatureFlags:
    
    @patch.dict("os.environ", {"MANAGER_ENABLE_OPS": "false"})
    def test_ops_module_respects_feature_flag(self):
        module = OpsModule()
        assert module.is_enabled() is False
    
    @patch.dict("os.environ", {"MANAGER_ENABLE_ENTERPRISE": "false"})
    def test_enterprise_module_respects_feature_flag(self):
        module = EnterpriseModule()
        assert module.is_enabled() is False
    
    @patch.dict("os.environ", {"MANAGER_ENABLE_AGENT": "true"})
    def test_agent_module_respects_feature_flag(self):
        from app.manager_bot.application.agent import AgentModule
        mock_gateway = Mock()
        module = AgentModule(mock_gateway)
        assert module.is_enabled() is True
```

##### test_module_discovery.py

```python
# tests/manager_bot/test_integration/test_module_discovery.py
import pytest
from app.manager_bot.registry import ModuleRegistry

class TestModuleDiscovery:
    
    def test_discover_all_modules(self):
        """Test que todos los módulos se descubren correctamente"""
        from app.manager_bot.application.ops import OpsModule
        from app.manager_bot.application.enterprise import EnterpriseModule
        from app.manager_bot.application.agent import AgentModule
        
        registry = ModuleRegistry()
        registry.register(OpsModule())
        registry.register(EnterpriseModule())
        
        # Agent no se registra hasta que esté habilitado
        
        modules = list(registry._modules.keys())
        
        assert "ops" in modules
        assert "enterprise" in modules
    
    def test_module_health_all_modules(self):
        """Test health check de todos los módulos"""
        from app.manager_bot.application.ops import OpsModule
        
        module = OpsModule()
        health = module.health_check()
        
        assert "status" in health
    
    def test_duplicate_module_registration_raises(self):
        """Test que registrar módulo duplicado lanza excepción"""
        registry = ModuleRegistry()
        from app.manager_bot.application.ops import OpsModule
        
        registry.register(OpsModule())
        
        with pytest.raises(ValueError, match="already registered"):
            registry.register(OpsModule())
```

### Cobertura de Tests Esperada

| Módulo | Tests Unitarios | Tests de Integración |
|--------|-----------------|---------------------|
| Registry | 6 | 2 |
| Module Contract | 3 | 0 |
| Transport/Router | 5 | 2 |
| OPS Module | 8 | 4 |
| Enterprise Module | 6 | 3 |
| Agent Gateway | 6 | 3 |
| Agent Module | 5 | 2 |
| **Total** | **39** | **16** |

### Comandos de Ejecución

```bash
# Ejecutar todos los tests del ManagerBot
pytest tests/manager_bot/ -v

# Ejecutar tests de un módulo específico
pytest tests/manager_bot/test_application/ops/ -v

# Ejecutar tests de integración
pytest tests/manager_bot/test_integration/ -v

# Ejecutar con coverage
pytest tests/manager_bot/ --cov=app.manager_bot --cov-report=html

# Ejecutar solo tests de контракт (contrato)
pytest tests/manager_bot/ -k "contract" -v
```

### Validación

- [ ] Tests de Registry: 6 unitarios + 2 integración
- [ ] Tests de Router: 5 unitarios + 2 integración
- [ ] Tests de OPS: 8 unitarios + 4 integración
- [ ] Tests de Enterprise: 6 unitarios + 3 integración
- [ ] Tests de Agent Gateway: 6 unitarios + 3 integración
- [ ] Tests de integración end-to-end: 5
- [ ] Coverage > 80% en código nuevo
- [ ] Tests pasan en CI/CD

---

## Feature Flags

| Flag | Módulo | Default | Descripción |
|------|--------|---------|-------------|
| `MANAGER_ENABLE_OPS` | OPS | `true` | Comandos operativos |
| `MANAGER_ENABLE_ENTERPRISE` | Enterprise | `true` | Funcionalidad Enterprise |
| `MANAGER_ENABLE_AGENT` | Agent | `false` | Agente autónomo (LLM) |
| `MANAGER_STRICT_MODE` | Global | `false` | Bloquear si módulo falla |

---

## Riesgos y Mitigaciones

| Riesgo | Impacto | Mitigación |
|--------|---------|------------|
| Regresiones en comandos | Alto | Tests de contrato por comando, feature flags |
| Dependencias legacy | Medio | Wrappers temporales, refactor incremental |
| Confusión operativa | Medio | Runbook único, feature flags para rollback |
| Agente no disponible | Bajo | Fallback a chat_service actual |

---

## Orden de Ejecución Sugerido

```
Semana 1: Fase 0 - Baseline y router unificado
Semana 2: Fase 1 - Migrar OPS
Semana 3: Fase 2 - Migrar Enterprise  
Semana 4: Fase 3 - Aislamiento del agente
Semana 5: Fase 4 - Limpieza y documentación
Semana 6: Fase 5 - Testing de casos de uso
```

**Total estimado**: 6 semanas

---

## Definition of Done

- [ ] Un solo ingress operativo: `app.webhook.entrypoint:app`
- [ ] `ManagerBot` es el único dispatcher
- [ ] OPS y Enterprise funcionan con el mismo token sin conflictos
- [ ] El agente autónomo queda aislado o desactivado por default
- [ ] Runbook único y consistente para despliegue
- [ ] **FASE 5: Suite completa de tests de casos de uso**
  - [ ] Tests de Registry (6 unitarios + 2 integración)
  - [ ] Tests de Router (5 unitarios + 2 integración)
  - [ ] Tests de OPS Module (8 unitarios + 4 integración)
  - [ ] Tests de Enterprise Module (6 unitarios + 3 integración)
  - [ ] Tests de Agent Gateway (6 unitarios + 3 integración)
  - [ ] Tests de integración end-to-end (5)
  - [ ] Coverage > 80% en código nuevo
- [ ] Todos los tests pasan
- [ ] Documentación actualizada
