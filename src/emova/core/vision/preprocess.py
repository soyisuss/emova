"""
Módulo para el preprocesamiento de imágenes faciales antes de la inferencia del modelo.
"""
import cv2
import numpy as np

def preprocess(image):
    """
    Preprocesa una imagen facial: redimensiona a 224x224, convierte a RGB,
    normaliza con estadísticas de ImageNet y cambia el formato a CHW.
    """
    # 4.7.5 Redimensionamiento: Interpolación Bilineal a 224x224
    image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_LINEAR)

    # Convertir a RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # 4.7.6 Normalización (Estadísticas ImageNet)
    image = image.astype(np.float32) / 255.0
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    
    image = (image - mean) / std

    # Retornamos en formato CHW, el cual es esperado por el modelo de IA
    image = np.transpose(image, (2, 0, 1))

    return image
