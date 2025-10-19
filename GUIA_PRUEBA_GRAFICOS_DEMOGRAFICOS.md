# 📊 Gráficos Demográficos en Dashboard - Guía de Prueba

## ✅ Implementación Completada

### Nuevos Gráficos Agregados:

1. **📊 Distribución por Género** (Gráfico de Dona)
   - Muestra proporción M/F
   - Colores: Azul (Masculino), Rosa (Femenino)
   - Incluye porcentajes en tooltips

2. **🎂 Distribución por Edad** (Gráfico de Barras)
   - Rangos: 0-18, 19-35, 36-60, 60+
   - Colores distintos por rango
   - Muestra cantidad y porcentaje

3. **👥📍 Género por Zona** (Barras Agrupadas)
   - Compara M/F en cada zona
   - Visualización lado a lado
   - Identifica zonas con mayor tráfico por género

4. **🎂📍 Edad por Zona** (Barras Apiladas)
   - Distribución etaria completa por zona
   - Rangos de edad apilados
   - Permite comparar perfil demográfico entre zonas

### Nuevas Tarjetas de Resumen:

- **👤 Género Predominante**: Muestra ♂️ o ♀️ según el género más común
- **🎂 Edad Más Común**: Muestra el rango de edad predominante

### Ubicación en el Dashboard:

```
┌─────────────────────────────────────────────┐
│ Tarjetas de Resumen (incluyendo demográfico)│
├─────────────────────────────────────────────┤
│ Distribución por Zonas | Actividad Temporal │
├─────────────────────────────────────────────┤
│ Tiempo de Permanencia (si disponible)       │
├─────────────────────────────────────────────┤
│ 👥 Distribución Género | 🎂 Distribución Edad│ ← NUEVO
├─────────────────────────────────────────────┤
│ 👥📍 Género por Zona | 🎂📍 Edad por Zona    │ ← NUEVO
├─────────────────────────────────────────────┤
│ Resto de información...                     │
└─────────────────────────────────────────────┘
```

## 🧪 Cómo Probar

### 1. Asegúrate de tener datos demográficos

Los gráficos solo aparecen si:
- ✅ El video fue procesado con PAR habilitado
- ✅ Los modelos NTQAI están cargados
- ✅ Hay personas detectadas con género/edad

### 2. Procesa un video

```bash
# Si aún no has procesado un video con los nuevos modelos:
1. Inicia la aplicación: .\start.bat
2. Abre: http://localhost:5173
3. Sube un video
4. Espera a que termine el procesamiento
```

### 3. Verifica en el Dashboard

1. Ve a la pestaña "Analytics Dashboard"
2. Selecciona la tarea procesada del dropdown
3. Deberías ver:
   - ✅ Dos nuevas tarjetas moradas (género y edad predominante)
   - ✅ 4 gráficos demográficos nuevos (si hay datos)

### 4. Qué verificar:

- [ ] **Tarjetas demográficas**: Se muestran con fondo morado
- [ ] **Gráfico de género**: Dona con 2 segmentos (M/F)
- [ ] **Gráfico de edad**: Barras con 4 rangos (0-18, 19-35, 36-60, 60+)
- [ ] **Género por zona**: Barras azul/rosa lado a lado por cada zona
- [ ] **Edad por zona**: Barras apiladas con colores por rango
- [ ] **Tooltips**: Muestran porcentajes al pasar el mouse
- [ ] **Responsive**: Se adapta a pantallas pequeñas

## 🐛 Posibles Problemas

### Si no ves los gráficos:

1. **"No hay gráficos demográficos"**
   - Verifica que el video tenga datos de género/edad en el CSV
   - Revisa la consola del navegador (F12) para errores
   - Asegúrate de que los modelos NTQAI estén cargados

2. **"Error loading charts"**
   - Abre DevTools (F12) → Console
   - Busca mensajes como "demographic_analysis"
   - Verifica que el backend esté devolviendo los datos

3. **"Gráficos se ven mal"**
   - Refresca la página (Ctrl+R)
   - Borra caché del navegador
   - Verifica que Chart.js esté cargado

## 📝 Datos Esperados del Backend

El backend debe devolver en `demographic_analysis`:

```javascript
{
  "has_data": true,
  "gender_distribution": {
    "counts": {"M": 5, "F": 3},
    "percentages": {"M": 62.5, "F": 37.5}
  },
  "age_distribution": {
    "counts": {"19-35": 4, "36-60": 3, "60+": 1},
    "percentages": {...}
  },
  "gender_by_zone": {
    "zone_0": {
      "counts": {"M": 2, "F": 1},
      "percentages": {...}
    }
  },
  "age_by_zone": {...},
  "summary": {
    "most_common_gender": "M",
    "most_common_age": "19-35"
  }
}
```

## 🎨 Estilo Visual

- **Tarjetas demográficas**: Fondo gradiente morado
- **Gráfico de género**: Dona con leyenda inferior
- **Gráfico de edad**: Barras verticales con colores vibrantes
- **Género por zona**: Barras agrupadas azul/rosa
- **Edad por zona**: Barras apiladas con 4 colores

## ✅ Checklist de Verificación

Antes de aprobar, verifica:

- [ ] Los 4 gráficos se renderizan correctamente
- [ ] Las tarjetas de resumen muestran datos correctos
- [ ] Los tooltips funcionan al pasar el mouse
- [ ] Los colores son distintivos y fáciles de leer
- [ ] El layout es responsive (prueba en ventana pequeña)
- [ ] No hay errores en la consola del navegador
- [ ] Los datos coinciden con el video procesado

## 🔧 Si necesitas cambios:

Avísame y puedo ajustar:
- Colores de los gráficos
- Tipo de visualización
- Información en tooltips
- Posición de los gráficos
- Estilos CSS

---

**Estado**: ✅ Listo para probar
**Archivos modificados**: `frontend/src/components/AnalyticsDashboard.vue`
**Próximo paso**: Probar con video real y reportar resultados

¡Buena suerte con las pruebas! 🚀
