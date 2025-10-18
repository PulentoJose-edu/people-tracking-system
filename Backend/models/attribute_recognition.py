"""
Pedestrian Attribute Recognition (PAR) Module
Clasificación de género y edad usando ResNet50 pre-entrenado en PETA dataset

Basado en: https://github.com/valencebond/Rethinking_of_PAR
"""

import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision.models import resnet50, ResNet50_Weights
import cv2
import numpy as np
from typing import Dict, Tuple, Optional
import os
from pathlib import Path


class PARModel:
    """
    Modelo de Reconocimiento de Atributos Peatonales
    Clasifica género y edad de personas detectadas
    """
    
    # Definición de categorías
    GENDER_LABELS = ['Masculino', 'Femenino']
    AGE_LABELS = ['Niño', 'Adolescente', 'Adulto Joven', 'Adulto', 'Mayor']
    
    def __init__(self, model_path: Optional[str] = None, device: str = 'cpu'):
        """
        Inicializa el modelo PAR
        
        Args:
            model_path: Ruta al checkpoint pre-entrenado (opcional)
            device: 'cpu' o 'cuda'
        """
        self.device = torch.device(device if torch.cuda.is_available() and device == 'cuda' else 'cpu')
        print(f"🔧 Inicializando PAR Model en: {self.device}")
        
        # Crear modelo
        self.model = self._build_model()
        
        # Cargar pesos pre-entrenados si existen
        if model_path and os.path.exists(model_path):
            self._load_checkpoint(model_path)
        else:
            print("⚠️  No se encontró checkpoint pre-entrenado. Usando modelo base.")
        
        self.model.to(self.device)
        self.model.eval()
        
        # Transformaciones de imagen (estándar PETA)
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((256, 128)),  # Altura x Ancho estándar PAR
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        # Caché de resultados por track_id
        self.cache = {}
        
    def _build_model(self) -> nn.Module:
        """
        Construye la arquitectura del modelo PAR
        ResNet50 backbone + Multi-label classification heads
        """
        # Usar ResNet50 pre-entrenado en ImageNet
        backbone = resnet50(weights=ResNet50_Weights.IMAGENET1K_V1)
        
        # Extraer features (sin la última capa FC)
        num_features = backbone.fc.in_features
        backbone.fc = nn.Identity()
        
        # Crear modelo PAR con múltiples heads
        model = nn.ModuleDict({
            'backbone': backbone,
            'gender_head': nn.Sequential(
                nn.Linear(num_features, 512),
                nn.ReLU(),
                nn.Dropout(0.5),
                nn.Linear(512, 2)  # 2 clases: Masculino, Femenino
            ),
            'age_head': nn.Sequential(
                nn.Linear(num_features, 512),
                nn.ReLU(),
                nn.Dropout(0.5),
                nn.Linear(512, 5)  # 5 clases de edad
            )
        })
        
        return model
    
    def _load_checkpoint(self, checkpoint_path: str):
        """Carga pesos pre-entrenados"""
        try:
            checkpoint = torch.load(checkpoint_path, map_location=self.device)
            
            # Intentar cargar el state dict
            if 'state_dict' in checkpoint:
                self.model.load_state_dict(checkpoint['state_dict'])
            elif 'model' in checkpoint:
                self.model.load_state_dict(checkpoint['model'])
            else:
                self.model.load_state_dict(checkpoint)
                
            print(f"✅ Checkpoint cargado desde: {checkpoint_path}")
        except Exception as e:
            print(f"❌ Error cargando checkpoint: {e}")
    
    def preprocess_bbox(self, frame: np.ndarray, bbox: Tuple[int, int, int, int]) -> torch.Tensor:
        """
        Preprocesa un bounding box para el modelo
        
        Args:
            frame: Frame completo del video (BGR)
            bbox: (x1, y1, x2, y2) coordenadas del bounding box
            
        Returns:
            Tensor preprocesado [1, 3, 256, 128]
        """
        x1, y1, x2, y2 = map(int, bbox)
        
        # Asegurar que las coordenadas estén dentro del frame
        h, w = frame.shape[:2]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        
        # Recortar persona
        person_crop = frame[y1:y2, x1:x2]
        
        # Si el crop es muy pequeño, devolver None
        if person_crop.size == 0 or person_crop.shape[0] < 10 or person_crop.shape[1] < 10:
            return None
        
        # Convertir BGR a RGB
        person_crop_rgb = cv2.cvtColor(person_crop, cv2.COLOR_BGR2RGB)
        
        # Aplicar transformaciones
        tensor = self.transform(person_crop_rgb)
        
        return tensor.unsqueeze(0)  # Add batch dimension
    
    @torch.no_grad()
    def predict(self, frame: np.ndarray, bbox: Tuple[int, int, int, int], 
                track_id: Optional[int] = None) -> Dict:
        """
        Predice género y edad de una persona
        
        Args:
            frame: Frame del video (BGR)
            bbox: (x1, y1, x2, y2) coordenadas del bounding box
            track_id: ID de tracking (opcional, para caché)
            
        Returns:
            Dict con predicciones:
            {
                'gender': str,
                'gender_confidence': float,
                'age': str,
                'age_confidence': float
            }
        """
        # Verificar caché
        if track_id is not None and track_id in self.cache:
            return self.cache[track_id]
        
        # Preprocesar
        tensor = self.preprocess_bbox(frame, bbox)
        if tensor is None:
            return self._get_default_result()
        
        tensor = tensor.to(self.device)
        
        try:
            # Forward pass
            features = self.model['backbone'](tensor)
            gender_logits = self.model['gender_head'](features)
            age_logits = self.model['age_head'](features)
            
            # Obtener predicciones con softmax
            gender_probs = torch.softmax(gender_logits, dim=1)[0]
            age_probs = torch.softmax(age_logits, dim=1)[0]
            
            # Extraer clase y confianza
            gender_idx = gender_probs.argmax().item()
            gender_conf = gender_probs[gender_idx].item()
            
            age_idx = age_probs.argmax().item()
            age_conf = age_probs[age_idx].item()
            
            result = {
                'gender': self.GENDER_LABELS[gender_idx],
                'gender_confidence': round(gender_conf, 3),
                'age': self.AGE_LABELS[age_idx],
                'age_confidence': round(age_conf, 3),
                'gender_probs': {label: round(prob.item(), 3) 
                                for label, prob in zip(self.GENDER_LABELS, gender_probs)},
                'age_probs': {label: round(prob.item(), 3) 
                             for label, prob in zip(self.AGE_LABELS, age_probs)}
            }
            
            # Guardar en caché
            if track_id is not None:
                self.cache[track_id] = result
            
            return result
            
        except Exception as e:
            print(f"Error en predicción PAR: {e}")
            return self._get_default_result()
    
    def predict_batch(self, frame: np.ndarray, bboxes: list, 
                     track_ids: Optional[list] = None) -> list:
        """
        Predice atributos para múltiples personas (batch processing)
        
        Args:
            frame: Frame del video (BGR)
            bboxes: Lista de (x1, y1, x2, y2) bounding boxes
            track_ids: Lista de track IDs (opcional)
            
        Returns:
            Lista de diccionarios con predicciones
        """
        if track_ids is None:
            track_ids = [None] * len(bboxes)
        
        results = []
        tensors = []
        valid_indices = []
        
        # Preprocesar todos los bboxes
        for idx, (bbox, track_id) in enumerate(zip(bboxes, track_ids)):
            # Verificar caché
            if track_id is not None and track_id in self.cache:
                results.append(self.cache[track_id])
                continue
            
            tensor = self.preprocess_bbox(frame, bbox)
            if tensor is not None:
                tensors.append(tensor)
                valid_indices.append((idx, track_id))
            else:
                results.insert(idx, self._get_default_result())
        
        # Si no hay tensors válidos, retornar
        if not tensors:
            return results
        
        # Batch processing
        try:
            batch_tensor = torch.cat(tensors, dim=0).to(self.device)
            
            with torch.no_grad():
                features = self.model['backbone'](batch_tensor)
                gender_logits = self.model['gender_head'](features)
                age_logits = self.model['age_head'](features)
                
                gender_probs = torch.softmax(gender_logits, dim=1)
                age_probs = torch.softmax(age_logits, dim=1)
            
            # Procesar cada resultado
            for i, (orig_idx, track_id) in enumerate(valid_indices):
                gender_idx = gender_probs[i].argmax().item()
                gender_conf = gender_probs[i][gender_idx].item()
                
                age_idx = age_probs[i].argmax().item()
                age_conf = age_probs[i][age_idx].item()
                
                result = {
                    'gender': self.GENDER_LABELS[gender_idx],
                    'gender_confidence': round(gender_conf, 3),
                    'age': self.AGE_LABELS[age_idx],
                    'age_confidence': round(age_conf, 3),
                    'gender_probs': {label: round(prob.item(), 3) 
                                    for label, prob in zip(self.GENDER_LABELS, gender_probs[i])},
                    'age_probs': {label: round(prob.item(), 3) 
                                 for label, prob in zip(self.AGE_LABELS, age_probs[i])}
                }
                
                # Guardar en caché
                if track_id is not None:
                    self.cache[track_id] = result
                
                results.insert(orig_idx, result)
            
        except Exception as e:
            print(f"Error en batch prediction: {e}")
            for orig_idx, _ in valid_indices:
                results.insert(orig_idx, self._get_default_result())
        
        return results
    
    def _get_default_result(self) -> Dict:
        """Resultado por defecto cuando no se puede hacer predicción"""
        return {
            'gender': 'Desconocido',
            'gender_confidence': 0.0,
            'age': 'Desconocido',
            'age_confidence': 0.0,
            'gender_probs': {},
            'age_probs': {}
        }
    
    def clear_cache(self):
        """Limpia el caché de predicciones"""
        self.cache.clear()
    
    def get_cache_size(self) -> int:
        """Retorna el tamaño del caché"""
        return len(self.cache)


# Función helper para crear instancia global (singleton pattern)
_par_model_instance = None

def get_par_model(model_path: Optional[str] = None, device: str = 'cpu') -> PARModel:
    """
    Obtiene o crea instancia global del modelo PAR (singleton)
    
    Args:
        model_path: Ruta al checkpoint (solo usado en primera llamada)
        device: 'cpu' o 'cuda'
        
    Returns:
        Instancia de PARModel
    """
    global _par_model_instance
    
    if _par_model_instance is None:
        _par_model_instance = PARModel(model_path=model_path, device=device)
    
    return _par_model_instance
