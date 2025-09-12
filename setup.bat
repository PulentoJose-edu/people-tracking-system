@echo off
echo ===========================================
echo   People Tracking System - Setup
echo ===========================================
echo.

echo [1/5] Verificando Python...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python no esta instalado. Por favor instala Python 3.11+
    echo Descarga desde: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [2/5] Verificando Node.js...
node --version
if %errorlevel% neq 0 (
    echo ERROR: Node.js no esta instalado. Por favor instala Node.js 18+
    echo Descarga desde: https://nodejs.org/
    pause
    exit /b 1
)

echo [3/5] Creando entorno virtual de Python...
if not exist .venv (
    python -m venv .venv
    echo Entorno virtual creado.
) else (
    echo Entorno virtual ya existe.
)

echo [4/5] Instalando dependencias del Backend...
.venv\Scripts\pip install -r Backend\requirements.txt

echo [5/5] Instalando dependencias del Frontend...
cd frontend
npm install
cd ..

echo.
echo ===========================================
echo   ¡Instalacion completada exitosamente!
echo ===========================================
echo.
echo Para iniciar la aplicacion ejecuta: start.bat
echo.
pause
