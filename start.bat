@echo off
echo ===========================================
echo   People Tracking System - Iniciando...
echo ===========================================
echo.

echo [1/3] Verificando instalacion...
if not exist .venv (
    echo ERROR: Entorno virtual no encontrado.
    echo Por favor ejecuta setup.bat primero.
    pause
    exit /b 1
)

if not exist frontend\node_modules (
    echo ERROR: Dependencias del frontend no instaladas.
    echo Por favor ejecuta setup.bat primero.
    pause
    exit /b 1
)

echo [2/3] Iniciando Backend (FastAPI)...
start "Backend - People Tracking API" cmd /k "cd /d %~dp0 && .venv\Scripts\python.exe -m uvicorn Backend.app.main:app --reload --host 127.0.0.1 --port 8000"

echo Esperando a que el backend inicie...
ping -n 4 127.0.0.1 >nul

echo [3/3] Iniciando Frontend (Vue.js)...
start "Frontend - People Tracking UI" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ===========================================
echo   ¡Aplicacion iniciada exitosamente!
echo ===========================================
echo.
echo Backend (API): http://127.0.0.1:8000
echo Frontend (UI): http://localhost:5173
echo Documentacion: http://127.0.0.1:8000/docs
echo.
echo Presiona cualquier tecla para abrir la aplicacion...
pause >nul
start http://localhost:5173
