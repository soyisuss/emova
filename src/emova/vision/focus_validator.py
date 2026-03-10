import cv2

def focus_score(frame):

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    return cv2.Laplacian(gray, cv2.CV_64F).var()


def is_blurry(frame, threshold=80):

    return focus_score(frame) < threshold