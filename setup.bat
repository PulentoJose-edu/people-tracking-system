@echo off
echo ===========================================
echo   People Tracking System - Setup
echo ===========================================
echo.

echo [1/6] Verificando Python...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python no esta instalado. Por favor instala Python 3.11+
    echo Descarga desde: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [2/6] Verificando Node.js...
node --version
if %errorlevel% neq 0 (
    echo ERROR: Node.js no esta instalado. Por favor instala Node.js 18+
    echo Descarga desde: https://nodejs.org/
    pause
    exit /b 1
)

echo [3/6] Creando entorno virtual de Python...
if not exist .venv (
    python -m venv .venv
    echo Entorno virtual creado.
) else (
    echo Entorno virtual ya existe.
)

echo [4/6] Instalando dependencias del Backend...
.venv\Scripts\pip install -r Backend\requirements.txt

echo [4.5/6] Verificando soporte GPU...
nvidia-smi >nul 2>&1
if %errorlevel% equ 0 (
    echo [GPU] Tarjeta NVIDIA detectada. Instalando PyTorch con soporte CUDA...
    .venv\Scripts\pip uninstall -y torch torchvision torchaudio
    .venv\Scripts\pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
) else (
    echo [GPU] No se detecto tarjeta NVIDIA o drivers. Se usara procesamiento por CPU.
)

echo [5/6] Instalando dependencias del Frontend...
cd frontend
call npm install
cd ..

echo [6/6] Descargando modelos NTQAI...
echo Esto puede tomar unos minutos (~700MB)...
call .venv\Scripts\python Backend\models\download_ntoai_models.py
if %errorlevel% neq 0 (
    echo ADVERTENCIA: Error al descargar los modelos NTQAI.
    echo Puedes descargarlos manualmente mas tarde con: python Backend\models\download_ntoai_models.py
)

echo.
echo ===========================================
echo   ¡Instalacion completada exitosamente!
echo ===========================================
echo.
echo Para iniciar la aplicacion ejecuta: start.bat
echo.
pause
