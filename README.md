# XRF FlamMap API Service

Este proyecto consiste en un Wrapper API desarrollado en Python para la automatizacion y modernizacion del simulador de incendios forestales FlamMap6. El sistema permite la ejecucion de simulaciones mediante peticiones HTTP, actuando como un puente entre clientes modernos y el software legacy.


## Estructura del Proyecto
La organizacion del repositorio sigue los estandares de desarrollo modular para separar la logica del servidor de los datos de simulacion:

xrf-flammap-service/
│
├── 📂 app/
│   ├── __init__.py             (Archivo vacío)
│   ├── main.py                 (Servidor API - El "Camarero")
│   ├── flammap_runner.py       (Robot de Automatización - El "Cocinero")
│   ├── config_writer.py        (Generador de archivos .WND y .FMS dinámicos)
│   └── fmp_manager.py          (Gestor de proyectos y compatibilidad V19)
│
├── 📂 data/
│   ├── 📂 inputs/              (Plantillas maestras: .fmp, .fzp, .lcp, .tif)
│   ├── 📂 output_files/        (Almacén final de resultados .TIF)
│   └── 📂 temp_sessions/       (Sesiones aisladas por UUID para multi-usuario)
│
├── requirements.txt            (fastapi, uvicorn, pyautogui, python-multipart)
└── README.md                   (Instrucciones de uso y despliegue)

## Descripcion de Componentes
* app/main.py: Gestiona los puntos de entrada (endpoints) de la API y recibe las peticiones externas.
* app/flammap_runner.py: Contiene la logica de automatizacion con PyAutoGUI para controlar la interfaz de FlamMap.
* app/fmp_manager.py: Encargado de clonar la plantilla maestra y generar los archivos .fmp y .fzp necesarios para que el motor GIS de FlamMap no falle al mover el proyecto de carpeta.
* app/config_writer.py: Escribe dinámicamente las tablas de humedad (.fms) y viento (.wnd) basadas en los porcentajes y valores recibidos por la API.
* data/temp_sessions: Carpeta crítica donde se crean subdirectorios únicos por cada petición (ej. 0fd5f684) para evitar colisiones de archivos entre usuarios.
* data/inputs: Directorio destinado a almacenar el paisaje (Landscape) y las tablas de humedad necesarias.
* data/outputs: Directorio destinado a guardar los resultados generados.

## Instalacion y Configuracion
1. Requisitos del Sistema:
* Python 3.10 o superior.
* FlamMap 6 instalado en el equipo.

2. Instalacion de Librerias:
Ejecute el siguiente comando para instalar las dependencias necesarias:
pip install -r requirements.txt

3. Ejecucion del Servicio:
Para iniciar el servidor en modo desarrollo, ejecute:
uvicorn app.main:app --reload


### Especificaciones del Software
| Componente | Versión Recomendada | Función en el Proyecto |
| :--- | :---: | :--- |
| **Python** | 3.10+ | Lógica del servidor y scripts |
| **FastAPI** | 0.109.0 | Gestión de rutas y endpoints |
| **PyAutoGUI** | 0.9.54 | Automatización de la interfaz (RPA) |
| **FlamMap** | 6.x | Motor de cálculo físico |


## Uso de la API
Una vez el servidor este activo, puede interactuar con el servicio a traves de la interfaz Swagger UI:

* URL de Documentacion: http://127.0.0.1:8000/docs
* Endpoint Principal: POST /lanzar-simulacion

Al ejecutar la peticion, el robot tomara el control del raton y teclado para abrir el proyecto, ejecutar el calculo y visualizar los resultados de Flame Length.


## Notas Importantes
* Automatizacion GUI: El robot depende de las coordenadas de pantalla. No mueva el raton ni cambie de ventana mientras la simulacion este en curso.
* Rutas de Archivos: Verifique que las rutas definidas en main.py coincidan con la ubicacion real de FlamMap y el archivo .fmp en su equipo.


## Autoria
* Desarrollador: Ciara Martín
* Institucion: XRF Lab (Periodo de Practicas)
* Version: 1.0 (Ronda 1)

