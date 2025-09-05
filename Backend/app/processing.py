import cv2
import pandas as pd
from ultralytics import YOLO
import supervision as sv
import numpy as np
import time
import os

# Diccionario en memoria para rastrear el estado de las tareas.
# En una app de producción, usarías una base de datos o Redis.
task_status = {}

def process_video_task(
    task_id: str,
    video_path: str,
    output_video_path: str,
    output_csv_path: str,
):
    """
    Función que procesa el video en segundo plano.
    Actualiza el estado de la tarea en el diccionario global.
    """
    try:
        # 1. Cargar modelo y video
        model = YOLO('yolov8n.pt')
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

        zones = [sv.PolygonZone(p, frame_resolution_wh=(width, height)) for p in POLYGONS]
        box_annotator = sv.BoxAnnotator(thickness=2, text_thickness=1, text_scale=0.5)

        # 3. Procesamiento
        data_list = []
        entered_ids_per_zone = {i: set() for i in range(len(zones))}
        total_counts_per_zone = {i: 0 for i in range(len(zones))}
        frame_count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            timestamp = frame_count / fps

            results = model.track(frame, persist=True, classes=[0], verbose=False, tracker="bytetrack.yaml")[0]
            detections = sv.Detections.from_ultralytics(results)

            if results.boxes.id is not None:
                detections.tracker_id = results.boxes.id.cpu().numpy().astype(int)

                for i, zone in enumerate(zones):
                    mask = zone.trigger(detections=detections)
                    detections_in_zone = detections[mask]

                    for tracker_id in detections_in_zone.tracker_id:
                        if tracker_id not in entered_ids_per_zone[i]:
                            entered_ids_per_zone[i].add(tracker_id)
                            total_counts_per_zone[i] += 1
                            data_list.append({
                                'timestamp_seconds': timestamp, 'frame': frame_count,
                                'zone_id': i, 'person_tracker_id': tracker_id,
                                'event': 'entry'
                            })

            # Anotación del frame
            labels = [f"ID {tracker_id}" for tracker_id in detections.tracker_id] if detections.tracker_id is not None else []
            annotated_frame = box_annotator.annotate(scene=frame.copy(), detections=detections, labels=labels)
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