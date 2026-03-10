from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider
from PySide6.QtCore import Qt, Slot
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
        
    @Slot(np.ndarray)
    def update_frame(self, frame):
        """Update the displayed image with a new OpenCV frame"""
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
