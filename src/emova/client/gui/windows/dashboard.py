from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QDialog, QGridLayout, QComboBox
from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtGui import QIcon
import os
import time

from emova.client.gui.components.video_player import VideoPlayer
from emova.client.gui.components.sidebar import Sidebar
from emova.client.gui.camera_thread import CameraThread
from emova.client.gui.components.task_overlay import TaskOverlay
from emova.core.session.session_manager import session_manager

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
    go_to_load_test = Signal()

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
        btn_add_tasks.setObjectName("btnAddTasks")
        btn_add_tasks.setProperty("class", "TopActionButton")
        btn_add_tasks.clicked.connect(self.go_to_add_tasks.emit)
        
        btn_edit_tasks = QPushButton("Editar tareas")
        btn_edit_tasks.setObjectName("btnEditTasks")
        btn_edit_tasks.setProperty("class", "TopActionButton")
        btn_edit_tasks.clicked.connect(self.go_to_edit_tasks.emit)
        
        btn_register = QPushButton("Registrar participante")
        btn_register.setObjectName("btnRegisterParticipant")
        btn_register.setProperty("class", "TopActionButton")
        btn_register.clicked.connect(self.go_to_register_participant.emit)
        
        btn_repeat_test = QPushButton("Repetir configuración de prueba")
        btn_repeat_test.setObjectName("btnRepeatTest")
        btn_repeat_test.setProperty("class", "TopActionButton")
        btn_repeat_test.clicked.connect(self.go_to_load_test.emit)
        
        top_actions_layout.addWidget(btn_add_tasks)
        top_actions_layout.addWidget(btn_edit_tasks)
        top_actions_layout.addWidget(btn_register)
        top_actions_layout.addWidget(btn_repeat_test)
        top_actions_layout.addStretch()
        
        # Central Video + Overlay Stack
        self.central_video_container = QWidget()
        central_video_layout = QGridLayout(self.central_video_container)
        central_video_layout.setContentsMargins(0, 0, 0, 0)
        
        # Video Player
        self.video_player = VideoPlayer()
        
        # Task Overlay (Flotante)
        # Parent is self (DashboardView) so it doesn't get clipped by the video container
        self.task_overlay = TaskOverlay(self)
        self.task_overlay.hide() # Hidden by default
        self.task_overlay.task_started.connect(self.handle_task_started)
        self.task_overlay.task_completed.connect(self.handle_task_completed)
        self.task_overlay.task_cancelled.connect(self.handle_task_cancelled)
        
        self.current_task_index = 0
        self.current_task_start_time = 0
        
        # Agregar SOLO el video player al grid layout
        central_video_layout.addWidget(self.video_player, 0, 0)
        
        # Absolute path to assets/images
        current_dir = os.path.dirname(os.path.abspath(__file__))
        icons_dir = os.path.abspath(os.path.join(current_dir, "..", "assets", "images"))
        
        # Bottom analysis actions
        bottom_actions_layout = QHBoxLayout()
        
        camera_layout = QVBoxLayout()
        camera_layout.setSpacing(5)
        
        lbl_camera = QLabel("Seleccione la cámara que desea usar:")
        lbl_camera.setStyleSheet("color: #7E38B7; font-weight: bold; font-size: 13px;")
        
        self.camera_selector = QComboBox()
        self.camera_selector.setObjectName("comboCameraSelector")
        plus_icon_path = os.path.join(icons_dir, "plus.svg").replace("\\", "/")
        self.camera_selector.setStyleSheet(f"""
            QComboBox {{
                border: 2px solid #7E38B7;
                border-radius: 8px;
                padding: 5px 10px;
                background-color: white;
                color: #333333;
                font-weight: bold;
                font-size: 14px;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left-width: 2px;
                border-left-color: #f3e5f5;
                border-left-style: solid;
            }}
            QComboBox::down-arrow {{
                image: url({plus_icon_path});
                width: 16px;
                height: 16px;
                margin-right: -4px;
            }}
            QComboBox QAbstractItemView {{
                border: 2px solid #7E38B7;
                selection-background-color: #7E38B7;
                selection-color: white;
                color: #333333;
                background-color: white;
            }}
        """)
        self.camera_selector.setMinimumWidth(250)
        self.populate_cameras()
        
        self.btn_start_analysis = QPushButton("Iniciar análisis")
        self.btn_start_analysis.setObjectName("btnStartAnalysis")
        icon_play = QIcon(os.path.join(icons_dir, "play.png"))
        self.btn_start_analysis.setIcon(icon_play)
        self.btn_start_analysis.setProperty("class", "AnalysisButton")
        self.btn_start_analysis.clicked.connect(self.start_camera)
        
        self.btn_stop_analysis = QPushButton("Detener análisis")
        self.btn_stop_analysis.setObjectName("btnStopAnalysis")
        icon_pause = QIcon(os.path.join(icons_dir, "pausa.png"))
        self.btn_stop_analysis.setIcon(icon_pause)
        self.btn_stop_analysis.setProperty("class", "AnalysisButton")
        self.btn_stop_analysis.clicked.connect(self.stop_camera)
        self.btn_stop_analysis.setEnabled(False) # Disabled initially
        
        bottom_actions_layout.addStretch()
        
        camera_layout.addWidget(lbl_camera)
        camera_layout.addWidget(self.camera_selector)
        
        bottom_actions_layout.addLayout(camera_layout)
        bottom_actions_layout.addSpacing(10)
        
        start_layout = QVBoxLayout()
        start_layout.addWidget(self.btn_start_analysis)
        
        bottom_actions_layout.addLayout(start_layout)
        bottom_actions_layout.addSpacing(20)
        bottom_actions_layout.addWidget(self.btn_stop_analysis)
        bottom_actions_layout.addStretch()
        
        # Assembly left side
        left_layout.addLayout(top_actions_layout)
        left_layout.addWidget(self.central_video_container, stretch=1)
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
        
        # Asegurar que los recuadros flotantes siempre estén visualmente por encima del video
        self.task_overlay.raise_()

    def show_privacy_notice(self):
        dialog = PrivacyNoticeDialog(self)
        dialog.exec()
        
    def start_camera(self):
        tasks = session_manager.tasks
        if not tasks:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Atención", "Aún no se han agregado tareas. Por favor agregue tareas antes de iniciar el análisis.")
            return

        self.btn_start_analysis.setEnabled(False)
        self.btn_stop_analysis.setEnabled(True)
        self.camera_selector.setEnabled(False)
        
        idx = self.camera_selector.currentIndex()
        self.camera_thread.camera_index = idx if idx >= 0 else 0
        self.camera_thread.start()
        
        self.video_player.reset_timer()
        self.video_player.start_timer()
        
        self.current_task_index = 0
        
        # Start showing tasks directly
        self.show_current_task()
        
    def show_current_task(self):
        tasks = session_manager.tasks
        if self.current_task_index < len(tasks):
            t = tasks[self.current_task_index]
            self.task_overlay.load_task(self.current_task_index + 1, t.get("title", ""), t.get("description", ""))
            self.task_overlay.show()
            self.task_overlay.raise_()
            
            # Centrar el widget flotante respecto al central_video_container, pero relativo a self
            video_rect = self.central_video_container.geometry()
            x = video_rect.x() + (video_rect.width() - self.task_overlay.width()) // 2
            y = video_rect.y() + (video_rect.height() - self.task_overlay.height()) // 2
            self.task_overlay.move(max(0, x), max(0, y))
            
            # Time tracking starts when user clicks 'Iniciar Tarea' in handle_task_started
        else:
            self.task_overlay.hide()
            self.stop_camera()
            self.show_usability_survey()
            
    def show_usability_survey(self):
        from emova.client.gui.components.survey_dialog import UsabilitySurveyDialog
        dialog = UsabilitySurveyDialog(self.window())
        dialog.exec()
            
    def handle_task_started(self):
        self.current_task_start_time = time.time()
        if hasattr(self, 'camera_thread'):
            self.camera_thread.is_detecting = True
            
    def handle_task_completed(self):
        if hasattr(self, 'camera_thread'):
            self.camera_thread.is_detecting = False
            
        # Calculate duration and save to session manager
        duration = int(time.time() - self.current_task_start_time)
        
        # Ensure the tasks array is up to date and can hold this info
        tasks = session_manager.tasks
        if self.current_task_index < len(tasks):
            tasks[self.current_task_index]["duration_seconds"] = duration
            
        self.current_task_index += 1
        self.show_current_task()
        
    def handle_task_cancelled(self):
        if hasattr(self, 'camera_thread'):
            self.camera_thread.is_detecting = False
        self.task_overlay.hide()
        # Optionally, could also stop analysis here if cancelling a task means aborting.
        
    def stop_camera(self):
        if hasattr(self, 'camera_thread'):
            self.camera_thread.is_detecting = False
            
        self.btn_start_analysis.setEnabled(True)
        self.btn_stop_analysis.setEnabled(False)
        self.camera_selector.setEnabled(True)
        self.camera_thread.stop()
        
        self.video_player.pause_timer()
        self.task_overlay.hide()
        self.video_player.show_stopped_message()
        
    @Slot(str, float)
    def handle_emotion(self, emotion, confidence):
        # Comprobar si hay una tarea corriendo para añadirle el nombre propio
        task_title = f"Tarea {self.current_task_index + 1}"
        if hasattr(session_manager, 'tasks') and self.current_task_index < len(session_manager.tasks):
            task_title = session_manager.tasks[self.current_task_index].get("title", task_title)
            
        # Anexar seguro
        if not hasattr(session_manager, 'emotions'):
            session_manager.emotions = []
            
        session_manager.emotions.append({
            "task": task_title,
            "emotion": emotion,
            "confidence": f"{confidence * 100:.1f}%",
            "timestamp": time.strftime('%H:%M:%S')
        })

    def closeEvent(self, event):
        # Ensure thread is stopped when dashboard is closed
        if hasattr(self, 'camera_thread') and self.camera_thread.isRunning():
            self.camera_thread.stop()
        super().closeEvent(event)

    def populate_cameras(self):
        from PySide6.QtMultimedia import QMediaDevices
        cameras = QMediaDevices.videoInputs()
        if not cameras:
            self.camera_selector.addItem("Sin cámaras disponibles")
            self.camera_selector.setEnabled(False)
            self.btn_start_analysis.setEnabled(False)
            return

        for camera in cameras:
            self.camera_selector.addItem(camera.description())

