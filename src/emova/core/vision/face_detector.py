import cv2
import numpy as np

class FaceDetector:

    def __init__(self, proto, model):

        self.net = cv2.dnn.readNetFromCaffe(proto, model)


    def detect(self, frame):
        # ... (la misma implementación de detect si se quiere mantener)
        blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104, 177, 123))
        self.net.setInput(blob)
        return self.net.forward()

    def get_faces(self, frame, confidence_threshold=0.6):
        """
        Detecta rostros usando el modelo SSD y devuelve las coordenadas de los bounding boxes.
        """
        h, w = frame.shape[:2]
        detections = self.detect(frame)
        
        faces = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > confidence_threshold:
                # Coordenadas relativas multiplicadas por ancho y alto reales
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                faces.append((startX, startY, endX, endY))
        return faces