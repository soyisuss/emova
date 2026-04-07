from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QSizePolicy
from PySide6.QtCore import Qt, Signal, QPoint

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
        
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(450, 250)
        self.setMaximumSize(800, 600)  # Aumentado para no cortar textos largos
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(25, 25, 25, 25) # Márgenes reducidos para dar más espacio
        self.main_layout.setSpacing(15)
        
        # Title bar with minimize button
        title_layout = QHBoxLayout()
        self.title_label = QLabel("Tarea 1: Titulo de la tarea")
        self.title_label.setObjectName("ViewTitle")
        self.title_label.setStyleSheet("color: #7E38B7; font-weight: bold; font-size: 24px;")
        self.title_label.setWordWrap(True)
        
        self.btn_toggle = QPushButton("-")
        self.btn_toggle.setFixedSize(30, 30)
        self.btn_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle.setStyleSheet("""
            QPushButton {
                background-color: #E0E0E0; border-radius: 15px; 
                color: black; font-weight: bold; font-size: 18px; padding-bottom: 2px;
            }
            QPushButton:hover { background-color: #D0D0D0; }
        """)
        self.btn_toggle.clicked.connect(self.toggle_minimize)
        
        title_layout.addWidget(self.title_label, stretch=1)
        title_layout.addWidget(self.btn_toggle)
        
        # Container for hidable content
        self.content_widget = QWidget()
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        self.desc_title = QLabel("Descripción:")
        self.desc_title.setStyleSheet("font-weight: bold; font-size: 16px;")
        
        self.desc_label = QLabel("...")
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet("font-size: 16px; color: #333;")
        self.desc_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        content_layout.addWidget(self.desc_title)
        content_layout.addWidget(self.desc_label, stretch=1)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)
        
        self.btn_action = QPushButton("Iniciar Tarea")
        self.btn_action.setProperty("class", "DialogButton")
        self.btn_action.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_action.setMinimumWidth(140)
        self.btn_action.clicked.connect(self.handle_action_click)
        
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.setProperty("class", "DialogButton")
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.setMinimumWidth(140)
        self.btn_cancel.clicked.connect(self.task_cancelled.emit)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_action)
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addStretch()
        
        content_layout.addLayout(btn_layout)
        
        self.main_layout.addLayout(title_layout)
        self.main_layout.addWidget(self.content_widget, stretch=1)
        
        self.state = "INIT"
        self.is_minimized = False
        
        # Drag coordinates
        self._drag_pos = None

    def toggle_minimize(self):
        self.is_minimized = not self.is_minimized
        if self.is_minimized:
            self.content_widget.hide()
            self.btn_toggle.setText("+")
            self.setMinimumSize(0, 0)
            self.resize(300, 60)
            self.main_layout.setContentsMargins(20, 10, 20, 10)
        else:
            self.content_widget.show()
            self.btn_toggle.setText("-")
            self.setMinimumSize(450, 250)
            self.setMaximumSize(800, 600)
            self.main_layout.setContentsMargins(25, 25, 25, 25)
            
    # ------ EVENTOS PARA ARRASTRAR EL OVERLAY ------
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Detecta la posición del clic dentro del widget
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and self._drag_pos:
            new_pos = event.globalPosition().toPoint() - self._drag_pos
            
            # Limitar el movimiento al contenedor padre
            if self.parent():
                parent_rect = self.parent().rect()
                max_x = parent_rect.width() - self.width()
                max_y = parent_rect.height() - self.height()
                clamped_x = max(0, min(new_pos.x(), max_x))
                clamped_y = max(0, min(new_pos.y(), max_y))
                self.move(clamped_x, clamped_y)
            else:
                self.move(new_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = None
            event.accept()
    # -----------------------------------------------
            
    def load_task(self, task_number, title, description):
        self.title_label.setText(f"Tarea {task_number}: {title}")
        self.desc_label.setText(description)
        self.reset_state()
        
    def reset_state(self):
        self.state = "INIT"
        self.btn_action.setText("Iniciar Tarea")
        self.btn_action.setStyleSheet("")
        if self.is_minimized:
            self.toggle_minimize()
        
    def handle_action_click(self):
        if self.state == "INIT":
            self.state = "STARTED"
            self.btn_action.setText("Completar Tarea")
            self.task_started.emit()
            self.toggle_minimize() # Opcional: minimizar auto al iniciar la tarea
        elif self.state == "STARTED":
            self.task_completed.emit()
