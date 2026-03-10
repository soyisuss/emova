import cv2
import numpy as np
from PySide6.QtCore import QThread, Signal
from emova.capture.camera import open_camera, read_frame
from emova.capture.fps_sampler import FPSSampler
from emova.model.emotion_predictor import predict_emotion

class CameraThread(QThread):
    # Signals to emit frames and prediction data back to the main UI thread
    frame_ready = Signal(np.ndarray)
    emotion_ready = Signal(str, float)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_running = False
        self.cap = None
        self.sampler = FPSSampler(3) # Process every 3rd frame just like old main.py
        
    def run(self):
        self._is_running = True
        self.cap = open_camera()
        
        while self._is_running:
            frame = read_frame(self.cap)
            
            if frame is None:
                continue
                
            # Emit the raw frame for the video player FIRST
            self.frame_ready.emit(frame)
            
            # Predict only on sampled frames
            if self.sampler.should_process():
                emotion, conf = predict_emotion(frame)
                self.emotion_ready.emit(emotion, conf)
                
            # Sleep slightly to allow thread switching. QThread.msleep(30) is ~33fps
            self.msleep(30)
            
        if self.cap is not None:
            self.cap.release()
            
    def stop(self):
        self._is_running = False
        self.wait() # Block until thread finishes
