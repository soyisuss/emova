import httpx
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QScrollArea, QWidget, QFrame, QMessageBox, QApplication
)
from PySide6.QtCore import Qt, Signal
from datetime import datetime

from emova.core.session.session_manager import session_manager

class LoadTestDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("LoadTestDialog")
        self.setWindowTitle("Repetir configuración de prueba")
        self.setFixedSize(600, 500)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        
        self.setStyleSheet("""
            #LoadTestDialog {
                background-color: white;
            }
            QLabel {
                color: #333333;
                background: transparent;
            }
        """)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(20)
        
        title = QLabel("Seleccionar Configuración de Prueba")
        title.setProperty("class", "ViewTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(title)
        
        # Scroll Area for the list
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setStyleSheet("background-color: transparent;")
        
        self.scroll_widget = QWidget()
        self.list_layout = QVBoxLayout(self.scroll_widget)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.list_layout.setSpacing(15)
        
        self.scroll_area.setWidget(self.scroll_widget)
        self.layout.addWidget(self.scroll_area, stretch=1)
        
        # Bottom Layout
        btn_layout = QHBoxLayout()
        btn_close = QPushButton("Cerrar")
        btn_close.setProperty("class", "DialogButton")
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)
        
        self.layout.addLayout(btn_layout)
        
        self.load_templates()
        
    def load_templates(self):
        # Muestra mensaje de carga
        self.clear_list()
        loading_label = QLabel("Cargando configuraciones desde MongoDB...")
        loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.list_layout.addWidget(loading_label)
        
        # Necesitamos procesar la red de manera sincrona/asincrona (PySide6 no le gusta bloquear, usamos request simple por ahora)
        QApplication.processEvents()
        
        try:
            # Reemplazar por url de la api centralizada en settings en un entorno productivo
            base_url = "http://127.0.0.1:8000"
            response = httpx.get(f"{base_url}/tests/templates", timeout=5.0)
            if response.status_code == 200:
                templates = response.json()
                self.populate_list(templates)
            else:
                self.show_error("Error al obtener las configuraciones.")
        except Exception as e:
            self.show_error(f"El servidor de base de datos no está disponible.\n{e}")
            
    def clear_list(self):
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
    def show_error(self, message):
        self.clear_list()
        
        err_widget = QWidget()
        err_layout = QVBoxLayout(err_widget)
        err_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        err_lbl = QLabel(message)
        err_lbl.setStyleSheet("font-size: 16px; color: #E74C3C; font-weight: bold; margin-top: 20px;")
        err_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        err_layout.addStretch()
        err_layout.addWidget(err_lbl)
        err_layout.addStretch()
        
        self.list_layout.addWidget(err_widget)
        
    def render_empty_state(self):
        self.clear_list()
        
        empty_widget = QWidget()
        empty_layout = QVBoxLayout(empty_widget)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_msg = QLabel("Aún no se registran pruebas")
        lbl_msg.setStyleSheet("font-size: 20px; color: #555555; font-weight: bold; margin-bottom: 20px;")
        lbl_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Opcional, un botón o texto de ayuda extra
        lbl_sub = QLabel("Genera una prueba en 'Agregar tareas' y finaliza el registro\npara que aparezca aquí.")
        lbl_sub.setStyleSheet("font-size: 14px; color: #888888;")
        lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        empty_layout.addStretch()
        empty_layout.addWidget(lbl_msg)
        empty_layout.addWidget(lbl_sub)
        empty_layout.addStretch()
        
        self.list_layout.addWidget(empty_widget)
        
    def populate_list(self, templates):
        self.clear_list()
        if not templates:
            self.render_empty_state()
            return
            
        for tmpl in templates:
            self.create_item_widget(tmpl)
            
    def create_item_widget(self, tmpl):
        w = QWidget()
        w.setStyleSheet("background-color: #F8F9FA; border-radius: 8px; border: 1px solid #DDDDDD;")
        l = QHBoxLayout(w)
        l.setContentsMargins(15, 15, 15, 15)
        
        info_layout = QVBoxLayout()
        # Parse datetime
        # Fastapi returns ISO format like: "2023-10-05T14:48:00"
        try:
            dt = datetime.fromisoformat(tmpl["createdAt"].replace("Z", "+00:00"))
            date_str = dt.strftime("%d/%m/%Y %H:%M")
        except:
            date_str = tmpl["createdAt"]
            
        title_lbl = QLabel(f"<b>{tmpl.get('name', 'Prueba')}</b> - {date_str}")
        title_lbl.setStyleSheet("font-size: 14px; color: #333; border: none; background: transparent;")
        
        tasks = tmpl.get("tasks", [])
        num_tasks = len(tasks)
        task_lbl = QLabel(f"{num_tasks} tareas registradas")
        task_lbl.setStyleSheet("font-size: 12px; color: #666; border: none; background: transparent;")
        
        info_layout.addWidget(title_lbl)
        info_layout.addWidget(task_lbl)
        
        btn_select = QPushButton("Cargar")
        btn_select.setProperty("class", "PrimaryButton")
        btn_select.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_select.setFixedWidth(100)
        btn_select.clicked.connect(lambda _, t=tasks: self.select_template(t))
        
        l.addLayout(info_layout)
        l.addStretch()
        l.addWidget(btn_select)
        
        self.list_layout.addWidget(w)
        
    def select_template(self, tasks):
        session_manager.clear_tasks() if hasattr(session_manager, 'clear_tasks') else None
        if not hasattr(session_manager, 'clear_tasks'):
            session_manager.tasks = []
            
        for t in tasks:
            session_manager.add_task(t.get("title", ""), t.get("description", ""))
            
        QMessageBox.information(self, "Éxito", f"Se han cargado {len(tasks)} tareas a la sesión actual.")
        self.accept()
