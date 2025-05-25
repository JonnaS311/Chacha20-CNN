import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import cv2
from deepface import DeepFace
import numpy as np
import time
import json
import subprocess
from scipy.spatial.distance import cosine
# Asegúrate de que compresion.py esté en el mismo directorio o sea accesible
from deepFace.compresion import compress_embedding # type: ignore
import sys

# --- Parámetros de Optimización y Configuración ---
PROCESS_EVERY_N_FRAMES = 3  # Procesar 1 de cada N fotogramas. Aumenta para más FPS, disminuye para detección más frecuente.
RESIZE_FRAME_TO_WIDTH = None # Opcional: Ancho para reescalar el fotograma (e.g., 640). None para no reescalar.
# Umbral de distancia para considerar una coincidencia.
# Facenet suele funcionar bien con < 0.4. Un valor más bajo es más estricto.
DISTANCE_THRESHOLD = 0.3
DEFAULT_MODEL_NAME = 'Facenet' # Modelo por defecto si no se carga uno del archivo
CAMERA_INDEX = 0 # Índice de la cámara
KNOWN_EMBEDDING_FILE = "./deepFace/embedding.json" # Ruta al archivo JSON de embeddings

def load_known_embedding(filepath, person_name):
    """Carga el embedding de referencia desde el archivo JSON."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        if person_name in data:
            embedding_data = data[person_name]
            known_vector = np.array(embedding_data['embedding'])
            model_name = embedding_data['model']
            print(f"Embedding de '{person_name}' cargado (Modelo: {model_name}) desde '{filepath}'.")
            return known_vector, model_name
        else:
            print(f"Error: No se encontró el nombre '{person_name}' en el archivo de embeddings '{filepath}'.")
            print(f"Nombres disponibles: {list(data.keys())}")
            return None, None
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo de embeddings '{filepath}'.")
        return None, None
    except json.JSONDecodeError:
        print(f"Error: El archivo JSON '{filepath}' está mal formateado o vacío.")
        return None, None
    except Exception as e:
        print(f"Error inesperado al cargar el embedding de '{person_name}': {e}")
        return None, None

def validacion(person_name_to_verify, main_exe_mode, main_exe_arg1, main_exe_arg2, main_exe_arg3_optional):

    if main_exe_mode not in ['0', '1']:
        print(f"Error: <modo_main_exe> debe ser '0' o '1'. Se recibió: {main_exe_mode}")
        sys.exit(1)
    if main_exe_mode == '1' and main_exe_arg3_optional is None:
        print("Error: El modo '1' para main.exe requiere un quinto argumento (arg_main_exe_extra_si_modo_1).")
        sys.exit(1)

    # --- Cargar Embedding Conocido ---
    known_embedding_vector, known_model_name = load_known_embedding(KNOWN_EMBEDDING_FILE, person_name_to_verify)

    if known_embedding_vector is None:
        print("No se pudo cargar el embedding de referencia. Saliendo.")
        sys.exit(1)
    
    # Si el embedding se cargó, la verificación está "activa" en el sentido de que estamos listos para verificar.
    active_model_name = known_model_name # Usar el modelo del embedding cargado

    # --- Inicializar Cámara ---
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print(f"Error: No se pudo abrir la cámara con índice {CAMERA_INDEX}.")
        sys.exit(1)

    print(f"Cámara abierta. Verificando para: '{person_name_to_verify}'.")
    print(f"Modelo activo para detección y verificación: {active_model_name}.")
    if RESIZE_FRAME_TO_WIDTH:
        print(f"Los fotogramas se reescalarán a un ancho de {RESIZE_FRAME_TO_WIDTH}px antes del procesamiento.")
    print(f"Se procesará 1 de cada {PROCESS_EVERY_N_FRAMES} fotogramas.")
    print(f"Umbral de distancia para '{person_name_to_verify}': {DISTANCE_THRESHOLD}")
    print("Presiona 'q' para salir manualmente.")

    # --- Variables para el Bucle ---
    prev_time_fps = 0
    main_loop_frame_counter = 0
    
    last_verification_text = "Esperando deteccion..."
    last_verification_color = (200, 200, 0) # Amarillo para "esperando"
    last_facial_area = None # Para dibujar el último cuadro delimitador conocido
    last_dist_text = ""     # Para dibujar la última distancia conocida
    
    running = True # Controla el bucle principal

    # --- Bucle Principal ---
    while running:
        ret, frame = cap.read()
        if not ret:
            print("Error: No se pudo leer el fotograma. ¿Cámara desconectada?")
            break

        main_loop_frame_counter += 1
        display_frame = frame.copy() # Copia para dibujar y mostrar

        # --- Reescalado Opcional del Fotograma para Procesamiento ---
        if RESIZE_FRAME_TO_WIDTH:
            h_orig, w_orig = frame.shape[:2]
            if w_orig > RESIZE_FRAME_TO_WIDTH: # Solo reescalar si es más grande
                aspect_ratio = h_orig / w_orig
                new_w = RESIZE_FRAME_TO_WIDTH
                new_h = int(new_w * aspect_ratio)
                processing_frame = cv2.resize(frame, (new_w, new_h))
            else:
                processing_frame = frame # Usar original si ya es pequeño
        else:
            processing_frame = frame

        # --- Procesamiento Facial y Verificación (Solo cada N fotogramas) ---
        if main_loop_frame_counter % PROCESS_EVERY_N_FRAMES == 0:
            try:
                # DeepFace.represent maneja la conversión BGR->RGB internamente.
                embedding_objs = DeepFace.represent(
                    img_path=processing_frame, # Usar el fotograma (potencialmente reescalado)
                    model_name=active_model_name,
                    enforce_detection=True, # Lanzará ValueError si no se detecta cara
                    detector_backend='opencv' # 'opencv' es generalmente el más rápido
                )

                # Si llegamos aquí, se detectó al menos una cara
                result = embedding_objs[0] # Tomar el embedding del primer rostro detectado
                current_embedding_vector = np.array(result['embedding'])
                
                # Coordenadas del rostro en el fotograma de procesamiento
                facial_area_proc = result['facial_area']
                x_proc, y_proc, w_proc, h_proc = facial_area_proc['x'], facial_area_proc['y'], facial_area_proc['w'], facial_area_proc['h']

                # Reescalar coordenadas a las dimensiones del display_frame original si se reescaló
                if RESIZE_FRAME_TO_WIDTH and frame.shape[1] > RESIZE_FRAME_TO_WIDTH:
                    scale_x = frame.shape[1] / processing_frame.shape[1]
                    scale_y = frame.shape[0] / processing_frame.shape[0]
                    x, y, w, h = int(x_proc * scale_x), int(y_proc * scale_y), int(w_proc * scale_x), int(h_proc * scale_y)
                else: # No hubo reescalado o el fotograma era pequeño
                    x, y, w, h = x_proc, y_proc, w_proc, h_proc
                last_facial_area = (x, y, w, h) # Guardar para dibujar

                # Realizar la verificación por distancia de coseno
                distance_cosine = cosine(current_embedding_vector, known_embedding_vector)
                last_dist_text = f"Dist: {distance_cosine:.4f}" # Mostrar con 4 decimales

                if distance_cosine < DISTANCE_THRESHOLD:
                    last_verification_text = f"ACCESO PERMITIDO ({person_name_to_verify})"
                    last_verification_color = (0, 255, 0) # Verde
                    print(f"\n¡Acceso Permitido para {person_name_to_verify}! Distancia: {distance_cosine:.4f}. Ejecutando acción...")

                    # Comprimir embedding y preparar para ejecutar main.exe
                    try:
                        compressed_key_bytes = compress_embedding(known_embedding_vector) # Asume que devuelve bytes
                        compressed_key_hex = compressed_key_bytes.hex() # Convertir a hexadecimal
                        
                        # Construir lista de argumentos para subprocess
                        cmd_args_for_subprocess = ['./main.exe', main_exe_mode, main_exe_arg1, main_exe_arg2, compressed_key_hex]
                        if main_exe_mode == '1':
                            cmd_args_for_subprocess.append(main_exe_arg3_optional) # Ya validado que no es None
                        
                        # Imprimir comando (sin la clave completa por seguridad en logs extensos)
                        print(f"Ejecutando: {' '.join(cmd_args_for_subprocess[:4])} <clave_comprimida_hex> ...")
                        
                        resultado_subprocess = subprocess.run(
                            cmd_args_for_subprocess, 
                            capture_output=True, 
                            text=True, 
                            check=False # No lanzar excepción en error, lo manejamos manualmente
                        )
                        
                        print("\n--- Salida de main.exe ---")
                        if resultado_subprocess.stdout:
                            print(f"stdout:\n{resultado_subprocess.stdout}")
                        if resultado_subprocess.stderr:
                            print(f"stderr:\n{resultado_subprocess.stderr}")
                        print(f"Código de retorno: {resultado_subprocess.returncode}")
                        print("--------------------------\n")
                        
                        if resultado_subprocess.returncode != 0:
                            last_verification_text = "Error en main.exe"
                            last_verification_color = (0,165,255) # Naranja para error de subproceso
                        
                        running = False # Detener el bucle principal después de la acción (éxito o error de main.exe)
                        # break # Salir inmediatamente del bucle while

                    except Exception as e_compress_subproc:
                        print(f"Error durante la compresión del embedding o la preparación de subprocess: {e_compress_subproc}")
                        last_verification_text = "Error Interno Script"
                        last_verification_color = (0, 0, 255) # Rojo para error grave del script
                        running = False # Detener el bucle principal
                        # break
                else: # Distancia mayor al umbral
                    last_verification_text = f"ACCESO DENEGADO ({person_name_to_verify})"
                    last_verification_color = (0, 0, 255) # Rojo
                    # Opcional: print(f"Acceso Denegado. Dist: {distance_cosine:.4f}") para no llenar la consola

            except ValueError: # Cara no detectada por DeepFace.represent con enforce_detection=True
                # Si no se detecta cara, podríamos limpiar el último bbox o mantenerlo.
                # Por ahora, si no hay cara, no se actualiza el estado de verificación.
                # last_facial_area = None # Descomentar para limpiar el bbox si no hay cara
                # last_verification_text = "Buscando rostro..."
                # last_verification_color = (200,200,0)
                pass 
            except Exception as e_represent:
                print(f"Error crítico con DeepFace.represent: {e_represent}")
                last_verification_text = "Error en DeepFace"
                last_verification_color = (0, 165, 255) # Naranja
                last_facial_area = None # Limpiar bbox en caso de error de DeepFace
                last_dist_text = ""
        
        # --- Dibujar Información en Pantalla (se ejecuta en cada fotograma) ---
        curr_time_fps = time.time()
        fps = 1 / (curr_time_fps - prev_time_fps) if (curr_time_fps - prev_time_fps) > 0 else 0
        prev_time_fps = curr_time_fps
        
        cv2.putText(display_frame, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(display_frame, f"Modelo: {active_model_name}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Dibujar el último estado de detección/verificación conocido
        if last_facial_area:
            x,y,w,h = last_facial_area
            cv2.rectangle(display_frame, (x, y), (x+w, y+h), last_verification_color, 2)
            cv2.putText(display_frame, active_model_name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, last_verification_color, 2)
            cv2.putText(display_frame, last_verification_text, (x, y - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, last_verification_color, 2)
            if last_dist_text:
                cv2.putText(display_frame, last_dist_text, (x, y + h + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, last_verification_color, 2)
        else: # Si no hay un área facial conocida (ej. al inicio o si se limpia)
             cv2.putText(display_frame, last_verification_text, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, last_verification_color, 2)

        # Indicador de que el script está "pensando" en los fotogramas que no procesa con DeepFace
        if main_loop_frame_counter % PROCESS_EVERY_N_FRAMES != 0 :
            processing_indicator_x = display_frame.shape[1] - 160 # Ajustar posición
            if processing_indicator_x < 10: processing_indicator_x = 10 
            cv2.putText(display_frame, "Analizando...", (processing_indicator_x, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 150, 0), 2)

        cv2.imshow(f"Verificacion Facial - {person_name_to_verify} (q: salir)", display_frame)

        # --- Salir con la Tecla 'q' ---
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("\nSaliendo por petición del usuario...")
            running = False # Detener el bucle principal
            # break
    
    # --- Fin del Bucle Principal ---
    # Si el bucle terminó porque running se puso a False (no por 'q' directamente en el último ciclo)
    # y fue una acción completada o un error manejado:
    if not (key == ord('q') and running is False): # Evitar doble mensaje si se presionó q y running ya era False
        if last_verification_text.startswith("ACCESO PERMITIDO") or "Error" in last_verification_text:
            print("Acción finalizada o error manejado. La ventana se cerrará en 5 segundos.")
            # Mostrar el último frame_display con el mensaje final
            cv2.imshow(f"Verificacion Facial - {person_name_to_verify} (q: salir)", display_frame)
            cv2.waitKey(5000) # Pausa de 5 segundos

    print("\nCerrando cámara y liberando recursos...")
    cap.release()
    cv2.destroyAllWindows()
    print("Programa finalizado.")

if __name__ == '__main__':
    pass 