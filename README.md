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
- ✅ Exportación de datos en CSV
- ✅ Video procesado con anotaciones
- ✅ Interfaz web intuitiva
- ✅ API REST documentada

## 📦 Instalación

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

### API Documentation

Accede a la documentación interactiva de la API en: http://127.0.0.1:8000/docs

## 📊 Análisis de Datos

El sistema genera dos archivos de salida:

1. **Video procesado**: Video con detecciones y contadores por zona
2. **CSV de datos**: Registro detallado de todas las detecciones

### Estructura del CSV

```csv
timestamp_seconds,frame,zone_id,person_tracker_id,event
0.04,1,0,9,entry
0.04,1,1,2,entry
...
```

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
- **Pandas**: Análisis de datos
- **PyTorch**: Framework de deep learning

### Frontend
- **Vue.js 3**: Framework progresivo de JavaScript
- **Vite**: Herramienta de build rápida
- **HTML5**: Interfaz web moderna

## 📁 Estructura del Proyecto

```
PT/
├── Backend/
│   ├── app/
│   │   ├── main.py          # API principal
│   │   └── processing.py    # Lógica de procesamiento
│   ├── requirements.txt     # Dependencias Python
│   ├── uploads/            # Videos subidos
│   └── outputs/            # Resultados procesados
├── frontend/
│   ├── src/
│   │   ├── App.vue         # Componente principal
│   │   └── main.js         # Punto de entrada
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
- [ ] Dashboard de análisis en tiempo real
- [ ] Alertas automáticas
- [ ] Exportación a diferentes formatos
- [ ] Análisis de patrones de movimiento

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
