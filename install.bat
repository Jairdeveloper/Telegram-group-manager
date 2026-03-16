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
