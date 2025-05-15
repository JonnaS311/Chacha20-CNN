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
KNOWN_EMBEDDING_FILE = "embedding.json"
DISTANCE_METRIC = 'cosine'

if not os.path.exists(KNOWN_EMBEDDING_FILE):
    with open(KNOWN_EMBEDDING_FILE, 'w') as f:
        json.dump({}, f, indent=4)


# --- Variables Globales ---
known_embedding_vector = None
known_model_name = None
verification_active = False
frames_to_wait = 10
frame_counter = 0

active_model_name = known_model_name if known_model_name else DEFAULT_MODEL_NAME

# --- Inicializar Cámara ---
cap = cv2.VideoCapture(CAMERA_INDEX)
if not cap.isOpened():
    print(f"Error: No se pudo abrir la cámara con índice {CAMERA_INDEX}")
    exit()

print(f"Cámara abierta. Modelo activo para detección: {active_model_name}.")
print("Presiona 'q' para salir.")

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
            # ... dibujado de rectángulo y texto ...
            cv2.rectangle(frame_display, (x, y), (x+w, y+h), verification_color if verification_active and verification_text else (0,255,0), 2)
            cv2.putText(frame_display, active_model_name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, verification_color if verification_active and verification_text else (0,255,0), 2)
            # incrementa contador mientras haya detección
            frame_counter += 1

            cv2.imshow(f"Verificacion Facial DeepFace (q: salir)", frame_display)
            # cuando lleves suficientes frames, guardas
            if frame_counter >= frames_to_wait:   
                data_to_save = {
                    "nombre": input("Añada el nombre de su clave biométrica:"),
                    "model": active_model_name,
                    "embedding": current_embedding_vector.tolist()
                }
                try:
                    with open(KNOWN_EMBEDDING_FILE, 'r+') as f:
                        existing = json.load(f)
                        existing[data_to_save.get("nombre")] = data_to_save       # añades tu objeto anidado
                        f.seek(0); f.truncate()
                        json.dump(existing, f, indent=4)
                    print(f"\n¡NUEVO embedding de referencia GUARDADO en '{KNOWN_EMBEDDING_FILE}' usando modelo '{active_model_name}'!")
                    known_embedding_vector = current_embedding_vector
                    known_model_name = active_model_name
                    verification_active = True
                    print("La verificación facial está ahora activa con el nuevo embedding.")
                    save_message_display_time = time.time() + 3
                    # resetea el contador para la próxima vez
                    frame_counter = 0
                    break
                except IOError as e_io:
                    print(f"\nError al guardar el archivo JSON: {e_io}")
        else:
            # si no detectas rostro, reinicia el contador
            frame_counter = 0

       
    except ValueError:
        verification_text = ""
        pass
    except Exception as e_represent:
        print(f"Error con DeepFace.represent: {e_represent}")
        pass

    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break

print("\nCerrando...")
cap.release()
cv2.destroyAllWindows()