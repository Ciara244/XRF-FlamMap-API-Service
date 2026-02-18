import os
import shutil

def crear_proyecto_temporal(template_path, lcp_path, wnd_path, fms_path, output_dir):

    project_name = "Simulacion.fmp"
    new_project_path = os.path.join(output_dir, project_name)

    abs_lcp = os.path.abspath(lcp_path)
    abs_wnd = os.path.abspath(wnd_path)
    abs_fms = os.path.abspath(fms_path)

    # 1. Leer el template en binario
    with open(template_path, 'rb') as f:
        contenido = f.read()

    texto = contenido.decode('cp1252', errors='ignore')

    # 2. Reemplazar rutas
    texto = texto.replace("LCP_FILENAME=", f"LCP_FILENAME={abs_lcp}")
    texto = texto.replace("FUEL_MOISTURE_FILE=", f"FUEL_MOISTURE_FILE={abs_fms}")
    texto = texto.replace("WIND_FILE=", f"WIND_FILE={abs_wnd}")

    nuevo_contenido = texto.encode('cp1252')

    # 3. Guardar nuevo .fmp
    with open(new_project_path, 'wb') as f:
        f.write(nuevo_contenido)

    # 4. Copiar el .fzp asociado
    template_fzp = os.path.splitext(template_path)[0] + ".fzp"
    new_fzp_path = os.path.join(output_dir, "Simulacion.fzp")

    if os.path.exists(template_fzp):
        shutil.copyfile(template_fzp, new_fzp_path)
    else:
        raise FileNotFoundError("No se encontró el archivo .fzp del template")

    return new_project_path
