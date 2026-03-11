def crop_face(frame, box):

    x1, y1, x2, y2 = box

    face = frame[y1:y2, x1:x2]

    return face