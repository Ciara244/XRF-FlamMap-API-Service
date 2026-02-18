from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
import uvicorn
import threading
import os
import shutil
import uuid  # Necesario para crear nombres únicos de sesión

# --- Módulos locales ---
from flammap_runner import ejecutar_simulacion_robot
from config_writer import crear_archivos_input
from fmp_manager import crear_proyecto_temporal 

app = FastAPI(
    title="XRF FlamMap Service (Pro)", 
    version="2.0",
    description="Servicio SaaS de Simulación de Incendios: Multi-usuario con sesiones aisladas"
)

# --- CONFIGURACIÓN GLOBAL ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORK_DIR = os.path.join(os.path.dirname(BASE_DIR), "data", "temp_sessions")
EXE_PATH = r"C:\Workspace\FlamMap6\FlamMap6.exe"
TEMPLATE_PATH = os.path.join(os.path.dirname(BASE_DIR), "data", "inputs", "FlamMap1.fmp")

# Crear directorio de trabajo si no existe
os.makedirs(WORK_DIR, exist_ok=True)

# SEMÁFORO: Solo permite un hilo a la vez
simulation_lock = threading.Lock()

@app.get("/")
def home():
    return {"status": "Online", "mode": "Professional SaaS"}

@app.post("/lanzar-simulacion")
async def trigger_simulation(
    # --- INPUTS (Ahora recibimos Archivo + Datos de Formulario) ---
    file: UploadFile = File(..., description="Archivo de paisaje (.LCP o .tif)"),
    wind_speed: float = Form(..., description="Velocidad viento (mph)"),
    wind_direction: int = Form(..., description="Dirección viento (grados)"),
    fuel_moisture: float = Form(..., description="Humedad combustible (%)")
):
    """
    Endpoint Profesional:
    1. Crea un ID único de sesión (para no mezclar usuarios).
    2. Guarda el LCP/tif subido en una carpeta aislada.
    3. Genera inputs y modifica el proyecto .FMP para apuntar a esa carpeta.
    4. Ejecuta el robot de forma segura (Lock).
    """

    # 1. PREPARACIÓN DE SESIÓN (Esto es nuevo: Aislamiento)
    session_id = str(uuid.uuid4())[:8]  # Ej: 'a1b2c3d4'
    session_dir = os.path.join(WORK_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)
    
    print(f"[Sesión {session_id}] Iniciando preparación...")

    # Rutas dinámicas para esta sesión específica
    lcp_path = os.path.join(session_dir, file.filename)
    output_tif = os.path.join(session_dir, "resultado.tif")

    try:
        # A. Guardar el archivo LCP que subió el usuario
        with open(lcp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # B. Generar Archivos de Entrada (Viento/Humedad) en la carpeta de sesión
        # Reutilizamos tu config_writer, pero le pasamos la carpeta dinámica
        wnd_path, fms_path = crear_archivos_input(
            session_dir, 
            wind_speed, 
            wind_direction, 
            fuel_moisture
        )

        # C. Crear Proyecto .FMP "Custom" (El paso clave del profesional)
        # Usamos la plantilla y cambiamos sus rutas internas
        project_session_path = crear_proyecto_temporal(
            TEMPLATE_PATH, 
            lcp_path, 
            wnd_path, 
            fms_path, 
            session_dir
        )

        # 2. SECCIÓN CRÍTICA (Bloqueo del Robot)
        # Intentar adquirir bloqueo (sin esperar, falla rápido)
        if not simulation_lock.acquire(blocking=False):
            raise HTTPException(
                status_code=503, 
                detail="Servidor ocupado con otra simulación. Intenta en unos segundos."
            )

        try:
            print(f"[Sesión {session_id}] Ejecutando Robot...")
            
            # Ejecutamos el robot apuntando al proyecto TEMPORAL de esta sesión
            exito = ejecutar_simulacion_robot(
                EXE_PATH, 
                project_session_path, # <--- Usamos el modificado, no el original
                output_tif
            )

            # 3. RESPUESTA
            if exito and os.path.exists(output_tif):
                return FileResponse(
                    path=output_tif, 
                    filename=f"simulacion_{session_id}.tif", 
                    media_type='image/tiff'
                )
            else:
                raise HTTPException(status_code=500, detail="El simulador no generó el archivo.")

        finally:
            # Liberar siempre el robot
            simulation_lock.release()
            print(f"[Sesión {session_id}] Robot liberado.")

    except Exception as e:
        print(f"Error crítico en sesión {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    # (Opcional: Podrías añadir código aquí para borrar session_dir tras enviar el archivo)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)