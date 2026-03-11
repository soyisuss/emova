from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QTextEdit, QScrollArea, QFrame, QMessageBox
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIntValidator

from emova.core.session.session_manager import session_manager
from emova.client.gui.components.custom_dialog import CustomDialog

class RegisterTaskView(QWidget):
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
        
        title = QLabel("Registro de Tareas")
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
        
        # Add the first default task block
        self.add_task_block(1)
        
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area, stretch=1)
        
        # --- Add New Task Button ---
        btn_add_task = QPushButton("+ Añadir tarea")
        btn_add_task.setProperty("class", "InlineActionButton")
        btn_add_task.setCursor(Qt.CursorShape.PointingHandCursor)
        self.task_count = 1
        btn_add_task.clicked.connect(self.on_add_task_clicked)
        
        action_layout = QHBoxLayout()
        action_layout.addWidget(btn_add_task)
        action_layout.addStretch()
        
        main_layout.addLayout(action_layout)
        
        # --- Bottom Finalize Button ---
        bottom_layout = QHBoxLayout()
        btn_finalize = QPushButton("Finalizar registro")
        btn_finalize.setProperty("class", "PrimaryButton")
        btn_finalize.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_finalize.setFixedWidth(300)
        btn_finalize.clicked.connect(self.save_tasks)
        
        bottom_layout.addStretch()
        bottom_layout.addWidget(btn_finalize)
        bottom_layout.addStretch()
        
        main_layout.addLayout(bottom_layout)
        
    def add_task_block(self, task_number):
        task_widget = QWidget()
        layout = QVBoxLayout(task_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        task_header_layout = QHBoxLayout()
        task_header_layout.setContentsMargins(0, 0, 0, 0)
        
        lbl_task_num = QLabel(f"Tarea {task_number}")
        lbl_task_num.setProperty("class", "TaskNumberLabel")
        # Give the label an object name so we can find it later for renumbering
        lbl_task_num.setObjectName("TaskNumberLabel")
        
        btn_edit = QPushButton("Guardar")
        btn_edit.setProperty("class", "EditButton")
        btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_edit.setFixedWidth(100)
        btn_edit.setStyleSheet("color: #7E38B7;")
        
        btn_delete = QPushButton("Eliminar")
        btn_delete.setProperty("class", "WarningButton")
        btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_delete.setFixedWidth(100)
        # Connect delete button to remove this specific task_widget
        btn_delete.clicked.connect(lambda _, w=task_widget: self.remove_task_block(w))
        
        task_header_layout.addWidget(lbl_task_num)
        task_header_layout.addStretch() # Push buttons to the right
        task_header_layout.addWidget(btn_edit)
        task_header_layout.addWidget(btn_delete)
        
        lbl_title = QLabel("Titulo de Tarea:")
        input_title = QLineEdit()
        # Default editable state
        input_title.setReadOnly(False)
        input_title.setStyleSheet("background-color: white; color: black; border: 2px solid #7E38B7;")
        
        lbl_desc = QLabel("Descripción:")
        input_desc = QTextEdit()
        input_desc.setFixedHeight(150)
        # Default editable state
        input_desc.setReadOnly(False)
        input_desc.setStyleSheet("background-color: white; color: black; border: 2px solid #7E38B7;")
        
        # Connect Edit button toggle logic
        btn_edit.clicked.connect(lambda _, ti=input_title, td=input_desc, btn=btn_edit: self.toggle_edit_mode(btn, ti, td))
        
        layout.addLayout(task_header_layout)
        layout.addWidget(lbl_title)
        layout.addWidget(input_title)
        layout.addWidget(lbl_desc)
        layout.addWidget(input_desc)
        
        self.tasks_layout.addWidget(task_widget)
        self.renumber_tasks() # Force re-evaluate UI button states
        
    def on_add_task_clicked(self):
        self.task_count += 1
        self.add_task_block(self.task_count)
        
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
            btn.setStyleSheet("") # Revert to global CSS class (.EditButton)
            
    def remove_task_block(self, task_widget):
        self.tasks_layout.removeWidget(task_widget)
        task_widget.deleteLater()
        self.task_count -= 1
        
        # If we deleted the last task, show the empty state again
        if self.task_count == 0:
            self.render_empty_state()
        else:
            # Auto-renumber the labels of remaining tasks
            self.renumber_tasks()
            
    def renumber_tasks(self):
        # Iterate over all task widgets in the layout and correct their displayed number
        for i in range(self.tasks_layout.count()):
            widget = self.tasks_layout.itemAt(i).widget()
            if widget:
                # Find the label
                label = widget.findChild(QLabel, "TaskNumberLabel")
                if label:
                    label.setText(f"Tarea {i + 1}")
                
                # Find the delete button
                delete_btn = widget.findChild(QPushButton)
                if delete_btn and delete_btn.text() == "Eliminar":
                    # If this is the only task remaining (count is 1), hide its delete button
                    if self.tasks_layout.count() == 1:
                        delete_btn.hide()
                    else:
                        delete_btn.show()

    def save_tasks(self):
        # Clear existing tasks to avoid appending duplicates from rapid clicking
        session_manager.clear_tasks() if hasattr(session_manager, 'clear_tasks') else None
        if not hasattr(session_manager, 'clear_tasks'):
            session_manager.tasks = [] # Fallback
            
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
                        
        if task_count == 0:
            dialog = CustomDialog(
                parent=self.window(),
                title="Campos Vacíos",
                message="No has ingresado información para registrar tareas."
            )
            dialog.exec()
            return
            
        dialog = CustomDialog(
            parent=self.window(),
            title="Registro Exitoso",
            message=f"{task_count} tarea(s) registrada(s) en la sesión actual."
        )
        dialog.exec()
        
        self.go_back.emit()
