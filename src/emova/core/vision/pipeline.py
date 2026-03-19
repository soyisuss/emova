import numpy as np
from typing import List, Dict, Any, Generator

from emova.core.capture.camera import read_frame
from emova.core.vision.face_detector import FaceDetector
from emova.core.vision.focus_validator import focus_score
from emova.core.vision.face_cropper import crop_face
from emova.core.vision.preprocess import preprocess

class VideoPreprocessingPipeline:
    def __init__(self, face_detector: FaceDetector, focus_threshold: float = 80.0):
        self.face_detector = face_detector
        self.focus_threshold = focus_threshold
        
    def process_frame(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Procesa un solo frame y sigue el pipeline detallado:
        1. 4.7.3 Verificación del enfoque (Laplaciano)
        2. 4.7.2 Detección de rostros (DNN SSD)
        3. 4.7.4 Recorte del rostro
        4. 4.7.5 & 4.7.6 Redimensionamiento y Normalización
        
        Devuelve una lista de diccionarios con la data de cada rostro procesado.
        """
        results = []
        
        # 1. Verificar Enfoque
        score = focus_score(frame)
        if score < self.focus_threshold:
            # Si el frame está borroso, no extraemos rostros para predicción de emoción.
            return results
            
        # 2. Detección de Rostros
        faces_boxes = self.face_detector.get_faces(frame)
        
        for box in faces_boxes:
            # 3. Recorte del Rostro
            face_img = crop_face(frame, box)
            
            # Prevenir recorte inválido si las coordenadas fueran erróneas (ya validadas pero por seguridad)
            if face_img.size == 0:
                continue
                
            # 4. Redimensionar (Bilineal) y Normalizar (ImageNet stats)
            processed_face = preprocess(face_img)
            
            results.append({
                "box": box,
                "face_tensor": processed_face,
                "focus_score": score
            })
            
        return results

    def process_video_stream(self, cap) -> Generator[List[Dict[str, Any]], None, None]:
        """
        4.7.1 Captura de video
        Aplica el procesamiento frame por frame al objeto de captura (cámara o video).
        """
        while True:
            frame = read_frame(cap)
            if frame is None:
                break
                
            yield self.process_frame(frame)
