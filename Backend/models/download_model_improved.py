"""
Script mejorado para descargar modelos pre-entrenados usando requests
"""

import os
import sys
from pathlib import Path

# Intentar importar requests, si no está, sugerirlo
try:
    import requests
    from tqdm import tqdm
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("⚠️  Módulo 'requests' no encontrado")
    print("   Instalando...")
    os.system("pip install requests tqdm")
    try:
        import requests
        from tqdm import tqdm
        HAS_REQUESTS = True
    except:
        print("❌ No se pudo instalar requests")
        HAS_REQUESTS = False


MODELS_DIR = Path(__file__).parent
CHECKPOINT_PATH = MODELS_DIR / "resnet50_peta_pretrained.pth"


def download_with_progress(url: str, destination: Path, description: str = "") -> bool:
    """
    Descarga un archivo con barra de progreso usando requests
    """
    try:
        print(f"\n📥 Descargando: {description or 'Modelo'}")
        print(f"   URL: {url}")
        print(f"   Destino: {destination}")
        
        # Hacer request con stream
        response = requests.get(url, stream=True, timeout=30, allow_redirects=True)
        
        # Verificar que la respuesta sea exitosa
        if response.status_code != 200:
            print(f"❌ Error HTTP {response.status_code}")
            return False
        
        # Obtener tamaño total
        total_size = int(response.headers.get('content-length', 0))
        
        # Descargar con barra de progreso
        block_size = 8192
        with open(destination, 'wb') as f:
            if total_size > 0:
                with tqdm(total=total_size, unit='B', unit_scale=True, desc="Descargando") as pbar:
                    for chunk in response.iter_content(chunk_size=block_size):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
            else:
                # Sin tamaño conocido
                print("   Descargando... (tamaño desconocido)")
                for chunk in response.iter_content(chunk_size=block_size):
                    if chunk:
                        f.write(chunk)
        
        # Verificar descarga
        if destination.exists() and destination.stat().st_size > 1024*1024:  # > 1MB
            print(f"✅ Descarga exitosa! ({destination.stat().st_size/(1024*1024):.1f} MB)")
            return True
        else:
            print("❌ Descarga incompleta")
            if destination.exists():
                destination.unlink()
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Timeout - la descarga tardó demasiado")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en la descarga: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False


# URLs actualizadas y verificadas
MODELS = {
    'huggingface_1': {
        'name': 'PAR ResNet50 (Hugging Face - Opción 1)',
        'url': 'https://huggingface.co/spaces/akhaliq/Pedestrian-Attribute-Recognition/resolve/main/checkpoints/resnet50_peta.pth',
        'accuracy': '~92% género, ~85% edad'
    },
    'huggingface_2': {
        'name': 'PAR ResNet50 (Hugging Face - Opción 2)',
        'url': 'https://hf.co/spaces/akhaliq/Pedestrian-Attribute-Recognition/resolve/main/checkpoints/resnet50_peta.pth',
        'accuracy': '~92% género, ~85% edad'
    }
}


def try_all_sources():
    """
    Intenta descargar de todas las fuentes disponibles
    """
    if not HAS_REQUESTS:
        print("\n❌ No se puede descargar sin el módulo 'requests'")
        print("   Instala con: pip install requests tqdm")
        return False
    
    print("\n" + "=" * 80)
    print("🔍 INTENTANDO DESCARGAR MODELO PRE-ENTRENADO")
    print("=" * 80)
    
    for key, model_info in MODELS.items():
        print(f"\n📦 Intentando: {model_info['name']}")
        print(f"   Precisión estimada: {model_info['accuracy']}")
        
        if download_with_progress(model_info['url'], CHECKPOINT_PATH, model_info['name']):
            print(f"\n✅ ¡Descarga exitosa desde {model_info['name']}!")
            return True
        
        print(f"❌ No se pudo descargar de esta fuente")
    
    return False


def show_manual_instructions():
    """
    Muestra instrucciones para descarga manual
    """
    print("\n" + "=" * 80)
    print("📚 INSTRUCCIONES DE DESCARGA MANUAL")
    print("=" * 80)
    print(f"""
No se pudo descargar automáticamente. Por favor descarga manualmente:

MÉTODO 1: Descarga Directa (Más Fácil)
──────────────────────────────────────
1. Abre tu navegador web
2. Ve a: https://huggingface.co/spaces/akhaliq/Pedestrian-Attribute-Recognition/tree/main/checkpoints
3. Haz clic derecho en "resnet50_peta.pth" → "Guardar enlace como..."
4. Guarda el archivo en:
   {CHECKPOINT_PATH}

MÉTODO 2: Usando wget (si lo tienes instalado)
───────────────────────────────────────────────
wget https://huggingface.co/spaces/akhaliq/Pedestrian-Attribute-Recognition/resolve/main/checkpoints/resnet50_peta.pth -O {CHECKPOINT_PATH}

MÉTODO 3: Usando curl
─────────────────────
curl -L https://huggingface.co/spaces/akhaliq/Pedestrian-Attribute-Recognition/resolve/main/checkpoints/resnet50_peta.pth -o {CHECKPOINT_PATH}

Una vez descargado, ejecuta:
python Backend/models/download_pretrained_model.py

para integrarlo en el sistema.
    """)


def main():
    print("\n╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "DESCARGA DE MODELO PRE-ENTRENADO" + " " * 25 + "║")
    print("╚" + "=" * 78 + "╝")
    
    # Verificar si ya existe
    if CHECKPOINT_PATH.exists() and CHECKPOINT_PATH.stat().st_size > 50*1024*1024:
        print(f"\n✅ Ya existe un modelo pre-entrenado!")
        print(f"   Ubicación: {CHECKPOINT_PATH}")
        print(f"   Tamaño: {CHECKPOINT_PATH.stat().st_size/(1024*1024):.1f} MB")
        
        response = input("\n¿Descargar uno nuevo? (s/n): ")
        if response.lower() != 's':
            print("Manteniendo modelo existente.")
            return 0
    
    # Intentar descargar
    if try_all_sources():
        print("\n🎉 ¡Modelo descargado exitosamente!")
        print("\nEjecuta ahora:")
        print("  python Backend/models/download_pretrained_model.py")
        print("\npara integrarlo en el sistema.")
        return 0
    else:
        show_manual_instructions()
        return 1


if __name__ == "__main__":
    sys.exit(main())
