"""
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
                
                # Crear modelo base primero (sin cargar desde pretrained con state_dict)
                self.gender_model = BeitForImageClassification.from_pretrained(
                    "microsoft/beit-base-patch16-224-pt22k-ft22k",
                    num_labels=2,
                    ignore_mismatched_sizes=True
                )
                
                # Cargar state_dict del modelo entrenado DESPUÉS
                state_dict = torch.load(gender_path, map_location=self.device, weights_only=False)
                
                # Cargar los pesos en el modelo
                self.gender_model.load_state_dict(state_dict, strict=False)
                
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
                
                # Crear modelo base primero (sin cargar desde pretrained con state_dict)
                self.age_model = BeitForImageClassification.from_pretrained(
                    "microsoft/beit-base-patch16-224-pt22k-ft22k",
                    num_labels=5,
                    ignore_mismatched_sizes=True
                )
                
                # Cargar state_dict del modelo entrenado DESPUÉS
                state_dict = torch.load(age_path, map_location=self.device, weights_only=False)
                
                # Cargar los pesos en el modelo
                self.age_model.load_state_dict(state_dict, strict=False)
                
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
    adapter = NTQAIModelsAdapter()
    if adapter.load_models():
        return adapter
    return None
