@echo off
echo ===========================================
echo   People Tracking System - Health Check
echo ===========================================
echo.

echo [1/3] Verificando Backend...
curl -s http://127.0.0.1:8000/docs >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Backend funcionando en http://127.0.0.1:8000
) else (
    echo ✗ Backend no responde
)

echo [2/3] Verificando Frontend...
curl -s http://localhost:5173 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Frontend funcionando en http://localhost:5173
) else (
    echo ✗ Frontend no responde
)

echo [3/3] Verificando dependencias...
if exist .venv (
    echo ✓ Entorno virtual encontrado
) else (
    echo ✗ Entorno virtual no encontrado
)

if exist frontend\node_modules (
    echo ✓ Dependencias de Node.js instaladas
) else (
    echo ✗ Dependencias de Node.js no instaladas
)

echo.
echo ===========================================
echo           Verificación completada
echo ===========================================
pause
