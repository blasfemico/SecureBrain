import cv2
import numpy as np
import mediapipe as mp
from MSS.object_detection import detect_objects
import time

# Configuración
CONFIG = {
    "min_time_in_area": 5,
    "pose_threshold": 0.7,
    "restricted_area": (100, 100, 400, 400),  # Coordenadas del área restringida
}

# MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

def analyze_behavior(frame):
    suspicious = False
    detected_objects = detect_objects(frame)

    # Verificar si hay personas en el frame
    if "person" not in detected_objects:
        return False

    # Analizar posturas
    suspicious_pose = detect_pose(frame)
    if suspicious_pose:
        print("[ALERTA] Postura sospechosa detectada.")
        suspicious = True

    # Analizar permanencia en área restringida
    bbox = get_person_bbox(frame)
    if bbox:
        time_in_area = track_time_in_area(bbox)
        if time_in_area >= CONFIG["min_time_in_area"]:
            print(f"[ALERTA] Persona en área restringida durante {time_in_area} segundos.")
            suspicious = True

    return suspicious

def detect_pose(frame):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_frame)

    if results.pose_landmarks:
        # Detectar si alguien está agachado (ejemplo básico)
        left_knee = results.pose_landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_KNEE]
        left_ankle = results.pose_landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_ANKLE]

        if left_knee.y - left_ankle.y < 0.1:  # Umbral para detectar si está agachado
            return True
    return False

# Seguimiento del tiempo en áreas restringidas
area_time_tracker = {}

def track_time_in_area(bbox):
    x, y, w, h = bbox
    restricted_area = CONFIG["restricted_area"]

    if x > restricted_area[0] and y > restricted_area[1] and x + w < restricted_area[2] and y + h < restricted_area[3]:
        if "person" not in area_time_tracker:
            area_time_tracker["person"] = time.time()
        return time.time() - area_time_tracker["person"]
    else:
        area_time_tracker.pop("person", None)
        return 0

def get_person_bbox(frame):
    # Simulación: Bounding box estático para pruebas
    return (150, 150, 200, 200)
