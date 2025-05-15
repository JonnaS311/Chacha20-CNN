import cv2
from deepface import DeepFace
import numpy as np
import time
import json
import os
from scipy.spatial.distance import cosine # type: ignore

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# --- Configuración ---
DEFAULT_MODEL_NAME = 'Facenet'
CAMERA_INDEX = 0
KNOWN_EMBEDDING_FILE = "mi_cara_embedding.json"
DISTANCE_METRIC = 'cosine'

# --- Variables Globales ---
known_embedding_vector = None
known_model_name = None
verification_active = False

# --- Cargar Embedding Conocido ---
try:
    with open(KNOWN_EMBEDDING_FILE, 'r') as f:
        data = json.load(f)
        known_embedding_vector = np.array(data['embedding'])
        known_model_name = data['model']
        verification_active = True
        print(f"Embedding de referencia cargado desde '{KNOWN_EMBEDDING_FILE}' (Modelo: {known_model_name})")
        print(f"Usando el modelo '{known_model_name}' para detección y verificación.")
except FileNotFoundError:
    print(f"ADVERTENCIA: No se encontró el archivo de embedding de referencia '{KNOWN_EMBEDDING_FILE}'.")
    print(f"La verificación facial no estará activa.")
    print(f"Presiona 's' para detectar tu cara y guardar un nuevo embedding de referencia (usando el modelo {DEFAULT_MODEL_NAME}).")
    known_model_name = DEFAULT_MODEL_NAME
except Exception as e:
    print(f"Error al cargar el embedding de referencia: {e}")
    print(f"La verificación facial no estará activa.")
    known_model_name = DEFAULT_MODEL_NAME

active_model_name = known_model_name if known_model_name else DEFAULT_MODEL_NAME

# --- Inicializar Cámara ---
cap = cv2.VideoCapture(CAMERA_INDEX)
if not cap.isOpened():
    print(f"Error: No se pudo abrir la cámara con índice {CAMERA_INDEX}")
    exit()

print(f"Cámara abierta. Modelo activo para detección: {active_model_name}.")
print("Presiona 'q' para salir.")
if not verification_active:
    print("Presiona 's' cuando tu cara esté en el recuadro para GUARDAR el embedding de referencia.")

prev_time = 0
last_saved_time = 0
save_message_display_time = 0
verification_text = ""
verification_color = (0, 0, 0)

# --- Bucle Principal ---
while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: No se pudo leer el fotograma.")
        break

    frame_display = frame.copy()
    current_embedding_vector = None

    curr_time = time.time()
    fps = 1 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
    prev_time = curr_time
    cv2.putText(frame_display, f"FPS: {int(fps)} | {frame_display.shape[1]}x{frame_display.shape[0]}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(frame_display, f"Modelo: {active_model_name}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    try:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        embedding_objs = DeepFace.represent(
            img_path=frame_rgb,
            model_name=active_model_name,
            enforce_detection=True,
            detector_backend='opencv'
        )

        if embedding_objs:
            result = embedding_objs[0]
            current_embedding_vector = np.array(result['embedding'])
            facial_area = result['facial_area']
            x, y, w, h = facial_area['x'], facial_area['y'], facial_area['w'], facial_area['h']

            if verification_active and known_embedding_vector is not None and current_embedding_vector is not None:
                try:
    
                    distance_cosine = cosine(current_embedding_vector, known_embedding_vector) 
                    
                    print(" Coseno", distance_cosine)
                    if distance_cosine < 0.3:
                        verification_text = "ACCESO PERMITIDO"
                        verification_color = (0, 255, 0)
                    else:
                        verification_text = "ACCESO DENEGADO"
                        verification_color = (0, 0, 255)

                    dist_text = f"Dist: {distance_cosine}"
                    cv2.putText(frame_display, dist_text, (x, y + h + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, verification_color, 2)
                except Exception as e_verify:
                    print(f"Error durante la verificación: {e_verify}")
                    verification_text = "Error Verificando"
                    verification_color = (0, 165, 255)

                cv2.putText(frame_display, verification_text, (x, y - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, verification_color, 2)

            cv2.rectangle(frame_display, (x, y), (x+w, y+h), verification_color if verification_active and verification_text else (0,255,0), 2)
            cv2.putText(frame_display, active_model_name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, verification_color if verification_active and verification_text else (0,255,0), 2)

    except ValueError:
        verification_text = ""
        pass
    except Exception as e_represent:
        print(f"Error con DeepFace.represent: {e_represent}")
        pass

    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break
    if save_message_display_time > time.time():
        (text_width, text_height), _ = cv2.getTextSize("REFERENCIA GUARDADA", cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
        text_x = frame_display.shape[1] - text_width - 10
        cv2.putText(frame_display, "REFERENCIA GUARDADA", (text_x, 60 if verification_active else 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,0,255), 2)


    cv2.imshow(f"Verificacion Facial DeepFace (q: salir)", frame_display)

print("\nCerrando...")
cap.release()
cv2.destroyAllWindows()