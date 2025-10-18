"""
Script para fine-tuning del modelo PAR en dataset PETA/PA-100K
Mejora significativa en la precisión de género y edad
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from pathlib import Path
import pandas as pd
from PIL import Image
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from models.attribute_recognition import PARModel


class PETADataset(Dataset):
    """
    Dataset para PETA (PEdesTrian Attribute dataset)
    
    Estructura esperada:
    PETA/
    ├── images/
    │   ├── person_001.jpg
    │   ├── person_002.jpg
    │   └── ...
    └── PETA.csv  # Con columnas: filename, gender, age_group
    
    Descargar PETA: http://www.ee.cuhk.edu.hk/~xgwang/PETA.html
    """
    
    def __init__(self, csv_path: str, images_dir: str, transform=None):
        self.df = pd.read_csv(csv_path)
        self.images_dir = Path(images_dir)
        self.transform = transform
        
        # Mapeo de etiquetas
        self.gender_map = {'Male': 0, 'Female': 1, 'M': 0, 'F': 1}
        self.age_map = {
            'Child': 0,      # Niño
            'Teen': 1,       # Adolescente
            'Young': 2,      # Adulto Joven
            'Adult': 3,      # Adulto
            'Elder': 4       # Mayor
        }
        
    def __len__(self):
        return len(self.df)
    
    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        
        # Cargar imagen
        img_path = self.images_dir / row['filename']
        image = Image.open(img_path).convert('RGB')
        
        if self.transform:
            image = self.transform(image)
        
        # Etiquetas
        gender_label = self.gender_map.get(row['gender'], 0)
        age_label = self.age_map.get(row['age_group'], 3)
        
        return image, gender_label, age_label


def train_par_model(
    train_csv: str,
    train_images: str,
    val_csv: str,
    val_images: str,
    checkpoint_path: str,
    epochs: int = 20,
    batch_size: int = 32,
    learning_rate: float = 0.001,
    device: str = 'cuda'
):
    """
    Fine-tune del modelo PAR
    
    Args:
        train_csv: Path al CSV de entrenamiento
        train_images: Directorio con imágenes de entrenamiento
        val_csv: Path al CSV de validación
        val_images: Directorio con imágenes de validación
        checkpoint_path: Donde guardar el modelo entrenado
        epochs: Número de épocas
        batch_size: Tamaño del batch
        learning_rate: Learning rate
        device: 'cuda' o 'cpu'
    """
    
    print("=" * 60)
    print("FINE-TUNING DEL MODELO PAR")
    print("=" * 60)
    
    device = torch.device(device if torch.cuda.is_available() else 'cpu')
    print(f"📱 Device: {device}")
    
    # 1. Preparar transformaciones (mismas que el modelo usa)
    transform = transforms.Compose([
        transforms.Resize((256, 128)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                           std=[0.229, 0.224, 0.225])
    ])
    
    # 2. Cargar datasets
    print("\n📁 Cargando datasets...")
    train_dataset = PETADataset(train_csv, train_images, transform)
    val_dataset = PETADataset(val_csv, val_images, transform)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, 
                             shuffle=True, num_workers=4)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, 
                           shuffle=False, num_workers=4)
    
    print(f"   Train samples: {len(train_dataset)}")
    print(f"   Val samples: {len(val_dataset)}")
    
    # 3. Cargar modelo base
    print("\n🔧 Cargando modelo base...")
    par_model = PARModel(device=str(device))
    model = par_model.model.to(device)
    
    # 4. Congelar backbone (solo entrenar heads)
    print("❄️  Congelando backbone (solo entrenar heads)...")
    for param in model['backbone'].parameters():
        param.requires_grad = False
    
    # Los heads sí se entrenan
    for param in model['gender_head'].parameters():
        param.requires_grad = True
    for param in model['age_head'].parameters():
        param.requires_grad = True
    
    # 5. Configurar entrenamiento
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam([
        {'params': model['gender_head'].parameters()},
        {'params': model['age_head'].parameters()}
    ], lr=learning_rate)
    
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.5)
    
    # 6. Entrenamiento
    best_val_acc = 0.0
    
    for epoch in range(epochs):
        print(f"\n{'='*60}")
        print(f"Epoch {epoch+1}/{epochs}")
        print(f"{'='*60}")
        
        # Entrenamiento
        model.train()
        train_loss = 0.0
        train_gender_correct = 0
        train_age_correct = 0
        train_total = 0
        
        for batch_idx, (images, gender_labels, age_labels) in enumerate(train_loader):
            images = images.to(device)
            gender_labels = gender_labels.to(device)
            age_labels = age_labels.to(device)
            
            # Forward pass
            features = model['backbone'](images)
            gender_outputs = model['gender_head'](features)
            age_outputs = model['age_head'](features)
            
            # Loss
            gender_loss = criterion(gender_outputs, gender_labels)
            age_loss = criterion(age_outputs, age_labels)
            loss = gender_loss + age_loss
            
            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            # Métricas
            train_loss += loss.item()
            _, gender_preds = torch.max(gender_outputs, 1)
            _, age_preds = torch.max(age_outputs, 1)
            train_gender_correct += (gender_preds == gender_labels).sum().item()
            train_age_correct += (age_preds == age_labels).sum().item()
            train_total += gender_labels.size(0)
            
            if (batch_idx + 1) % 10 == 0:
                print(f"   Batch {batch_idx+1}/{len(train_loader)} - "
                      f"Loss: {loss.item():.4f}")
        
        # Métricas de entrenamiento
        train_loss /= len(train_loader)
        train_gender_acc = 100. * train_gender_correct / train_total
        train_age_acc = 100. * train_age_correct / train_total
        
        print(f"\n📊 Train - Loss: {train_loss:.4f} | "
              f"Gender Acc: {train_gender_acc:.2f}% | "
              f"Age Acc: {train_age_acc:.2f}%")
        
        # Validación
        model.eval()
        val_loss = 0.0
        val_gender_correct = 0
        val_age_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for images, gender_labels, age_labels in val_loader:
                images = images.to(device)
                gender_labels = gender_labels.to(device)
                age_labels = age_labels.to(device)
                
                features = model['backbone'](images)
                gender_outputs = model['gender_head'](features)
                age_outputs = model['age_head'](features)
                
                gender_loss = criterion(gender_outputs, gender_labels)
                age_loss = criterion(age_outputs, age_labels)
                loss = gender_loss + age_loss
                
                val_loss += loss.item()
                _, gender_preds = torch.max(gender_outputs, 1)
                _, age_preds = torch.max(age_outputs, 1)
                val_gender_correct += (gender_preds == gender_labels).sum().item()
                val_age_correct += (age_preds == age_labels).sum().item()
                val_total += gender_labels.size(0)
        
        val_loss /= len(val_loader)
        val_gender_acc = 100. * val_gender_correct / val_total
        val_age_acc = 100. * val_age_correct / val_total
        val_avg_acc = (val_gender_acc + val_age_acc) / 2
        
        print(f"📊 Val   - Loss: {val_loss:.4f} | "
              f"Gender Acc: {val_gender_acc:.2f}% | "
              f"Age Acc: {val_age_acc:.2f}%")
        
        # Guardar mejor modelo
        if val_avg_acc > best_val_acc:
            best_val_acc = val_avg_acc
            checkpoint = {
                'epoch': epoch,
                'state_dict': model.state_dict(),
                'optimizer': optimizer.state_dict(),
                'val_gender_acc': val_gender_acc,
                'val_age_acc': val_age_acc,
                'model_type': 'resnet50_par_finetuned'
            }
            torch.save(checkpoint, checkpoint_path)
            print(f"✅ Mejor modelo guardado! (Val Acc: {val_avg_acc:.2f}%)")
        
        scheduler.step()
    
    print("\n" + "=" * 60)
    print("✅ ENTRENAMIENTO COMPLETADO")
    print(f"   Mejor Val Accuracy: {best_val_acc:.2f}%")
    print(f"   Modelo guardado en: {checkpoint_path}")
    print("=" * 60)


if __name__ == "__main__":
    """
    Ejemplo de uso:
    
    1. Descargar PETA dataset de: http://www.ee.cuhk.edu.hk/~xgwang/PETA.html
    2. Organizar datos en estructura:
       data/PETA/
       ├── images/
       └── annotations.csv
    
    3. Ejecutar:
       python finetune_par.py
    """
    
    # Configuración
    DATA_DIR = Path("data/PETA")
    TRAIN_CSV = DATA_DIR / "train.csv"
    TRAIN_IMAGES = DATA_DIR / "images"
    VAL_CSV = DATA_DIR / "val.csv"
    VAL_IMAGES = DATA_DIR / "images"
    CHECKPOINT_PATH = Path(__file__).parent / "resnet50_peta_finetuned.pth"
    
    # Verificar que existen los datos
    if not TRAIN_CSV.exists():
        print("❌ Error: No se encontró el dataset PETA")
        print(f"   Esperado en: {TRAIN_CSV}")
        print("\n📚 Pasos para obtener PETA:")
        print("   1. Descargar de: http://www.ee.cuhk.edu.hk/~xgwang/PETA.html")
        print("   2. Extraer y organizar en data/PETA/")
        print("   3. Crear train.csv y val.csv con columnas: filename, gender, age_group")
        exit(1)
    
    # Entrenar
    train_par_model(
        train_csv=str(TRAIN_CSV),
        train_images=str(TRAIN_IMAGES),
        val_csv=str(VAL_CSV),
        val_images=str(VAL_IMAGES),
        checkpoint_path=str(CHECKPOINT_PATH),
        epochs=20,
        batch_size=32,
        learning_rate=0.001,
        device='cuda'  # Cambiar a 'cpu' si no tienes GPU
    )
