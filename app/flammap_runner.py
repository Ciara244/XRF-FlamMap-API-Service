import os
import subprocess

def preparar_y_ejecutar_flammap(ruta_base, lcp_path, porcentaje_humedad, velocidad_viento):
    
    if ruta_base.endswith('.fmp') or os.path.isfile(ruta_base):
        session_dir = os.path.dirname(ruta_base)
    else:
        session_dir = ruta_base

    flammap_exe = r"C:\Workspace\FB\bin\TestFlamMap.exe" 
    
    session_dir = session_dir.replace("\\", "/")
    lcp_path = str(lcp_path).replace("\\", "/")
    
    input_file_path = f"{session_dir}/config_simulacion.input"
    cmd_file_path = f"{session_dir}/run_cmd.txt"
    output_base_path = f"{session_dir}/resultados_simulacion"
    
    contenido_input = f"""FlamMap-Inputs-File-Version-1
        FUEL_MOISTURES_DATA: 1
        0 {porcentaje_humedad} {porcentaje_humedad} {porcentaje_humedad} 100 100
        FOLIAR_MOISTURE_CONTENT: 100
        CROWN_FIRE_METHOD: Finney
        NUMBER_PROCESSORS: 1
        WIND_SPEED: {velocidad_viento}
        WIND_DIRECTION: 240
        SPREAD_DIRECTION_FROM_MAX: 0
        GRIDDED_WINDS_GENERATE: Yes
        GRIDDED_WINDS_RESOLUTION: 60.0

        FLAMELENGTH:
        SPREADRATE:
        INTENSITY:
        HEATAREA:
        CROWNSTATE:
        CROWNFRACTIONBURNED:
        SOLARRADIATION:
        FUELMOISTURE1:
        FUELMOISTURE10:
        FUELMOISTURE100:
        FUELMOISTURE1000:
        MIDFLAME:
        HORIZRATE:
        MAXSPREADDIR:
        ELLIPSEDIM_A:
        ELLIPSEDIM_B:
        ELLIPSEDIM_C:
        MAXSPOT_DIR:
        MAXSPOT_DX:
        WINDDIRGRID:
        WINDSPEEDGID:
    """

    with open(input_file_path, "w") as f:
        f.write(contenido_input)

    contenido_cmd = f'{lcp_path} {input_file_path} {output_base_path} 2\n'
    
    with open(cmd_file_path, "w") as f:
        f.write(contenido_cmd)

    print(f"Ejecutando motor FlamMap en consola...")
    comando = [flammap_exe, cmd_file_path]
    
    try:
        resultado = subprocess.run(
            comando, 
            capture_output=True, 
            text=True
        )
        
        mapa_llama = f"{output_base_path}_FLAMELENGTH.tif"
        mapa_propagacion = f"{output_base_path}_SPREADRATE.tif"
        
        if os.path.exists(mapa_llama) and os.path.exists(mapa_propagacion):
            return [mapa_llama, mapa_propagacion]
        else:
            print("No se encontraron los archivos con el nombre que Python esperaba.")
            return []
            
    except Exception as e:
        print(f"Error de Python: {str(e)}")
        return []