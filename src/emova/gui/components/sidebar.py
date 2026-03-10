from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
import os

class Sidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(150)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Absolute path to assets/images
        current_dir = os.path.dirname(os.path.abspath(__file__))
        icons_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "..", "..", "assets", "images"))
        
        # Generar reporte
        lbl_generate = QLabel("Generar reporte")
        lbl_generate.setProperty("class", "SidebarLabel")
        lbl_generate.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        btn_generate = QPushButton()
        icon_generate = QIcon(os.path.join(icons_dir, "archivo.png"))
        btn_generate.setIcon(icon_generate)
        btn_generate.setIconSize(QSize(40, 40))
        btn_generate.setProperty("class", "SidebarButton")
        btn_generate.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout.addWidget(lbl_generate)
        layout.addWidget(btn_generate)
        
        # Descargar reporte
        lbl_download = QLabel("Desacargar reporte")
        lbl_download.setProperty("class", "SidebarLabel")
        lbl_download.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        btn_download = QPushButton()
        icon_download = QIcon(os.path.join(icons_dir, "guardar.png"))
        btn_download.setIcon(icon_download)
        btn_download.setIconSize(QSize(40, 40))
        btn_download.setProperty("class", "SidebarButton")
        btn_download.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout.addWidget(lbl_download)
        layout.addWidget(btn_download)
        
        # Historial de reportes
        lbl_history = QLabel("Historial de reportes")
        lbl_history.setProperty("class", "SidebarLabel")
        lbl_history.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        btn_history = QPushButton()
        icon_history = QIcon(os.path.join(icons_dir, "historial.png"))
        btn_history.setIcon(icon_history)
        btn_history.setIconSize(QSize(40, 40))
        btn_history.setProperty("class", "SidebarButton")
        btn_history.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout.addWidget(lbl_history)
        layout.addWidget(btn_history)

