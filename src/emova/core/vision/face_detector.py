import cv2
import numpy as np

class FaceDetector:

    def __init__(self, proto, model):

        self.net = cv2.dnn.readNetFromCaffe(proto, model)


    def detect(self, frame):

        h, w = frame.shape[:2]

        blob = cv2.dnn.blobFromImage(
            frame,
            1.0,
            (300,300),
            (104,177,123)
        )

        self.net.setInput(blob)

        detections = self.net.forward()

        return detections