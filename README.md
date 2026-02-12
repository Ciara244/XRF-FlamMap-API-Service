# XRF FlamMap API Service

Este proyecto consiste en un Wrapper API desarrollado en Python para la automatizacion y modernizacion del simulador de incendios forestales FlamMap6. El sistema permite la ejecucion de simulaciones mediante peticiones HTTP, actuando como un puente entre clientes modernos y el software legacy.


## Estructura del Proyecto
La organizacion del repositorio sigue los estandares de desarrollo modular para separar la logica del servidor de los datos de simulacion:

xrf-flammap-service/
│
├── 📂 app/
│   ├── __init__.py             (Archivo vacío)
│   ├── main.py                 (El Servidor API - El "Camarero")
│   └── flammap_runner.py       (El Robot - El "Cocinero")
│
├── 📂 data/
│   ├── 📂 inputs/              (Aquí guardas tus .LCP y .FMS de prueba)
│   ├── 📂 output_files/        (Aquí se guardarán los resultados)
│
├── ProyectoXRF_Ronda1.fmp      (¡IMPORTANTE! Tu archivo de proyecto maestro)
├── requirements.txt            (fastapi, uvicorn, pyautogui, python-multipart)
└── README.md                   (Explicación de cómo usarlo)

## Descripcion de Componentes
* app/main.py: Gestiona los puntos de entrada (endpoints) de la API y recibe las peticiones externas.
* app/flammap_runner.py: Contiene la logica de automatizacion con PyAutoGUI para controlar la interfaz de FlamMap.
* data/inputs: Directorio destinado a almacenar el paisaje (Landscape) y las tablas de humedad necesarias.
* data/outputs: Directorio destinado a guardar los resultados generados.
* ProyectoXRF_Ronda1.fmp: Archivo principal que contiene la configuracion fisica y el modelo Scott/Reinhardt (2001). Prueba


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

