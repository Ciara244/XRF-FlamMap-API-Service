import os
import time
import logging
import subprocess
from pywinauto.application import Application

logger = logging.getLogger("FlamMapRobot")

def ejecutar_simulacion_robot(exe_path, project_path, output_path):
    """
    Robot completo: Navega, lanza 22-tabs, pulsa OK, expande árbol y selecciona mapa Flame Length.
    """
    try:
        # 1. Limpieza previa del archivo de salida para evitar confusiones
        if os.path.exists(output_path):
            os.remove(output_path)

        # 2. Abrir FlamMap con el proyecto que le hemos pasado
        logger.info(f"Abriendo: {project_path}")
        subprocess.Popen([exe_path, project_path])
        time.sleep(7) 

        # 3. Conectar y dar foco a la ventana principal de FlamMap
        app = Application(backend="win32").connect(path=exe_path)
        main_win = app.window(title_re="FlamMap 6.*")
        main_win.set_focus()

        # 4. Obtener ruta del árbol y hacer clic derecho en Run1
        tree = main_win.child_window(class_name="SysTreeView32")
        root_name = tree.roots()[0].text()
        path_run1 = f"\\{root_name}\\Analysis Areas\\Entire Landscape (Default)\\Runs\\Run1"
        
        logger.info(f"Navegando a: {path_run1}")
        item_run = tree.get_item(path_run1)
        item_run.ensure_visible()
        item_run.click_input(button='right')
        time.sleep(1.5)

        # 5. Abrir Properties con 2 DOWN + ENTER (método más directo)
        logger.info("Abriendo propiedades...")
        main_win.type_keys("{DOWN 2}{ENTER}")
        time.sleep(4) 

        # 6. Interacción con la ventana de Propiedades para lanzar la simulación con 22-tabs
        try:
            prop_win = app.window(title="Run Properties")
            prop_win.set_focus()
            
            logger.info("Enviando secuencia: Ctrl+Tab y 22 Tabs...")
            prop_win.type_keys("^{TAB}") # Cambiar pestaña
            time.sleep(1)
            prop_win.type_keys("{TAB 22}") 
            time.sleep(1)
            prop_win.type_keys("{ENTER}") # Lanzar
            
        except Exception as e:
            logger.warning(f"Fallo en ventana específica, intentando foco general: {e}")
            prop_win = app.top_window()
            prop_win.set_focus()
            prop_win.type_keys("^{TAB}{TAB 22}{ENTER}")

     # 7. Cierre rápido de la ventana properties : Capturar popup de progreso y cerrar con ENTER
        logger.info("Esperando ventana de 'Execution complete'...")
        
        # Bucle rápido para capturar el popup instantáneo
        for _ in range(20): 
            try:
                # Obtenemos la ventana de arriba del todo
                ventana_final = app.top_window()
                
                # Verificamos si es el popup de progreso por su clase o texto
                if "Progress" in ventana_final.window_text() or "#32770" in ventana_final.class_name():
                    logger.info("✅ Ventana de éxito detectada. Cerrando...")
                    # Forzamos foco y enviamos ENTER directamente
                    ventana_final.set_focus()
                    # A veces un solo ENTER no basta, así que enviamos un TAB extra para asegurarnos de que el botón OK esté seleccionado, luego ENTER para cerrar
                    ventana_final.type_keys("{TAB}{ENTER}") 
                    
                    logger.info("Simulación cerrada correctamente.")
                    break
            except:
                pass
            time.sleep(2) #Reintentos rápidos cada 2 segundos

        # 8. Cerrar la ventana de propiedades conmétodo de seguridad (Alt+F4) para evitar bloqueos en el árbol
        logger.info("Cerrando propiedades con método de seguridad...")
        
        # 8.1. Forzamos una espera para que Windows registre el cierre del OK anterior
        time.sleep(1.5) 
        
        # 8.2. En vez de app.window, usamos la ventana activa del sistema para enviar el Alt+F4, esto es más directo y evita problemas de foco específicos
        from pywinauto import keyboard
        
        try:
            # Traemos la ventana al frente para asegurarnos de que el Alt+F4 se envíe al lugar correcto
            prop_win = app.window(title_re=".*Properties.*")
            prop_win.set_focus()
            
            # Enviamos el Alt+F4 usando el módulo keyboard de pywinauto, que es más robusto para enviar combinaciones de teclas a la ventana activa
            # % es ALT, {F4} es la tecla F4, y pause es un pequeño retraso entre teclas para asegurar que se registre correctamente
            prop_win.type_keys("%{F4}", pause=0.1) 
            
            logger.info("Alt+F4 enviado con éxito.")
        except:
            # Si falla el método de arriba, enviamos un Alt+F4 "al aire" que cerrará cualquier ventana activa, 
            # pero es mejor que dejar la ventana de propiedades abierta bloqueando el árbol
            keyboard.send_keys('%{F4}')
            logger.info("Alt+F4 enviado al sistema global.")

        time.sleep(2) # Espera vital para que el árbol se desbloquee

        # 9. Navegar al resultado de Run1 y hacer clic en Flame Length para mostrar el mapa, ahora sin la ventana gris bloqueando el árbol
        logger.info("Expandiendo Run1 para ver Flame Length...")
        try:
            item_run1 = tree.get_item(path_run1)
            item_run1.expand()
            time.sleep(1)
            
            # Buscamos la capa hija "Flame Length" dentro de Run1 y hacemos clic para mostrar el mapa
            item_flame = tree.get_item(path_run1 + "\\Flame Length")
            item_flame.click_input()
            logger.info("🚀 ¡Mapa de Flame Length en pantalla!")
            return True
        except Exception as e:
            logger.error(f"Error navegando al mapa: {e}")
            return False
        except Exception as e:
            logger.error(f"Error al navegar por los resultados: {e}")

        # 10. Validación final del archivo en disco
        logger.info("Validando existencia del archivo .tif...")
        timeout = 60
        start_wait = time.time()
        while time.time() - start_wait < timeout:
            if os.path.exists(output_path):
                logger.info(f"ÉXITO: Archivo detectado en {output_path}")
                return True
            time.sleep(2)
        
        logger.error("ERROR: El archivo no se generó tras la simulación.")
        return False

    except Exception as e: logger.error(f"Error en la ejecución del robot: {e}")
    