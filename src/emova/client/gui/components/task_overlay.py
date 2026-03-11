from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QSizePolicy
from PySide6.QtCore import Qt, Signal

class TaskOverlay(QFrame):
    task_started = Signal()
    task_completed = Signal()
    task_cancelled = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TaskOverlay")
        self.setStyleSheet("""
            QFrame#TaskOverlay {
                background-color: white;
                border-radius: 8px;
                border: 2px solid #E0E0E0;
            }
        """)
        
        # Center the overlay, ensure it doesn't take up the whole screen
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(400, 300)
        self.setMaximumSize(600, 400)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)
        
        # Title
        self.title_label = QLabel("Tarea 1: Titulo de la tarea")
        self.title_label.setObjectName("ViewTitle") # Reusing purple title style
        self.title_label.setStyleSheet("color: #7E38B7; font-weight: bold; font-size: 24px;")
        self.title_label.setWordWrap(True)
        
        # Description
        desc_title = QLabel("Descripción:")
        desc_title.setStyleSheet("font-weight: bold; font-size: 16px;")
        
        self.desc_label = QLabel("...")
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet("font-size: 16px; color: #333;")
        self.desc_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        # We simulate lines with a styled widget or just rely on text wrapping
        # A simple frame with a bottom border could simulate lines if we really want,
        # but standard label wrapping is cleaner.
        
        desc_layout = QVBoxLayout()
        desc_layout.addWidget(desc_title)
        desc_layout.addWidget(self.desc_label, stretch=1)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)
        
        self.btn_action = QPushButton("Iniciar Tarea")
        self.btn_action.setProperty("class", "PrimaryButton")
        self.btn_action.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_action.clicked.connect(self.handle_action_click)
        
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.setProperty("class", "PrimaryButton") # Assuming it gets styled purple too, maybe we should reuse a different class if needed, but styling seems to use same box.
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.clicked.connect(self.task_cancelled.emit)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_action)
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addStretch()
        
        # Assemble
        main_layout.addWidget(self.title_label)
        main_layout.addLayout(desc_layout, stretch=1)
        main_layout.addLayout(btn_layout)
        
        self.state = "INIT" # "INIT" or "STARTED"
        
    def load_task(self, task_number, title, description):
        self.title_label.setText(f"Tarea {task_number}: {title}")
        self.desc_label.setText(description)
        self.reset_state()
        
    def reset_state(self):
        self.state = "INIT"
        self.btn_action.setText("Iniciar Tarea")
        self.btn_action.setStyleSheet("") # Clear any custom inline styles if needed
        
    def handle_action_click(self):
        if self.state == "INIT":
            self.state = "STARTED"
            self.btn_action.setText("Completar Tarea")
            # Could change style to green or keep it primary
            self.task_started.emit()
        elif self.state == "STARTED":
            self.task_completed.emit()
