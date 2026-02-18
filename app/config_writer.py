import os

def crear_archivos_input(session_dir, wind_speed, wind_direction, fuel_moisture):
    """Genera inputs físicos asegurando compatibilidad y escritura."""
    wnd_path = os.path.join(session_dir, "input_wind.wnd")
    fms_path = os.path.join(session_dir, "input_moisture.fms")

    # 1. Archivo de Viento
    with open(wnd_path, "w", encoding='latin-1') as f:
        f.write("ENGLISH\n")
        f.write(f"08 15 1300 {wind_speed} {wind_direction} 0\n")
        f.flush()
        os.fsync(f.fileno())

    # 2. Archivo de Humedad (Modelos 1 a 260 para cubrir todo)
    with open(fms_path, "w", encoding='latin-1') as f:
        f.write("ENGLISH\n")
        for code in range(1, 261):
            f.write(f"{code} {fuel_moisture} {fuel_moisture} {fuel_moisture} 100 100\n")
        f.flush()
        os.fsync(f.fileno())

    return wnd_path, fms_path