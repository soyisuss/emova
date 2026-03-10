import cv2

def open_camera(index=0):

    cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)

    if not cap.isOpened():
        raise Exception("No se pudo abrir la cámara")

    return cap


def read_frame(cap):

    ret, frame = cap.read()

    if not ret:
        return None

    return frame