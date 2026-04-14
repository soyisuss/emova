import os
import random
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QSizePolicy
from PySide6.QtCore import Qt, Signal, QTimer, QPoint
from PySide6.QtGui import QPixmap

from emova.core.session.session_manager import session_manager

class CalibrationOverlay(QFrame):
    calibration_completed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("CalibrationOverlay")
        self.setStyleSheet("""
            QFrame#CalibrationOverlay {
                background-color: white;
                border-radius: 8px;
                border: 2px solid #7E38B7;
            }
        """)
        
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setFixedSize(600, 500)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(25, 25, 25, 25)
        self.main_layout.setSpacing(15)
        
        self.title_label = QLabel("Calibrando...")
        self.title_label.setObjectName("ViewTitle")
        self.title_label.setStyleSheet("color: #7E38B7; font-weight: bold; font-size: 22px;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.desc_label = QLabel("Por favor, observe la siguiente imagen.")
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet("font-size: 16px; color: #333;")
        self.desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("background-color: #EEE; border-radius: 4px;")
        self.image_label.setFixedSize(400, 300)
        self.image_label.setScaledContents(True)
        
        self.status_label = QLabel("Preparando...")
        self.status_label.setStyleSheet("font-size: 16px; color: #666; margin-top: 10px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        
        self.main_layout.addWidget(self.title_label)
        self.main_layout.addWidget(self.desc_label)
        self.main_layout.addWidget(self.image_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.status_label)
        
        self.current_phase = "" # "positive" or "negative"
        self.latest_emotion = None
        self.latest_confidence = 0.0
        
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.capture_and_next)
        
        # Paths to images
        base_dir = os.getcwd()
        self.pos_dir = os.path.join(base_dir, "docs", "CALIBRACION", "POSITIVO")
        self.neg_dir = os.path.join(base_dir, "docs", "CALIBRACION", "NEGATIVO")
        
    def start_calibration(self):
        self.show()
        self.raise_()
        self.load_phase("positive")
        
    def update_latest_emotion(self, emotion, confidence):
        # Called constantly from dashboard via camera_thread
        self.latest_emotion = emotion
        self.latest_confidence = confidence
        
    def load_phase(self, phase):
        self.current_phase = phase
        self.latest_emotion = None # reset
        directory = self.pos_dir if phase == "positive" else self.neg_dir
        
        try:
            images = [f for f in os.listdir(directory) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if images:
                selected_image = random.choice(images)
                pixmap = QPixmap(os.path.join(directory, selected_image))
                self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation))
            else:
                self.image_label.setText(f"Sin imágenes en {phase}")
        except Exception as e:
            self.image_label.setText("Error cargando imagen")
            print(f"Error cargando imágenes para la calibración: {e}")
            
        self.status_label.setText("Por favor, espere un momento mientras capturamos sus expresiones faciales.")
        self.status_label.setStyleSheet("color: #E67E22; font-weight: bold; font-size: 16px;")
        
        # Wait 5 seconds
        self.timer.start(5000)
        
    def capture_and_next(self):
        self.status_label.setText("¡Capturado!")
        self.status_label.setStyleSheet("color: #27AE60; font-weight: bold;")
        
        # Store in SessionManager 
        if self.latest_emotion:
            session_manager.set_calibration(
                self.current_phase, 
                self.latest_emotion, 
                self.latest_confidence
            )
        else:
            # Fallback if no emotion was detected during that time
            session_manager.set_calibration(self.current_phase, "Desconocido", 0.0)
            
        if self.current_phase == "positive":
            # Proceder a imagen negativa
            QTimer.singleShot(1000, lambda: self.load_phase("negative"))
        else:
            # Finalizado
            QTimer.singleShot(1000, self.finish_calibration)
            
    def finish_calibration(self):
        self.hide()
        self.calibration_completed.emit()
