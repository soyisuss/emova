import cv2
import numpy as np

def preprocess(image):
    # 4.7.5 Redimensionamiento: Interpolación Bilineal a 224x224
    image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_LINEAR)

    # Convertir a RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # 4.7.6 Normalización (Estadísticas ImageNet)
    image = image.astype(np.float32) / 255.0
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    
    image = (image - mean) / std

    # Retornamos formato CHW (opcionalmente) o HWC, usualmente PyTorch expects CHW
    image = np.transpose(image, (2, 0, 1))

    return image