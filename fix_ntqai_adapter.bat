@echo off
REM Script de actualización rápida para corregir el adaptador NTQAI
REM Soluciona: "state_dict cannot be passed together with a model name"

echo ========================================
echo   ACTUALIZAR ADAPTADOR NTQAI
echo ========================================
echo.

echo Este script regenera ntqai_adapter.py con la version corregida
echo que es compatible con transformers 4.46+
echo.

set /p confirm="Continuar? (S/N): "
if /i not "%confirm%"=="S" (
    echo Cancelado.
    exit /b 0
)

echo.
echo [1/3] Navegando a Backend/models...
cd Backend\models
if %errorlevel% neq 0 (
    echo [ERROR] No se encontro el directorio Backend/models
    pause
    exit /b 1
)

echo.
echo [2/3] Respaldando adaptador actual...
if exist ntqai_adapter.py (
    copy ntqai_adapter.py ntqai_adapter.py.backup >nul 2>&1
    echo [OK] Respaldo creado: ntqai_adapter.py.backup
) else (
    echo [WARN] No existe ntqai_adapter.py previo
)

echo.
echo [3/3] Regenerando adaptador...
python download_ntoai_models.py --adapter-only
if %errorlevel% neq 0 (
    echo.
    echo [WARN] No existe flag --adapter-only, ejecutando script completo...
    echo Esto verificara los modelos y regenerara el adaptador.
    echo.
    python download_ntoai_models.py
)

echo.
echo ========================================
echo   ACTUALIZACION COMPLETADA
echo ========================================
echo.
echo El adaptador ntqai_adapter.py ha sido actualizado.
echo.
echo Proximos pasos:
echo 1. Reinicia el backend (si esta corriendo)
echo 2. Verifica con: python ../../verify_setup.py
echo.

pause
