import cv2
import threading
from MSS.behavior_analysis import analyze_behavior
from MSS.notification import send_alert
from MSS.object_detection import detect_objects
import time

# Variables globales
camera = None
motion_detection_thread = None
running = False
last_alert_time = 0

# Configuración
CONFIG = {
    "min_area": 1500,
    "sensitivity": 25,
    "alert_interval": 10,  # Segundos entre alertas
}

# Lógica principal
def motion_detection_logic():
    global running, camera, last_alert_time

    first_frame = None

    while running:
        ret, frame = camera.read()
        if not ret:
            break

        # Convertir a escala de grises y suavizar
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        # Configurar el primer frame para comparación
        if first_frame is None or time.time() % 60 == 0:
            first_frame = gray
            continue

        # Calcular diferencias y detectar movimiento
        frame_delta = cv2.absdiff(first_frame, gray)
        thresh = cv2.threshold(frame_delta, CONFIG["sensitivity"], 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)

        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        suspicious_detected = False

        for contour in contours:
            if cv2.contourArea(contour) < CONFIG["min_area"]:
                continue

            # Analizar comportamiento
            suspicious = analyze_behavior(frame)
            if suspicious:
                suspicious_detected = True
                current_time = time.time()
                if current_time - last_alert_time > CONFIG["alert_interval"]:
                    last_alert_time = current_time
                    send_alert(frame, "Alerta: Comportamiento sospechoso detectado.")

        # Mostrar el frame procesado
        cv2.imshow("Detección de Movimiento", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()

# Iniciar detección de movimiento
def start_motion_detection():
    global camera, motion_detection_thread, running
    if running:
        return
    camera = cv2.VideoCapture(0)
    running = True
    motion_detection_thread = threading.Thread(target=motion_detection_logic)
    motion_detection_thread.start()

# Detener detección de movimiento
def stop_motion_detection():
    global running, motion_detection_thread
    if not running:
        return
    running = False
    motion_detection_thread.join()
