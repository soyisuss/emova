"""
Módulo para la captura de fotogramas desde la cámara web o fuentes de video utilizando OpenCV.
"""
import cv2

def open_source(source=0):
    """
    Abre la cámara web (usando DirectShow en Windows para carga rápida) o un archivo de video.
    """
    if isinstance(source, int):
        cap = cv2.VideoCapture(source, cv2.CAP_DSHOW)
    else:
        cap = cv2.VideoCapture(source)

    if not cap.isOpened():
        raise Exception(f"No se pudo abrir la fuente de video: {source}")

    return cap


def read_frame(cap):
    """
    Lee un único fotograma de la fuente de captura de video abierta.
    Retorna None si la captura finalizó o falló.
    """
    ret, frame = cap.read()

    if not ret:
        return None

    return frame