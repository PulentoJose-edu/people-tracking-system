import cv2
import pandas as pd
from ultralytics import YOLO
import supervision as sv
import numpy as np
import time
import os
import warnings
import sys
from pathlib import Path

# Agregar path para imports de modelos
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configurar para mostrar advertencias de deprecación solo una vez
warnings.filterwarnings("once", category=DeprecationWarning)

# Diccionario en memoria para rastrear el estado de las tareas.
# En una app de producción, usarías una base de datos o Redis.
task_status = {}

# MEJORAS DE TRACKING IMPLEMENTADAS:
# 1. YOLOv8s en lugar de YOLOv8n: Mejor precisión en detección
# 2. BotSORT en lugar de ByteTrack: Mejor manejo de oclusiones y cruces
# 3. Parámetros optimizados: conf=0.3, iou=0.5, max_det=50
# 4. PAR (Pedestrian Attribute Recognition): Detección de género y edad

# Importar modelo PAR (lazy loading)
_par_model = None
_use_ntqai = True  # Flag para usar modelos NTQAI (True) o baseline PAR (False)

def get_par_model():
    """Lazy loading del modelo PAR para no ralentizar el inicio"""
    global _par_model, _use_ntqai
    if _par_model is None:
        try:
            if _use_ntqai:
                # Intentar cargar modelos NTQAI (precisión ~95% género, ~88% edad)
                print("🔄 Cargando modelos NTQAI especializados...")
                from models.ntqai_adapter import create_ntqai_model
                _par_model = create_ntqai_model()
                if _par_model:
                    print("✅ Modelos NTQAI cargados exitosamente")
                    print("   - Género: ~95% precisión")
                    print("   - Edad: ~88% precisión")
                else:
                    print("⚠️  No se pudieron cargar modelos NTQAI, usando baseline...")
                    _use_ntqai = False
            
            if not _use_ntqai or _par_model is None:
                # Fallback: usar modelo PAR baseline
                print("🔄 Cargando modelo PAR baseline...")
                from models.attribute_recognition import get_par_model as _get_par
                model_path = Path(__file__).parent.parent / 'models' / 'resnet50_peta.pth'
                _par_model = _get_par(
                    model_path=str(model_path) if model_path.exists() else None,
                    device='cpu'  # Usar 'cuda' si tienes GPU disponible
                )
                print("✅ Modelo PAR baseline cargado")
        except Exception as e:
            print(f"⚠️  No se pudo cargar modelo PAR: {e}")
            import traceback
            traceback.print_exc()
            _par_model = None
    return _par_model

def process_video_task(
    task_id: str,
    video_path: str,
    output_video_path: str,
    output_csv_path: str,
    enable_par: bool = True,  # Nuevo parámetro para habilitar/deshabilitar PAR
    par_interval: int = 10,   # Analizar PAR cada N frames (reducido de 15 a 10 para más análisis)
):
    """
    Función que procesa el video en segundo plano.
    Actualiza el estado de la tarea en el diccionario global.
    
    Args:
        task_id: ID único de la tarea
        video_path: Ruta al video de entrada
        output_video_path: Ruta para guardar video procesado
        output_csv_path: Ruta para guardar datos CSV
        enable_par: Habilitar análisis de género y edad (default: True)
        par_interval: Analizar atributos cada N frames (default: 15)
    """
    try:
        # 1. Cargar modelo YOLO
        model = YOLO('yolov8s.pt')  # Small model - mejor balance precisión/velocidad que nano
        
        # 1b. Cargar modelo PAR si está habilitado
        par_model = None
        if enable_par:
            par_model = get_par_model()
            if par_model:
                print(f"🎯 PAR habilitado - Análisis cada {par_interval} frames")
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise IOError(f"No se pudo abrir el video {video_path}")

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        task_status[task_id] = {
            "status": "processing",
            "progress": 0,
            "total_frames": total_frames
        }

        # 2. Configurar video de salida y zonas
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
        
        # Definición de polígonos (igual que en tu script)
        POLYGONS = [
            np.array([[0, 0], [width // 2, 0], [width // 2, height // 2], [0, height // 2]], np.int32),
            np.array([[width // 2, 0], [width, 0], [width, height // 2], [width // 2, height // 2]], np.int32),
            np.array([[0, height // 2], [width // 2, height // 2], [width // 2, height], [0, height]], np.int32),
            np.array([[width // 2, height // 2], [width, height // 2], [width, height], [width // 2, height]], np.int32)
        ]

        zones = [sv.PolygonZone(p) for p in POLYGONS]
        bounding_box_annotator = sv.BoundingBoxAnnotator(thickness=2)
        label_annotator = sv.LabelAnnotator(text_thickness=1, text_scale=0.5)

        # 3. Procesamiento
        data_list = []
        entered_ids_per_zone = {i: set() for i in range(len(zones))}
        total_counts_per_zone = {i: 0 for i in range(len(zones))}
        # Rastrear personas actualmente en cada zona para detectar salidas
        current_ids_per_zone = {i: set() for i in range(len(zones))}
        previous_ids_per_zone = {i: set() for i in range(len(zones))}
        frame_count = 0
        
        # Caché de atributos demográficos por track_id
        demographic_cache = {}

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            timestamp = frame_count / fps

            # Usar BotSORT con parámetros optimizados para mejor tracking en cruces
            results = model.track(
                frame, 
                persist=True, 
                classes=[0],  # Solo personas
                verbose=False, 
                tracker="botsort.yaml",  # Mejor tracker para oclusiones y cruces
                conf=0.3,     # Umbral de confianza más bajo para detectar personas parcialmente ocultas
                iou=0.5,      # Intersection over Union threshold
                max_det=50    # Máximo de detecciones por frame
            )[0]
            detections = sv.Detections.from_ultralytics(results)

            if results.boxes.id is not None:
                detections.tracker_id = results.boxes.id.cpu().numpy().astype(int)

                # Análisis PAR (Pedestrian Attribute Recognition) cada N frames
                if par_model and frame_count % par_interval == 0:
                    # Batch processing de atributos demográficos
                    bboxes = detections.xyxy.tolist()  # Lista de [x1, y1, x2, y2]
                    track_ids = detections.tracker_id.tolist()
                    
                    try:
                        if _use_ntqai:
                            # Usar modelos NTQAI (procesamiento individual por persona)
                            from PIL import Image
                            for bbox, track_id in zip(bboxes, track_ids):
                                x1, y1, x2, y2 = map(int, bbox)
                                # Extraer crop de la persona
                                person_crop = frame[y1:y2, x1:x2]
                                
                                if person_crop.size > 0:
                                    # Convertir BGR a RGB
                                    person_rgb = cv2.cvtColor(person_crop, cv2.COLOR_BGR2RGB)
                                    pil_image = Image.fromarray(person_rgb)
                                    
                                    # Predicción con NTQAI
                                    result = par_model.predict(pil_image)
                                    
                                    # Mapear a formato compatible
                                    demographic_cache[track_id] = {
                                        'gender': result['gender'],  # 'M' o 'F'
                                        'gender_confidence': result['gender_conf'],
                                        'age': result['age_group'],  # '0-18', '19-35', etc.
                                        'age_confidence': result['age_conf']
                                    }
                        else:
                            # Usar modelo PAR baseline (procesamiento batch)
                            par_results = par_model.predict_batch(frame, bboxes, track_ids)
                            
                            # Guardar en caché
                            for track_id, par_result in zip(track_ids, par_results):
                                if par_result['gender'] != 'Desconocido':
                                    demographic_cache[track_id] = par_result
                                    
                    except Exception as e:
                        print(f"⚠️  Error en análisis PAR (frame {frame_count}): {e}")
                        import traceback
                        traceback.print_exc()

                # Guardar el estado anterior
                previous_ids_per_zone = {i: current_ids_per_zone[i].copy() for i in range(len(zones))}
                # Resetear el estado actual
                current_ids_per_zone = {i: set() for i in range(len(zones))}

                # Detectar personas actualmente en cada zona
                for i, zone in enumerate(zones):
                    mask = zone.trigger(detections=detections)
                    detections_in_zone = detections[mask]

                    for tracker_id in detections_in_zone.tracker_id:
                        current_ids_per_zone[i].add(tracker_id)
                        
                        # Detectar ENTRADA: persona no estaba en zona anterior pero sí está ahora
                        if tracker_id not in previous_ids_per_zone[i]:
                            if tracker_id not in entered_ids_per_zone[i]:
                                entered_ids_per_zone[i].add(tracker_id)
                                total_counts_per_zone[i] += 1
                            
                            # Obtener atributos demográficos del caché
                            demo_attrs = demographic_cache.get(tracker_id, {})
                            
                            data_list.append({
                                'timestamp_seconds': timestamp, 
                                'frame': frame_count,
                                'zone_id': i, 
                                'person_tracker_id': tracker_id,
                                'event': 'entry',
                                'gender': demo_attrs.get('gender', 'Desconocido'),
                                'gender_confidence': demo_attrs.get('gender_confidence', 0.0),
                                'age': demo_attrs.get('age', 'Desconocido'),
                                'age_confidence': demo_attrs.get('age_confidence', 0.0)
                            })

                # Detectar SALIDAS: personas que estaban en zona anterior pero ya no están
                for i in range(len(zones)):
                    exited_ids = previous_ids_per_zone[i] - current_ids_per_zone[i]
                    for tracker_id in exited_ids:
                        # Obtener atributos demográficos del caché
                        demo_attrs = demographic_cache.get(tracker_id, {})
                        
                        data_list.append({
                            'timestamp_seconds': timestamp, 
                            'frame': frame_count,
                            'zone_id': i, 
                            'person_tracker_id': tracker_id,
                            'event': 'exit',
                            'gender': demo_attrs.get('gender', 'Desconocido'),
                            'gender_confidence': demo_attrs.get('gender_confidence', 0.0),
                            'age': demo_attrs.get('age', 'Desconocido'),
                            'age_confidence': demo_attrs.get('age_confidence', 0.0)
                        })

            # Anotación del frame con atributos demográficos
            if detections.tracker_id is not None:
                labels = []
                for tracker_id in detections.tracker_id:
                    demo_attrs = demographic_cache.get(tracker_id, {})
                    
                    # Crear etiqueta con ID, género y edad
                    if demo_attrs:
                        gender_short = demo_attrs.get('gender', 'N/A')
                        # Si es de una letra (M/F), usar directamente
                        if len(gender_short) == 1:
                            gender_display = gender_short
                        else:
                            gender_display = gender_short[0]  # Tomar primera letra
                        
                        age_short = demo_attrs.get('age', 'N/A')
                        
                        # Abreviar edad - compatible con ambos formatos
                        age_abbr = {
                            # Formato baseline PAR
                            'Niño': 'Niño',
                            'Adolescente': 'Adol',
                            'Adulto Joven': 'A.Jov',
                            'Adulto': 'Adult',
                            'Mayor': 'Mayor',
                            'Desconocido': '?',
                            'Unknown': '?',
                            # Formato NTQAI (rangos)
                            '0-18': '<18',
                            '19-35': '19-35',
                            '36-60': '36-60',
                            '60+': '60+'
                        }.get(age_short, age_short if len(age_short) <= 6 else '?')
                        
                        labels.append(f"ID{tracker_id} {gender_display}/{age_abbr}")
                    else:
                        labels.append(f"ID {tracker_id}")
            else:
                labels = []
            
            annotated_frame = bounding_box_annotator.annotate(scene=frame.copy(), detections=detections)
            annotated_frame = label_annotator.annotate(scene=annotated_frame, detections=detections, labels=labels)
            for i, zone in enumerate(zones):
                polygon = zone.polygon.astype(int)
                count = total_counts_per_zone[i]
                cv2.polylines(annotated_frame, [polygon], True, (255, 255, 255), 2)
                cv2.putText(annotated_frame, f"Zona {i}: {count}", (polygon[0][0], polygon[0][1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            out.write(annotated_frame)

            # Actualizar progreso
            if frame_count % 30 == 0: # Actualiza cada 30 frames
                task_status[task_id]["progress"] = frame_count

        # 4. Limpieza y guardado
        cap.release()
        out.release()

        if data_list:
            df = pd.DataFrame(data_list)
            df.to_csv(output_csv_path, index=False)
        
        # 5. Marcar la tarea como completada
        task_status[task_id].update({
            "status": "completed",
            "progress": total_frames,
            "results": {
                "video_url": f"/download/video/{task_id}",
                "csv_url": f"/download/csv/{task_id}",
            }
        })

    except Exception as e:
        task_status[task_id] = {"status": "failed", "error": str(e)}