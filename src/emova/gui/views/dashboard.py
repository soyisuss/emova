from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QDialog
from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtGui import QIcon
import os

from emova.gui.components.video_player import VideoPlayer
from emova.gui.components.sidebar import Sidebar
from emova.gui.camera_thread import CameraThread

class PrivacyNoticeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PrivacyDialog")
        self.setFixedSize(500, 350)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        title = QLabel("Aviso de Privacidad y Uso de Datos")
        title.setObjectName("PrivacyTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        text = QLabel(
            "El sistema recolecta únicamente los datos necesarios para la "
            "prueba de usabilidad, incluyendo información general y "
            "expresiones faciales procesadas en tiempo real. No se "
            "almacenan videos y los datos se usan solo con fines "
            "académicos y de análisis. La información no se comparte con "
            "terceros y se protege conforme a la Ley Federal de Protección "
            "de Datos Personales en Posesión de los Particulares "
            "(LFPDPPP). Al participar, el usuario acepta este uso."
        )
        text.setObjectName("PrivacyText")
        text.setWordWrap(True)
        text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)
        
        btn_accept = QPushButton("Aceptar aviso")
        btn_accept.setProperty("class", "DialogButton")
        btn_accept.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_accept.clicked.connect(self.accept)
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setProperty("class", "DialogButton")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(btn_accept)
        btn_layout.addWidget(btn_cancel)
        
        layout.addWidget(title)
        layout.addWidget(text)
        layout.addLayout(btn_layout)


class DashboardView(QWidget):
    go_to_add_tasks = Signal()
    go_to_edit_tasks = Signal()
    go_to_register_participant = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Left side containing top actions, video, and bottom actions
        left_layout = QVBoxLayout()
        left_layout.setSpacing(20)
        
        # Top actions
        top_actions_layout = QHBoxLayout()
        top_actions_layout.setSpacing(15)
        
        btn_add_tasks = QPushButton("Agregar tareas")
        btn_add_tasks.setProperty("class", "TopActionButton")
        btn_add_tasks.clicked.connect(self.go_to_add_tasks.emit)
        
        btn_edit_tasks = QPushButton("Editar Tareas")
        btn_edit_tasks.setProperty("class", "TopActionButton")
        btn_edit_tasks.clicked.connect(self.go_to_edit_tasks.emit)
        
        btn_register = QPushButton("Registrar participante")
        btn_register.setProperty("class", "TopActionButton")
        btn_register.clicked.connect(self.go_to_register_participant.emit)
        
        btn_new_test = QPushButton("Nueva Prueba de Usabilidad")
        btn_new_test.setProperty("class", "TopActionButton")
        
        top_actions_layout.addWidget(btn_add_tasks)
        top_actions_layout.addWidget(btn_edit_tasks)
        top_actions_layout.addWidget(btn_register)
        top_actions_layout.addWidget(btn_new_test)
        top_actions_layout.addStretch()
        
        # Connect specific actions to our mockups
        btn_new_test.clicked.connect(self.show_privacy_notice)
        
        # Video Player
        self.video_player = VideoPlayer()
        
        # Absolute path to assets/images
        current_dir = os.path.dirname(os.path.abspath(__file__))
        icons_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "..", "..", "assets", "images"))
        
        # Bottom analysis actions
        bottom_actions_layout = QHBoxLayout()
        
        self.btn_start_analysis = QPushButton(" Iniciar análisis")
        icon_play = QIcon(os.path.join(icons_dir, "play.png"))
        self.btn_start_analysis.setIcon(icon_play)
        self.btn_start_analysis.setProperty("class", "AnalysisButton")
        self.btn_start_analysis.clicked.connect(self.start_camera)
        
        self.btn_stop_analysis = QPushButton(" Detener Análisis")
        icon_pause = QIcon(os.path.join(icons_dir, "pausa.png"))
        self.btn_stop_analysis.setIcon(icon_pause)
        self.btn_stop_analysis.setProperty("class", "AnalysisButton")
        self.btn_stop_analysis.clicked.connect(self.stop_camera)
        self.btn_stop_analysis.setEnabled(False) # Disabled initially
        
        bottom_actions_layout.addStretch()
        bottom_actions_layout.addWidget(self.btn_start_analysis)
        bottom_actions_layout.addSpacing(20)
        bottom_actions_layout.addWidget(self.btn_stop_analysis)
        bottom_actions_layout.addStretch()
        
        # Assembly left side
        left_layout.addLayout(top_actions_layout)
        left_layout.addWidget(self.video_player, stretch=1)
        left_layout.addLayout(bottom_actions_layout)
        
        # Right Sidebar
        self.sidebar = Sidebar()
        
        # Assemble overall
        main_layout.addLayout(left_layout, stretch=1)
        main_layout.addWidget(self.sidebar)
        
        # Initialize camera thread
        self.camera_thread = CameraThread()
        self.camera_thread.frame_ready.connect(self.video_player.update_frame)
        self.camera_thread.emotion_ready.connect(self.handle_emotion)

    def show_privacy_notice(self):
        dialog = PrivacyNoticeDialog(self)
        dialog.exec()
        
    def start_camera(self):
        self.btn_start_analysis.setEnabled(False)
        self.btn_stop_analysis.setEnabled(True)
        self.camera_thread.start()
        
    def stop_camera(self):
        self.btn_start_analysis.setEnabled(True)
        self.btn_stop_analysis.setEnabled(False)
        self.camera_thread.stop()
        
    @Slot(str, float)
    def handle_emotion(self, emotion, confidence):
        # We can implement visual updates for emotion prediction here later
        pass

    def closeEvent(self, event):
        # Ensure thread is stopped when dashboard is closed
        if hasattr(self, 'camera_thread') and self.camera_thread.isRunning():
            self.camera_thread.stop()
        super().closeEvent(event)
