#!/bin/bash

echo "==========================================="
echo "   People Tracking System - Setup"
echo "==========================================="
echo

echo "[1/5] Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 no está instalado. Por favor instala Python 3.11+"
    echo "Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "macOS: brew install python3"
    exit 1
fi
python3 --version

echo "[2/5] Verificando Node.js..."
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js no está instalado. Por favor instala Node.js 18+"
    echo "Ubuntu/Debian: curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt-get install -y nodejs"
    echo "macOS: brew install node"
    exit 1
fi
node --version

echo "[3/5] Creando entorno virtual de Python..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "Entorno virtual creado."
else
    echo "Entorno virtual ya existe."
fi

echo "[4/5] Instalando dependencias del Backend..."
source .venv/bin/activate
pip install -r Backend/requirements.txt

echo "[5/5] Instalando dependencias del Frontend..."
cd frontend
npm install
cd ..

echo
echo "==========================================="
echo "   ¡Instalación completada exitosamente!"
echo "==========================================="
echo
echo "Para iniciar la aplicación ejecuta: ./start.sh"
echo
