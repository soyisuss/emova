from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider
from PySide6.QtCore import Qt, Slot, QTimer
from PySide6.QtGui import QImage, QPixmap
import numpy as np

class VideoPlayer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Main video viewing area
        self.video_area = QWidget()
        self.video_area.setObjectName("VideoContainer")
        self.video_area.setMinimumSize(640, 360) # 16:9 placeholder
        self.video_area.setStyleSheet("background-color: transparent;") # Ensure no extra box
        
        video_layout = QVBoxLayout(self.video_area)
        video_layout.setContentsMargins(0, 0, 0, 0)
        
        # The actual frame display
        self.video_frame = QLabel()
        self.video_frame.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_frame.setStyleSheet("background-color: #3D404A; border-radius: 4px;")
        
        self.placeholder_text = QLabel("Iniciando cámara...")
        self.placeholder_text.setStyleSheet("color: white; font-size: 18px;")
        self.placeholder_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # We will stack them or just replace the text
        video_layout.addWidget(self.video_frame)
        self.video_frame.hide() # Hide until we get a frame
        video_layout.addWidget(self.placeholder_text)
        
        layout.addWidget(self.video_area, stretch=1)
        
        # Progress bar area
        progress_layout = QHBoxLayout()
        progress_layout.setContentsMargins(10, 5, 10, 10)
        
        self.time_start = QLabel("0:00")
        self.time_start.setStyleSheet("color: #CCCCCC; font-size: 12px;")
        
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(0)
        self.slider.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.time_end = QLabel("10:06") # Mock
        self.time_end.setStyleSheet("color: #CCCCCC; font-size: 12px;")
        
        progress_layout.addWidget(self.time_start)
        progress_layout.addWidget(self.slider)
        progress_layout.addWidget(self.time_end)
        
        layout.addLayout(progress_layout)
        
        # Timer for simulated progress
        self.timer = QTimer(self)
        self.timer.setInterval(1000) # 1 second tick
        self.timer.timeout.connect(self.update_timer)
        self.current_seconds = 0
        
    def update_timer(self):
        self.current_seconds += 1
        minutes = self.current_seconds // 60
        seconds = self.current_seconds % 60
        self.time_start.setText(f"{minutes}:{seconds:02d}")
        
        # Optionally update slider based on a fixed 10:06 length (606 seconds)
        progress = (self.current_seconds / 606.0) * 100
        self.slider.setValue(int(progress))
        
    def start_timer(self):
        self.timer.start()
        
    def pause_timer(self):
        self.timer.stop()
        
    def reset_timer(self):
        self.timer.stop()
        self.current_seconds = 0
        self.time_start.setText("0:00")
        self.slider.setValue(0)
        
        self.is_stopped = False
        # Reset placeholder text
        self.placeholder_text.setStyleSheet("color: white; font-size: 18px; background-color: transparent;")
        self.placeholder_text.setText("Iniciando cámara...")
        self.video_frame.hide()
        self.placeholder_text.show()

    def show_stopped_message(self):
        """Displays a stopped message when the camera stream is aborted."""
        self.is_stopped = True
        self.video_frame.clear()
        self.video_frame.hide()
        
        # Display large white block spanning the layout
        self.placeholder_text.setStyleSheet("background-color: white; color: black; font-size: 24px; border-radius: 4px;")
        self.placeholder_text.setText("Análisis detenido")
        self.placeholder_text.show()
        
    @Slot(np.ndarray)
    def update_frame(self, frame):
        """Update the displayed image with a new OpenCV frame"""
        if getattr(self, 'is_stopped', False):
            return
            
        if self.placeholder_text.isVisible():
            self.placeholder_text.hide()
            self.video_frame.show()
            
        # Convert BGR (OpenCV) to RGB (Qt)
        rgb_image = frame[..., ::-1].copy()
        
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        
        # Scale to fit label while maintaining aspect ratio
        pixmap = QPixmap.fromImage(qt_image)
        scaled_pixmap = pixmap.scaled(self.video_frame.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        
        self.video_frame.setPixmap(scaled_pixmap)
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # We probably want to keep the aspect ratio when the container resizes 
        # but the QLabel handles it if we recalculate the pixmap. 
        # For simplicity, we just rely on the next frame update to correct size.
