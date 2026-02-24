from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
import uvicorn
import threading
import os
import shutil
import uuid  # Necesario para crear nombres únicos de sesión

# --- Módulos locales ---
from flammap_runner import preparar_y_ejecutar_flammap
from config_writer import crear_archivos_input
from fmp_manager import crear_proyecto_temporal 

app = FastAPI(
    title="XRF FlamMap Service", 
    version="2.0",
    description="Servicio SaaS de Simulación de Incendios: Multi-usuario con sesiones aisladas y ejecución en segundo plano"
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
    return {"status": "Online", "mode": "Professional SaaS (Headless)"}

@app.post("/lanzar-simulacion")
async def trigger_simulation(
    # --- INPUTS ---
    file: UploadFile = File(..., description="Archivo de paisaje (.LCP o .tif)"),
    wind_speed: float = Form(..., description="Velocidad viento (mph)"),
    wind_direction: int = Form(..., description="Dirección viento (grados)"),
    fuel_moisture: float = Form(..., description="Humedad combustible (%)")
):
    """
    Endpoint Profesional:
    1. Crea un ID único de sesión.
    2. Guarda el LCP/tif subido.
    3. Genera inputs de configuración.
    4. Ejecuta el motor de FlamMap en consola de forma segura (Lock).
    5. Devuelve el mapa TIF resultante.
    """

    # 1. PREPARACIÓN DE SESIÓN
    session_id = str(uuid.uuid4())[:8] 
    session_dir = os.path.join(WORK_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)
    
    print(f"[Sesión {session_id}] Iniciando preparación...")

    # Rutas dinámicas para esta sesión específica
    lcp_path = os.path.join(session_dir, file.filename)

    try:
        # A. Guardar el archivo LCP que subió el usuario
        with open(lcp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # B. Generar Archivos de Entrada (Mantenemos tu lógica anterior por compatibilidad)
        wnd_path, fms_path = crear_archivos_input(
            session_dir, wind_speed, wind_direction, fuel_moisture
        )

        # C. Crear Proyecto .FMP 
        project_session_path = crear_proyecto_temporal(
            TEMPLATE_PATH, lcp_path, wnd_path, fms_path, session_dir
        )

        # 2. SECCIÓN CRÍTICA (Bloqueo del motor)
        if not simulation_lock.acquire(blocking=False):
            raise HTTPException(
                status_code=503, 
                detail="Servidor ocupado con otra simulación. Intenta en unos segundos."
            )

        try:
            print(f"[Sesión {session_id}] Ejecutando motor en segundo plano...")
            
            # Ejecutamos el motor de consola apuntando a la sesión actual
            archivos_generados = preparar_y_ejecutar_flammap(
                project_session_path,
                lcp_path,
                fuel_moisture,
                wind_speed
            )

            # 3. RESPUESTA
            # Verificamos que el motor nos haya devuelto la lista con los TIFs
            if archivos_generados and len(archivos_generados) > 0:
                mapa_principal = archivos_generados[0] # Tomamos el FLAMELENGTH
                
                return FileResponse(
                    path=mapa_principal, 
                    filename=f"simulacion_{session_id}_FlameLength.tif", 
                    media_type='image/tiff'
                )
            else:
                raise HTTPException(status_code=500, detail="El simulador falló internamente al crear los archivos TIF.")

        finally:
            # Liberar siempre el hilo, pase lo que pase
            simulation_lock.release()
            print(f"[Sesión {session_id}] Hilo de ejecución liberado.")

    except HTTPException:
        # Relanzamos las excepciones HTTP tal cual para que FastAPI las gestione
        raise
        
    except Exception as e:
        print(f"Error crítico en sesión {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)