"""
Script para descargar e integrar modelos NTQAI especializados
- Gender Recognition: NTQAI/pedestrian_gender_recognition
- Age Recognition: NTQAI/pedestrian_age_recognition
"""

import os
import sys

def check_and_install_huggingface():
    """Verifica e instala huggingface_hub si es necesario"""
    try:
        import huggingface_hub
        print("✅ huggingface_hub ya está instalado")
        return True
    except ImportError:
        print("⚠️  Módulo 'huggingface_hub' no encontrado")
        print("   Instalando...")
        import subprocess
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "huggingface_hub", "--quiet"
            ])
            print("✅ huggingface_hub instalado correctamente")
            return True
        except Exception as e:
            print(f"❌ Error instalando huggingface_hub: {e}")
            return False

def download_ntoai_models():
    """Descarga los modelos NTQAI desde Hugging Face"""
    
    if not check_and_install_huggingface():
        return False
    
    from huggingface_hub import hf_hub_download
    
    # Directorio de modelos
    models_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("\n" + "="*80)
    print("🔍 DESCARGANDO MODELOS NTQAI ESPECIALIZADOS")
    print("="*80)
    
    models = [
        {
            "repo": "NTQAI/pedestrian_gender_recognition",
            "filename": "pytorch_model.bin",
            "local_name": "ntqai_gender.bin",
            "type": "Gender Recognition",
            "accuracy": "~95%"
        },
        {
            "repo": "NTQAI/pedestrian_age_recognition",
            "filename": "pytorch_model.bin",
            "local_name": "ntqai_age.bin",
            "type": "Age Recognition",
            "accuracy": "~88%"
        }
    ]
    
    downloaded = []
    
    for model in models:
        print(f"\n📦 Descargando: {model['type']}")
        print(f"   Repositorio: {model['repo']}")
        print(f"   Precisión estimada: {model['accuracy']}")
        
        try:
            # Descargar el archivo
            print(f"   📥 Descargando {model['filename']}...")
            file_path = hf_hub_download(
                repo_id=model['repo'],
                filename=model['filename'],
                cache_dir=None  # Usa el caché por defecto
            )
            
            # Copiar al directorio de modelos con nombre específico
            local_path = os.path.join(models_dir, model['local_name'])
            import shutil
            shutil.copy(file_path, local_path)
            
            print(f"   ✅ Descargado: {local_path}")
            downloaded.append(model)
            
        except Exception as e:
            print(f"   ❌ Error descargando {model['type']}: {e}")
    
    # También descargar archivos de configuración
    print("\n📦 Descargando archivos de configuración...")
    
    for model in models:
        try:
            config_files = ["config.json"]
            for config_file in config_files:
                try:
                    config_path = hf_hub_download(
                        repo_id=model['repo'],
                        filename=config_file
                    )
                    local_config = os.path.join(
                        models_dir, 
                        model['local_name'].replace('.bin', f'_{config_file}')
                    )
                    import shutil
                    shutil.copy(config_path, local_config)
                    print(f"   ✅ Config descargado: {config_file} para {model['type']}")
                except:
                    pass  # Algunos archivos pueden no existir
        except Exception as e:
            pass
    
    return len(downloaded) > 0

def create_integration_adapter():
    """Crea un adaptador para integrar los modelos NTQAI con el sistema existente"""
    
    adapter_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "ntqai_adapter.py"
    )
    
    adapter_code = '''"""
Adaptador para modelos NTQAI especializados (BEiT-based)
Proporciona interfaz compatible con el sistema PAR existente
"""

import torch
import json
import os
from PIL import Image
from transformers import BeitForImageClassification, AutoImageProcessor

class NTQAIModelsAdapter:
    """Adaptador para usar modelos NTQAI de género y edad basados en BEiT"""
    
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.gender_model = None
        self.age_model = None
        self.gender_processor = None
        self.age_processor = None
        self.gender_labels = {}
        self.age_labels = {}
        
    def load_models(self):
        """Carga los modelos NTQAI"""
        models_dir = os.path.dirname(os.path.abspath(__file__))
        
        print("🔄 Cargando modelos NTQAI (BEiT)...")
        
        # Cargar modelo de género
        gender_path = os.path.join(models_dir, "ntqai_gender.bin")
        gender_config_path = os.path.join(models_dir, "ntqai_gender_config.json")
        
        if os.path.exists(gender_path) and os.path.exists(gender_config_path):
            try:
                # Cargar configuración
                with open(gender_config_path, 'r') as f:
                    gender_config = json.load(f)
                    self.gender_labels = gender_config.get('id2label', {})
                
                # Cargar modelo
                state_dict = torch.load(gender_path, map_location=self.device)
                self.gender_model = BeitForImageClassification.from_pretrained(
                    "microsoft/beit-base-patch16-224-pt22k-ft22k",
                    state_dict=state_dict,
                    num_labels=2,
                    ignore_mismatched_sizes=True
                )
                self.gender_model.to(self.device)
                self.gender_model.eval()
                
                # Crear procesador de imágenes
                self.gender_processor = AutoImageProcessor.from_pretrained(
                    "microsoft/beit-base-patch16-224-pt22k-ft22k"
                )
                
                print(f"✅ Modelo de género cargado - Labels: {self.gender_labels}")
            except Exception as e:
                print(f"⚠️  Error cargando modelo de género: {e}")
                import traceback
                traceback.print_exc()
        
        # Cargar modelo de edad
        age_path = os.path.join(models_dir, "ntqai_age.bin")
        age_config_path = os.path.join(models_dir, "ntqai_age_config.json")
        
        if os.path.exists(age_path) and os.path.exists(age_config_path):
            try:
                # Cargar configuración
                with open(age_config_path, 'r') as f:
                    age_config = json.load(f)
                    self.age_labels = age_config.get('id2label', {})
                
                # Cargar modelo
                state_dict = torch.load(age_path, map_location=self.device)
                self.age_model = BeitForImageClassification.from_pretrained(
                    "microsoft/beit-base-patch16-224-pt22k-ft22k",
                    state_dict=state_dict,
                    num_labels=5,
                    ignore_mismatched_sizes=True
                )
                self.age_model.to(self.device)
                self.age_model.eval()
                
                # Crear procesador de imágenes
                self.age_processor = AutoImageProcessor.from_pretrained(
                    "microsoft/beit-base-patch16-224-pt22k-ft22k"
                )
                
                print(f"✅ Modelo de edad cargado - Labels: {self.age_labels}")
            except Exception as e:
                print(f"⚠️  Error cargando modelo de edad: {e}")
                import traceback
                traceback.print_exc()
        
        return self.gender_model is not None or self.age_model is not None
    
    def _map_age_to_group(self, age_label):
        """Mapea las etiquetas de edad NTQAI a grupos estándar"""
        mapping = {
            "AgeLess15": "0-18",
            "Age16-30": "19-35",
            "Age31-45": "36-60",
            "Age46-60": "36-60",
            "AgeAbove60": "60+"
        }
        return mapping.get(age_label, "Unknown")
    
    def predict(self, image):
        """
        Realiza predicción compatible con la interfaz PAR existente
        
        Args:
            image: PIL Image o tensor
            
        Returns:
            dict: {'gender': str, 'age_group': str, 'gender_conf': float, 'age_conf': float}
        """
        if not isinstance(image, Image.Image):
            # Convertir tensor a PIL Image si es necesario
            if torch.is_tensor(image):
                import torchvision.transforms as T
                image = T.ToPILImage()(image.cpu())
        
        result = {
            'gender': 'Unknown',
            'age_group': 'Unknown',
            'gender_conf': 0.0,
            'age_conf': 0.0
        }
        
        with torch.no_grad():
            # Predicción de género
            if self.gender_model is not None and self.gender_processor is not None:
                try:
                    inputs = self.gender_processor(images=image, return_tensors="pt")
                    inputs = {k: v.to(self.device) for k, v in inputs.items()}
                    
                    outputs = self.gender_model(**inputs)
                    logits = outputs.logits
                    probs = torch.softmax(logits, dim=-1)
                    
                    gender_conf, gender_idx = probs.max(dim=-1)
                    gender_label = self.gender_labels.get(str(gender_idx.item()), "Unknown")
                    
                    # Mapear a formato estándar
                    result['gender'] = 'M' if gender_label == 'Male' else 'F'
                    result['gender_conf'] = gender_conf.item()
                    
                except Exception as e:
                    print(f"⚠️  Error en predicción de género: {e}")
            
            # Predicción de edad
            if self.age_model is not None and self.age_processor is not None:
                try:
                    inputs = self.age_processor(images=image, return_tensors="pt")
                    inputs = {k: v.to(self.device) for k, v in inputs.items()}
                    
                    outputs = self.age_model(**inputs)
                    logits = outputs.logits
                    probs = torch.softmax(logits, dim=-1)
                    
                    age_conf, age_idx = probs.max(dim=-1)
                    age_label = self.age_labels.get(str(age_idx.item()), "Unknown")
                    
                    # Mapear a grupos estándar
                    result['age_group'] = self._map_age_to_group(age_label)
                    result['age_conf'] = age_conf.item()
                    
                except Exception as e:
                    print(f"⚠️  Error en predicción de edad: {e}")
        
        return result

# Función de compatibilidad con la interfaz anterior
def create_ntqai_model():
    """Crea y carga los modelos NTQAI"""
    adapter = NTOAIModelsAdapter()
    if adapter.load_models():
        return adapter
    return None
'''
    
    with open(adapter_path, 'w', encoding='utf-8') as f:
        f.write(adapter_code)
    
    print(f"\n✅ Adaptador creado: {adapter_path}")

def main():
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "DESCARGA DE MODELOS NTQAI" + " "*33 + "║")
    print("╚" + "="*78 + "╝\n")
    
    # Descargar modelos
    success = download_ntoai_models()
    
    if success:
        # Crear adaptador
        create_integration_adapter()
        
        print("\n" + "="*80)
        print("✅ DESCARGA COMPLETADA")
        print("="*80)
        print("\n📋 PRÓXIMOS PASOS:")
        print("\n1. Los modelos NTQAI están descargados y listos")
        print("2. Se ha creado el adaptador ntqai_adapter.py")
        print("\n3. Para usar los modelos, ejecuta:")
        print("   python Backend/models/test_ntqai_models.py")
        print("\n4. Para integrar en el sistema, modifica Backend/app/processing.py")
        print("   para usar NTOAIModelsAdapter en lugar de PARModel")
        
    else:
        print("\n" + "="*80)
        print("❌ NO SE PUDO COMPLETAR LA DESCARGA")
        print("="*80)
        print("\n📚 DESCARGA MANUAL:")
        print("1. Ve a: https://huggingface.co/NTQAI/pedestrian_gender_recognition")
        print("2. Descarga 'pytorch_model.bin' y guárdalo como 'ntqai_gender.bin'")
        print("3. Ve a: https://huggingface.co/NTQAI/pedestrian_age_recognition")
        print("4. Descarga 'pytorch_model.bin' y guárdalo como 'ntqai_age.bin'")
        print("5. Coloca ambos archivos en Backend/models/")

if __name__ == "__main__":
    main()
