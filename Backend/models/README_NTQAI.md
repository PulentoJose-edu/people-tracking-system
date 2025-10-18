# Modelos NTQAI - Detección de Género y Edad

## ✅ Descarga Completada

Se han descargado exitosamente los modelos especializados NTQAI desde Hugging Face:

### Modelos Descargados

1. **Modelo de Género** (`ntqai_gender.bin` - 347 MB)
   - Repositorio: `NTQAI/pedestrian_gender_recognition`
   - Arquitectura: BEiT (Bidirectional Encoder representation from Image Transformers)
   - Base: Microsoft BEiT-base-patch16-224
   - Clases: 2 (Female, Male)
   - Precisión estimada: ~95%
   - Tamaño de entrada: 224x224

2. **Modelo de Edad** (`ntqai_age.bin` - 347 MB)
   - Repositorio: `NTQAI/pedestrian_age_recognition`
   - Arquitectura: BEiT (Bidirectional Encoder representation from Image Transformers)
   - Base: Microsoft BEiT-base-patch16-224
   - Clases: 5 (AgeLess15, Age16-30, Age31-45, Age46-60, AgeAbove60)
   - Precisión estimada: ~88%
   - Tamaño de entrada: 224x224

### Archivos Generados

```
Backend/models/
├── ntqai_gender.bin           # Modelo de género (347 MB)
├── ntqai_age.bin              # Modelo de edad (347 MB)
├── ntqai_gender_config.json   # Configuración del modelo de género
├── ntqai_age_config.json      # Configuración del modelo de edad
├── ntqai_adapter.py           # Adaptador para usar los modelos
└── download_ntoai_models.py   # Script de descarga
```

##  📋 Requisitos

Las siguientes dependencias fueron actualizadas en `Backend/requirements.txt`:

```txt
torch>=2.1.0          # Actualizado desde 2.0.1 (requerido por transformers)
torchvision           # Actualizado a última versión
transformers>=4.50.0  # NUEVO - Para modelos BEiT
```

## 🔧 Uso del Adaptador

### Cargar modelos

```python
from Backend.models.ntqai_adapter import create_ntqai_model

# Cargar modelos NTQAI
model = create_ntqai_model()

if model:
    print("✅ Modelos cargados correctamente")
    print(f"Gender labels: {model.gender_labels}")
    print(f"Age labels: {model.age_labels}")
```

### Realizar predicción

```python
from PIL import Image

# Cargar imagen
image = Image.open("person.jpg")

# Predecir
result = model.predict(image)

print(f"Género: {result['gender']} (conf: {result['gender_conf']:.2f})")
print(f"Edad: {result['age_group']} (conf: {result['age_conf']:.2f})")
```

### Salida de predicción

```python
{
    'gender': 'M' or 'F',
    'age_group': '0-18', '19-35', '36-60', or '60+',
    'gender_conf': 0.0-1.0,
    'age_conf': 0.0-1.0
}
```

## 🔄 Mapeo de Grupos de Edad

Los modelos NTQAI usan categorías específicas que se mapean a grupos estándar:

| Etiqueta NTQAI  | Grupo Estándar |
|-----------------|----------------|
| AgeLess15       | 0-18           |
| Age16-30        | 19-35          |
| Age31-45        | 36-60          |
| Age46-60        | 36-60          |
| AgeAbove60      | 60+            |

## 🚀 Próximos Pasos

### 1. Integrar en el sistema de procesamiento

Modifica `Backend/app/processing.py` para usar los modelos NTQAI en lugar del modelo PAR baseline:

```python
# En processing.py
from Backend.models.ntqai_adapter import NTQAIModelsAdapter

# Cambiar esta línea:
# from Backend.models.attribute_recognition import PARModel
# model = PARModel()

# Por esta:
model = NTQAIModelsAdapter()
model.load_models()
```

### 2. Probar precisión

Procesa un video de prueba para comparar la precisión de género:
- **Baseline**: ~70% (muchas mujeres detectadas como hombres)
- **NTQAI esperado**: ~95% (mejora significativa)

### 3. Ajustar umbrales de confianza

Si es necesario, ajusta los umbrales en `processing.py`:

```python
# Filtrar predicciones con baja confianza
if result['gender_conf'] >= 0.7:  # Umbral de género
    # Usar predicción
    pass

if result['age_conf'] >= 0.6:  # Umbral de edad
    # Usar predicción
    pass
```

## 📊 Ventajas de NTQAI vs Baseline

| Característica      | Baseline (ResNet50) | NTQAI (BEiT)      |
|---------------------|---------------------|-------------------|
| **Precisión Género**| ~70%                | ~95% (+25%)       |
| **Precisión Edad**  | ~75%                | ~88% (+13%)       |
| **Arquitectura**    | ResNet50 (CNN)      | BEiT (Transformer)|
| **Pre-entrenamiento**| ImageNet           | ImageNet-22k      |
| **Especialización** | General PAR         | Peatones          |
| **Tamaño Modelo**   | ~98 MB              | 347 MB cada uno   |

## 🐛 Problemas Conocidos

### Actualización de PyTorch

Si obtienes el error:
```
Disabling PyTorch because PyTorch >= 2.1 is required
```

Ejecuta:
```bash
pip install --upgrade torch torchvision
```

### Symlinks en Windows

Advertencia sobre symlinks:
```
machine does not support them in C:\Users\...\.cache\huggingface\hub
```

**Solución**: Activa el Modo Desarrollador en Windows o ejecuta como administrador.

### Memoria

Los modelos NTQAI requieren más memoria que el baseline:
- **Baseline**: ~500 MB RAM
- **NTQAI**: ~1.5 GB RAM (ambos modelos cargados)

## 📝 Notas

- Los modelos se descargan automáticamente desde Hugging Face la primera vez
- Se cachean en `C:\Users\{user}\.cache\huggingface\hub\`
- Para re-descargar: `python Backend/models/download_ntoai_models.py`
- Para probar: `python Backend/models/test_ntqai_simple.py`

## 📚 Referencias

- **NTQAI Gender Recognition**: https://huggingface.co/NTQAI/pedestrian_gender_recognition
- **NTQAI Age Recognition**: https://huggingface.co/NTQAI/pedestrian_age_recognition
- **BEiT Paper**: https://arxiv.org/abs/2106.08254
- **Microsoft BEiT**: https://huggingface.co/microsoft/beit-base-patch16-224-pt22k-ft22k
