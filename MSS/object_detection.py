import cv2
import numpy as np

CONFIG = {
    "model_weights": "./models/yolov4.weights",
    "model_config": "./models/yolov4.cfg",
    "labels": "./models/coco.names",
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

    return detected_objects
