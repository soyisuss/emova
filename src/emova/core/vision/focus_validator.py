"""
Módulo para validación del enfoque de los fotogramas (detección de borrosidad).
"""
import cv2

def focus_score(frame):
    """
    Calcula el puntaje de enfoque de un fotograma utilizando la varianza del Laplaciano.
    Un valor bajo indica que la imagen está borrosa.
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Retorna la varianza del operador Laplaciano
    return cv2.Laplacian(gray, cv2.CV_64F).var()


def is_blurry(frame, threshold=80):
    """
    Determina si un fotograma está borroso comparando su puntaje de enfoque con un umbral.
    """
    return focus_score(frame) < threshold