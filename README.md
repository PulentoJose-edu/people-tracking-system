# People Tracking System 👥📊

Sistema avanzado de seguimiento, conteo y análisis demográfico de personas usando YOLO v8, modelos NTQAI y dashboard interactivo.

## 📋 Descripción

Sistema completo de análisis de video que combina:
- **Detección y tracking** de personas con YOLOv8 y ByteTrack
- **Análisis demográfico** con modelos NTQAI (género y edad ~95% precisión)
- **Analytics en tiempo real** con dashboard interactivo
- **Detección de entrada/salida** y cálculo de permanencia por zona

## 🏗️ Arquitectura

- **Frontend**: Vue.js 3 + Vite + Chart.js
- **Backend**: FastAPI (Python) + Analytics Engine
- **Detección**: YOLOv8 (Ultralytics)
- **Tracking**: ByteTrack
- **PAR (Pedestrian Attribute Recognition)**: Modelos NTQAI BEiT
  - Género: ~95% precisión (2 clases: M/F)
  - Edad: ~88% precisión (5 rangos etarios)
- **Análisis**: Supervision + Pandas + NumPy

## 🚀 Características Principales

### 🎯 Detección y Tracking
- ✅ Detección de personas en tiempo real con YOLOv8
- ✅ Seguimiento multi-objeto con ByteTrack
- ✅ División en 4 zonas configurables
- ✅ Detección automática de entrada/salida por zona

### 👤 Análisis Demográfico (NTQAI)
- ✅ **Detección de género** (Masculino/Femenino) ~95% precisión
- ✅ **Clasificación de edad** en 5 rangos (0-18, 19-35, 36-60, 60+)
- ✅ Confidence scores para cada predicción
- ✅ Procesamiento optimizado por lotes (batch processing)
- ✅ Sistema de caché por track_id

### 📊 Analytics Dashboard
- ✅ **Métricas demográficas interactivas**:
  - Distribución por género (gráfico de dona)
  - Distribución por edad (gráfico de barras)
  - Análisis demográfico por zona
- ✅ **Tiempo de permanencia preciso**
- ✅ **Análisis temporal** (tráfico por horas)
- ✅ **Estadísticas por zona** en tiempo real
- ✅ Visualizaciones con Chart.js

### 💾 Exportación de Datos
- ✅ CSV con datos demográficos completos (9 columnas)
- ✅ Video procesado con anotaciones visuales
- ✅ API REST con endpoints de analytics
- ✅ Interfaz web intuitiva


## ⚡ Inicio Rápido

### 🪟 **Windows**
```bash
# 1. Clonar el repositorio
git clone https://github.com/PulentoJose-edu/people-tracking-system.git
cd people-tracking-system

# 2. Ejecutar instalación automática (instala dependencias Python y Node.js)
setup.bat

# 3. Descargar modelos NTQAI (género y edad - ~700MB total)
cd Backend\models
python download_ntoai_models.py
cd ..\..

# 4. Iniciar la aplicación (backend + frontend simultáneamente)
start.bat
```

### 🐧 **Linux / 🍎 macOS**
```bash
# 1. Clonar el repositorio
git clone https://github.com/PulentoJose-edu/people-tracking-system.git
cd people-tracking-system

# 2. Ejecutar instalación automática
chmod +x setup.sh start.sh
./setup.sh

# 3. Descargar modelos NTQAI
cd Backend/models
python download_ntoai_models.py
cd ../..

# 4. Iniciar la aplicación
./start.sh
```

### 🌐 **Acceso a la aplicación**
- **Frontend (Interfaz)**: http://localhost:5173
- **Backend (API)**: http://127.0.0.1:8000
- **Documentación API**: http://127.0.0.1:8000/docs

### 📦 **Modelos NTQAI Requeridos**

Los modelos de detección demográfica se descargan desde Hugging Face:

| Modelo | Tamaño | Repositorio | Precisión |
|--------|--------|-------------|-----------|
| **Género** | 347 MB | `NTQAI/pedestrian_gender_recognition` | ~95% |
| **Edad** | 347 MB | `NTQAI/pedestrian_age_recognition` | ~88% |

**Total**: ~700 MB

#### ⚠️ **IMPORTANTE: Configuración de Modelos NTQAI**

El script `download_ntoai_models.py` descarga automáticamente:

1. **Archivos de modelos**:
   - `ntqai_gender.bin` (347 MB)
   - `ntqai_age.bin` (347 MB)

2. **Archivos de configuración**:
   - `ntqai_gender_config.json` (mapeo de labels de género)
   - `ntqai_age_config.json` (mapeo de labels de edad)

3. **Adaptador de integración**:
   - `ntqai_adapter.py` (interfaz Python para los modelos)

**El script crea estos 5 archivos automáticamente en `Backend/models/`**. Si faltan, el sistema de análisis demográfico no funcionará.

#### ✅ **Verificar Instalación de Modelos**

```bash
# Windows
cd Backend\models
dir ntqai*.*

# Linux/Mac
cd Backend/models
ls -lh ntqai*.*
```

**Deberías ver**:
```
ntqai_adapter.py         (~8 KB)
ntqai_age.bin           (347 MB)
ntqai_age_config.json   (~1 KB)
ntqai_gender.bin        (347 MB)
ntqai_gender_config.json (~1 KB)
```

Si faltan archivos, ejecuta nuevamente:
```bash
python download_ntoai_models.py
```

> **Nota**: La primera ejecución de `download_ntoai_models.py` puede tardar varios minutos dependiendo de tu conexión a internet.


## 🆕 Instalación en PC Nuevo (Guía Completa)

Si estás instalando el proyecto en una máquina nueva por primera vez, sigue esta lista de verificación:

### ✅ **Checklist de Instalación**

1. **Prerrequisitos del Sistema**
   - [ ] Python 3.11+ instalado (`python --version`)
   - [ ] Node.js 20+ instalado (`node --version`)
   - [ ] Git instalado (`git --version`)
   - [ ] ~2 GB de espacio libre en disco

2. **Clonar y Preparar**
   ```bash
   git clone https://github.com/PulentoJose-edu/people-tracking-system.git
   cd people-tracking-system
   ```

3. **Instalar Dependencias**
   ```bash
   # Windows
   setup.bat
   
   # Linux/Mac
   chmod +x setup.sh && ./setup.sh
   ```

4. **⚠️ CRÍTICO: Descargar Modelos NTQAI**
   ```bash
   # Windows
   cd Backend\models
   python download_ntoai_models.py
   
   # Linux/Mac
   cd Backend/models
   python download_ntoai_models.py
   ```
   
   **Este paso descarga ~700MB y crea 5 archivos esenciales**:
   - `ntqai_gender.bin` + `ntqai_gender_config.json`
   - `ntqai_age.bin` + `ntqai_age_config.json`
   - `ntqai_adapter.py` (generado automáticamente)

5. **Verificar que TODO esté listo**
   ```bash
   # Windows
   dir ntqai*.*
   
   # Linux/Mac
   ls -lh ntqai*.*
   ```
   
   Debes ver **5 archivos** (total ~700MB)

6. **Iniciar la Aplicación**
   ```bash
   # Volver a la raíz del proyecto
   cd ..\..  # Windows
   cd ../..  # Linux/Mac
   
   # Iniciar
   start.bat  # Windows
   ./start.sh # Linux/Mac
   ```

7. **✅ VERIFICAR INSTALACIÓN (Recomendado)**
   ```bash
   python verify_setup.py
   ```
   
   Este script verifica:
   - Versión de Python y Node.js
   - Paquetes instalados
   - Modelos NTQAI descargados (5 archivos)
   - Estructura de directorios
   - Puertos disponibles

8. **Abrir en el Navegador**
   - Frontend: http://localhost:5173
   - Backend API: http://127.0.0.1:8000/docs

### 🚨 **Errores Comunes en Primera Instalación**

| Error | Solución |
|-------|----------|
| "ModuleNotFoundError: No module named 'transformers'" | `pip install transformers>=4.50.0` |
| "NTQAI models not found" | Ejecutar `download_ntoai_models.py` |
| "No se pudo cargar modelo PAR" | Verificar que existan los 5 archivos `ntqai_*.*` |
| "huggingface_hub not found" | `pip install huggingface_hub` |
| Backend no inicia | Verificar que el puerto 8000 esté libre |

---

## 📦 Instalación Manual (Avanzada)

### Prerrequisitos

- **Python** 3.11+
- **Node.js** 20.19+ o 22.12+
- **npm** o yarn
- **Git**
- **~2 GB de espacio** en disco (modelos + dependencias)

### Backend

```bash
cd Backend

# Instalar dependencias Python
pip install -r requirements.txt

# CRÍTICO: Descargar modelos NTQAI (género + edad + configs)
cd models
python download_ntoai_models.py
cd ..
```

**Dependencias principales**:
- `ultralytics` - YOLOv8
- `torch>=2.1.0` - PyTorch (actualizado para transformers)
- `transformers>=4.50.0` - Hugging Face (modelos NTQAI BEiT)
- `fastapi` - Framework web
- `opencv-python` - Procesamiento de video
- `supervision` - Herramientas CV
- `pandas`, `numpy` - Análisis de datos

### Frontend

```bash
cd frontend

# Instalar dependencias Node.js
npm install
```

**Dependencias principales**:
- `vue@3` - Framework frontend
- `chart.js` - Visualizaciones
- `axios` - Cliente HTTP
- `vite` - Build tool


## 🏃‍♂️ Uso del Sistema

### Ejecutar Backend

```bash
cd Backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

El backend estará disponible en: **http://127.0.0.1:8000**

### Ejecutar Frontend

```bash
cd frontend
npm run dev
```

El frontend estará disponible en: **http://localhost:5173**

---

## 📊 Dashboard de Analytics

### Acceso al Dashboard

1. **Procesa un video** a través de la interfaz principal
2. **Ve a la pestaña "Analytics Dashboard"**
3. **Selecciona la tarea procesada** del dropdown

### Visualizaciones Disponibles

#### 📈 **Métricas Principales**
- Total de personas detectadas
- Personas únicas identificadas
- Tiempo promedio de permanencia
- Duración total del video

#### 👥 **Analytics Demográficos** (NTQAI)
- **Tarjetas de resumen**:
  - Género predominante (♂️/♀️)
  - Edad más común (rango etario)
- **Gráfico de Género** (dona): Distribución M/F con porcentajes
- **Gráfico de Edad** (barras): 4 rangos con cantidades y %
- **Género por Zona** (barras agrupadas): Comparación M/F por área
- **Edad por Zona** (barras apiladas): Distribución etaria por área

#### ⏱️ **Análisis de Permanencia**
- Distribución de tiempos (< 10s, 10-30s, 30-60s, > 60s)
- Tiempo promedio por zona
- Número de visitas por zona

#### 🕐 **Análisis Temporal**
- Gráfico de actividad por timestamp
- Pico de actividad (frame con más detecciones)
- Promedio de detecciones por segundo

#### 📍 **Análisis por Zonas**
- Entradas totales por zona
- Personas únicas por zona
- Duración de actividad por zona
- Transiciones entre zonas

### API Endpoints de Analytics

```bash
# Resumen general de todas las tareas
GET /analytics/summary

# Análisis completo de una tarea específica
GET /analytics/analyze/{task_id}
# Incluye: demographic_analysis, dwell_time_analysis, zone_analysis, temporal_analysis, flow_analysis
```

**Ejemplo de respuesta** con datos demográficos:

```json
{
  "demographic_analysis": {
    "has_data": true,
    "gender_distribution": {
      "counts": {"M": 25, "F": 18},
      "percentages": {"M": 58.14, "F": 41.86}
    },
    "age_distribution": {
      "counts": {"19-35": 20, "36-60": 15, "0-18": 5, "60+": 3},
      "percentages": {"19-35": 46.51, "36-60": 34.88, "0-18": 11.63, "60+": 6.98}
    },
    "gender_by_zone": {
      "zone_0": {"counts": {"M": 10, "F": 5}, "percentages": {...}},
      "zone_1": {"counts": {"M": 8, "F": 7}, "percentages": {...}}
    },
    "age_by_zone": {...},
    "summary": {
      "most_common_gender": "M",
      "most_common_age": "19-35"
    }
  }
}
```

---

## 📊 Análisis de Datos Generados

### Archivos de Salida

Cada video procesado genera:

1. **Video Procesado** (`*_processed.mp4`)
   - Anotaciones visuales de detección
   - IDs de tracking
   - **Etiquetas demográficas** (ej: "ID5 M/19-35")
   - Contadores por zona

2. **Archivo CSV** (`*_data.csv`) con **9 columnas**:

```csv
timestamp_seconds,frame,zone_id,person_tracker_id,event,gender,gender_confidence,age,age_confidence
0.04,1,0,3,entry,Desconocido,0.0,Desconocido,0.0
0.4,10,1,42,entry,Masculino,0.539,Adulto,0.244
1.48,37,2,44,exit,Femenino,0.515,Adulto,0.236
```

**Columnas del CSV**:
- `timestamp_seconds`: Tiempo del evento
- `frame`: Número de frame
- `zone_id`: ID de la zona (0-3)
- `person_tracker_id`: ID único del tracking
- `event`: Tipo de evento (`entry` o `exit`)
- `gender`: Género detectado (`M`, `F`, o `Desconocido`)
- `gender_confidence`: Confianza del modelo (0.0-1.0)
- `age`: Rango de edad (`0-18`, `19-35`, `36-60`, `60+`, o `Desconocido`)
- `age_confidence`: Confianza del modelo (0.0-1.0)

> **Nota sobre "Desconocido"**: Las personas aparecen como "Desconocido" en:
> - El primer frame (aún no se han procesado atributos)
> - Personas con baja calidad de imagen (borrosas, muy lejanas)
> - Personas de espaldas u ocluidas

3. **Analytics JSON** (vía API)
   - Estadísticas agregadas
   - Distribuciones demográficas
   - Métricas por zona
   - Análisis temporal

---

## 👤 Sistema de Detección Demográfica (PAR)

### Arquitectura NTQAI

**Modelos BEiT** (Bidirectional Encoder representation from Image Transformers):
- **Backbone**: Microsoft BEiT-base-patch16-224
- **Input**: Bounding box recortado 224x224
- **Batch processing**: Procesa múltiples personas simultáneamente
- **Caché inteligente**: Evita re-procesar la misma persona

### Categorías de Clasificación

**Género:**
- Masculino (M)
- Femenino (F)

**Edad (5 rangos):**
- **0-18 años**: Niños y adolescentes
- **19-35 años**: Adultos jóvenes
- **36-60 años**: Adultos
- **60+ años**: Adultos mayores
- **Desconocido**: No detectado o baja confianza

### Optimizaciones de Performance

- ✅ **Análisis throttled**: Se ejecuta cada 15 frames (configurable)
- ✅ **Caché por track_id**: Reutiliza predicciones previas
- ✅ **Lazy loading**: Modelos se cargan solo cuando se necesitan
- ✅ **Activación opcional**: Sistema PAR puede deshabilitarse

### Métricas de Rendimiento

| Configuración | FPS | Overhead |
|--------------|-----|----------|
| Sin PAR | 30-50 | - |
| Con PAR (interval=15) | 20-30 | ~30% |
| Con PAR (interval=30) | 25-35 | ~20% |

**Precisión**:
- Género: ~95% (modelos NTQAI)
- Edad: ~88% (modelos NTQAI)

### Configuración Avanzada

Para ajustar el comportamiento del sistema PAR:

```python
# En Backend/app/processing.py
process_video_task(
    ...,
    enable_par=True,       # Activar/desactivar PAR
    par_interval=15        # Frames entre análisis (default: 15)
)
```


## 🎯 Zonas de Detección

El sistema divide automáticamente el frame en **4 zonas** para análisis espacial:

```
┌─────────┬─────────┐
│  Zona 0 │ Zona 1  │  ← Zonas superiores
├─────────┼─────────┤
│  Zona 2 │ Zona 3  │  ← Zonas inferiores
└─────────┴─────────┘
```

**Eventos detectados por zona**:
- `entry`: Persona entra a la zona
- `exit`: Persona sale de la zona

**Métricas calculadas**:
- Total de entradas por zona
- Personas únicas por zona
- Tiempo promedio de permanencia
- Distribución demográfica (género/edad)
- Transiciones entre zonas

---

## 🛠️ Stack Tecnológico

### Backend (Python)
| Tecnología | Versión | Propósito |
|-----------|---------|-----------|
| **FastAPI** | Latest | Framework web moderno y rápido |
| **Ultralytics YOLOv8** | Latest | Detección de personas |
| **PyTorch** | ≥2.1.0 | Deep learning framework |
| **Transformers** | ≥4.50.0 | Modelos NTQAI BEiT |
| **OpenCV** | Latest | Procesamiento de video |
| **Supervision** | Latest | Herramientas de CV |
| **ByteTrack** | - | Algoritmo de tracking multi-objeto |
| **Pandas** | Latest | Análisis de datos |
| **NumPy** | 1.26.4 | Computación numérica |

### Frontend (JavaScript)
| Tecnología | Versión | Propósito |
|-----------|---------|-----------|
| **Vue.js** | 3 | Framework progresivo |
| **Vite** | Latest | Build tool rápida |
| **Chart.js** | Latest | Visualizaciones interactivas |
| **Axios** | Latest | Cliente HTTP |

### Modelos de IA
| Modelo | Tamaño | Propósito | Precisión |
|--------|--------|-----------|-----------|
| **YOLOv8n** | ~6 MB | Detección de personas | Alta |
| **NTQAI Gender** | 347 MB | Clasificación de género | ~95% |
| **NTQAI Age** | 347 MB | Clasificación de edad | ~88% |

---

## 📁 Estructura del Proyecto

```
people-tracking-system/
├── Backend/
│   ├── app/
│   │   ├── main.py              # API principal FastAPI
│   │   ├── processing.py        # Pipeline de procesamiento + PAR
│   │   └── analytics.py         # Motor de análisis y métricas
│   ├── models/
│   │   ├── ntqai_adapter.py     # Adaptador para modelos NTQAI
│   │   ├── download_ntoai_models.py  # Descarga modelos
│   │   ├── ntqai_gender.bin     # Modelo de género (347 MB)
│   │   ├── ntqai_age.bin        # Modelo de edad (347 MB)
│   │   ├── README_NTQAI.md      # Documentación NTQAI
│   │   └── README_PAR.md        # Documentación PAR
│   ├── uploads/                 # Videos subidos
│   ├── outputs/                 # Resultados procesados
│   │   ├── *_processed.mp4      # Videos con anotaciones
│   │   └── *_data.csv           # Datos de tracking + demografía
│   └── requirements.txt         # Dependencias Python
│
├── frontend/
│   ├── src/
│   │   ├── App.vue              # Componente principal
│   │   ├── main.js              # Punto de entrada
│   │   └── components/
│   │       ├── AnalyticsDashboard.vue  # Dashboard completo
│   │       └── HelloWorld.vue   # Componente de bienvenida
│   ├── package.json             # Dependencias Node.js
│   └── public/                  # Archivos estáticos
│
├── yolov8n.pt                   # Modelo YOLO (descarga automática)
├── setup.bat / setup.sh         # Scripts de instalación
├── start.bat / start.sh         # Scripts de inicio
├── README.md                    # Este archivo
├── FEATURE_PAR_README.md        # Documentación de la feature PAR
├── GUIA_PRUEBA_GRAFICOS_DEMOGRAFICOS.md  # Guía de testing
└── DASHBOARD_PLAN.md            # Plan del dashboard
```

---


## 🔧 Configuración

### Variables de Entorno

El sistema utiliza las siguientes configuraciones:

- **Backend URL**: `http://127.0.0.1:8000`
- **Frontend URL**: `http://localhost:5173`
- **Modelo YOLO**: `yolov8n.pt` (se descarga automáticamente)
- **Modelos NTQAI**: Requieren descarga manual con `download_ntoai_models.py`

### CORS

El backend está configurado para permitir conexiones desde:
- `http://localhost:5173`
- `http://127.0.0.1:5173`

### Configuración del Sistema PAR

Ajustes disponibles en `Backend/app/processing.py`:

```python
# Activar/desactivar análisis demográfico
ENABLE_PAR = True  # Default: True

# Intervalo de análisis (frames)
PAR_INTERVAL = 15  # Default: 15 frames

# Dispositivo de procesamiento
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
```

---

## 🔍 Troubleshooting

### Problemas Comunes y Soluciones

#### ❌ **Error de NumPy**
```bash
# Solución
pip uninstall numpy -y
pip install numpy==1.26.4
```

#### ❌ **Error de OpenCV**
```bash
# Solución
pip install opencv-python-headless==4.10.0.84
```

#### ❌ **Error: "No se pudo cargar modelo PAR"** o **"NTQAI models not found"**

**Causa**: Los modelos NTQAI no están descargados o faltan archivos de configuración.

**Solución completa**:
```bash
# 1. Ve al directorio de modelos
cd Backend/models

# 2. Ejecuta el script de descarga (crea 5 archivos necesarios)
python download_ntoai_models.py

# 3. Verifica que se crearon todos los archivos
# Windows:
dir ntqai*.*

# Linux/Mac:
ls -lh ntqai*.*

# Deberías ver:
# - ntqai_adapter.py (adaptador Python)
# - ntqai_gender.bin (modelo de género)
# - ntqai_gender_config.json (configuración)
# - ntqai_age.bin (modelo de edad)
# - ntqai_age_config.json (configuración)
```

**Si el error persiste**:
```bash
# Eliminar archivos existentes y descargar de nuevo
rm ntqai_*.* (o del *.*)  # Linux/Mac (o Windows)
python download_ntoai_models.py
```

#### ❌ **PyTorch incompatible con transformers**
```bash
# Actualizar PyTorch
pip install torch>=2.1.0 torchvision
pip install transformers>=4.50.0
```

#### ❌ **Error: "state_dict cannot be passed together with a model name"**

**Causa**: Versión incompatible de `transformers` (4.46+) cambió la API de carga de modelos.

**Solución**:
```bash
# Opción 1: Actualizar el adaptador (recomendado)
cd Backend/models
python download_ntoai_models.py  # Regenera ntqai_adapter.py con código corregido

# Opción 2: Si el error persiste, verifica versiones
pip install transformers==4.57.1 torch>=2.9.0
```

**Explicación técnica**: El error ocurre porque versiones nuevas de `transformers` no permiten pasar `state_dict` directamente en `from_pretrained()`. El código corregido:
1. Primero crea el modelo base: `BeitForImageClassification.from_pretrained(...)`
2. Luego carga los pesos: `model.load_state_dict(state_dict, strict=False)`

#### ❌ **Puerto ocupado**
- **Backend**: Cambia el puerto en el comando uvicorn:
  ```bash
  uvicorn app.main:app --reload --port 8001
  ```
- **Frontend**: Vite asignará automáticamente otro puerto disponible

#### ❌ **CUDA out of memory** (GPUs con poca VRAM)
```python
# En Backend/models/ntqai_adapter.py, forzar CPU:
device = 'cpu'  # En lugar de 'cuda'
```

#### ❌ **Procesamiento muy lento con PAR**
```python
# Ajustar intervalo de análisis en processing.py:
PAR_INTERVAL = 30  # En lugar de 15
```

#### ❌ **Modelos NTQAI no se descargan**
```bash
# Verificar conexión a Hugging Face
pip install --upgrade huggingface_hub

# Descargar manualmente
cd Backend/models
python download_ntoai_models.py
```

### Verificación de Instalación

```bash
# Verificar backend
cd Backend
python -c "import torch, transformers, ultralytics; print('✅ OK')"

# Verificar modelos NTQAI
python -c "import os; print('Gender:', os.path.exists('models/ntqai_gender.bin')); print('Age:', os.path.exists('models/ntqai_age.bin'))"

# Verificar frontend
cd ../frontend
npm list vue chart.js axios
```

---

## 🧪 Pruebas de Rendimiento

El sistema incluye herramientas completas para medir tiempos de respuesta del backend y dashboard.

### Quick Start

#### Probar Backend (con task_id existente)
```bash
python test_performance.py --task-id TU_TASK_ID_AQUI
```

#### Probar Dashboard
```bash
# Instalar dependencias
pip install selenium

# Ejecutar prueba
python test_dashboard_performance.py --tool selenium
```

#### Script Interactivo (Windows)
```bash
run_performance_tests.bat
```

### Métricas Clave

| Componente | Métrica | Objetivo |
|------------|---------|----------|
| **Backend API** | `/analytics/analyze` | < 500ms |
| **Backend API** | `/status/{task_id}` | < 100ms |
| **Backend Streaming** | Video TTFB | < 200ms |
| **Dashboard** | Page Load | < 3s |
| **Dashboard** | First Contentful Paint | < 1.8s |
| **Dashboard** | Time to Interactive | < 3.8s |

### Herramientas Disponibles

- **`test_performance.py`**: Pruebas completas del backend
  - Tiempo de carga de video
  - Tiempo de procesamiento
  - Latencia de APIs
  - Streaming de video

- **`test_dashboard_performance.py`**: Pruebas del frontend
  - Tiempo de carga de página
  - Métricas de renderizado
  - Performance del navegador
  - Auditoría con Lighthouse

- **`run_performance_tests.bat`**: Script interactivo para Windows

### Documentación Completa

Ver **`GUIA_PRUEBAS_RENDIMIENTO.md`** para:
- ✅ Instrucciones detalladas de uso
- ✅ Interpretación de resultados
- ✅ Web Vitals y métricas clave
- ✅ Casos de uso comunes
- ✅ Solución de problemas

---


## 📈 Roadmap y Mejoras Futuras

### ✅ Implementado
- [x] Detección de personas en tiempo real
- [x] Tracking multi-objeto con ByteTrack
- [x] Detección de entrada y salida por zonas
- [x] Cálculo de tiempo de permanencia
- [x] Dashboard de analytics interactivo
- [x] Análisis de tráfico temporal
- [x] **Sistema PAR con modelos NTQAI**
- [x] **Detección de género (~95% precisión)**
- [x] **Clasificación de edad en 5 rangos (~88% precisión)**
- [x] **Visualizaciones demográficas en dashboard**
- [x] **Análisis demográfico por zona**
- [x] **Exportación de datos con columnas demográficas**

### 🔜 Próximas Mejoras

#### Análisis Demográfico
- [ ] Toggle para incluir/excluir "Desconocido" en gráficos
- [ ] Filtro por umbral de confidence mínimo
- [ ] Exportación de analytics demográficos a Excel/PDF
- [ ] Fine-tuning de modelos NTQAI con datasets específicos (PETA, PA-100K)

#### Funcionalidades Core
- [ ] Configuración dinámica de zonas (dibujar en interfaz)
- [ ] Re-identificación de personas (reconocer visitantes recurrentes)
- [ ] Detección de emociones/expresiones faciales
- [ ] Tracking de trayectorias completas con heatmap
- [ ] Detección de grupos/familias que se mueven juntos
- [ ] Reconocimiento de acciones/poses (detenerse, mirar, etc.)

#### Analytics Avanzado
- [ ] Dashboard en tiempo real (streaming)
- [ ] Alertas automáticas (aforo, tiempo de espera)
- [ ] Reportes automatizados por email
- [ ] Predicciones con ML (forecast de tráfico)
- [ ] Análisis de conversión (funnel por zonas)
- [ ] Correlación con eventos externos (clima, eventos)

#### Visualizaciones
- [ ] Mapa de calor interactivo
- [ ] Replay de video con overlay de métricas
- [ ] Vista 3D de movimientos
- [ ] Comparativas entre periodos

#### Integraciones
- [ ] API REST completa documentada con Swagger
- [ ] Webhooks para eventos en tiempo real
- [ ] Integración con CRM/POS
- [ ] Exportación a Google Analytics/Mixpanel

#### Sistema
- [ ] Sistema multi-tenant (múltiples clientes)
- [ ] Roles y permisos de usuario
- [ ] Gestión de múltiples cámaras simultáneas
- [ ] Procesamiento en GPU optimizado
- [ ] Queue system con Celery/Redis
- [ ] Anonimización automática (GDPR compliance)
- [ ] App móvil (iOS/Android)

---

## 🎓 Casos de Uso

### 🏬 **Retail Analytics**
- Análisis de flujo de clientes
- Perfil demográfico de visitantes
- Tiempo de permanencia por zona/producto
- Optimización de layouts
- Identificar zonas "calientes" vs "frías"

### 🏢 **Gestión de Espacios**
- Optimización del uso de espacios públicos
- Identificar cuellos de botella
- Análisis de patrones de movimiento
- Planificación de capacidad

### 🔒 **Seguridad**
- Monitoreo de acceso a áreas restringidas
- Conteo de aforo en tiempo real
- Alertas de tiempo de permanencia excesivo
- Análisis de comportamiento

### 🎯 **Eventos**
- Tracking de asistentes
- Engagement por stand/área
- Queue management
- Métricas de éxito del evento

### 📊 **Investigación**
- Estudios de comportamiento
- Análisis demográfico de poblaciones
- Patrones de movilidad
- Validación de hipótesis

---

## 🤝 Contribución

¡Las contribuciones son bienvenidas! Sigue estos pasos:

1. **Fork** el proyecto
2. Crea una **rama** para tu feature:
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. **Commit** tus cambios:
   ```bash
   git commit -m 'feat: Add some AmazingFeature'
   ```
4. **Push** a la rama:
   ```bash
   git push origin feature/AmazingFeature
   ```
5. Abre un **Pull Request**

### Convenciones

- Usa commits semánticos: `feat:`, `fix:`, `docs:`, `refactor:`
- Añade tests para nuevas funcionalidades
- Actualiza la documentación
- Sigue el estilo de código existente

---

## 📄 Licencia

Este proyecto está bajo la **Licencia MIT**. Ver el archivo `LICENSE` para más detalles.

---

## 👥 Autores

- **Joel Pulento** - Desarrollo inicial y mantenimiento

---

## 🙏 Agradecimientos

### Librerías y Frameworks
- [Ultralytics](https://ultralytics.com/) por YOLOv8
- [Supervision](https://supervision.roboflow.com/) por herramientas de CV
- [FastAPI](https://fastapi.tiangolo.com/) por el excelente framework
- [Vue.js](https://vuejs.org/) por el framework frontend
- [Chart.js](https://www.chartjs.org/) por visualizaciones

### Modelos de IA
- [NTQAI](https://huggingface.co/NTQAI) por los modelos BEiT de género y edad
- [Microsoft](https://github.com/microsoft/unilm/tree/master/beit) por la arquitectura BEiT
- [Hugging Face](https://huggingface.co/) por la plataforma de modelos

### Datasets y Research
- PETA (Pedestrian Attribute) Dataset
- PA-100K Dataset
- ByteTrack algorithm

---

## 📞 Soporte y Contacto

### Documentación Adicional

- **API Docs**: http://127.0.0.1:8000/docs (cuando el backend esté corriendo)
- **Guía de Testing**: `GUIA_PRUEBA_GRAFICOS_DEMOGRAFICOS.md`
- **Guía de Pruebas de Rendimiento**: `GUIA_PRUEBAS_RENDIMIENTO.md` ⭐ NUEVO
- **Fix Error NTQAI**: `FIX_NTQAI_ERROR.md` 🔧 **Si tienes error de state_dict**
- **Feature PAR**: `FEATURE_PAR_README.md`
- **Modelos NTQAI**: `Backend/models/README_NTQAI.md`
- **Sistema PAR**: `Backend/models/README_PAR.md`

### Si tienes problemas:

1. ✅ Revisa la **sección de Troubleshooting** arriba
2. ✅ Verifica que todas las **dependencias estén instaladas**
3. ✅ Consulta los **logs del backend y frontend**
4. ✅ Revisa la **documentación de la API**
5. ✅ Abre un **issue en GitHub** con:
   - Descripción del problema
   - Pasos para reproducir
   - Logs relevantes
   - Sistema operativo y versiones

### Recursos

- **Repositorio**: https://github.com/PulentoJose-edu/people-tracking-system
- **Issues**: https://github.com/PulentoJose-edu/people-tracking-system/issues
- **Discussions**: https://github.com/PulentoJose-edu/people-tracking-system/discussions

---

## 🌟 Features Destacados

> Este sistema es único porque combina:
> - ✨ **Detección de alta precisión** con YOLOv8
> - 🎯 **Análisis demográfico avanzado** con NTQAI (~95% género)
> - 📊 **Dashboard interactivo** con visualizaciones en tiempo real
> - ⚡ **Performance optimizado** con batch processing y caché
> - 🔧 **Fácil de usar** con scripts de instalación automatizada
> - 📚 **Bien documentado** con guías completas
> - 🚀 **Extensible** con arquitectura modular

---

**⭐ Si este proyecto te resulta útil, considera darle una estrella en GitHub!**
