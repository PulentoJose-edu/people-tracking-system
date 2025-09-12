# People Tracking System

Sistema de seguimiento de personas en tiempo real utilizando YOLO v8 y análisis de datos con dashboard interactivo.

## 🚀 Características

- **Detección de Personas**: Utiliza YOLO v8 para detección precisa de personas en video
- **Seguimiento en Tiempo Real**: Implementa ByteTrack para seguimiento continuo de personas
- **Análisis de Zonas**: Detecta entrada y salida de personas en zonas específicas
- **Dashboard Analytics**: Interface interactiva con gráficos y estadísticas
- **Tiempo de Permanencia**: Cálculo preciso del tiempo que las personas permanecen en cada zona
- **Análisis Temporal**: Estadísticas de tráfico por horas y distribución de permanencia

## 🏗️ Arquitectura

### Backend (FastAPI)
- **YOLO v8**: Modelo de detección de objetos
- **ByteTrack**: Algoritmo de seguimiento multi-objeto
- **Supervision**: Herramientas de visión por computadora
- **Pandas**: Análisis y procesamiento de datos
- **Analytics Engine**: Procesador de métricas y estadísticas

### Frontend (Vue 3 + Vite)
- **Vue 3**: Framework principal con Composition API
- **Chart.js**: Visualización de datos y gráficos interactivos
- **Axios**: Cliente HTTP para comunicación con API
- **Responsive Design**: Interface adaptable a diferentes dispositivos

## 📊 Funcionalidades del Dashboard

### Métricas Principales
- **Total de Personas Detectadas**
- **Promedio de Tiempo de Permanencia**
- **Personas Actualmente en Zona**
- **Tráfico por Hora**

### Visualizaciones
- **Gráfico de Barras**: Tráfico de personas por hora
- **Histograma**: Distribución de tiempos de permanencia
- **Métricas por Zona**: Estadísticas específicas de cada área
- **Línea de Tiempo**: Análisis temporal del flujo de personas

## 🔧 Instalación y Configuración

### Prerrequisitos
- Python 3.11+
- Node.js 18+
- Cámara web o archivo de video para procesamiento

### Backend Setup
```bash
cd Backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## 📈 Analytics y Datos

El sistema genera archivos CSV con datos de seguimiento:
- `person_tracking_data.csv`: Datos de entrada y salida por zona
- Análisis automático de patrones de movimiento
- Cálculo de tiempos de permanencia precisos
- Estadísticas de tráfico temporal

### Estructura de Datos
```csv
timestamp,person_id,zone,event_type,x,y,confidence
2024-01-01 10:30:15,1,zona_1,entry,320,240,0.95
2024-01-01 10:32:45,1,zona_1,exit,380,260,0.92
```

## 🎯 Casos de Uso

- **Retail Analytics**: Análisis de flujo de clientes en tiendas
- **Seguridad**: Monitoreo de acceso a áreas restringidas
- **Gestión de Espacios**: Optimización del uso de espacios públicos
- **Investigación**: Estudios de comportamiento y patrones de movimiento

## 🔄 Flujo de Trabajo

1. **Captura de Video**: Procesamiento en tiempo real o archivos grabados
2. **Detección**: YOLO v8 identifica personas en cada frame
3. **Seguimiento**: ByteTrack mantiene identidades consistentes
4. **Análisis de Zonas**: Detección de eventos de entrada/salida
5. **Almacenamiento**: Guardado de datos en formato CSV
6. **Visualización**: Dashboard en tiempo real con métricas actualizadas

## 🛠️ Tecnologías Utilizadas

### Backend
- FastAPI
- YOLO v8 (Ultralytics)
- OpenCV
- Supervision
- ByteTrack
- Pandas
- NumPy

### Frontend
- Vue 3
- Vite
- Chart.js
- Axios
- CSS3 (Grid & Flexbox)

## 📝 API Endpoints

- `GET /`: Endpoint principal de procesamiento de video
- `GET /analytics/summary`: Resumen de métricas principales
- `GET /analytics/hourly-traffic`: Tráfico por horas
- `GET /analytics/dwell-time-distribution`: Distribución de tiempos de permanencia
- `GET /analytics/zone-stats`: Estadísticas por zona

## 🚀 Desarrollo

### Estructura del Proyecto
```
people-tracking-system/
├── Backend/
│   ├── app/
│   │   ├── main.py          # Servidor FastAPI principal
│   │   ├── processing.py    # Lógica de procesamiento de video
│   │   └── analytics.py     # Motor de análisis de datos
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── components/
    │   │   └── AnalyticsDashboard.vue  # Dashboard principal
    │   ├── App.vue
    │   └── main.js
    └── package.json
```

## 📊 Métricas de Rendimiento

- **Detección**: ~30 FPS en hardware estándar
- **Precisión**: >90% en condiciones normales de iluminación
- **Seguimiento**: Mantiene identidades a través de oclusiones temporales
- **Latencia**: <100ms para procesamiento en tiempo real

## 🔮 Roadmap

- [ ] Implementación de alertas en tiempo real
- [ ] Soporte para múltiples cámaras
- [ ] Machine Learning para predicción de patrones
- [ ] Exportación de reportes automatizados
- [ ] Integración con sistemas de seguridad existentes

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request
