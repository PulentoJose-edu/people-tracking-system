#!/bin/bash

echo "==========================================="
echo "   People Tracking System - Iniciando..."
echo "==========================================="
echo

echo "[1/3] Verificando instalación..."
if [ ! -d ".venv" ]; then
    echo "ERROR: Entorno virtual no encontrado."
    echo "Por favor ejecuta ./setup.sh primero."
    exit 1
fi

if [ ! -d "frontend/node_modules" ]; then
    echo "ERROR: Dependencias del frontend no instaladas."
    echo "Por favor ejecuta ./setup.sh primero."
    exit 1
fi

echo "[2/3] Iniciando Backend (FastAPI)..."
source .venv/bin/activate
python -m uvicorn Backend.app.main:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

echo "Esperando a que el backend inicie..."
sleep 3

echo "[3/3] Iniciando Frontend (Vue.js)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo
echo "==========================================="
echo "   ¡Aplicación iniciada exitosamente!"
echo "==========================================="
echo
echo "Backend (API): http://127.0.0.1:8000"
echo "Frontend (UI): http://localhost:5173"
echo "Documentación: http://127.0.0.1:8000/docs"
echo
echo "Para detener la aplicación, presiona Ctrl+C"
echo
echo "Abriendo aplicación en el navegador..."
if command -v xdg-open > /dev/null; then
    xdg-open http://localhost:5173
elif command -v open > /dev/null; then
    open http://localhost:5173
fi

# Esperar y limpiar procesos al salir
trap 'kill $BACKEND_PID $FRONTEND_PID 2>/dev/null' EXIT
wait
