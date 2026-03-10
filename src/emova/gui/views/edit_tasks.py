from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QTextEdit, QScrollArea, QFrame
from PySide6.QtCore import Qt, Signal

class EditTaskView(QWidget):
    go_back = Signal() # Signal to go back to the dashboard
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 20, 40, 40)
        main_layout.setSpacing(20)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # --- Top Navigation Bar ---
        top_layout = QHBoxLayout()
        
        btn_back = QPushButton("← Regresar")
        btn_back.setProperty("class", "BackButton")
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.clicked.connect(self.go_back.emit)
        
        title = QLabel("Edición de tareas")
        title.setProperty("class", "ViewTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Add stretch to center the title properly
        top_layout.addWidget(btn_back)
        top_layout.addStretch()
        top_layout.addWidget(title)
        top_layout.addStretch()
        # To strictly center, we need a dummy widget of same width as back button on the right
        dummy = QWidget()
        dummy.setFixedWidth(btn_back.sizeHint().width() if btn_back.sizeHint().width() > 0 else 100)
        top_layout.addWidget(dummy)
        
        main_layout.addLayout(top_layout)
        
        # --- Scrollable Content Area ---
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("background-color: transparent;")
        
        scroll_widget = QWidget()
        self.tasks_layout = QVBoxLayout(scroll_widget)
        self.tasks_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.tasks_layout.setSpacing(30)
        
        # Add placeholder task blocks to edit
        self.add_edit_task_block(1, "Encontrar la sección de reportes", "Navega por la interfaz hasta localizar el historial...")
        self.add_edit_task_block(2, "Cambiar la configuración", "Accede al perfil y cambia la contraseña...")
        
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area, stretch=1)
        
        # --- Bottom Finalize Button ---
        bottom_layout = QHBoxLayout()
        btn_finalize = QPushButton("Finalizar edición")
        btn_finalize.setProperty("class", "PrimaryButton")
        btn_finalize.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_finalize.setFixedWidth(300)
        
        bottom_layout.addStretch()
        bottom_layout.addWidget(btn_finalize)
        bottom_layout.addStretch()
        
        main_layout.addLayout(bottom_layout)
        
    def add_edit_task_block(self, task_number, title_text, desc_text):
        task_widget = QWidget()
        layout = QVBoxLayout(task_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        lbl_task_num = QLabel(f"Tarea {task_number}")
        lbl_task_num.setProperty("class", "TaskNumberLabel")
        
        lbl_title = QLabel("Titulo de Tarea:")
        input_title = QLineEdit(title_text)
        
        lbl_desc = QLabel("Descripción:")
        input_desc = QTextEdit()
        input_desc.setText(desc_text)
        input_desc.setFixedHeight(150)
        
        # Edit action button for each task
        btn_edit = QPushButton("✎ Editar")
        btn_edit.setProperty("class", "InlineActionButton")
        btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        
        action_layout = QHBoxLayout()
        action_layout.addWidget(btn_edit)
        action_layout.addStretch()
        
        layout.addWidget(lbl_task_num)
        layout.addWidget(lbl_title)
        layout.addWidget(input_title)
        layout.addWidget(lbl_desc)
        layout.addWidget(input_desc)
        layout.addLayout(action_layout)
        
        self.tasks_layout.addWidget(task_widget)
