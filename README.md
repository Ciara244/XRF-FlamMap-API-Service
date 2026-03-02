# XRF FlamMap API Service (Headless Edition)

Este proyecto consiste en una **API REST profesional desarrollada en Python** para la orquestación y ejecución automatizada del motor de simulación de incendios **FlamMap**.

A diferencia de versiones anteriores basadas en automatización de interfaz (GUI), esta **versión 2.0 implementa una arquitectura Headless (sin interfaz)**.

El sistema interactúa directamente con los ejecutables de consola del Missoula Fire Sciences Lab, permitiendo:

- Simulaciones en segundo plano
- Gestión de colas
- Aislamiento de sesiones
- Rendimiento superior sin bloquear el escritorio del usuario

---

## Características Principales

### Arquitectura Backend Real

Ejecución mediante `subprocess` y tuberías de sistema, eliminando la necesidad de simular clics de ratón.

### Multiusuario y Aislado

Sistema de sesiones basado en **UUID** que permite múltiples simulaciones simultáneas sin colisiones de archivos.

### Salida de Datos Raw

Generación y retorno de mapas **GeoTIFF (.tif)** listos para análisis en sistemas GIS:

- QGIS
- ArcGIS

### Input Dinámico

Generación automática de archivos de configuración:

- `.input`
- `.wnd`
- `.fms`

Basada en los parámetros recibidos vía HTTP.

---

## Estructura del Proyecto

```
FLAMMAPSERVICEXRF/
│
├── app/
│   ├── __init__.py
│   ├── main.py              # Servidor API FastAPI (Orquestador)
│   ├── flammap_runner.py   # Motor de ejecución FlamMap
│   ├── config_writer.py    # Generador de archivos .input y comandos
│   └── fmp_manager.py      # Gestión de sesiones y directorios
│
├── data/
│   ├── inputs/             # Plantillas base y archivos de prueba
│   ├── outputs/            # Resultados persistentes (opcional)
│   └── temp_sessions/      # Entornos aislados por UUID
│
├── pruebas/                # Scripts de prueba
│
├── requirements           # Dependencias Python
└── README.md              # Documentación
```

---

## Descripción de Componentes

### app/main.py

El corazón de la API.

Responsabilidades:

- Gestionar endpoints  
- Validar archivos subidos (.lcp / .tif)  
- Crear entornos aislados  
- Ejecutar simulaciones  
- Devolver resultados al cliente  

---

### app/flammap_runner.py

Motor de ejecución.

Responsabilidades:

- Construir comandos del sistema  
- Invocar `TestFlamMap.exe` en segundo plano  
- Ejecutar simulaciones en background  
- Verificar archivos `.tif` generados  

---

### app/config_writer.py

Generador de archivos de configuración.

Responsabilidades:

- Crear archivos `.input`  
- Definir variables de humedad  
- Definir viento  
- Configurar generación de grids  

---

### data/temp_sessions/

Directorio de trabajo temporal (**Sandbox**).

Cada petición crea una carpeta única:

```
data/temp_sessions/a1b2c3d4/
```

Esto asegura que los datos de un usuario no interfieran con los de otro.

---

## Instalación y Requisitos

### 1. Requisitos del Sistema

Python **3.10 o superior**

#### Ejecutables de Consola de FlamMap

No sirve la versión estándar de escritorio.

Se requiere la versión de línea de comandos.

Fuente:

Alturas Solutions / Fire Lab API

Archivo necesario:

```
TestFlamMap.exe
```

Ubicación típica:

```
bin/TestFlamMap.exe
```

---

### 2. Instalación de Librerías

```
pip install -r requirements
```

---

### 3. Configuración de Rutas

Edite el archivo:

```
app/flammap_runner.py
```

Configure la ruta al ejecutable:

```python
flammap_exe = r"C:\Workspace\FB\bin\TestFlamMap.exe"
```

---

##  Ejecución del Servicio

Para iniciar el servidor:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

El servicio estará disponible en:

```
http://127.0.0.1:8000
```

---

##  Uso de la API

### Opción A — Swagger UI

Acceder desde el navegador:

```
http://127.0.0.1:8000/docs
```

Permite probar los endpoints visualmente.

---

### Opción B — Terminal (cURL)

Ejemplo de ejecución:

```bash
curl -X POST "http://127.0.0.1:8000/lanzar-simulacion" ^
  -F "wind_speed=20" ^
  -F "wind_direction=225" ^
  -F "fuel_moisture=6" ^
  -F "file=@C:\Ruta\A\Tu\Paisaje.tif" ^
  --output mapa_fuego.tif
```

---

##  Salida de Datos

El sistema genera múltiples capas raster.

Por defecto la API devuelve:

**Flame Length (Longitud de Llama)**

El motor también calcula:

- Rate of Spread (Velocidad de propagación)
- Fireline Intensity (Intensidad)
- Crown Fire Activity (Fuego de copas)
- Wind Vectors (Vectores de viento)

---

##  Especificaciones Técnicas

| Componente | Versión | Función |
|-----------|---------|---------|
| Python | 3.10+ | Lenguaje base |
| FastAPI | 0.109+ | Framework API |
| Subprocess | StdLib | Ejecución de procesos |
| TestFlamMap | 6.x CLI | Motor de cálculo |

---

##  Notas Importantes

### Formato de Archivos

El motor es sensible a rutas con:

- Espacios
- Caracteres especiales

El sistema lo gestiona automáticamente, pero se recomienda usar nombres simples.

---

### Visualización

Los resultados son **GeoTIFF de 32 bits**.

Se recomienda visualizar en:

- QGIS
- ArcGIS

Aplicando:

**Pseudocolor Monobanda**

---

## Autoría

**Desarrollador:** Ciara Martín  
**Institución:** XRF Lab (Periodo de Prácticas)  
**Versión:** 2.0 (Headless Architecture)