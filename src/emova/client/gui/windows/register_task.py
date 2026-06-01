from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QTextEdit, QScrollArea, QFrame, QMessageBox
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIntValidator
import httpx
from datetime import datetime

from emova.core.session.session_manager import session_manager
from emova.client.gui.components.custom_dialog import CustomDialog

class RegisterTaskView(QWidget):
    go_back = Signal() # Señal para regresar al dashboard
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 20, 40, 40)
        main_layout.setSpacing(20)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # --- Barra de navegación superior ---
        top_layout = QHBoxLayout()
        
        btn_back = QPushButton("← Regresar")
        btn_back.setProperty("class", "BackButton")
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.clicked.connect(self.go_back.emit)
        
        title = QLabel("Registro de Tareas")
        title.setProperty("class", "ViewTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Agregar espaciado para centrar el título correctamente
        top_layout.addWidget(btn_back)
        top_layout.addStretch()
        top_layout.addWidget(title)
        top_layout.addStretch()
        # Para centrar estrictamente, se agrega un widget vacío en el lado derecho
        dummy = QWidget()
        dummy.setFixedWidth(btn_back.sizeHint().width() if btn_back.sizeHint().width() > 0 else 100)
        top_layout.addWidget(dummy)
        
        main_layout.addLayout(top_layout)
        
        # --- Alias de la prueba ---
        alias_layout = QHBoxLayout()
        lbl_alias = QLabel("Alias / Nombre de la Prueba:")
        lbl_alias.setStyleSheet("font-weight: bold; font-size: 16px; color: #333;")
        self.input_alias = QLineEdit()
        self.input_alias.setPlaceholderText("Ej. Prueba Piloto Sistema XYZ")
        self.input_alias.setStyleSheet("background-color: white; color: black; border: 2px solid #7E38B7; padding: 5px; font-size: 14px;")
        
        alias_layout.addWidget(lbl_alias)
        alias_layout.addWidget(self.input_alias)
        
        main_layout.addLayout(alias_layout)
        
        # --- Área de contenido desplazable ---
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("background-color: transparent;")
        
        scroll_widget = QWidget()
        self.tasks_layout = QVBoxLayout(scroll_widget)
        self.tasks_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.tasks_layout.setSpacing(30)
        
        # Agregar el bloque de tarea inicial por defecto
        self.add_task_block(1)
        
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area, stretch=1)
        
        # --- Botón para agregar nueva tarea ---
        btn_add_task = QPushButton("+ Añadir tarea")
        btn_add_task.setProperty("class", "InlineActionButton")
        btn_add_task.setCursor(Qt.CursorShape.PointingHandCursor)
        self.task_count = 1
        btn_add_task.clicked.connect(self.on_add_task_clicked)
        
        action_layout = QHBoxLayout()
        action_layout.addWidget(btn_add_task)
        action_layout.addStretch()
        
        main_layout.addLayout(action_layout)
        
        # --- Botón inferior para finalizar ---
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
        lbl_task_num.setObjectName("TaskNumberLabel")
        
        btn_delete = QPushButton("✖ Eliminar")
        btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_delete.setStyleSheet("""
            QPushButton {
                color: #E74C3C;
                background-color: transparent;
                font-weight: bold;
                font-size: 15px;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                color: #C0392B;
            }
        """)
        btn_delete.clicked.connect(lambda _, w=task_widget: self.remove_task_block(w))
        
        task_header_layout.addWidget(lbl_task_num)
        task_header_layout.addStretch()
        task_header_layout.addWidget(btn_delete)
        
        lbl_title = QLabel("Titulo de Tarea:")
        input_title = QLineEdit()
        input_title.setReadOnly(False)
        input_title.setStyleSheet("background-color: white; color: black; border: 2px solid #7E38B7;")
        
        lbl_desc = QLabel("Descripción:")
        input_desc = QTextEdit()
        input_desc.setFixedHeight(120)
        input_desc.setReadOnly(False)
        input_desc.setStyleSheet("background-color: white; color: black; border: 2px solid #7E38B7;")
        
        layout.addLayout(task_header_layout)
        layout.addWidget(lbl_title)
        layout.addWidget(input_title)
        layout.addWidget(lbl_desc)
        layout.addWidget(input_desc)
        
        self.tasks_layout.addWidget(task_widget)
        self.renumber_tasks() # Forzar la reevaluación de estados de los botones en la interfaz
        
    def on_add_task_clicked(self):
        self.task_count += 1
        self.add_task_block(self.task_count)
        
    def toggle_edit_mode(self, btn, input_title, input_desc):
        # Si está bloqueado, se desbloquea
        if input_title.isReadOnly():
            input_title.setReadOnly(False)
            input_desc.setReadOnly(False)
            
            # Cambiar diseño visual para indicar estado editable
            input_title.setStyleSheet("background-color: white; color: black; border: 2px solid #7E38B7;")
            input_desc.setStyleSheet("background-color: white; color: black; border: 2px solid #7E38B7;")
            
            btn.setText("Guardar")
            btn.setStyleSheet("color: #7E38B7;") # Color morado que indica acción para guardar
        else:
            # Si está desbloqueado, se vuelve a bloquear
            input_title.setReadOnly(True)
            input_desc.setReadOnly(True)
            
            # Revertir diseño visual para indicar estado bloqueado
            input_title.setStyleSheet("background-color: #EFEFEF; color: #555555; border: 2px solid #333333;")
            input_desc.setStyleSheet("background-color: #EFEFEF; color: #555555; border: 2px solid #333333;")
            
            btn.setText("Editar")
            btn.setStyleSheet("") # Revertir a la clase CSS global (.EditButton)
            
    def remove_task_block(self, task_widget):
        self.tasks_layout.removeWidget(task_widget)
        task_widget.deleteLater()
        self.task_count -= 1
        
        # Si se eliminó la última tarea, mostrar de nuevo el estado vacío
        if self.task_count == 0:
            self.render_empty_state()
        else:
            # Renumerar automáticamente las etiquetas de las tareas restantes
            self.renumber_tasks()
            
    def renumber_tasks(self):
        # Iterar sobre los widgets de tareas en el diseño y corregir su numeración
        for i in range(self.tasks_layout.count()):
            widget = self.tasks_layout.itemAt(i).widget()
            if widget:
                # Buscar la etiqueta
                label = widget.findChild(QLabel, "TaskNumberLabel")
                if label:
                    label.setText(f"Tarea {i + 1}")
                
                # Buscar el botón de eliminación
                for btn in widget.findChildren(QPushButton):
                    if btn.text() == "✖ Eliminar":
                        if self.tasks_layout.count() == 1:
                            btn.hide()
                        else:
                            btn.show()
                        break

    def save_tasks(self):
        # Limpiar tareas existentes para evitar duplicados por clics rápidos
        session_manager.clear_tasks() if hasattr(session_manager, 'clear_tasks') else None
        if not hasattr(session_manager, 'clear_tasks'):
            session_manager.tasks = [] # Respaldo
            
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
            
        # Guardar en MongoDB
        try:
            alias = self.input_alias.text().strip()
            if not alias:
                alias = f"Prueba #{session_manager.test_id} ({datetime.now().strftime('%d/%m/%Y %H:%M')})"
                
            from emova.client.api_client import ApiClient
            api_client = ApiClient.get_instance()
            base_url = api_client.base_url
            payload = {
                "test_id": session_manager.test_id,
                "name": alias,
                "tasks": session_manager.tasks
            }
            token = api_client.token
            headers = {"Authorization": f"Bearer {token}"} if token else {}
            httpx.post(f"{base_url}/tests/templates/", json=payload, headers=headers, timeout=3.0)
        except Exception as e:
            print(f"Advertencia: No se pudo guardar la configuración en BD: {e}")
            
        dialog = CustomDialog(
            parent=self.window(),
            title="Registro Exitoso",
            message=f"{task_count} tarea(s) registrada(s) en la sesión actual."
        )
        dialog.exec()
        
        self.go_back.emit()
