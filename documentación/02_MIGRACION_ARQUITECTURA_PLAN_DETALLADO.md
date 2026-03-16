# Plan de Implementación Detallado - Migración de Arquitectura

> **Fecha**: 2026-03-13
> **Versión**: 2.0 (Actualizada)
> **Referencia**: `02_MIGRACION_ARQUITECTURA.md`

---

## 1. Resumen de la Migración

### Cambio Clave: Un Único Entrypoint

La arquitectura actual consolidó **todo en un solo entrypoint**:

| Antes (Incorrecto) | Ahora (Correcto) |
|-------------------|-----------------|
| `robot-webhook` + `robot-api` | **`robot`** (único) |
| Puerto 8001 + Puerto 8000 | Puerto 8080 (todo junto) |

### Arquitectura Final

```
┌─────────────────────────────────────────────────────────────┐
│                         robot                                │
│              (Puerto 8080 - FastAPI)                        │
├─────────────────────────────────────────────────────────────┤
│  ├── /webhook/{token}    → Telegram Updates                │
│  ├── /health             → Health check                    │
│  ├── /metrics            → Prometheus metrics              │
│  ├── /manager/*          → ManagerBot (OPS + Enterprise)  │
│  └── /manager/health    → Health del ManagerBot            │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Tabla de Tareas

| Fase | Tarea | Archivo(s) | Estado |
|------|-------|-----------|--------|
| 1 | Actualizar pyproject.toml | `pyproject.toml` | ⬜ Pendiente |
| 2 | Agregar main() a webhook entrypoint | `app/webhook/entrypoint.py` | ⬜ Pendiente |
| 3 | Actualizar worker.py | `worker.py` | ⬜ Pendiente |
| 4 | Crear install.sh | `install.sh` | ⬜ Pendiente |
| 5 | Crear install.bat | `install.bat` | ⬜ Pendiente |
| 6 | Actualizar README.md | `README.md` | ⬜ Pendiente |
| 7 | Documentar deprecaciones | - | ⬜ Pendiente |

---

## 3. Fase 1: Actualizar pyproject.toml

### Objetivo
Completar el archivo `pyproject.toml` con todas las dependencias y un único entry point.

### Implementación

Reemplazar el contenido completo de `pyproject.toml`:

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
    "uvicorn[standard]>=0.41.0",
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
    "click>=8.3.0",
    "jinja2>=3.1.0",
    "aiofiles>=25.1.0",
    "email-validator>=2.3.0",
    "python-dateutil>=2.9.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=9.0.0",
    "pytest-asyncio>=0.24.0",
    "pytest-cov>=6.0.0",
]

[project.scripts]
robot = "app.webhook.entrypoint:main"
robot-worker = "worker:main"

[tool.setuptools.packages.find]
where = ["."]
include = ["app*", "chat_service*", "migrations*", "scripts*"]
exclude = ["tests*"]

[tool.setuptools.package-data]
app = ["py.typed"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
asyncio_mode = "auto"
```

### Verificación
```bash
pip install -e .
```

---

## 4. Fase 2: Agregar main() a webhook entrypoint

### Objetivo
Agregar función `main()` a `app/webhook/entrypoint.py` para permitir ejecución como CLI.

### Implementación

**Paso 1:** Leer el archivo actual y agregar la función `main()` al final:

```python
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
        log_level="info",
    )


if __name__ == "__main__":
    main()
```

### Variables de Entorno
| Variable | Default | Descripción |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Host para binding |
| `PORT` | `8080` | Puerto del servidor |
| `RELOAD` | `false` | Habilitar reload automático |

---

## 5. Fase 3: Actualizar worker.py

### Objetivo
Verificar que `worker.py` tenga función `main()` compatible con entry point.

### Implementación

**Paso 1:** Modificar `worker.py`:

```python
"""Entrypoint for RQ worker (Docker / k8s)."""
import sys

from redis import Redis

try:
    from rq import Worker, Queue
except Exception as exc:
    print(f"Failed to import RQ worker runtime: {exc}")
    print("Install compatible dependencies and run worker in a supported runtime (recommended: Docker/Linux).")
    sys.exit(1)

from app.config.settings import load_worker_settings

WORKER_SETTINGS = load_worker_settings()
QUEUE_NAMES = WORKER_SETTINGS.queue_names
REDIS_URL = WORKER_SETTINGS.redis_url
REDIS_CONN = Redis.from_url(REDIS_URL)


def main():
    """Entry point para CLI."""
    import logging
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)
    
    logger.info(f"Starting RQ worker for queues: {QUEUE_NAMES}")
    
    queues = [Queue(name, connection=REDIS_CONN) for name in QUEUE_NAMES]
    worker = Worker(queues, connection=REDIS_CONN)
    worker.work()


if __name__ == "__main__":
    main()
```

---

## 6. Fase 4: Crear install.sh

### Objetivo
Crear script de instalación para Linux/Mac.

### Implementación

**Paso 1:** Crear archivo `install.sh`:

```bash
#!/bin/bash
#
# install.sh - Script de instalación para Linux/Mac
# Uso: ./install.sh
#

set -e

echo "============================================"
echo "  Robot App - Instalación"
echo "============================================"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 no está instalado."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "Error: Se requiere Python $REQUIRED_VERSION o superior. Versión actual: $PYTHON_VERSION"
    exit 1
fi

echo "Python version: $PYTHON_VERSION ✓"

# Verificar pip
if ! command -v pip &> /dev/null; then
    echo "Error: pip no está instalado."
    exit 1
fi

echo " pip installed ✓"

# Instalar/actualizar pip
echo ""
echo "Actualizando pip..."
python3 -m pip install --upgrade pip

# Instalar package en modo editable
echo ""
echo "Instalando robot-app en modo editable..."
pip install -e .

echo ""
echo "============================================"
echo "  Instalación completada!"
echo "============================================"
echo ""
echo "Comandos disponibles:"
echo "  robot           - Iniciar servidor (webhook + API + ManagerBot)"
echo "  robot-worker    - Iniciar worker de tareas"
echo ""
echo "Para más información, consulta README.md"
echo ""
echo "Variables de entorno opcionales:"
echo "  HOST=0.0.0.0    # Host del servidor"
echo "  PORT=8080       # Puerto del servidor"
echo "  RELOAD=true     # Recarga automática (desarrollo)"
echo ""

# Hacer ejecutable
chmod +x install.sh
```

---

## 7. Fase 5: Crear install.bat

### Objetivo
Crear script de instalación para Windows.

### Implementación

**Paso 1:** Crear archivo `install.bat`:

```batch
@echo off
REM install.bat - Script de instalación para Windows
REM Uso: install.bat

echo.
echo ============================================
echo   Robot App - Instalacion
echo ============================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python no esta instalado.
    pause
    exit /b 1
)

echo Python detectado:
python --version
echo.

REM Verificar pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo Error: pip no esta instalado.
    pause
    exit /b 1
)

echo pip detectado:
pip --version
echo.

REM Actualizar pip
echo Actualizando pip...
python -m pip install --upgrade pip
echo.

REM Instalar en modo editable
echo Instalando robot-app en modo editable...
pip install -e .
echo.

echo ============================================
echo   Instalacion completada!
echo ============================================
echo.
echo Comandos disponibles:
echo   robot           - Iniciar servidor (webhook + API + ManagerBot)
echo   robot-worker    - Iniciar worker de tareas
echo.
echo Para mas informacion, consulta README.md
echo.
echo Variables de entorno opcionales:
echo   HOST=0.0.0.0    - Host del servidor
echo   PORT=8080       - Puerto del servidor
echo   RELOAD=true     - Recarga automatica (desarrollo)
echo.

pause
```

---

## 8. Fase 6: Actualizar README.md

### Objetivo
Actualizar el README.md con las nuevas instrucciones de instalación y ejecución.

### Implementación

**Paso 1:** Agregar sección de instalación al README.md:

```markdown
---

## Instalación y Ejecución

### Requisitos
- Python 3.10+
- pip

### Instalación

#### Linux/Mac
```bash
./install.sh
```

#### Windows
```batch
install.bat
```

#### Manual
```bash
pip install -e .
```

### Ejecución

#### Opción 1: Comandos CLI (después de instalación)
```bash
robot           # Servidor completo en puerto 8080
robot-worker    # Worker de tareas
```

#### Opción 2: Módulos Python
```bash
python -m app.webhook.entrypoint
python worker.py
```

#### Opción 3: Uvicorn directo
```bash
uvicorn app.webhook.entrypoint:app --host 0.0.0.0 --port 8080
```

### Variables de Entorno

| Variable | Default | Descripción |
|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | - | Token del bot de Telegram (requerido) |
| `WEBHOOK_TOKEN` | - | Token para validación de webhook |
| `CHATBOT_API_URL` | `http://127.0.0.1:8000/api/v1/chat` | URL del API de chat |
| `REDIS_URL` | - | URL de Redis (opcional) |
| `HOST` | `0.0.0.0` | Host del servidor |
| `PORT` | `8080` | Puerto del servidor |
| `RELOAD` | `false` | Recarga automática (desarrollo) |
| `MANAGER_ENABLE_OPS` | `true` | Habilitar módulo OPS |
| `MANAGER_ENABLE_ENTERPRISE` | `true` | Habilitar módulo Enterprise |
| `MANAGER_ENABLE_AGENT` | `false` | Habilitar agente autónomo |

### Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install -e .

COPY . .

CMD ["robot"]
```

### Desarrollo

```bash
# Instalar con dependencias de desarrollo
pip install -e ".[dev]"

# Ejecutar con reload automático
RELOAD=true PORT=8080 robot

# Ejecutar tests
pytest -q
```

---

## Legacy (Deprecated)

Los siguientes entrypoints están **deprecated** y no deben usarse:

| Archivo | Razón |
|---------|-------|
| `app/api/entrypoint.py` | API ya incluida en webhook entrypoint |
| `app/telegram_ops/entrypoint.py` | OPS migrado a ManagerBot vía webhook |
| `telegram_adapter.py` | Legacy adapter, no operativo |

```

---

## 9. Fase 7: Documentar Deprecaciones

### Objetivo
Crear documentación sobre los entrypoints obsoletos.

### Implementación

Agregar notas de deprección en los archivos obsoletos:

**`app/api/entrypoint.py`** - Agregar al docstring:
```python
"""Canonical API entrypoint (composition root).

.. deprecated::
    Este entrypoint está deprecated desde 2026-03-13.
    Use `app.webhook.entrypoint:app` como único punto de entrada.
    La API ya está incluida en el webhook entrypoint en /manager/*.
"""
```

**`app/telegram_ops/entrypoint.py`** - Ya debería tener deprección.

**`telegram_adapter.py`** - Ya tiene deprección documentada.

---

## 10. Comparación: Antes vs Después

| Aspecto | Antes | Después |
|---------|-------|---------|
| Dependencias | `requirements.txt` | `pyproject.toml` |
| Entry point principal | `uvicorn app.webhook.entrypoint:app` | `robot` |
| Puerto webhook | 8001 | 8080 |
| Puerto API | 8000 | Incluido en 8080 |
| Worker | `python worker.py` | `robot-worker` |
| PYTHONPATH | Requiere raíz del proyecto | No requiere |
| Docker CMD | `uvicorn app.webhook.entrypoint:app` | `robot` |

---

## 11. Verificación Post-Implementación

```bash
# 1. Instalar
pip install -e .

# 2. Verificar comandos disponibles
robot         # Servidor completo
robot-worker  # Worker

# 3. Probar ejecución
python -c "from app.webhook.entrypoint import main; print('OK')"

# 4. Verificar que todo funciona
python -m app.webhook.entrypoint &
# Debería iniciar en puerto 8080
```

---

## 12. Resolución de Problemas

### Error: "command not found: robot"
```bash
# Verificar instalación
pip show robot-app

# Reinstalar
pip install -e . --force-reinstall
```

### Error: "ModuleNotFoundError: No module named 'app'"
```bash
# El paquete no se instaló correctamente
pip install -e .
```

### Error: Puerto en uso
```bash
# Cambiar puerto
PORT=8081 robot
```

---

## 13. Resumen de Archivos a Modificar/Crear

| Archivo | Acción | Detalle |
|---------|--------|---------|
| `pyproject.toml` | Modificar | Entry points unificados (`robot`, `robot-worker`) |
| `app/webhook/entrypoint.py` | Agregar | Función `main()` al final |
| `worker.py` | Modificar | Agregar función `main()` |
| `install.sh` | Crear | Script de instalación Linux/Mac |
| `install.bat` | Crear | Script de instalación Windows |
| `README.md` | Actualizar | Nueva sección de instalación |
| `app/api/entrypoint.py` | Documentar | Agregar deprección |
