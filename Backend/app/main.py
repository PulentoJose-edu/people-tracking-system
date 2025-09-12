from fastapi import FastAPI, File, UploadFile, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import shutil
import traceback
from Backend.app.processing import process_video_task, task_status
from Backend.app.analytics import analytics_processor

app = FastAPI(title="People Tracking API", version="1.0.0")

# Configurar CORS para permitir que el frontend (Vue) se comunique
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes
    allow_credentials=False,  # Cambiar a False cuando usamos "*"
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directorios para guardar archivos temporales y resultados
UPLOAD_DIR = "Backend/uploads"
OUTPUT_DIR = "Backend/outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.post("/upload-and-process/")
async def upload_and_process(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    task_id = str(uuid.uuid4())
    
    # Rutas de archivos
    input_path = os.path.join(UPLOAD_DIR, f"{task_id}_{file.filename}")
    output_video_path = os.path.join(OUTPUT_DIR, f"{task_id}_processed.mp4")
    output_csv_path = os.path.join(OUTPUT_DIR, f"{task_id}_data.csv")

    # Guardar el archivo subido
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Iniciar la tarea en segundo plano
    background_tasks.add_task(
        process_video_task,
        task_id,
        input_path,
        output_video_path,
        output_csv_path
    )
    
    task_status[task_id] = {"status": "pending"}
    
    return {"message": "El procesamiento del video ha comenzado.", "task_id": task_id}

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    return task_status.get(task_id, {"status": "not_found"})

@app.get("/download/{file_type}/{task_id}")
async def download_file(file_type: str, task_id: str):
    if file_type == "video":
        file_path = os.path.join(OUTPUT_DIR, f"{task_id}_processed.mp4")
        media_type = "video/mp4"
        filename = "video_procesado.mp4"
    elif file_type == "csv":
        file_path = os.path.join(OUTPUT_DIR, f"{task_id}_data.csv")
        media_type = "text/csv"
        filename = "datos_conteo.csv"
    else:
        return {"error": "Tipo de archivo no válido"}, 404
        
    if not os.path.exists(file_path):
        return {"error": "Archivo no encontrado"}, 404
        
    return FileResponse(path=file_path, media_type=media_type, filename=filename)

# ===== ANALYTICS ENDPOINTS =====

@app.options("/analytics/analyze/{task_id}")
async def options_analyze(task_id: str):
    """
    Handle CORS preflight requests for analyze endpoint
    """
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*"
        }
    )

@app.get("/analytics/analyze/{task_id}")
async def analyze_task_data(task_id: str):
    """
    Analiza los datos de una tarea específica y retorna estadísticas detalladas
    """
    try:
        csv_path = os.path.join(OUTPUT_DIR, f"{task_id}_data.csv")
        
        if not os.path.exists(csv_path):
            return JSONResponse(
                content={"error": "CSV file not found for this task"},
                status_code=404,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "*"
                }
            )
        
        # Procesar los datos reales del CSV
        analysis = analytics_processor.process_csv_data(csv_path)
        
        if "error" in analysis:
            return JSONResponse(
                content={"error": analysis["error"]},
                status_code=500,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "*"
                }
            )
        
        # Convertir cualquier int64 a int o float para JSON serialization
        def convert_numpy_types(obj):
            if hasattr(obj, 'item'):  # numpy scalar
                return obj.item()
            elif isinstance(obj, dict):
                return {k: convert_numpy_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(v) for v in obj]
            else:
                return obj
        
        # Aplicar conversión a todo el análisis
        clean_analysis = convert_numpy_types(analysis)
        
        return JSONResponse(
            content=clean_analysis,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "*"
            }
        )
    
    except Exception as e:
        print(f"Error in analyze_task_data: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            content={"error": str(e)},
            status_code=500,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "*"
            }
        )

@app.get("/analytics/visualization/{task_id}")
async def get_visualization_data(task_id: str):
    """
    Retorna datos optimizados para visualización en el dashboard
    """
    csv_path = os.path.join(OUTPUT_DIR, f"{task_id}_data.csv")
    
    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="CSV file not found for this task")
    
    analysis = analytics_processor.process_csv_data(csv_path)
    
    if "error" in analysis:
        raise HTTPException(status_code=500, detail=analysis["error"])
    
    viz_data = analytics_processor.generate_visualization_data(analysis)
    
    return JSONResponse(content=viz_data)

@app.get("/analytics/debug")
async def debug_summary():
    """
    Endpoint de debug para CORS
    """
    try:
        import os
        return JSONResponse(
            content={
                "debug": "working", 
                "output_dir_exists": os.path.exists(OUTPUT_DIR),
                "files_count": len([f for f in os.listdir(OUTPUT_DIR) if f.endswith("_data.csv")]) if os.path.exists(OUTPUT_DIR) else 0
            },
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "*"
            }
        )
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "*"
            }
        )

@app.get("/test-cors")
async def test_cors():
    """
    Endpoint de prueba para CORS
    """
    return JSONResponse(
        content={"message": "CORS funciona correctamente", "status": "ok"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*"
        }
    )

@app.options("/analytics/summary")
async def options_summary():
    """
    Handle CORS preflight requests
    """
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*"
        }
    )

@app.get("/analytics/summary")
async def get_all_tasks_summary():
    """
    Retorna un resumen de todas las tareas procesadas
    """
    try:
        tasks = []
        
        if os.path.exists(OUTPUT_DIR):
            csv_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith("_data.csv")]
            
            for filename in csv_files:
                task_id = filename.replace("_data.csv", "")
                csv_path = os.path.join(OUTPUT_DIR, filename)
                
                try:
                    # Procesar cada archivo CSV para obtener un resumen real
                    analysis = analytics_processor.process_csv_data(csv_path)
                    
                    if "error" not in analysis and "summary" in analysis:
                        # Convertir numpy types
                        summary = analysis["summary"]
                        
                        tasks.append({
                            "task_id": task_id,
                            "timestamp": float(os.path.getctime(csv_path)),
                            "summary": {
                                "total_detections": int(summary.get("total_detections", 0)),
                                "unique_persons": int(summary.get("unique_persons", 0)),
                                "duration_seconds": float(summary.get("duration_seconds", 0.0)),
                                "zones_count": int(summary.get("zones_count", 0)),
                                "detection_rate": float(summary.get("detection_rate", 0.0))
                            }
                        })
                    else:
                        # Si hay error en el procesamiento, crear datos básicos
                        tasks.append({
                            "task_id": task_id,
                            "timestamp": float(os.path.getctime(csv_path)),
                            "summary": {
                                "total_detections": 0,
                                "unique_persons": 0,
                                "duration_seconds": 0.0,
                                "zones_count": 0,
                                "detection_rate": 0.0
                            }
                        })
                except Exception as e:
                    print(f"Error processing {filename}: {str(e)}")
                    # Crear entrada básica en caso de error
                    tasks.append({
                        "task_id": task_id,
                        "timestamp": float(os.path.getctime(csv_path)),
                        "summary": {
                            "total_detections": 0,
                            "unique_persons": 0,
                            "duration_seconds": 0.0,
                            "zones_count": 0,
                            "detection_rate": 0.0
                        }
                    })
        
        return JSONResponse(
            content={
                "total_tasks": len(tasks),
                "tasks": sorted(tasks, key=lambda x: x["timestamp"], reverse=True)
            },
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "*"
            }
        )
    
    except Exception as e:
        print(f"Error in summary endpoint: {str(e)}")
        return JSONResponse(
            content={
                "total_tasks": 0,
                "tasks": [],
                "error": str(e)
            },
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "*"
            }
        )

@app.get("/analytics/compare")
async def compare_tasks(task_ids: str):
    """
    Compara múltiples tareas. task_ids debe ser una lista separada por comas
    """
    task_list = task_ids.split(",")
    comparison_data = {}
    
    for task_id in task_list:
        csv_path = os.path.join(OUTPUT_DIR, f"{task_id.strip()}_data.csv")
        
        if os.path.exists(csv_path):
            analysis = analytics_processor.process_csv_data(csv_path)
            if "error" not in analysis:
                comparison_data[task_id.strip()] = analysis["summary"]
    
    if not comparison_data:
        raise HTTPException(status_code=404, detail="No valid tasks found for comparison")
    
    return JSONResponse(content=comparison_data)