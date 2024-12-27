import cv2
import numpy as np
import logging
import os

# Configuración del sistema de logs
log_folder = "logs"
os.makedirs(log_folder, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_folder, "object_detection.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG = {
    "model_weights": os.path.join(BASE_DIR, "models", "yolov4.weights"),
    "model_config": os.path.join(BASE_DIR, "models", "yolov4.cfg"),
    "labels": os.path.join(BASE_DIR, "models", "coco.names"),
}

def load_model():
    net = cv2.dnn.readNetFromDarknet(CONFIG["model_config"], CONFIG["model_weights"])
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
    return net, net.getUnconnectedOutLayersNames()

def detect_objects(frame):
    net, output_layers = load_model()
    blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    outputs = net.forward(output_layers)

    labels = open(CONFIG["labels"]).read().strip().split("\n")
    detected_objects = []

    for output in outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                detected_objects.append(labels[class_id])
                logging.info(f"Objeto detectado: {labels[class_id]} (Confianza: {confidence:.2f})")

    if not detected_objects:
        logging.info("No se detectaron objetos relevantes en el frame.")

    return detected_objects
