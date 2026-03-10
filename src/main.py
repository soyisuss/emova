import sys
import os
import cv2
from PySide6.QtWidgets import QApplication
from emova.gui.main_window import MainWindow

# Backend imports kept for future integration
# from emova.capture.camera import open_camera, read_frame
# from emova.capture.fps_sampler import FPSSampler
# from emova.model.emotion_predictor import predict_emotion

def main():
    app = QApplication(sys.argv)
    
    # Load stylesheet
    style_path = os.path.join(os.path.dirname(__file__), "emova", "gui", "resources", "style.qss")
    if os.path.exists(style_path):
        with open(style_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    else:
        print(f"Warning: Stylesheet not found at {style_path}")
        
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()