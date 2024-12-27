import cv2
import numpy as np
import mediapipe as mp
from MSS.object_detection import detect_objects
import logging
import time
import os

# Configuración del sistema de logs
log_folder = "logs"
os.makedirs(log_folder, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_folder, "behavior_analysis.log"),
    level=logging.DEBUG,  # Cambiado a DEBUG para más detalles
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Configuración
CONFIG = {
    "min_time_in_area": 5,  # Tiempo mínimo para considerar comportamiento sospechoso
}

# MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

def analyze_behavior(frame):
    suspicious = False
    detected_objects = detect_objects(frame)

    if "person" not in detected_objects:
        logging.info("No se detectaron personas en el frame.")
        print("No se detectaron personas en el frame.")
        return False

    logging.info("Persona detectada. Analizando comportamiento en todo el rango de la cámara...")
    print("Persona detectada. Analizando comportamiento en todo el rango de la cámara...")

    # Analizar posturas
    suspicious_pose = detect_pose(frame)
    if suspicious_pose:
        logging.warning("Postura sospechosa detectada (agachado o inusual).")
        print("Postura sospechosa detectada (agachado o inusual).")
        suspicious = True

    # Analizar permanencia en el rango completo de la cámara
    time_in_view = track_time_in_view()
    if time_in_view >= CONFIG["min_time_in_area"]:
        logging.warning(f"Persona visible durante {time_in_view:.2f} segundos. Comportamiento sospechoso confirmado.")
        print(f"Persona visible durante {time_in_view:.2f} segundos. Comportamiento sospechoso confirmado.")
        suspicious = True

    return suspicious

def detect_pose(frame):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_frame)

    if results.pose_landmarks:
        # Detectar si alguien está agachado
        left_knee = results.pose_landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_KNEE]
        left_ankle = results.pose_landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_ANKLE]

        if left_knee.y - left_ankle.y < 0.1:
            logging.info("Persona detectada en posición agachada.")
            print("Persona detectada en posición agachada.")
            return True
    return False

# Seguimiento del tiempo en el rango completo de la cámara
time_in_view_tracker = {}

def track_time_in_view():
    if "person" not in time_in_view_tracker:
        time_in_view_tracker["person"] = time.time()
    return time.time() - time_in_view_tracker["person"]
