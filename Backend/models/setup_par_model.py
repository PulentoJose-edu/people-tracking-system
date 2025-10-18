"""
Script para descargar y configurar el modelo PAR pre-entrenado
"""

import os
import sys
from pathlib import Path
import urllib.request
import torch

# Configuración
MODEL_DIR = Path(__file__).parent
CHECKPOINT_PATH = MODEL_DIR / "resnet50_peta.pth"

# URLs de modelos pre-entrenados (alternativas)
MODEL_URLS = {
    # Si tienes acceso a modelos entrenados, agregar URLs aquí
    # 'resnet50_peta': 'https://..../resnet50_peta.pth',
}


def download_model(url: str, destination: Path):
    """Descarga un modelo desde una URL"""
    print(f"📥 Descargando modelo desde: {url}")
    print(f"📁 Guardando en: {destination}")
    
    try:
        urllib.request.urlretrieve(url, destination)
        print("✅ Modelo descargado exitosamente")
        return True
    except Exception as e:
        print(f"❌ Error descargando modelo: {e}")
        return False


def create_pretrained_checkpoint():
    """
    Crea un checkpoint inicial con ResNet50 pre-entrenado en ImageNet
    Este modelo servirá como baseline hasta que se entrene específicamente
    """
    print("🔧 Creando checkpoint baseline con ResNet50 pre-entrenado...")
    
    from torchvision.models import resnet50, ResNet50_Weights
    import torch.nn as nn
    
    # Cargar ResNet50 pre-entrenado
    backbone = resnet50(weights=ResNet50_Weights.IMAGENET1K_V1)
    num_features = backbone.fc.in_features
    backbone.fc = nn.Identity()
    
    # Crear heads para género y edad
    model = nn.ModuleDict({
        'backbone': backbone,
        'gender_head': nn.Sequential(
            nn.Linear(num_features, 512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, 2)
        ),
        'age_head': nn.Sequential(
            nn.Linear(num_features, 512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, 5)
        )
    })
    
    # Guardar checkpoint
    checkpoint = {
        'state_dict': model.state_dict(),
        'model_type': 'resnet50_par_baseline',
        'description': 'ResNet50 pre-trained on ImageNet with PAR heads (baseline)',
        'gender_labels': ['Masculino', 'Femenino'],
        'age_labels': ['Niño', 'Adolescente', 'Adulto Joven', 'Adulto', 'Mayor']
    }
    
    torch.save(checkpoint, CHECKPOINT_PATH)
    print(f"✅ Checkpoint baseline creado: {CHECKPOINT_PATH}")
    print("⚠️  Nota: Este es un modelo baseline. Para mejor precisión,")
    print("   entrena el modelo con un dataset específico de PAR (ej: PETA, PA-100K)")
    
    return True


def setup_model():
    """Configura el modelo PAR"""
    print("=" * 60)
    print("🚀 SETUP DEL MODELO PAR")
    print("=" * 60)
    
    # Verificar si ya existe el checkpoint
    if CHECKPOINT_PATH.exists():
        print(f"✅ Checkpoint encontrado: {CHECKPOINT_PATH}")
        
        # Verificar integridad
        try:
            checkpoint = torch.load(CHECKPOINT_PATH, map_location='cpu')
            print(f"📊 Tipo de modelo: {checkpoint.get('model_type', 'unknown')}")
            print(f"📝 Descripción: {checkpoint.get('description', 'N/A')}")
            return True
        except Exception as e:
            print(f"⚠️  Error cargando checkpoint: {e}")
            print("Recreando checkpoint...")
    
    # Intentar descargar modelo pre-entrenado
    if 'resnet50_peta' in MODEL_URLS:
        if download_model(MODEL_URLS['resnet50_peta'], CHECKPOINT_PATH):
            return True
    
    # Si no se puede descargar, crear baseline
    print("\n📦 No se encontró modelo pre-entrenado.")
    print("Creando modelo baseline con ResNet50...")
    
    return create_pretrained_checkpoint()


def test_model():
    """Test básico del modelo"""
    print("\n" + "=" * 60)
    print("🧪 PRUEBA DEL MODELO")
    print("=" * 60)
    
    try:
        sys.path.insert(0, str(MODEL_DIR.parent))
        from models.attribute_recognition import PARModel
        
        # Crear modelo
        model = PARModel(
            model_path=str(CHECKPOINT_PATH) if CHECKPOINT_PATH.exists() else None,
            device='cpu'
        )
        
        print("✅ Modelo cargado correctamente")
        print(f"📊 Categorías de género: {model.GENDER_LABELS}")
        print(f"📊 Categorías de edad: {model.AGE_LABELS}")
        print(f"💾 Caché size: {model.get_cache_size()}")
        
        # Test con imagen dummy
        import numpy as np
        dummy_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        dummy_bbox = (100, 100, 200, 300)
        
        result = model.predict(dummy_frame, dummy_bbox, track_id=1)
        print(f"\n🎯 Test de predicción:")
        print(f"   Género: {result['gender']} ({result['gender_confidence']:.2%})")
        print(f"   Edad: {result['age']} ({result['age_confidence']:.2%})")
        
        print("\n✅ Modelo funcionando correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n")
    success = setup_model()
    
    if success:
        print("\n")
        test_model()
        print("\n" + "=" * 60)
        print("✅ SETUP COMPLETADO")
        print("=" * 60)
        print("\n📚 Siguiente paso:")
        print("   Integrar el modelo en el pipeline de tracking (processing.py)")
    else:
        print("\n" + "=" * 60)
        print("❌ SETUP FALLÓ")
        print("=" * 60)
        sys.exit(1)
