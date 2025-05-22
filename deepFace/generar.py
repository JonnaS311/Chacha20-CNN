import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0' # Mantenido por si es necesario para tu entorno TensorFlow/CPU
import cv2
from deepface import DeepFace
import numpy as np
import time
import json
import sys

def generar(nombre):
    # --- Configuración ---
    DEFAULT_MODEL_NAME = 'Facenet'
    CAMERA_INDEX = 0 # 0 para la cámara por defecto, o el índice de tu cámara IP/USB
    KNOWN_EMBEDDING_FILE = "./deepFace/embedding.json" # Ruta al archivo JSON para guardar embeddings

    # --- Parámetros de Optimización ---
    PROCESS_EVERY_N_FRAMES = 3  # Procesar 1 de cada N fotogramas. Aumenta para más FPS, disminuye para detección más frecuente.
    RESIZE_FRAME_TO_WIDTH = None # Opcional: Ancho para reescalar el fotograma (e.g., 640). None para no reescalar.

    # --- Inicialización del Archivo de Embeddings ---
    if not os.path.exists(KNOWN_EMBEDDING_FILE):
        try:
            with open(KNOWN_EMBEDDING_FILE, 'w') as f:
                json.dump({}, f, indent=4)
            print(f"Archivo de embeddings '{KNOWN_EMBEDDING_FILE}' creado.")
        except IOError as e:
            print(f"Error: No se pudo crear el archivo de embeddings '{KNOWN_EMBEDDING_FILE}': {e}")
            sys.exit(1)

    # --- Variables Globales ---
    frames_to_wait_for_save = 10  # Número de detecciones exitosas consecutivas antes de guardar.
    # Contador de fotogramas donde se detectó una cara consecutivamente (en los fotogramas procesados)
    consecutive_successful_detections = 0 

    active_model_name = DEFAULT_MODEL_NAME

    # --- Inicializar Cámara ---
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print(f"Error: No se pudo abrir la cámara con índice {CAMERA_INDEX}. Verifica el índice o la conexión.")
        sys.exit(1)

    print(f"Cámara abierta (Índice: {CAMERA_INDEX}). Modelo activo para detección: {active_model_name}.")
    if RESIZE_FRAME_TO_WIDTH:
        print(f"Los fotogramas se reescalarán a un ancho de {RESIZE_FRAME_TO_WIDTH}px antes del procesamiento.")
    print(f"Se procesará 1 de cada {PROCESS_EVERY_N_FRAMES} fotogramas.")
    print(f"Se guardará el embedding tras {frames_to_wait_for_save} detecciones consecutivas exitosas en fotogramas procesados.")
    print("Presiona 'q' para salir.")

    # --- Variables para el Bucle ---
    prev_time_fps = 0
    main_loop_frame_counter = 0 # Contador total de fotogramas leídos de la cámara

    # --- Bucle Principal ---
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: No se pudo leer el fotograma. ¿Cámara desconectada?")
            break

        main_loop_frame_counter += 1
        display_frame = frame.copy() # Copia del fotograma para mostrar (con dibujos)

        # --- Reescalado Opcional del Fotograma ---
        if RESIZE_FRAME_TO_WIDTH:
            h, w = frame.shape[:2]
            if w > RESIZE_FRAME_TO_WIDTH:
                aspect_ratio = h / w
                new_w = RESIZE_FRAME_TO_WIDTH
                new_h = int(new_w * aspect_ratio)
                processing_frame = cv2.resize(frame, (new_w, new_h))
            else:
                processing_frame = frame # No reescalar si ya es más pequeño
        else:
            processing_frame = frame

        # --- Procesamiento Facial (Solo cada N fotogramas) ---
        current_embedding_vector = None # Para almacenar el embedding del fotograma actual si se procesa
        face_detected_in_current_processing_cycle = False

        if main_loop_frame_counter % PROCESS_EVERY_N_FRAMES == 0:
            try:
                # DeepFace espera imágenes en RGB, pero maneja la conversión BGR->RGB internamente.
                # Pasamos el 'processing_frame' (que es BGR de OpenCV) directamente.
                embedding_objs = DeepFace.represent(
                    img_path=processing_frame, # Fotograma (potencialmente reescalado)
                    model_name=active_model_name,
                    enforce_detection=True, # Lanzará ValueError si no se detecta cara
                    detector_backend='opencv' # 'opencv' es generalmente el más rápido
                )

                if embedding_objs: # Debería ser siempre true si enforce_detection=True y no hay error
                    result = embedding_objs[0] # Tomar el primer rostro detectado
                    current_embedding_vector = np.array(result['embedding'])
                    facial_area = result['facial_area']
                    x, y, w, h = facial_area['x'], facial_area['y'], facial_area['w'], facial_area['h']

                    # Ajustar coordenadas si el fotograma fue reescalado
                    if RESIZE_FRAME_TO_WIDTH and frame.shape[1] > RESIZE_FRAME_TO_WIDTH:
                        scale_x = frame.shape[1] / processing_frame.shape[1]
                        scale_y = frame.shape[0] / processing_frame.shape[0]
                        x, y, w, h = int(x * scale_x), int(y * scale_y), int(w * scale_x), int(h * scale_y)

                    # Dibujar rectángulo en el fotograma de visualización
                    cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(display_frame, active_model_name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    
                    consecutive_successful_detections += 1
                    face_detected_in_current_processing_cycle = True

            except ValueError: # Común si enforce_detection=True y no se encuentra cara
                # print("INFO: No se detectó ninguna cara en el fotograma procesado.") # Puede ser muy verboso
                consecutive_successful_detections = 0 # Reiniciar contador si no se detecta cara
            except Exception as e_represent:
                print(f"Error durante DeepFace.represent: {e_represent}")
                consecutive_successful_detections = 0 # Reiniciar contador en caso de otros errores

        # --- Lógica para Guardar Embedding ---
        if consecutive_successful_detections >= frames_to_wait_for_save and current_embedding_vector is not None:
            nombre_persona = nombre # Nombre por defecto
            data_to_save = {
                "nombre": nombre_persona,
                "model": active_model_name,
                "embedding": current_embedding_vector.tolist()
            }
            try:
                with open(KNOWN_EMBEDDING_FILE, 'r+') as f:
                    try:
                        existing_data = json.load(f)
                    except json.JSONDecodeError: # Archivo vacío o JSON inválido
                        existing_data = {}
                    
                    existing_data[data_to_save["nombre"]] = data_to_save # Añadir o actualizar
                    f.seek(0) # Volver al inicio del archivo
                    f.truncate() # Limpiar el archivo
                    json.dump(existing_data, f, indent=4) # Escribir los datos actualizados
                
                print(f"\n¡ÉXITO! Embedding de '{nombre_persona}' GUARDADO en '{KNOWN_EMBEDDING_FILE}' (Modelo: '{active_model_name}').")
                print("Saliendo del programa...")
                break # Salir del bucle principal después de guardar

            except IOError as e_io:
                print(f"\nError Crítico: No se pudo leer/escribir en el archivo JSON '{KNOWN_EMBEDDING_FILE}': {e_io}")
                consecutive_successful_detections = 0 # Reiniciar para evitar bucle de error si el problema persiste
            except Exception as e_save:
                print(f"\nError inesperado al guardar el embedding: {e_save}")
                consecutive_successful_detections = 0


        # --- Mostrar Información en Pantalla ---
        curr_time_fps = time.time()
        fps = 1 / (curr_time_fps - prev_time_fps) if (curr_time_fps - prev_time_fps) > 0 else 0
        prev_time_fps = curr_time_fps
        
        info_text_fps = f"FPS: {int(fps)}"
        info_text_model = f"Modelo: {active_model_name}"
        info_text_detections = f"Detecciones seguidas: {consecutive_successful_detections}/{frames_to_wait_for_save}"

        cv2.putText(display_frame, info_text_fps, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(display_frame, info_text_model, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(display_frame, info_text_detections, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        if main_loop_frame_counter % PROCESS_EVERY_N_FRAMES != 0 and not face_detected_in_current_processing_cycle:
            cv2.putText(display_frame, "Procesando...", (display_frame.shape[1] - 150, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 150, 0), 2)


        # --- Mostrar Fotograma ---
        cv2.imshow(f"Registro Facial DeepFace (q: salir)", display_frame)

        # --- Salir con la Tecla 'q' ---
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("\nSaliendo por petición del usuario...")
            break

    # --- Limpieza Final ---
    print("Cerrando cámara y ventanas...")
    cap.release()
    cv2.destroyAllWindows()
    print("Programa finalizado.")


if __name__ == '__main__':
    pass