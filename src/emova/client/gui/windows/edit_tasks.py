from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QTextEdit, QScrollArea, QFrame, QSizePolicy
from PySide6.QtCore import Qt, Signal
import httpx
from datetime import datetime

from emova.core.session.session_manager import session_manager
from emova.client.gui.components.custom_dialog import CustomDialog

class EditTaskView(QWidget):
    go_back = Signal() # Signal to go back to the dashboard
    go_to_add = Signal() # Signal to route to the Creation View
    
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
        
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area, stretch=1)
        
        # --- Bottom Finalize Button ---
        self.bottom_layout = QHBoxLayout()
        self.bottom_layout.setSpacing(20)
        
        self.btn_add_more = QPushButton("Agregar más tareas (+)")
        self.btn_add_more.setProperty("class", "AnalysisButton")
        self.btn_add_more.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add_more.setFixedWidth(250)
        self.btn_add_more.clicked.connect(self.go_to_add_more)
        
        self.btn_finalize = QPushButton("Finalizar edición")
        self.btn_finalize.setProperty("class", "PrimaryButton")
        self.btn_finalize.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_finalize.setFixedWidth(250)
        self.btn_finalize.clicked.connect(self.save_tasks)
        
        self.bottom_layout.addStretch()
        self.bottom_layout.addWidget(self.btn_add_more)
        self.bottom_layout.addWidget(self.btn_finalize)
        self.bottom_layout.addStretch()
        
        main_layout.addLayout(self.bottom_layout)
        
    def load_tasks_from_session(self):
        """Clears the current layout and generates blocks based on the SessionManager."""
        # Clean current layout cleanly
        while self.tasks_layout.count():
            child = self.tasks_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        tasks = session_manager.tasks
        
        if not tasks:
            # Render Empty State View
            self.render_empty_state()
            self.btn_finalize.hide() # Hide since there is nothing to finalize
            self.btn_add_more.hide()
        else:
            self.btn_finalize.show()
            self.btn_add_more.show()
            for i, t in enumerate(tasks, 1):
                self.add_edit_task_block(i, t.get("title", ""), t.get("description", ""))
                
    def render_empty_state(self):
        empty_widget = QWidget()
        empty_layout = QVBoxLayout(empty_widget)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_msg = QLabel("Aún no se agregan tareas")
        lbl_msg.setStyleSheet("font-size: 20px; color: #555555; font-weight: bold; margin-bottom: 20px;")
        lbl_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        btn_add_now = QPushButton("Ir a agregar tareas +")
        btn_add_now.setProperty("class", "AnalysisButton") # Reusing purple button style
        btn_add_now.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add_now.setFixedWidth(250)
        btn_add_now.clicked.connect(self.go_to_add.emit)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn_add_now)
        btn_layout.addStretch()
        
        empty_layout.addStretch()
        empty_layout.addWidget(lbl_msg)
        empty_layout.addLayout(btn_layout)
        empty_layout.addStretch()
        
        self.tasks_layout.addWidget(empty_widget)
        
    def add_edit_task_block(self, task_number, title_text, desc_text, is_new=False):
        task_widget = QWidget()
        layout = QVBoxLayout(task_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        lbl_task_num = QLabel(f"Tarea {task_number}")
        lbl_task_num.setProperty("class", "TaskNumberLabel")
        
        lbl_title = QLabel("Titulo de Tarea:")
        input_title = QLineEdit(title_text)
        input_title.setReadOnly(True)
        input_title.setStyleSheet("background-color: #EFEFEF; color: #555555; border: 2px solid #333333;")
        
        lbl_desc = QLabel("Descripción:")
        input_desc = QTextEdit()
        input_desc.setText(desc_text)
        input_desc.setFixedHeight(150)
        input_desc.setReadOnly(True)
        input_desc.setStyleSheet("background-color: #EFEFEF; color: #555555; border: 2px solid #333333;")
        
        # Edit action button for each task
        btn_edit = QPushButton("Editar")
        btn_edit.setProperty("class", "InlineActionButton")
        btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Connect Edit button toggle logic
        btn_edit.clicked.connect(lambda _, ti=input_title, td=input_desc, btn=btn_edit: self.toggle_edit_mode(btn, ti, td))
        
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
        
        if is_new:
            self.toggle_edit_mode(btn_edit, input_title, input_desc)

    def toggle_edit_mode(self, btn, input_title, input_desc):
        # If currently locked, unlock it
        if input_title.isReadOnly():
            input_title.setReadOnly(False)
            input_desc.setReadOnly(False)
            
            # Change visuals to indicate editable state
            input_title.setStyleSheet("background-color: white; color: black; border: 2px solid #7E38B7;")
            input_desc.setStyleSheet("background-color: white; color: black; border: 2px solid #7E38B7;")
            
            btn.setText("Guardar")
            btn.setStyleSheet("color: #7E38B7;") # Purple indicating action to save
        else:
            # If unlocked, lock it back
            input_title.setReadOnly(True)
            input_desc.setReadOnly(True)
            
            # Revert visuals to indicate locked
            input_title.setStyleSheet("background-color: #EFEFEF; color: #555555; border: 2px solid #333333;")
            input_desc.setStyleSheet("background-color: #EFEFEF; color: #555555; border: 2px solid #333333;")
            
            btn.setText("Editar")
            btn.setStyleSheet("") # Revert to global CSS class (.InlineActionButton)

    def _rebuild_tasks_from_ui(self):
        # Clear existing tasks to rebuild from UI state
        session_manager.clear_tasks() if hasattr(session_manager, 'clear_tasks') else None
        if not hasattr(session_manager, 'clear_tasks'):
            session_manager.tasks = []
            
        task_count = 0
        for i in range(self.tasks_layout.count()):
            widget = self.tasks_layout.itemAt(i).widget()
            if widget:
                title_input = widget.findChild(QLineEdit)
                desc_input = widget.findChild(QTextEdit)
                if title_input and desc_input:
                    title = title_input.text().strip()
                    desc = desc_input.toPlainText().strip()
                    
                    if title or desc:
                        session_manager.add_task(title, desc)
                        task_count += 1
        return task_count
        
    def go_to_add_more(self):
        task_num = self.tasks_layout.count() + 1
        self.add_edit_task_block(task_num, "", "", is_new=True)

    def save_tasks(self):
        task_count = self._rebuild_tasks_from_ui()
        
        if task_count == 0:
            dialog = CustomDialog(
                parent=self.window(),
                title="Lista Vacía",
                message="Se han eliminado todas las tareas del registro."
            )
            dialog.exec()
        else:
            # Save to MongoDB
            try:
                base_url = "http://127.0.0.1:8000"
                payload = {
                    "test_id": session_manager.test_id,
                    "name": f"Prueba #{session_manager.test_id} ({datetime.now().strftime('%d/%m/%Y %H:%M')})",
                    "tasks": session_manager.tasks
                }
                httpx.post(f"{base_url}/tests/templates/", json=payload, timeout=3.0)
            except Exception as e:
                print(f"Advertencia: No se pudo guardar la configuración en BD: {e}")
                
            dialog = CustomDialog(
                parent=self.window(),
                title="Edición Exitosa",
                message=f"{task_count} tarea(s) actualizada(s) en la sesión actual."
            )
            dialog.exec()
            
        self.go_back.emit()
