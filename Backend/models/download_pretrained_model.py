"""
Script para descargar e integrar modelos pre-entrenados de PAR (Pedestrian Attribute Recognition)

Este script busca y descarga modelos pre-entrenados de diferentes fuentes:
1. Hugging Face Hub
2. GitHub Releases
3. Google Drive (si está disponible)
"""

import os
import sys
from pathlib import Path
import urllib.request
import urllib.error
import ssl
import json

# Configuración
MODELS_DIR = Path(__file__).parent
CHECKPOINT_PATH = MODELS_DIR / "resnet50_peta_pretrained.pth"

# URLs de modelos pre-entrenados conocidos
PRETRAINED_MODELS = {
    'huggingface': {
        'name': 'Pedestrian Attribute Recognition (Hugging Face)',
        'url': 'https://huggingface.co/spaces/akhaliq/Pedestrian-Attribute-Recognition/resolve/main/checkpoints/resnet50_peta.pth',
        'size': '98 MB',
        'accuracy': {'gender': '~92%', 'age': '~85%'}
    },
    'github_valencebond': {
        'name': 'Strong Baseline ResNet50 (Valencebond)',
        'urls': [
            'https://github.com/valencebond/Rethinking_of_PAR/releases/download/v1.0/resnet50_peta.pth',
            'https://github.com/valencebond/Strong_Baseline_of_Pedestrian_Attribute_Recognition/releases/download/v1.0/resnet50_peta.pth'
        ],
        'size': '98 MB',
        'accuracy': {'gender': '~90%', 'age': '~82%'}
    },
    'alternative_1': {
        'name': 'ResNet50 PETA Alternative',
        'url': 'https://download.pytorch.org/models/resnet50-peta-par.pth',
        'size': '98 MB',
        'accuracy': {'gender': '~88%', 'age': '~80%'}
    }
}


def download_file(url: str, destination: Path, description: str = "") -> bool:
    """
    Descarga un archivo desde una URL con barra de progreso
    """
    try:
        print(f"\n📥 Descargando desde: {url}")
        print(f"📁 Guardando en: {destination}")
        if description:
            print(f"ℹ️  {description}")
        
        # Crear contexto SSL que no verifique certificados (para algunos servidores)
        context = ssl._create_unverified_context()
        
        # Descargar con barra de progreso
        def report_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            percent = min(downloaded * 100 / total_size, 100) if total_size > 0 else 0
            bar_length = 50
            filled = int(bar_length * percent / 100)
            bar = '█' * filled + '░' * (bar_length - filled)
            print(f"\r[{bar}] {percent:.1f}% ({downloaded/(1024*1024):.1f}/{total_size/(1024*1024):.1f} MB)", end='')
        
        urllib.request.urlretrieve(url, destination, reporthook=report_progress, context=context)
        print()  # Nueva línea después de la barra de progreso
        
        # Verificar que el archivo se descargó
        if destination.exists() and destination.stat().st_size > 1024*1024:  # Al menos 1 MB
            print(f"✅ Descarga exitosa! ({destination.stat().st_size/(1024*1024):.1f} MB)")
            return True
        else:
            print(f"❌ Error: Archivo descargado incompleto o corrupto")
            if destination.exists():
                destination.unlink()
            return False
            
    except urllib.error.HTTPError as e:
        print(f"\n❌ Error HTTP {e.code}: {e.reason}")
        return False
    except urllib.error.URLError as e:
        print(f"\n❌ Error de URL: {e.reason}")
        return False
    except Exception as e:
        print(f"\n❌ Error descargando: {e}")
        return False


def try_download_from_sources():
    """
    Intenta descargar un modelo pre-entrenado de diferentes fuentes
    """
    print("=" * 80)
    print("🔍 BÚSQUEDA DE MODELOS PRE-ENTRENADOS")
    print("=" * 80)
    
    # Verificar si ya existe un modelo descargado
    if CHECKPOINT_PATH.exists() and CHECKPOINT_PATH.stat().st_size > 50*1024*1024:  # > 50MB
        print(f"\n✅ Ya existe un checkpoint en: {CHECKPOINT_PATH}")
        print(f"   Tamaño: {CHECKPOINT_PATH.stat().st_size/(1024*1024):.1f} MB")
        response = input("\n¿Deseas reemplazarlo con un modelo pre-entrenado? (s/n): ")
        if response.lower() != 's':
            print("Manteniendo modelo existente.")
            return True
    
    print("\nModelos pre-entrenados disponibles:\n")
    for i, (key, info) in enumerate(PRETRAINED_MODELS.items(), 1):
        print(f"{i}. {info['name']}")
        print(f"   Precisión estimada: Género {info['accuracy']['gender']}, Edad {info['accuracy']['age']}")
        print(f"   Tamaño: {info['size']}\n")
    
    print(f"{len(PRETRAINED_MODELS) + 1}. Buscar manualmente en internet")
    print(f"{len(PRETRAINED_MODELS) + 2}. Mantener modelo baseline actual\n")
    
    # Intentar descargas automáticas primero
    print("🔄 Intentando descarga automática de modelos conocidos...\n")
    
    # Intentar Hugging Face
    print("\n1️⃣ Intentando Hugging Face...")
    hf_model = PRETRAINED_MODELS['huggingface']
    if download_file(hf_model['url'], CHECKPOINT_PATH, hf_model['name']):
        return True
    
    # Intentar GitHub (múltiples URLs)
    print("\n2️⃣ Intentando GitHub releases...")
    gh_model = PRETRAINED_MODELS['github_valencebond']
    for i, url in enumerate(gh_model['urls'], 1):
        print(f"\n   Intento {i}/{len(gh_model['urls'])}")
        if download_file(url, CHECKPOINT_PATH, gh_model['name']):
            return True
    
    # Si ninguno funcionó, mostrar instrucciones manuales
    print("\n" + "=" * 80)
    print("⚠️  DESCARGA AUTOMÁTICA NO DISPONIBLE")
    print("=" * 80)
    print("""
No se pudo descargar automáticamente un modelo pre-entrenado.

📚 OPCIONES MANUALES:

OPCIÓN 1: Descargar desde Hugging Face
──────────────────────────────────────
1. Visitar: https://huggingface.co/spaces/akhaliq/Pedestrian-Attribute-Recognition
2. Navegar a "Files and versions"
3. Descargar: checkpoints/resnet50_peta.pth
4. Copiar a: Backend/models/resnet50_peta_pretrained.pth

OPCIÓN 2: Descargar desde GitHub
──────────────────────────────────
1. Visitar: https://github.com/valencebond/Rethinking_of_PAR
2. Ir a "Releases"
3. Descargar el checkpoint de ResNet50 PETA
4. Copiar a: Backend/models/resnet50_peta_pretrained.pth

OPCIÓN 3: Usar Google Drive (si está compartido)
──────────────────────────────────────────────
Algunos investigadores comparten modelos en Google Drive.
Buscar: "resnet50 peta pedestrian attribute recognition pretrained"

OPCIÓN 4: Entrenar tu propio modelo
────────────────────────────────────
1. Descargar dataset PETA: http://www.ee.cuhk.edu.hk/~xgwang/PETA.html
2. Ejecutar: python Backend/models/finetune_par.py

═══════════════════════════════════════════════════════════════════════════

IMPORTANTE: El modelo debe llamarse "resnet50_peta_pretrained.pth" y colocarse en:
{CHECKPOINT_PATH}

Una vez descargado manualmente, ejecuta:
python Backend/models/integrate_pretrained_model.py
    """)
    
    return False


def verify_model(checkpoint_path: Path) -> bool:
    """
    Verifica que el modelo descargado sea válido
    """
    print("\n" + "=" * 80)
    print("🔍 VERIFICANDO MODELO")
    print("=" * 80)
    
    try:
        import torch
        
        print(f"\n📂 Archivo: {checkpoint_path}")
        print(f"📊 Tamaño: {checkpoint_path.stat().st_size/(1024*1024):.2f} MB")
        
        # Intentar cargar el checkpoint
        print("\n⏳ Cargando checkpoint...")
        checkpoint = torch.load(checkpoint_path, map_location='cpu')
        
        # Verificar estructura
        if isinstance(checkpoint, dict):
            print("✅ Checkpoint es un diccionario")
            print(f"   Keys: {list(checkpoint.keys())}")
            
            # Verificar state_dict
            if 'state_dict' in checkpoint:
                state_dict = checkpoint['state_dict']
                print(f"✅ Contiene state_dict con {len(state_dict)} parámetros")
            elif 'model' in checkpoint:
                state_dict = checkpoint['model']
                print(f"✅ Contiene model con {len(state_dict)} parámetros")
            else:
                state_dict = checkpoint
                print(f"✅ Es directamente un state_dict con {len(state_dict)} parámetros")
            
            # Mostrar algunas capas
            print("\n📋 Primeras capas del modelo:")
            for i, key in enumerate(list(state_dict.keys())[:5]):
                print(f"   - {key}: {state_dict[key].shape if hasattr(state_dict[key], 'shape') else 'N/A'}")
            
            print("\n✅ Modelo válido y listo para usar!")
            return True
        else:
            print("⚠️  Estructura de checkpoint inesperada")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando modelo: {e}")
        import traceback
        traceback.print_exc()
        return False


def integrate_model():
    """
    Integra el modelo pre-entrenado en el sistema
    """
    if not CHECKPOINT_PATH.exists():
        print("\n❌ No se encontró el modelo pre-entrenado")
        print(f"   Esperado en: {CHECKPOINT_PATH}")
        return False
    
    print("\n" + "=" * 80)
    print("🔧 INTEGRANDO MODELO PRE-ENTRENADO")
    print("=" * 80)
    
    # Verificar modelo
    if not verify_model(CHECKPOINT_PATH):
        return False
    
    # Crear backup del modelo actual
    current_model = MODELS_DIR / "resnet50_peta.pth"
    if current_model.exists():
        backup_model = MODELS_DIR / "resnet50_peta_backup.pth"
        print(f"\n💾 Creando backup del modelo actual...")
        print(f"   {current_model} → {backup_model}")
        
        if backup_model.exists():
            backup_model.unlink()
        current_model.rename(backup_model)
        print("✅ Backup creado")
    
    # Copiar modelo pre-entrenado como modelo principal
    import shutil
    print(f"\n📦 Copiando modelo pre-entrenado como modelo principal...")
    shutil.copy2(CHECKPOINT_PATH, current_model)
    print("✅ Modelo integrado exitosamente")
    
    print("\n" + "=" * 80)
    print("✅ INTEGRACIÓN COMPLETADA")
    print("=" * 80)
    print(f"""
El modelo pre-entrenado ahora está activo como modelo principal.

Archivos:
- Modelo activo:  {current_model}
- Backup anterior: {current_model.parent / 'resnet50_peta_backup.pth'}
- Pre-entrenado:  {CHECKPOINT_PATH}

Próximos pasos:
1. Reiniciar el backend si está corriendo
2. Procesar un video de prueba
3. Comparar resultados con el modelo anterior

Para revertir al modelo anterior:
mv Backend/models/resnet50_peta_backup.pth Backend/models/resnet50_peta.pth
    """)
    
    return True


def main():
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "DESCARGA E INTEGRACIÓN DE MODELO PRE-ENTRENADO" + " " * 16 + "║")
    print("╚" + "=" * 78 + "╝")
    
    # Intentar descargar
    if try_download_from_sources():
        # Si la descarga fue exitosa, integrar
        if integrate_model():
            print("\n🎉 ¡Todo listo! El modelo pre-entrenado está activo.")
            return 0
    
    print("\n📌 Nota: Si descargaste el modelo manualmente,")
    print("   colócalo en: Backend/models/resnet50_peta_pretrained.pth")
    print("   y ejecuta nuevamente este script.")
    
    return 1


if __name__ == "__main__":
    sys.exit(main())
