from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider
from PySide6.QtCore import Qt, Slot, QTimer
from PySide6.QtGui import QImage, QPixmap
import numpy as np

class VideoPlayer(QWidget):
    """
    Componente reproductor de video. Muestra la transmisión de la cámara en vivo
    con superposiciones visuales y administra la barra de progreso de tiempo.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Área principal de visualización de video
        self.video_area = QWidget()
        self.video_area.setObjectName("VideoContainer")
        self.video_area.setMinimumSize(640, 360) # Marcador de posición de proporción 16:9
        self.video_area.setStyleSheet("background-color: transparent;") # Asegurar que no haya un recuadro adicional
        
        video_layout = QVBoxLayout(self.video_area)
        video_layout.setContentsMargins(0, 0, 0, 0)
        
        # Visualización del fotograma actual
        self.video_frame = QLabel()
        self.video_frame.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_frame.setStyleSheet("background-color: #3D404A; border-radius: 4px;")
        
        self.placeholder_text = QLabel("Bienvenido a EMOVA\n\n1. Seleccione una cámara en el panel inferior.\n2. Presione 'Iniciar análisis'.\n3. Siga las instrucciones de las tareas.")
        self.placeholder_text.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        self.placeholder_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Los apilamos o simplemente reemplazamos el texto
        video_layout.addWidget(self.video_frame)
        self.video_frame.hide() # Ocultar hasta obtener un fotograma
        video_layout.addWidget(self.placeholder_text)
        
        layout.addWidget(self.video_area, stretch=1)
        
        # Área de barra de progreso
        progress_layout = QHBoxLayout()
        progress_layout.setContentsMargins(10, 5, 10, 10)
        
        self.time_start = QLabel("0:00")
        self.time_start.setStyleSheet("color: #CCCCCC; font-size: 12px;")
        
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(0)
        self.slider.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.time_end = QLabel("10:06") # Simulación de tiempo final
        self.time_end.setStyleSheet("color: #CCCCCC; font-size: 12px;")
        
        progress_layout.addWidget(self.time_start)
        progress_layout.addWidget(self.slider)
        progress_layout.addWidget(self.time_end)
        
        layout.addLayout(progress_layout)
        
        # Temporizador para simular el progreso
        self.timer = QTimer(self)
        self.timer.setInterval(1000) # Intervalo de 1 segundo
        self.timer.timeout.connect(self.update_timer)
        self.current_seconds = 0
        
    def update_timer(self):
        self.current_seconds += 1
        minutes = self.current_seconds // 60
        seconds = self.current_seconds % 60
        self.time_start.setText(f"{minutes}:{seconds:02d}")
        
        # Opcionalmente actualiza el control deslizante basándose en una duración fija de 10:06 (606 segundos)
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
        # Restablecer texto del marcador de posición
        self.placeholder_text.setStyleSheet("color: white; font-size: 20px; background-color: transparent; font-weight: bold;")
        self.placeholder_text.setText("Bienvenido a EMOVA\n\n1. Seleccione una cámara en el panel inferior.\n2. Presione 'Iniciar análisis'.\n3. Siga las instrucciones de las tareas.")
        self.video_frame.hide()
        self.placeholder_text.show()
 
    def show_stopped_message(self):
        """Muestra un mensaje de detenido cuando se aborta la transmisión de la cámara."""
        self.is_stopped = True
        self.video_frame.clear()
        self.video_frame.hide()
        
        # Muestra un bloque grande blanco a lo largo del diseño
        self.placeholder_text.setStyleSheet("background-color: white; color: black; font-size: 24px; border-radius: 4px;")
        self.placeholder_text.setText("Análisis detenido")
        self.placeholder_text.show()
        
    @Slot(np.ndarray)
    def update_frame(self, frame):
        """Actualiza la imagen mostrada con un nuevo fotograma de OpenCV."""
        if getattr(self, 'is_stopped', False):
            return
            
        if self.placeholder_text.isVisible():
            self.placeholder_text.hide()
            self.video_frame.show()
            
        # Convertir BGR (OpenCV) a RGB (Qt)
        rgb_image = frame[..., ::-1].copy()
        
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        
        # Escalar para ajustar a la etiqueta manteniendo la relación de aspecto
        pixmap = QPixmap.fromImage(qt_image)
        scaled_pixmap = pixmap.scaled(self.video_frame.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        
        self.video_frame.setPixmap(scaled_pixmap)
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Probablemente deseamos mantener la relación de aspecto cuando el contenedor cambie de tamaño,
        # pero el QLabel se encarga de esto si recalculamos el pixmap.
        # Por simplicidad, confiamos en la siguiente actualización del fotograma para corregir el tamaño.

