# Solución: Error "state_dict cannot be passed together with a model name"

## 🚨 Problema

Al iniciar el backend, aparece este error:

```
⚠️  Error cargando modelo de género: state_dict cannot be passed together with a model name or a gguf_file. Use one of the two loading strategies.
ValueError: state_dict cannot be passed together with a model name or a gguf_file.
```

## 📋 Causa

Este error ocurre por una **incompatibilidad entre versiones** de la librería `transformers`:

- **Versiones antiguas** (<4.46): Permitían pasar `state_dict` directamente en `from_pretrained()`
- **Versiones nuevas** (≥4.46): Requieren cargar el modelo primero y luego aplicar `load_state_dict()`

El archivo `ntqai_adapter.py` en tu PC tiene el código antiguo que ya no funciona con versiones recientes de `transformers`.

---

## ✅ Solución Rápida (Recomendada)

### **Opción 1: Usar el Script de Actualización (Windows)**

```bash
# Desde la raíz del proyecto
fix_ntqai_adapter.bat
```

Este script:
1. Crea un respaldo del adaptador actual
2. Regenera `ntqai_adapter.py` con el código correcto
3. No requiere descargar los modelos de nuevo (~700MB)

### **Opción 2: Regenerar Manualmente**

```bash
# 1. Ir al directorio de modelos
cd Backend/models

# 2. Respaldar el adaptador actual (opcional)
copy ntqai_adapter.py ntqai_adapter.py.backup   # Windows
cp ntqai_adapter.py ntqai_adapter.py.backup     # Linux/Mac

# 3. Regenerar el adaptador
python download_ntoai_models.py

# 4. Volver a la raíz
cd ../..

# 5. Verificar
python verify_setup.py
```

**Nota**: El script `download_ntoai_models.py` detecta si los modelos ya están descargados y solo regenera el adaptador si es necesario.

---

## 🔧 Solución Alternativa: Pull desde Git

Si tienes acceso al repositorio actualizado:

```bash
# Opción A: Pull de la rama main
git pull origin main

# Opción B: Solo actualizar el archivo específico
git checkout origin/main -- Backend/models/ntqai_adapter.py
git checkout origin/main -- Backend/models/download_ntoai_models.py
```

---

## 🧪 Verificar la Solución

Después de aplicar cualquiera de las soluciones:

```bash
# 1. Verificar instalación
python verify_setup.py

# 2. Iniciar el backend
cd Backend
uvicorn app.main:app --reload

# 3. Buscar en los logs:
# ✅ Debe aparecer: "✅ Modelo de género cargado"
# ✅ Debe aparecer: "✅ Modelo de edad cargado"
# ❌ NO debe aparecer: "⚠️ No se pudieron cargar modelos NTQAI"
```

---

## 📝 Código Correcto (Referencia)

El código corregido en `ntqai_adapter.py` debe verse así:

### ❌ **Código Antiguo (Causa el Error)**
```python
# NO FUNCIONA en transformers ≥4.46
state_dict = torch.load(gender_path, map_location=self.device)
self.gender_model = BeitForImageClassification.from_pretrained(
    "microsoft/beit-base-patch16-224-pt22k-ft22k",
    state_dict=state_dict,  # ❌ Este parámetro ya no se acepta
    num_labels=2,
    ignore_mismatched_sizes=True
)
```

### ✅ **Código Nuevo (Correcto)**
```python
# FUNCIONA en todas las versiones
# Paso 1: Crear modelo base
self.gender_model = BeitForImageClassification.from_pretrained(
    "microsoft/beit-base-patch16-224-pt22k-ft22k",
    num_labels=2,
    ignore_mismatched_sizes=True
)

# Paso 2: Cargar pesos entrenados
state_dict = torch.load(gender_path, map_location=self.device, weights_only=False)
self.gender_model.load_state_dict(state_dict, strict=False)
```

---

## 🔍 Verificación de Versiones

Para verificar qué versiones tienes instaladas:

```bash
pip list | grep -E "transformers|torch"
# o en Windows:
pip list | findstr "transformers torch"
```

**Versiones recomendadas** (probadas y funcionando):
- `transformers==4.57.1`
- `torch==2.9.0` o superior

---

## 🆘 Si el Problema Persiste

1. **Limpia caché de Python**:
   ```bash
   # Windows
   del /s /q Backend\__pycache__
   del /s /q Backend\app\__pycache__
   del /s /q Backend\models\__pycache__
   
   # Linux/Mac
   find Backend -type d -name __pycache__ -exec rm -rf {} +
   ```

2. **Reinstala dependencias**:
   ```bash
   pip uninstall transformers torch -y
   pip install transformers==4.57.1 torch>=2.9.0
   ```

3. **Verifica archivos NTQAI**:
   ```bash
   cd Backend/models
   dir ntqai*.*  # Windows
   ls -lh ntqai*.*  # Linux/Mac
   
   # Debe mostrar 5 archivos:
   # - ntqai_adapter.py
   # - ntqai_gender.bin
   # - ntqai_gender_config.json
   # - ntqai_age.bin
   # - ntqai_age_config.json
   ```

4. **Elimina y regenera todo**:
   ```bash
   cd Backend/models
   del ntqai*.*  # Windows
   rm ntqai*.*   # Linux/Mac
   
   python download_ntoai_models.py
   ```

---

## 📚 Referencias

- **Issue Original**: Incompatibilidad introducida en `transformers` v4.46
- **Documentación**: [Hugging Face Transformers - from_pretrained](https://huggingface.co/docs/transformers/main_classes/model#transformers.PreTrainedModel.from_pretrained)
- **Changelog**: [transformers v4.46 Breaking Changes](https://github.com/huggingface/transformers/releases/tag/v4.46.0)

---

## ✅ Checklist de Solución

- [ ] Respaldar `ntqai_adapter.py` actual
- [ ] Ejecutar `fix_ntqai_adapter.bat` o regenerar manualmente
- [ ] Verificar que se generó el nuevo adaptador
- [ ] Ejecutar `python verify_setup.py`
- [ ] Reiniciar el backend
- [ ] Verificar en logs que los modelos se cargan correctamente
- [ ] Probar procesamiento de video con análisis demográfico

---

**💡 Tip**: Si trabajas en múltiples PCs, asegúrate de hacer `git pull` regularmente para tener las últimas correcciones.
