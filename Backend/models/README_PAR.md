# Sistema de Detección de Edad y Género (PAR)

## 📋 Descripción General

Sistema de **Pedestrian Attribute Recognition (PAR)** integrado en el pipeline de tracking de personas. Utiliza deep learning con ResNet50 para clasificar automáticamente el género y rango de edad de las personas detectadas.

## 🎯 Características

### Categorías de Clasificación

**Género:**
- Masculino
- Femenino

**Edad:**
- Niño (0-12 años)
- Adolescente (13-17 años)
- Adulto Joven (18-30 años)
- Adulto (31-60 años)
- Mayor (60+ años)

### Optimizaciones

- ✅ **Análisis throttled**: Se ejecuta cada 15 frames (configurable) para mejor rendimiento
- ✅ **Caché por track_id**: Evita re-análisis de la misma persona
- ✅ **Batch processing**: Procesa múltiples personas simultáneamente
- ✅ **Lazy loading**: El modelo PAR solo se carga cuando se necesita
- ✅ **Activación opcional**: Se puede deshabilitar completamente

## 🏗️ Arquitectura

```
┌─────────────────┐
│  Video Frame    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  YOLO Detection │
│   + Tracking    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     Cada 15 frames
│  PAR Analysis   │ ◄───────────────
│  (Gender + Age) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Cache Results  │
│   by track_id   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  CSV + Video    │
│   with labels   │
└─────────────────┘
```

### Modelo PAR

**Backbone**: ResNet50 pre-entrenado en ImageNet
**Arquitectura**:
- Input: Bounding box recortado (256x128)
- Backbone: ResNet50 (2048 features)
- Gender Head: FC(2048→512→2) + Softmax
- Age Head: FC(2048→512→5) + Softmax

## 📦 Instalación

### 1. Instalar dependencias

```bash
pip install -r Backend/requirements.txt
```

### 2. Configurar modelo PAR

```bash
cd Backend/models
python setup_par_model.py
```

Este script:
- Descarga ResNet50 pre-entrenado (si está disponible)
- O crea un modelo baseline con ImageNet
- Verifica la integridad del modelo
- Ejecuta test básico

## 🚀 Uso

### Procesamiento de Video con PAR

```python
from Backend.app.processing import process_video_task

process_video_task(
    task_id="unique_id",
    video_path="input.mp4",
    output_video_path="output.mp4",
    output_csv_path="data.csv",
    enable_par=True,      # Habilitar análisis demográfico
    par_interval=15       # Analizar cada 15 frames
)
```

### Uso Directo del Modelo PAR

```python
from Backend.models.attribute_recognition import get_par_model
import cv2

# Cargar modelo (singleton)
model = get_par_model(device='cpu')

# Leer frame
frame = cv2.imread('frame.jpg')

# Predecir para una persona
bbox = (100, 100, 200, 400)  # x1, y1, x2, y2
result = model.predict(frame, bbox, track_id=1)

print(f"Género: {result['gender']} ({result['gender_confidence']:.2%})")
print(f"Edad: {result['age']} ({result['age_confidence']:.2%})")

# Batch processing
bboxes = [(100,100,200,400), (300,150,400,450)]
track_ids = [1, 2]
results = model.predict_batch(frame, bboxes, track_ids)
```

### API REST

El análisis demográfico se incluye automáticamente en el endpoint de analytics:

```bash
GET /analytics/analyze/{task_id}
```

Respuesta incluye:
```json
{
  "demographic_analysis": {
    "gender_distribution": {
      "counts": {"Masculino": 15, "Femenino": 10},
      "percentages": {"Masculino": 60.0, "Femenino": 40.0}
    },
    "age_distribution": {
      "counts": {...},
      "percentages": {...}
    },
    "gender_by_zone": {...},
    "age_by_zone": {...},
    "summary": {
      "total_persons_classified": 25,
      "classification_rate": 92.3,
      "average_gender_confidence": 0.876,
      "average_age_confidence": 0.743
    }
  }
}
```

## 📊 Formato CSV de Salida

El CSV ahora incluye columnas adicionales:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| timestamp_seconds | float | Timestamp del evento |
| frame | int | Número de frame |
| zone_id | int | ID de la zona |
| person_tracker_id | int | ID único de tracking |
| event | str | 'entry' o 'exit' |
| **gender** | str | Género clasificado |
| **gender_confidence** | float | Confianza (0-1) |
| **age** | str | Rango de edad |
| **age_confidence** | float | Confianza (0-1) |

## ⚙️ Configuración

### Parámetros del Procesamiento

```python
# En processing.py o via API
{
    "enable_par": True,        # Activar/desactivar PAR
    "par_interval": 15,        # Frames entre análisis (mayor = más rápido, menor = más datos)
}
```

### Optimización de Rendimiento

**CPU (default)**:
- `par_interval = 15` (analizar cada 15 frames)
- Batch size automático

**GPU (si disponible)**:
```python
model = get_par_model(device='cuda')
```
- `par_interval = 5-10` (más frecuente)
- Procesamiento más rápido

### Memoria

El caché se limpia automáticamente al finalizar cada video. Si procesas videos muy largos con muchas personas:

```python
# Limpiar caché manualmente
model.clear_cache()
```

## 🎨 Visualización en Video

Las etiquetas en el video procesado muestran:
- **Sin PAR**: `ID 1`
- **Con PAR**: `ID1 M/Adult` (ID, Género/Edad abreviado)

Abreviaturas de edad:
- Niño → Niño
- Adolescente → Adol
- Adulto Joven → A.Jov
- Adulto → Adult
- Mayor → Mayor

## 🧪 Testing

```bash
# Test del modelo PAR
cd Backend/models
python setup_par_model.py

# Test de integración
python -m pytest Backend/tests/test_par_integration.py
```

## 📈 Métricas de Rendimiento

### Precisión Esperada (con modelo baseline)

- **Género**: ~70-80% (baseline), >90% (entrenado en PETA)
- **Edad**: ~60-70% (baseline), >80% (entrenado en PETA)

### Velocidad

- **Sin PAR**: ~30-50 FPS (depende de hardware)
- **Con PAR (CPU, interval=15)**: ~20-30 FPS
- **Con PAR (GPU, interval=15)**: ~25-40 FPS

### Memoria

- **Modelo PAR**: ~100-150 MB RAM
- **Caché**: ~1-2 KB por persona tracked

## 🔧 Troubleshooting

### Error: "No se pudo cargar modelo PAR"

```bash
cd Backend/models
python setup_par_model.py
```

### Error: "CUDA out of memory"

Cambiar a CPU:
```python
model = get_par_model(device='cpu')
```

### Predicciones incorrectas

1. **Entrenar modelo específico**: El modelo baseline usa solo ImageNet
2. **Ajustar par_interval**: Más análisis = más datos para votación
3. **Verificar calidad de video**: Resolución baja afecta precisión

### Procesamiento muy lento

1. **Aumentar par_interval**: De 15 a 30 frames
2. **Deshabilitar PAR temporalmente**: `enable_par=False`
3. **Usar GPU si está disponible**

## 📚 Referencias

- [Rethinking of PAR](https://github.com/valencebond/Rethinking_of_PAR)
- [Pedestrian Attribute Recognition PyTorch](https://github.com/dangweili/pedestrian-attribute-recognition-pytorch)
- [PETA Dataset](http://www.ee.cuhk.edu.hk/~xgwang/PETA.html)
- [PA-100K Dataset](https://github.com/xh-liu/HydraPlus-Net)

## 🚀 Próximas Mejoras

- [ ] Modelo pre-entrenado en PETA/PA-100K
- [ ] Fine-tuning para cámaras cenitales
- [ ] Detección de más atributos (ropa, accesorios)
- [ ] Optimización cuantizada para mejor FPS
- [ ] Integración con re-identification
- [ ] Dashboard de calibración de modelo

## 📄 Licencia

Ver LICENSE en el directorio raíz del proyecto.
