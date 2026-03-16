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

# Hacer ejecutable el propio script si no lo está
if [ ! -x "$0" ]; then
    chmod +x "$0"
fi
