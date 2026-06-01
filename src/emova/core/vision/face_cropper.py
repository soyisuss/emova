"""
Módulo para el recorte de regiones de interés (rostros) en fotogramas de video.
"""

def crop_face(frame, box):
    """
    Recorta el rostro detectado dentro del fotograma utilizando las coordenadas de la caja delimitadora.
    Asegura que los límites no excedan las dimensiones de la imagen.
    """
    h, w = frame.shape[:2]
    x1, y1, x2, y2 = box

    # Asegurar que los límites estén dentro de la imagen
    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = min(w, x2)
    y2 = min(h, y2)

    face = frame[y1:y2, x1:x2]

    return face