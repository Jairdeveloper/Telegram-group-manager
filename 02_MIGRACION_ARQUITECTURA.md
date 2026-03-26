# Migración de Arquitectura: Paquete Instalable Unificado

> **Fecha**: 2026-03-13
> **Estado**: Propuesta actualizada según arquitectura vigente

---

## 1. Estado Actual del Proyecto

### 1.1 Arquitectura Consolidada (Según RUNBOOK_VIGENTE)

El proyecto usa un **único entrypoint** para toda la aplicación:

```
┌─────────────────────────────────────────────────────────────┐
│                    app.webhook.entrypoint:app               │
│                     (FastAPI - Puerto 8080)                 │
├─────────────────────────────────────────────────────────────┤
│  ├── /webhook/{token}    → Telegram Updates                │
│  ├── /health             → Health check                    │
│  ├── /metrics            → Prometheus metrics              │
│  └── /manager/*          → ManagerBot (OPS + Enterprise)  │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Entry Points Actuales

| Archivo | Estado | Propósito |
|--------|--------|-----------|
| `app/webhook/entrypoint.py` | **ACTIVO** | Webhook + API + ManagerBot |
| `app/api/entrypoint.py` | DEPRECATED | API standalone (ya incluido en webhook) |
| `app/telegram_ops/entrypoint.py` | DEPRECATED | OPS polling (migrado a webhook) |
| `telegram_adapter.py` | DEPRECATED | Legacy adapter |
| `worker.py` | **ACTIVO** | RQ worker para tareas async |

### 1.3 pyproject.toml Actual (Básico)

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "robot-app"
version = "0.1.0"
description = "Manufacturing robot application"
requires-python = ">=3.10"

[tool.setuptools.packages.find]
where = ["."]
include = ["app*"]
```

**Problemas:**
- ❌ No define dependencias (requiere `requirements.txt` separado)
- ❌ No define scripts/entry points de CLI
- ❌ No incluye paquetes necesarios (`chat_service`, `migrations`, `scripts`)
- ❌ Imports absolutos requieren PYTHONPATH o ejecución desde raíz

---

## 2. Análisis de Opciones

### Opción 1: Paquete Instalable Completo ✅ **Recomendada**

**Pros:**
- Resuelve imports definitivamente (`pip install -e .` una vez)
- Estándar profesional Python
- Unifica dependencias en un solo archivo
- Comandos CLI cortos y profesionales
- Compatible con Docker y despliegues

**Contras:**
- Requiere configurar pyproject.toml correctamente

### Opción 2: Módulos Python Directos

```bash
python -m app.webhook.entrypoint
python worker.py
```

**Pros:**
- Funciona sin instalar

**Contras:**
- Requiere PYTHONPATH
- No es idiomático para producción

### Opción 3: Scripts Launcher (sys.path)

**No recomendado** - Mala práctica, inconsistente.

---

## 3. Propuesta: Paquete Instalable Unificado

### 3.1 pyproject.toml Completo

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "robot-app"
version = "1.0.0"
description = "Manufacturing robot application with Telegram integration"
requires-python = ">=3.10"
readme = "README.md"
license = {text = "MIT"}
authors = [
    {name = "Robot Team", email = "team@robot.local"}
]
dependencies = [
    "fastapi>=0.133.0",
    "uvicorn>=0.41.0",
    "python-telegram-bot>=22.6",
    "redis>=7.2.1",
    "rq>=1.16.0",
    "sqlalchemy>=2.0.0",
    "psycopg2-binary>=2.9.0",
    "pydantic>=2.12.0",
    "pydantic-settings>=2.13.0",
    "python-dotenv>=1.0.0",
    "httpx>=0.28.0",
    "prometheus-client>=0.24.0",
    "pyyaml>=6.0.0",
    "python-dateutil>=2.9.0",
    "aiofiles>=25.1.0",
    "email-validator>=2.3.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=9.0.0",
    "pytest-asyncio>=0.24.0",
]

[project.scripts]
robot = "app.webhook.entrypoint:main"
robot-webhook = "app.webhook.entrypoint:main"
robot-worker = "worker:main"

[tool.setuptools.packages.find]
where = ["."]
include = ["app*", "chat_service*", "migrations*", "scripts*"]

[tool.setuptools.package-data]
app = ["py.typed"]
```

### 3.2 Entry Point Principal

Agregar función `main()` a `app/webhook/entrypoint.py`:

```python
# app/webhook/entrypoint.py - agregar al final
def main():
    """Entry point para CLI."""
    import uvicorn
    import os
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8080"))
    reload = os.getenv("RELOAD", "false").lower() == "true"
    
    uvicorn.run(
        "app.webhook.entrypoint:app",
        host=host,
        port=port,
        reload=reload,
    )

if __name__ == "__main__":
    main()
```

### 3.3 Worker Entry Point

El `worker.py` ya tiene `if __name__ == "__main__"`, pero necesitamos una función `main()`:

```python
# worker.py - agregar función main()
def main():
    """Entry point para CLI del worker."""
    queues = [Queue(name, connection=REDIS_CONN) for name in QUEUE_NAMES]
    worker = Worker(queues, connection=REDIS_CONN)
    worker.work()

if __name__ == "__main__":
    main()
```

---

## 4. Plan de Implementación

### Fase 1: Actualizar pyproject.toml
- [ ] Completar `[project]` con todas las dependencias
- [ ] Agregar `[project.scripts]` con entry points unificados
- [ ] Incluir todos los paquetes necesarios

### Fase 2: Agregar main() a entrypoints
- [ ] `app/webhook/entrypoint.py` → agregar `main()`
- [ ] `worker.py` → agregar `main()`

### Fase 3: Scripts de Instalación
- [ ] Crear `install.sh` (Linux/Mac)
- [ ] Crear `install.bat` (Windows)

### Fase 4: Limpieza de Legacy
- [ ] Documentar que `app/api/entrypoint.py` está deprecated
- [ ] Documentar que `app/telegram_ops/entrypoint.py` está deprecated
- [ ] Documentar que `telegram_adapter.py` está deprecated

---

## 5. Uso Después de Migración

### Instalación
```bash
# Una vez
pip install -e .
# O con scripts
./install.sh   # Linux/Mac
install.bat   # Windows
```

### Ejecución
```bash
# Opción 1: Comandos CLI (después de pip install -e .)
robot              # Inicia webhook + API + ManagerBot
robot-webhook      # Alias para robot
robot-worker       # Inicia RQ worker

# Opción 2: Módulos Python (siempre funciona)
python -m app.webhook.entrypoint
python worker.py
```

### Docker
```dockerfile
# Dockerfile
COPY pyproject.toml .
RUN pip install -e .
CMD ["robot"]
```

---

## 6. Comparación: Antes vs Después

| Aspecto | Antes | Después |
|---------|-------|---------|
| Dependencias | requirements.txt | pyproject.toml |
| Entry point | `uvicorn app.webhook.entrypoint:app` | `robot` |
| Worker | `python worker.py` | `robot-worker` |
| PYTHONPATH | Requiere raíz del proyecto | No requiere |
| Docker CMD | `uvicorn app.webhook.entrypoint:app` | `robot` |

---

## 7. Recomendación Final

**Implementar Opción 1** (paquete instalable completo):

1. ✅ **pyproject.toml completo** - Unifica dependencias y metadatos
2. ✅ **Un único entry point** - `robot` que corre todo
3. ✅ **Entry point separado para worker** - `robot-worker`
4. ✅ **Scripts de instalación** - Facilita onboarding
5. ✅ **Compatible con Docker** - deployment estándar

Esta aproximación es:
- ✅ Estándar de industria Python moderno
- ✅ Mantenible a largo plazo
- ✅ Compatible con Docker y cualquier orchestrator
- ✅ Facilita testing y CI/CD
- ✅ Unifica documentación y operación

---

## Anexo: Entry Points Obsoletos (No usar)

| Archivo | Razón |
|---------|-------|
| `app/api/entrypoint.py` | API ya incluida en webhook entrypoint |
| `app/telegram_ops/entrypoint.py` | OPS migrado a ManagerBot vía webhook |
| `telegram_adapter.py` | Legacy adapter, no operativo |
