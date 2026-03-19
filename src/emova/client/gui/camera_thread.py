import os
import cv2
import numpy as np
from PySide6.QtCore import QThread, Signal
from emova.core.capture.camera import open_source, read_frame
from emova.core.capture.fps_sampler import FPSSampler
from emova.core.model.emotion_predictor import predict_emotion
from emova.core.vision.face_detector import FaceDetector
from emova.core.vision.pipeline import VideoPreprocessingPipeline

class CameraThread(QThread):
    # Signals to emit frames and prediction data back to the main UI thread
    frame_ready = Signal(np.ndarray)
    emotion_ready = Signal(str, float)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_running = False
        self.cap = None
        self.sampler = FPSSampler(3) # Process every 3rd frame
        
        # Inicializar pipeline de preprocesamiento
        proto = os.path.join("models", "deploy.prototxt")
        model = os.path.join("models", "res10_300x300_ssd_iter_140000_fp16.caffemodel")
        
        try:
            self.detector = FaceDetector(proto, model)
            self.pipeline = VideoPreprocessingPipeline(self.detector)
        except Exception as e:
            print(f"Error inicializando pipeline (modelos posiblemente faltantes): {e}")
            self.pipeline = None
        
    def run(self):
        self._is_running = True
        self.cap = open_source(0)
        
        while self._is_running:
            frame = read_frame(self.cap)
            
            if frame is None:
                continue
                
            display_frame = frame.copy()
            
            if self.pipeline:
                results = self.pipeline.process_frame(frame)
                
                # Dibujar recuadros en los rostros detectados
                for res in results:
                    x1, y1, x2, y2 = res['box']
                    cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    
                # Predecir sólo si es momento en base al sampleo y si hay caras
                if len(results) > 0 and self.sampler.should_process():
                    # Para la UI, tomamos el primer rostro por ahora
                    tensor = results[0]['face_tensor']
                    emotion, conf = predict_emotion(tensor)
                    self.emotion_ready.emit(emotion, conf)
            else:
                # Comportamiento de emergencia si falla el pipeline
                if self.sampler.should_process():
                    emotion, conf = predict_emotion(frame)
                    self.emotion_ready.emit(emotion, conf)

            # Emitir para la vista en el VideoPlayer
            self.frame_ready.emit(display_frame)
            
            # Sleep slightly to allow thread switching (~33fps)
            self.msleep(30)
            
        if self.cap is not None:
            self.cap.release()
            
    def stop(self):
        self._is_running = False
        self.wait() # Block until thread finishes
