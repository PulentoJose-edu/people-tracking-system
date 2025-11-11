"""
Script de verificación de instalación del People Tracking System
Verifica que todos los componentes necesarios estén instalados correctamente
"""

import sys
import os
from pathlib import Path

def print_header(text):
    """Imprime un encabezado con formato"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def check_python_version():
    """Verifica la versión de Python"""
    print("\n🐍 Verificando versión de Python...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 11:
        print(f"  ✅ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"  ❌ Python {version.major}.{version.minor}.{version.micro} (Requiere 3.11+)")
        return False

def check_python_packages():
    """Verifica paquetes de Python necesarios"""
    print("\n📦 Verificando paquetes de Python...")
    
    required_packages = {
        'fastapi': 'FastAPI',
        'torch': 'PyTorch',
        'transformers': 'Transformers (Hugging Face)',
        'ultralytics': 'YOLOv8',
        'opencv': 'OpenCV',
        'supervision': 'Supervision',
        'pandas': 'Pandas',
        'numpy': 'NumPy',
        'huggingface_hub': 'Hugging Face Hub'
    }
    
    all_ok = True
    for package, name in required_packages.items():
        try:
            if package == 'opencv':
                import cv2
            else:
                __import__(package)
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ❌ {name} - No instalado")
            all_ok = False
    
    return all_ok

def check_ntqai_models():
    """Verifica que los modelos NTQAI estén descargados"""
    print("\n🤖 Verificando modelos NTQAI...")
    
    models_dir = Path(__file__).parent / "Backend" / "models"
    
    required_files = {
        'ntqai_adapter.py': 'Adaptador NTQAI',
        'ntqai_gender.bin': 'Modelo de Género',
        'ntqai_gender_config.json': 'Config Género',
        'ntqai_age.bin': 'Modelo de Edad',
        'ntqai_age_config.json': 'Config Edad'
    }
    
    all_ok = True
    for filename, description in required_files.items():
        filepath = models_dir / filename
        if filepath.exists():
            size = filepath.stat().st_size
            size_mb = size / (1024 * 1024)
            if size_mb > 1:
                print(f"  ✅ {description} ({size_mb:.1f} MB)")
            else:
                print(f"  ✅ {description} ({size / 1024:.1f} KB)")
        else:
            print(f"  ❌ {description} - No encontrado")
            all_ok = False
    
    if not all_ok:
        print("\n  ⚠️  Ejecuta: cd Backend/models && python download_ntoai_models.py")
    
    return all_ok

def check_yolo_model():
    """Verifica que el modelo YOLO esté presente"""
    print("\n🎯 Verificando modelo YOLO...")
    
    yolo_path = Path(__file__).parent / "yolov8n.pt"
    
    if yolo_path.exists():
        size = yolo_path.stat().st_size / (1024 * 1024)
        print(f"  ✅ YOLOv8n ({size:.1f} MB)")
        return True
    else:
        print(f"  ⚠️  YOLOv8n - No encontrado (se descargará automáticamente en el primer uso)")
        return True  # No es crítico

def check_directories():
    """Verifica que existan los directorios necesarios"""
    print("\n📁 Verificando estructura de directorios...")
    
    base_dir = Path(__file__).parent
    required_dirs = [
        'Backend',
        'Backend/app',
        'Backend/models',
        'Backend/uploads',
        'Backend/outputs',
        'frontend',
        'frontend/src',
        'frontend/src/components'
    ]
    
    all_ok = True
    for dir_path in required_dirs:
        full_path = base_dir / dir_path
        if full_path.exists():
            print(f"  ✅ {dir_path}")
        else:
            print(f"  ❌ {dir_path} - No encontrado")
            all_ok = False
    
    return all_ok

def check_nodejs():
    """Verifica instalación de Node.js"""
    print("\n📗 Verificando Node.js...")
    
    import subprocess
    try:
        result = subprocess.run(
            ['node', '--version'], 
            capture_output=True, 
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"  ✅ Node.js {version}")
            
            # Verificar npm
            try:
                result = subprocess.run(
                    ['npm', '--version'], 
                    capture_output=True, 
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    npm_version = result.stdout.strip()
                    print(f"  ✅ npm {npm_version}")
            except:
                print(f"  ⚠️  npm no encontrado")
            
            return True
        return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print(f"  ❌ Node.js no encontrado o no instalado")
        return False

def check_frontend_dependencies():
    """Verifica que las dependencias del frontend estén instaladas"""
    print("\n🎨 Verificando dependencias del frontend...")
    
    frontend_dir = Path(__file__).parent / "frontend"
    node_modules = frontend_dir / "node_modules"
    
    if node_modules.exists():
        print(f"  ✅ node_modules existe")
        
        # Verificar paquetes clave
        key_packages = ['vue', 'chart.js', 'axios', 'vite']
        for package in key_packages:
            package_dir = node_modules / package
            if package_dir.exists():
                print(f"  ✅ {package}")
            else:
                print(f"  ⚠️  {package} - Puede no estar instalado")
        return True
    else:
        print(f"  ❌ node_modules no existe")
        print(f"  ⚠️  Ejecuta: cd frontend && npm install")
        return False

def check_ports():
    """Verifica que los puertos estén disponibles"""
    print("\n🔌 Verificando puertos...")
    
    import socket
    
    ports = {
        8000: 'Backend (FastAPI)',
        5173: 'Frontend (Vite)'
    }
    
    all_available = True
    for port, service in ports.items():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            print(f"  ⚠️  Puerto {port} ({service}) - EN USO")
            all_available = False
        else:
            print(f"  ✅ Puerto {port} ({service}) - Disponible")
    
    return all_available

def generate_report(results):
    """Genera un reporte final"""
    print_header("REPORTE FINAL")
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"\n📊 Verificaciones completadas: {passed}/{total}")
    
    if passed == total:
        print("\n✅ ¡TODO LISTO! El sistema está correctamente configurado.")
        print("\n🚀 Para iniciar la aplicación:")
        print("   Windows: start.bat")
        print("   Linux/Mac: ./start.sh")
    else:
        print("\n⚠️  Hay algunos problemas que requieren atención:")
        print("\n❌ Componentes con problemas:")
        for check, status in results.items():
            if not status:
                print(f"   - {check}")
        
        print("\n📖 Consulta el README.md para instrucciones detalladas.")
        print("   Sección: 🆕 Instalación en PC Nuevo (Guía Completa)")

def main():
    """Función principal"""
    print_header("VERIFICACIÓN DE INSTALACIÓN")
    print("People Tracking System - Setup Checker")
    
    results = {}
    
    # Realizar todas las verificaciones
    results['Python Version'] = check_python_version()
    results['Python Packages'] = check_python_packages()
    results['NTQAI Models'] = check_ntqai_models()
    results['YOLO Model'] = check_yolo_model()
    results['Directory Structure'] = check_directories()
    results['Node.js'] = check_nodejs()
    results['Frontend Dependencies'] = check_frontend_dependencies()
    results['Ports Availability'] = check_ports()
    
    # Generar reporte
    generate_report(results)
    
    # Código de salida
    if all(results.values()):
        return 0
    else:
        return 1

if __name__ == "__main__":
    exit_code = main()
    input("\nPresiona Enter para salir...")
    sys.exit(exit_code)
