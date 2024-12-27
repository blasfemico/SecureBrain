import cv2
import threading
from MSS.behavior_analysis import analyze_behavior
from MSS.notification import send_alert
import time
import logging
from datetime import datetime
import os

# Configuración de logs
log_folder = "logs"
os.makedirs(log_folder, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_folder, "motion_detection.log"),
    level=logging.DEBUG,  # Cambiado a DEBUG para más detalles
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Variables globales
camera = None
motion_detection_thread = None
running = False
last_alert_time = 0

# Configuración
CONFIG = {
    "min_area": 1500,  # Área mínima para detectar movimiento
    "max_area": 50000,  # Área máxima para evitar contornos excesivamente grandes
    "sensitivity": 25,  # Sensibilidad para detectar movimiento
    "presence_time": 5,  # Segundos para considerar que alguien está presente
    "alert_interval": 10,  # Segundos entre alertas
    "save_images": True,  # Guardar imágenes de comportamiento sospechoso
    "output_folder": os.path.join(log_folder, "images"),
    "frame_skip": 5,  # Procesar 1 de cada N frames con YOLO
}

# Asegurar la carpeta de salida
os.makedirs(CONFIG["output_folder"], exist_ok=True)

# Estado de presencia
presence_tracker = {}

def show_camera_feed():
    """Mostrar el feed de la cámara en tiempo real en una ventana separada."""
    while running:
        ret, frame = camera.read()
        if not ret:
            logging.warning("No se pudo leer el frame de la cámara.")
            print("No se pudo leer el frame de la cámara.")
            break

        # Mostrar el frame en una ventana
        cv2.imshow("Cámara en Tiempo Real", frame)

        # Salir si se presiona 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

def detect_movement(frame, first_frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
    frame_delta = cv2.absdiff(first_frame, gray)
    thresh = cv2.threshold(frame_delta, CONFIG["sensitivity"], 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)

    contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    logging.info(f"Contornos detectados: {len(contours)}")
    print(f"Contornos detectados: {len(contours)}")
    return contours

def motion_detection_logic():
    global running, camera, last_alert_time

    first_frame = None
    first_frame_initialized = False  # Nueva variable para rastrear la inicialización del primer frame
    logging.info("Iniciando lógica de detección de movimiento.")
    print("Iniciando lógica de detección de movimiento.")
    frame_count = 0

    while running:
        ret, frame = camera.read()
        if not ret:
            logging.warning("No se pudo leer el frame de la cámara.")
            print("No se pudo leer el frame de la cámara.")
            break

        frame = cv2.resize(frame, (320, 240))

        # Inicializar primer frame una vez o actualizarlo periódicamente
        if first_frame is None:
            first_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            first_frame = cv2.GaussianBlur(first_frame, (21, 21), 0)
            if not first_frame_initialized:
                logging.info("Primer frame inicializado por primera vez.")
                print("Primer frame inicializado por primera vez.")
                first_frame_initialized = True
            continue
        elif frame_count % 300 == 0:  # Actualizar el primer frame cada 300 frames
            first_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            first_frame = cv2.GaussianBlur(first_frame, (21, 21), 0)
            logging.info("Primer frame actualizado después de 300 frames.")
            print("Primer frame actualizado después de 300 frames.")

        contours = detect_movement(frame, first_frame)

        for contour in contours:
            area = cv2.contourArea(contour)
            if area < CONFIG["min_area"] or area > CONFIG["max_area"]:
                continue

            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            object_id = "person"
            if object_id not in presence_tracker:
                presence_tracker[object_id] = time.time()
            elif time.time() - presence_tracker[object_id] >= CONFIG["presence_time"]:
                analyze_and_notify(frame)
                presence_tracker.pop(object_id, None)

        cv2.imshow("Detección de Movimiento", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

        frame_count += 1
        time.sleep(0.05)

    camera.release()
    cv2.destroyAllWindows()
    logging.info("Detección de movimiento finalizada.")


def analyze_and_notify(frame):
    """Analizar comportamiento y enviar notificaciones si es sospechoso."""
    suspicious = analyze_behavior(frame)
    if suspicious:
        current_time = time.time()
        if current_time - last_alert_time > CONFIG["alert_interval"]:
            logging.warning("Comportamiento sospechoso detectado. Enviando alerta.")
            print("Comportamiento sospechoso detectado. Enviando alerta.")
            send_alert(frame, "Alerta: Comportamiento sospechoso detectado.")
            if CONFIG["save_images"]:
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                image_path = f"{CONFIG['output_folder']}/alert_{timestamp}.jpg"
                cv2.imwrite(image_path, frame)
                logging.info(f"Foto guardada: {image_path}")
                print(f"Foto guardada: {image_path}")

def start_motion_detection():
    """Iniciar la detección de movimiento y el feed de la cámara."""
    global camera, motion_detection_thread, running
    if running:
        return
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not camera.isOpened():
        logging.error("No se pudo acceder a la cámara.")
        print("No se pudo acceder a la cámara.")
        return

    running = True

    motion_detection_thread = threading.Thread(target=motion_detection_logic)
    motion_detection_thread.start()
    camera_feed_thread = threading.Thread(target=show_camera_feed)
    camera_feed_thread.start()

    logging.info("Hilo de detección de movimiento y feed de cámara iniciado.")
    print("Hilo de detección de movimiento y feed de cámara iniciado.")

def stop_motion_detection():
    """Detener la detección de movimiento y el feed de la cámara."""
    global running, motion_detection_thread
    if not running:
        return

    running = False
    motion_detection_thread.join()
    camera.release()
    cv2.destroyAllWindows()  
    logging.info("Hilo de detección de movimiento detenido.")
    print("Hilo de detección de movimiento detenido.")
