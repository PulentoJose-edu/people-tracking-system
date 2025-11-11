@echo off
REM Script de inicio rápido para pruebas de rendimiento
REM Asegúrate de que backend y frontend estén corriendo

echo ========================================
echo   PRUEBAS DE RENDIMIENTO - INICIO
echo ========================================
echo.

REM Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no encontrado
    exit /b 1
)

echo Selecciona el tipo de prueba:
echo.
echo 1. Backend (requiere backend corriendo en :8000)
echo 2. Dashboard (requiere frontend corriendo en :5173)
echo 3. Ambos
echo 4. Solo verificar servicios
echo.

set /p choice="Ingresa tu opcion (1-4): "

if "%choice%"=="4" goto :check_services
if "%choice%"=="1" goto :test_backend
if "%choice%"=="2" goto :test_dashboard
if "%choice%"=="3" goto :test_both

echo Opcion invalida
exit /b 1

:check_services
echo.
echo Verificando servicios...
echo.

echo Probando Backend (http://localhost:8000)...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Backend disponible
) else (
    echo [X] Backend NO disponible
    echo     Inicia con: cd Backend ^&^& uvicorn app.main:app --reload
)

echo.
echo Probando Frontend (http://localhost:5173)...
curl -s http://localhost:5173 >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Frontend disponible
) else (
    echo [X] Frontend NO disponible
    echo     Inicia con: cd frontend ^&^& npm run dev
)

echo.
pause
exit /b 0

:test_backend
echo.
echo ========================================
echo   PRUEBAS DE BACKEND
echo ========================================
echo.

set /p task_id="Ingresa el task_id (o presiona Enter para usar el ultimo): "

if "%task_id%"=="" (
    set task_id=4dd7bafa-b26c-4e93-af1f-d46bcdc24123
)

echo.
echo Ejecutando prueba con task_id: %task_id%
echo.

python test_performance.py --task-id %task_id% --output resultados_backend.json

echo.
echo Resultados guardados en: resultados_backend.json
echo.
pause
exit /b 0

:test_dashboard
echo.
echo ========================================
echo   PRUEBAS DE DASHBOARD
echo ========================================
echo.

echo Instalando dependencias (si es necesario)...
pip install selenium >nul 2>&1

echo.
echo Ejecutando prueba del dashboard...
echo.

python test_dashboard_performance.py --tool selenium

echo.
pause
exit /b 0

:test_both
echo.
echo ========================================
echo   PRUEBAS COMPLETAS
echo ========================================
echo.

call :test_backend
call :test_dashboard

exit /b 0
