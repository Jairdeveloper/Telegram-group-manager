# Migración de Arquitectura - Fases 1-7 Completadas

> **Fecha**: 2026-03-13
> **Proyecto**: Chatbot Manufacturing
> **Estado**: ✅ Migración completada

---

## Resumen de la Migración

### Cambio Clave: Un Único Entrypoint

La arquitectura actual consolidó **todo en un solo entrypoint**:

| Antes (Incorrecto) | Ahora (Correcto) |
|-------------------|-----------------|
| `robot-webhook` + `robot-api` | **`robot`** (único) |
| Puerto 8001 + Puerto 8000 | Puerto 8000 (todo junto, evita errores en Windows) |

### Arquitectura Final

```
┌─────────────────────────────────────────────────────────────┐
│                         robot                                │
│              (Puerto 8000 - FastAPI)                        │
├─────────────────────────────────────────────────────────────┤
│  ├── /webhook/{token}    → Telegram Updates                │
│  ├── /health             → Health check                    │
│  ├── /metrics            → Prometheus metrics              │
│  └── /manager/*          → ManagerBot (OPS + Enterprise)  │
└─────────────────────────────────────────────────────────────┘
```

---

## Fase 1: Actualizar pyproject.toml ✅ COMPLETADA

### Objetivo
Completar el archivo `pyproject.toml` con todas las dependencias y un único entry point.

### Cambios Realizados

El archivo `pyproject.toml` fue actualizado con:

```toml
[project.scripts]
robot = "app.webhook.entrypoint:main"
robot-worker = "worker:main"
```

### Entry Points Definidos

| Comando | Módulo | Puerto |
|---------|--------|--------|
| `robot` | `app.webhook.entrypoint:main` | 8000 |
| `robot-worker` | `worker:main` | - |

---

## Fase 2: Agregar main() a webhook entrypoint ✅ COMPLETADA

### Objetivo
Agregar función `main()` a `app/webhook/entrypoint.py` para permitir ejecución como CLI.

### Cambios Realizados

Se agregó función `main()` al archivo `app/webhook/entrypoint.py`:

```python
def main():
    """Entry point para CLI."""
    import uvicorn
    import os
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))  # 8000 para evitar errores de permisos en Windows
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
| `PORT` | `8000` | Puerto del servidor (evita errores de permisos en Windows) |
| `RELOAD` | `false` | Habilitar reload automático |

---

## Fase 3: Actualizar worker.py ✅ COMPLETADA

### Objetivo
Agregar función `main()` a `worker.py` compatible con entry point.

### Cambios Realizados

Se agregó función `main()` al archivo `worker.py`:

```python
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

## Fase 4: Crear install.sh ✅ COMPLETADA

### Objetivo
Crear script de instalación para Linux/Mac.

### Cambios Realizados

Se creó el archivo `install.sh`:

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
echo "  PORT=8000       # Puerto del servidor (evita errores en Windows)"
echo "  RELOAD=true     # Recarga automática (desarrollo)"
echo ""
```

### Uso

```bash
./install.sh
```

---

## Fase 5: Crear install.bat ✅ COMPLETADA

### Objetivo
Crear script de instalación para Windows.

### Cambios Realizados

Se creó el archivo `install.bat`:

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
echo   PORT=8000       - Puerto del servidor
echo   RELOAD=true     - Recarga automatica (desarrollo)
echo.

pause
```

### Uso

```batch
install.bat
```

---

## Fase 6: Actualizar README.md ✅ COMPLETADA

### Objetivo
Actualizar el README.md con las nuevas instrucciones de instalación y ejecución.

### Cambios Realizados

Se agregaron las siguientes secciones al README.md:

1. **Sección 10: Instalación y Ejecución**
   - Requisitos
   - Instalación (Linux/Mac, Windows, Manual)
   - Ejecución (CLI, Módulos Python, Uvicorn)
   - Variables de entorno
   - Docker
   - Desarrollo

2. **Sección Legacy (Deprecated)**
   - Lista de entrypoints obsoletos

---

## Fase 7: Documentar deprecaciones ✅ COMPLETADA

### Objetivo
Agregar notas de deprecación a los archivos legacy.

### Cambios Realizados

Se agregaron notas de deprecación a los siguientes archivos:

#### 1. `app/api/entrypoint.py`
```python
"""Canonical API entrypoint (composition root).

.. deprecated::
    Este entrypoint está deprecated desde 2026-03-13.
    Use `app.webhook.entrypoint:app` como único punto de entrada.
    La API ya está incluida en el webhook entrypoint en /manager/*.
"""
```

#### 2. `app/telegram_ops/entrypoint.py`
```python
"""Transitional Telegram OPS bot for health, webhook and E2E checks.

.. deprecated::
    Este entrypoint está deprecated desde 2026-03-13.
    Use `app.webhook.entrypoint:app` como único punto de entrada.
    Los comandos OPS (/health, /e2e, /webhookinfo, /logs) ahora se manejan
    vía ManagerBot en el webhook entrypoint.
"""
```

#### 3. `telegram_adapter.py`
Ya tenía documentación de deprecación desde versiones anteriores.

### Archivos deprecated (no usar)

| Archivo | Razón |
|---------|-------|
| `app/api/entrypoint.py` | API ya incluida en webhook entrypoint |
| `app/telegram_ops/entrypoint.py` | OPS migrado a ManagerBot vía webhook |
| `telegram_adapter.py` | Legacy adapter, no operativo |

---

## Fase 8: Configuración de Debug en VS Code ✅ COMPLETADA

### Objetivo
Crear configuración de launch.json para debug de la aplicación en VS Code.

### Problema Resuelto
Error `ImportError: attempted relative import with no known parent package` cuando se hacia debug desde VS Code.

### Solución
Ejecutar la app como módulo de Python, no como archivo individual.

### Cambios Realizados

Se creó el archivo `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
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
        },
        {
            "name": "Python: Robot (Debug with Reload)",
            "type": "debugpy",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "app.webhook.entrypoint:app",
                "--host", "0.0.0.0",
                "--port", "8000",
                "--reload"
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
            "justMyCode": true
        }
    ]
}
```

### Claves de la configuración

| Propiedad | Valor | Propósito |
|-----------|-------|-----------|
| `module` | `"uvicorn"` | Ejecuta como módulo, no como archivo |
| `args` | `"app.webhook.entrypoint:app"` | Apunta al entrypoint correcto |
| `PYTHONPATH` | `"${workspaceFolder}"` | Asegura que `app` sea reconocible como paquete |

### Notas sobre el Puerto

- **Puerto 8000**: Puerto por defecto para evitar errores de permisos en Windows (el 8080 requiere admin)
- Para cambiar el puerto: `PORT=9000 robot` o modificar en launch.json

### Uso

1. Ve a **Run and Debug** (Ctrl+Shift+D)
2. Selecciona **"Python: Robot (Webhook)"**
3. Presiona **F5**

---

## Tabla de Progreso

| Fase | Tarea | Estado |
|------|-------|--------|
| 1 | Actualizar pyproject.toml | ✅ Completado |
| 2 | Agregar main() a webhook entrypoint | ✅ Completado |
| 3 | Actualizar worker.py | ✅ Completado |
| 4 | Crear install.sh | ✅ Completado |
| 5 | Crear install.bat | ✅ Completado |
| 6 | Actualizar README.md | ✅ Completado |
| 7 | Documentar deprecaciones | ✅ Completado |

---

## Migración Completada ✅

## Comparación: Antes vs Después

| Aspecto | Antes | Después |
|---------|-------|---------|
| Dependencias | `requirements.txt` separado | Integrado en `pyproject.toml` |
| Entry point | `uvicorn app.webhook.entrypoint:app` | `robot` |
| Puerto | 8001 | 8000 |
| Worker | `python worker.py` | `robot-worker` |
| Versión | 0.1.0 | 1.0.0 |

---

## Verificación

Para probar la instalación:

```bash
# Instalar el paquete
pip install -e .

# Probar servidor
robot

# Probar worker (en otra terminal)
robot-worker

# O con variables de entorno
HOST=0.0.0.0 PORT=8000 robot
```

---

## Archivos Modificados/Creados

| Archivo | Cambio |
|---------|--------|
| `pyproject.toml` | Agregadas dependencias y entry points |
| `app/webhook/entrypoint.py` | Agregada función `main()` |
| `worker.py` | Agregada función `main()` |
| `install.sh` | Creado script de instalación Linux/Mac |
| `install.bat` | Creado script de instalación Windows |
| `README.md` | Agregada sección de instalación |
| `app/api/entrypoint.py` | Agregada deprecación |
| `app/telegram_ops/entrypoint.py` | Agregada deprecación |

---

*Documento generado para la Migración de Arquitectura*
*Versión: 1.0*
*Fecha: 2026-03-13*
