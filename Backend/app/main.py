from fastapi import FastAPI, File, UploadFile, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import shutil
from app.processing import process_video_task, task_status

app = FastAPI()

# Configurar CORS para permitir que el frontend (Vue) se comunique
origins = [
    "http://localhost:5173", # Puerto por defecto de Vue/Vite
    "http://127.0.0.1:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directorios para guardar archivos temporales y resultados
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
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