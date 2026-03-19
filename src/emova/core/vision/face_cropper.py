def crop_face(frame, box):
    h, w = frame.shape[:2]
    x1, y1, x2, y2 = box

    # Asegurar que los límites estén dentro de la imagen
    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = min(w, x2)
    y2 = min(h, y2)

    face = frame[y1:y2, x1:x2]

    return face