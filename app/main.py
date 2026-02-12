from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from flammap_runner import ejecutar_simulacion_robot
import uvicorn
import os

app = FastAPI(
    title="XRF FlamMap Service", 
    version="1.1",
    description="Servicio de Simulación de Incendios con automatización de 22-Tabs"
)

# Definición del modelo de datos para la solicitud de simulación, con campo para la ruta del archivo de salida que el robot generará tras la simulación.
class SimRequest(BaseModel):
    exe_path: str = r"C:\Workspace\FlamMap6\FlamMap6.exe"
    project_path: str = r"C:\Workspace\FlamMap6\Tutorial\FlamMap1.fmp"
    output_path: str = r"C:\Workspace\FlamMap6\Tutorial\MillerLCP_Run1.tif"

@app.get("/")
def home():
    return {"status": "Online", "info": "Servicio de Simulación XRF Activo"}

@app.post("/lanzar-simulacion")
def trigger_simulation(config: SimRequest):
    """
    Endpoint que activa al robot. 
    Cumple el objetivo XRF de ofrecer una API documentada para crear simulaciones.
    """
    print(f"Petición recibida. Ejecutando robot para: {config.project_path}")
    
    # Validar existencia del ejecutable antes de intentar lanzar la simulación
    if not os.path.exists(config.exe_path):
        raise HTTPException(status_code=404, detail="No se encontró el ejecutable de FlamMap")

    # Llamada al robot (ahora con 3 parámetros) y captura de su resultado para la respuesta de la API
    exito = ejecutar_simulacion_robot(
        config.exe_path, 
        config.project_path, 
        config.output_path
    )
    
    # Respuesta basada en el resultado del robot, con mensajes claros para el cliente de la API
    if exito: 
        return {
            "status": "success", 
            "mensaje": "Simulación completada y validada", 
            "output": config.output_path
        }
    # En caso de fallo, se devuelve un error 500 con un mensaje detallado para facilitar la depuración por parte del cliente de la API
    else:
        raise HTTPException(
            status_code=500, 
            detail="La simulación falló o no se generó el archivo de salida"
        )

# Punto de entrada para ejecutar el servicio con Uvicorn, que es un servidor ASGI recomendado para FastAPI.
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)