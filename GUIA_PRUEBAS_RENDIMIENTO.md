# Guía de Pruebas de Rendimiento

Esta guía describe cómo realizar pruebas de tiempo de respuesta del sistema de seguimiento de personas.

## 📋 Tabla de Contenidos

1. [Requisitos](#requisitos)
2. [Pruebas del Backend](#pruebas-del-backend)
3. [Pruebas del Dashboard](#pruebas-del-dashboard)
4. [Métricas Clave](#métricas-clave)
5. [Interpretación de Resultados](#interpretación-de-resultados)

---

## Requisitos

### Backend (Python)
```bash
pip install requests
```

### Dashboard/Frontend
Elige una de estas opciones:

**Opción 1: Playwright (Recomendado)**
```bash
pip install playwright
playwright install
```

**Opción 2: Selenium**
```bash
pip install selenium
# Descarga ChromeDriver: https://chromedriver.chromium.org/
```

**Opción 3: Lighthouse (Opcional, requiere Node.js)**
```bash
npm install -g lighthouse
```

---

## Pruebas del Backend

### 1. Prueba Básica (con Task ID existente)

Si ya tienes un video procesado y conoces su `task_id`:

```bash
python test_performance.py --task-id TU_TASK_ID_AQUI
```

**Ejemplo:**
```bash
python test_performance.py --task-id 4dd7bafa-b26c-4e93-af1f-d46bcdc24123
```

**Qué mide:**
- ✅ Tiempo de respuesta de `/analytics/analyze/{task_id}` (10 repeticiones)
- ✅ Tiempo de respuesta de `/video/{task_id}` streaming (5 repeticiones)
- ✅ Estadísticas: media, mediana, min, max, P95, P99

### 2. Prueba Completa (con carga de video)

Para probar todo el flujo desde la carga:

```bash
python test_performance.py --full --video "ruta/al/video.mp4"
```

**Ejemplo:**
```bash
python test_performance.py --full --video "Backend/uploads/test_video.mp4"
```

**Qué mide:**
- ✅ Tiempo de carga del video
- ✅ Tiempo de procesamiento completo
- ✅ Polling del estado (progreso)
- ✅ API de analytics
- ✅ Streaming de video

### 3. Cambiar URL del Backend

Si tu backend está en otra URL:

```bash
python test_performance.py --url http://192.168.1.100:8000 --task-id TASK_ID
```

### 4. Guardar Resultados

Especifica un archivo de salida:

```bash
python test_performance.py --task-id TASK_ID --output resultados_backend.json
```

---

## Pruebas del Dashboard

### 1. Prueba con Selenium (Más Compatible)

```bash
python test_dashboard_performance.py --tool selenium
```

**Qué mide:**
- ✅ Tiempo de carga de la página (3 repeticiones)
- ✅ Métricas de navegador (DOM Ready, Load Time, Response Time)
- ✅ Detección de elementos (área de carga, gráficos)
- ✅ Screenshot del dashboard

### 2. Prueba con Playwright (Más Completo)

```bash
python test_dashboard_performance.py --tool playwright
```

**Qué mide:**
- ✅ Tiempo de carga de página
- ✅ DOM Content Loaded
- ✅ First Paint
- ✅ Interacción con elementos
- ✅ Monitoreo de llamadas a API
- ✅ Performance del navegador

### 3. Auditoría con Lighthouse

```bash
python test_dashboard_performance.py --tool selenium --lighthouse
```

**Qué mide:**
- ✅ First Contentful Paint (FCP)
- ✅ Largest Contentful Paint (LCP)
- ✅ Speed Index
- ✅ Total Blocking Time (TBT)
- ✅ Cumulative Layout Shift (CLS)
- ✅ Time to Interactive (TTI)

### 4. Cambiar URL del Dashboard

```bash
python test_dashboard_performance.py --url http://localhost:3000
```

---

## Métricas Clave

### Backend

| Métrica | Descripción | Objetivo |
|---------|-------------|----------|
| **Upload Time** | Tiempo para cargar video al servidor | < 5s para videos < 50MB |
| **Processing Time** | Tiempo total de análisis del video | Depende del largo (ej: 1x-2x duración real) |
| **Status API** | Tiempo de respuesta `/status/{task_id}` | < 100ms |
| **Analytics API** | Tiempo de respuesta `/analytics/analyze/{task_id}` | < 500ms |
| **Video Stream TTFB** | Time To First Byte del streaming | < 200ms |

### Dashboard

| Métrica | Descripción | Objetivo Web Vitals |
|---------|-------------|---------------------|
| **Page Load** | Tiempo de carga completa | < 3s |
| **DOM Content Loaded** | Tiempo hasta DOM listo | < 1.5s |
| **First Contentful Paint (FCP)** | Primer elemento visible | < 1.8s (Bueno) |
| **Largest Contentful Paint (LCP)** | Elemento principal visible | < 2.5s (Bueno) |
| **Time to Interactive (TTI)** | Página completamente interactiva | < 3.8s (Bueno) |
| **Total Blocking Time (TBT)** | Tiempo bloqueado por JS | < 200ms (Bueno) |
| **Cumulative Layout Shift (CLS)** | Cambios inesperados de layout | < 0.1 (Bueno) |

---

## Interpretación de Resultados

### Ejemplo de Salida - Backend

```
📈 RESUMEN DE RENDIMIENTO
========================================

ANALYTICS:
  Muestras: 10
  Media: 245.32ms
  Mediana: 238.50ms
  Min: 189.23ms
  Max: 378.45ms
  Desv. estándar: 52.18ms
  P95: 342.10ms
  P99: 365.28ms
```

**Interpretación:**
- ✅ **Bueno**: Media < 500ms, P95 < 1000ms
- ⚠️ **Regular**: Media 500-1000ms, P95 1000-2000ms
- ❌ **Lento**: Media > 1000ms, P95 > 2000ms

### Ejemplo de Salida - Dashboard

```
📊 Métricas de Performance:
  First Contentful Paint: 0.8s (score: 95/100)
  Largest Contentful Paint: 1.2s (score: 98/100)
  Speed Index: 1.1s (score: 96/100)
  Total Blocking Time: 120ms (score: 92/100)
  Cumulative Layout Shift: 0.05 (score: 100/100)
  Time to Interactive: 1.8s (score: 94/100)
```

**Interpretación:**
- ✅ **Excelente**: Score > 90
- ⚠️ **Bueno**: Score 50-89
- ❌ **Necesita mejora**: Score < 50

---

## Casos de Uso Comunes

### Caso 1: Comparar Antes/Después de Optimización

```bash
# Antes
python test_performance.py --task-id TASK_ID --output antes.json

# Hacer cambios de optimización...

# Después
python test_performance.py --task-id TASK_ID --output despues.json

# Comparar archivos JSON manualmente
```

### Caso 2: Prueba de Estrés (Múltiples Usuarios)

```bash
# Terminal 1
python test_performance.py --task-id TASK_ID

# Terminal 2 (simultáneo)
python test_performance.py --task-id TASK_ID

# Terminal 3 (simultáneo)
python test_performance.py --task-id TASK_ID
```

### Caso 3: Monitoreo Continuo

Crear un script batch/shell que ejecute las pruebas periódicamente:

**Windows (monitor.bat):**
```batch
@echo off
:loop
echo [%date% %time%] Ejecutando prueba de rendimiento...
python test_performance.py --task-id 4dd7bafa-b26c-4e93-af1f-d46bcdc24123
timeout /t 300
goto loop
```

**Linux/Mac (monitor.sh):**
```bash
#!/bin/bash
while true; do
    echo "[$(date)] Ejecutando prueba de rendimiento..."
    python test_performance.py --task-id 4dd7bafa-b26c-4e93-af1f-d46bcdc24123
    sleep 300
done
```

---

## Solución de Problemas

### Backend no responde
```bash
# Verificar que el backend esté corriendo
curl http://localhost:8000/health

# O inicia el backend
cd Backend
uvicorn app.main:app --reload
```

### Dashboard no responde
```bash
# Verificar que el frontend esté corriendo
cd frontend
npm run dev
```

### Error: "Module not found: requests"
```bash
pip install requests
```

### Error: "playwright not found"
```bash
pip install playwright
playwright install
```

### ChromeDriver no compatible
```bash
# Actualizar Selenium
pip install --upgrade selenium

# Descargar ChromeDriver compatible con tu versión de Chrome
# https://chromedriver.chromium.org/downloads
```

---

## Mejores Prácticas

1. **Ejecuta múltiples pruebas**: Una sola ejecución puede tener variaciones. Usa al menos 5-10 repeticiones.

2. **Cierra otras aplicaciones**: Para resultados más precisos, cierra navegadores y aplicaciones pesadas.

3. **Usa conexión estable**: La red puede afectar los resultados. Usa conexión cableada si es posible.

4. **Documenta cambios**: Guarda los resultados antes y después de cambios para comparar.

5. **Establece baseline**: Ejecuta pruebas al inicio del proyecto para tener una referencia.

6. **Automatiza**: Integra las pruebas en tu CI/CD para detectar regresiones de rendimiento.

---

## Recursos Adicionales

- **Web Vitals**: https://web.dev/vitals/
- **Lighthouse Documentation**: https://developer.chrome.com/docs/lighthouse/
- **Performance API**: https://developer.mozilla.org/en-US/docs/Web/API/Performance
- **Playwright Docs**: https://playwright.dev/python/
- **Selenium Docs**: https://www.selenium.dev/documentation/

---

## Próximos Pasos

1. Ejecuta una prueba básica para establecer tu baseline
2. Identifica cuellos de botella
3. Implementa optimizaciones
4. Vuelve a probar y compara resultados
5. Documenta mejoras obtenidas

¿Preguntas? Consulta el README principal o abre un issue en el repositorio.
