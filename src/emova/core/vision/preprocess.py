import cv2
import numpy as np

def preprocess(image):

    image = cv2.resize(image, (224,224))

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    image = image / 255.0

    return image