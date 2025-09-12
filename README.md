# People Tracking System

Sistema de seguimiento y conteo de personas usando YOLO v8 con interfaz web Vue.js y backend FastAPI.

## 📋 Descripción

Este proyecto implementa un sistema completo de análisis de video para detectar, rastrear y contar personas en tiempo real. Utiliza el modelo YOLO v8 para la detección de objetos y divide el frame en 4 zonas para el análisis de flujo de personas.

## 🏗️ Arquitectura

- **Frontend**: Vue.js 3 + Vite
- **Backend**: FastAPI (Python)
- **Procesamiento de video**: YOLOv8 + OpenCV
- **Tracking**: ByteTrack
- **Análisis de zonas**: Supervision

## 🚀 Características

- ✅ Detección de personas en tiempo real
- ✅ Seguimiento de objetos (tracking)
- ✅ División en 4 zonas configurables
- ✅ Conteo de entradas por zona
- ✅ **Detección de entrada y salida de personas**
- ✅ **Cálculo de tiempo de permanencia preciso**
- ✅ **Dashboard de analytics interactivo**
- ✅ **Análisis de tráfico por horas**
- ✅ **Distribución de tiempos de permanencia**
- ✅ **Métricas por zona en tiempo real**
- ✅ Exportación de datos en CSV
- ✅ Video procesado con anotaciones
- ✅ Interfaz web intuitiva
- ✅ API REST documentada

## � Inicio Rápido

### 🪟 **Windows**
```bash
# 1. Clonar el repositorio
git clone https://github.com/PulentoJose-edu/people-tracking-system.git
cd people-tracking-system

# 2. Ejecutar instalación automática
setup.bat

# 3. Iniciar la aplicación
start.bat
```

### 🐧 **Linux / 🍎 macOS**
```bash
# 1. Clonar el repositorio
git clone https://github.com/PulentoJose-edu/people-tracking-system.git
cd people-tracking-system

# 2. Ejecutar instalación automática
./setup.sh

# 3. Iniciar la aplicación
./start.sh
```

### 🌐 **Acceso a la aplicación**
- **Frontend (Interfaz)**: http://localhost:5173
- **Backend (API)**: http://127.0.0.1:8000
- **Documentación**: http://127.0.0.1:8000/docs

## �📦 Instalación Manual

### Prerrequisitos

- Python 3.11+
- Node.js 20.19+ o 22.12+
- npm o yarn

### Backend

```bash
cd Backend
pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
```

## 🏃‍♂️ Uso

### Ejecutar Backend

```bash
cd Backend
python -m uvicorn app.main:app --reload
```

El backend estará disponible en: http://127.0.0.1:8000

### Ejecutar Frontend

```bash
cd frontend
npm run dev
```

El frontend estará disponible en: http://localhost:5173

### Dashboard de Analytics

Una vez que ambos servicios estén ejecutándose:

1. **Procesa un video** a través de la interfaz principal
2. **Accede al Dashboard** en http://localhost:5173 para ver:
   - Métricas principales (total personas, tiempo promedio de permanencia)
   - Gráfico de tráfico por horas
   - Distribución de tiempos de permanencia
   - Estadísticas detalladas por zona

### API Documentation

Accede a la documentación interactiva de la API en: http://127.0.0.1:8000/docs

### Nuevos Endpoints de Analytics

- `GET /analytics/summary` - Resumen de métricas principales
- `GET /analytics/hourly-traffic` - Tráfico de personas por hora
- `GET /analytics/dwell-time-distribution` - Distribución de tiempos de permanencia
- `GET /analytics/zone-stats` - Estadísticas detalladas por zona

## 📊 Análisis de Datos

El sistema genera múltiples tipos de análisis y archivos de salida:

### Archivos de Salida

1. **Video procesado**: Video con detecciones y contadores por zona
2. **CSV de datos**: Registro detallado de todas las detecciones con eventos de entrada/salida
3. **Analytics en tiempo real**: Dashboard web con métricas y visualizaciones

### Estructura del CSV

```csv
timestamp,person_id,zone,event_type,x,y,confidence
2024-01-01 10:30:15,1,zona_1,entry,320,240,0.95
2024-01-01 10:32:45,1,zona_1,exit,380,260,0.92
```

### Dashboard de Analytics

El dashboard proporciona visualizaciones interactivas incluyendo:

- **Métricas Principales**: Total de personas, tiempo promedio de permanencia, personas activas
- **Tráfico por Horas**: Gráfico de barras mostrando el flujo de personas por hora
- **Distribución de Permanencia**: Histograma de tiempos que las personas permanecen en las zonas
- **Estadísticas por Zona**: Métricas específicas para cada zona de detección
- **Análisis Temporal**: Patrones de comportamiento y flujo de personas

## 🎯 Zonas de Detección

El sistema divide automáticamente el frame en 4 zonas:

```
┌─────────┬─────────┐
│  Zona 0 │ Zona 1  │
├─────────┼─────────┤
│  Zona 2 │ Zona 3  │
└─────────┴─────────┘
```

## 🛠️ Tecnologías

### Backend
- **FastAPI**: Framework web moderno y rápido
- **Ultralytics YOLOv8**: Modelo de detección de objetos
- **OpenCV**: Procesamiento de video
- **Supervision**: Herramientas de visión por computadora
- **ByteTrack**: Algoritmo de seguimiento multi-objeto
- **Pandas**: Análisis de datos y procesamiento de CSV
- **NumPy**: Computación numérica para analytics
- **PyTorch**: Framework de deep learning

### Frontend
- **Vue.js 3**: Framework progresivo de JavaScript
- **Vite**: Herramienta de build rápida
- **Chart.js**: Librería de gráficos para visualizaciones
- **Axios**: Cliente HTTP para comunicación con API
- **HTML5/CSS3**: Interfaz web moderna y responsiva

## 📁 Estructura del Proyecto

```
PT/
├── Backend/
│   ├── app/
│   │   ├── main.py          # API principal
│   │   ├── processing.py    # Lógica de procesamiento con detección entrada/salida
│   │   └── analytics.py     # Motor de análisis y métricas avanzadas
│   ├── requirements.txt     # Dependencias Python
│   ├── uploads/            # Videos subidos
│   └── outputs/            # Resultados procesados
├── frontend/
│   ├── src/
│   │   ├── App.vue         # Componente principal
│   │   ├── main.js         # Punto de entrada
│   │   └── components/
│   │       └── AnalyticsDashboard.vue  # Dashboard de analytics
│   ├── package.json        # Dependencias Node.js
│   └── public/             # Archivos estáticos
└── README.md
```

## 🔧 Configuración

### Variables de Entorno

El sistema utiliza las siguientes configuraciones:

- **Backend URL**: http://127.0.0.1:8000
- **Frontend URL**: http://localhost:5173
- **Modelo YOLO**: yolov8n.pt (se descarga automáticamente)

### CORS

El backend está configurado para permitir conexiones desde:
- http://localhost:5173
- http://127.0.0.1:5173

## 📈 Posibles Mejoras

- [ ] Configuración dinámica de zonas
- [ ] Múltiples modelos YOLO
- [ ] Base de datos para histórico
- [x] **Dashboard de análisis en tiempo real**
- [x] **Cálculo de tiempo de permanencia**
- [x] **Análisis de tráfico por horas**
- [x] **Detección de entrada y salida**
- [ ] Alertas automáticas basadas en métricas
- [ ] Exportación a diferentes formatos (PDF, Excel)
- [ ] Análisis de patrones de movimiento
- [ ] Predicción de flujo de personas
- [ ] Integración con cámaras IP
- [ ] Soporte para múltiples cámaras simultáneas

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👥 Autores

- Tu nombre - Desarrollo inicial

## 🙏 Agradecimientos

- [Ultralytics](https://ultralytics.com/) por YOLOv8
- [Supervision](https://supervision.roboflow.com/) por las herramientas de análisis
- [FastAPI](https://fastapi.tiangolo.com/) por el excelente framework
- [Vue.js](https://vuejs.org/) por el framework frontend

## 📞 Soporte

Si tienes alguna pregunta o problema, por favor:

1. Revisa la documentación de la API
2. Verifica que todas las dependencias estén instaladas
3. Consulta los logs del backend y frontend
4. Abre un issue en GitHub

## 🔍 Troubleshooting

### Problemas Comunes

**Error de NumPy**:
```bash
pip uninstall numpy -y && pip install numpy==1.26.4
```

**Error de OpenCV**:
```bash
pip install opencv-python-headless==4.10.0.84
```

**Puerto ocupado**:
- Backend: Cambia el puerto en el comando uvicorn
- Frontend: Vite asignará automáticamente otro puerto disponible
