import httpx
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QScrollArea, QFrame, QMessageBox, QApplication, QStackedWidget
)
from PySide6.QtCore import Qt, Signal
from datetime import datetime

from emova.core.session.session_manager import session_manager

class LoadTestView(QWidget):
    go_back = Signal() # Signal to return to dashboard
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("LoadTestView")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 20, 40, 40)
        main_layout.setSpacing(20)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # --- Top Navigation Bar ---
        top_layout = QHBoxLayout()
        
        self.btn_back = QPushButton("← Regresar")
        self.btn_back.setProperty("class", "BackButton")
        self.btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_back.clicked.connect(self.handle_back)
        
        title = QLabel("Seleccionar Configuración de Prueba")
        title.setProperty("class", "ViewTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        top_layout.addWidget(self.btn_back)
        top_layout.addStretch()
        top_layout.addWidget(title)
        top_layout.addStretch()
        
        dummy = QWidget()
        dummy.setFixedWidth(self.btn_back.sizeHint().width() if self.btn_back.sizeHint().width() > 0 else 100)
        top_layout.addWidget(dummy)
        
        main_layout.addLayout(top_layout)
        
        # --- Stack Container ---
        self.stack = QStackedWidget()
        
        # ==========================================
        # PAGE 0: List View
        # ==========================================
        self.page_list = QWidget()
        page_list_layout = QVBoxLayout(self.page_list)
        page_list_layout.setContentsMargins(0,0,0,0)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("background-color: transparent;")
        
        self.scroll_widget = QWidget()
        self.list_layout = QVBoxLayout(self.scroll_widget)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.list_layout.setSpacing(15)
        
        scroll_area.setWidget(self.scroll_widget)
        page_list_layout.addWidget(scroll_area)
        
        # ==========================================
        # PAGE 1: Detail View
        # ==========================================
        self.page_detail = QWidget()
        detail_layout = QVBoxLayout(self.page_detail)
        detail_layout.setContentsMargins(0,0,0,0)
        
        # Header showing selected template name
        self.lbl_detail_title = QLabel("Detalles de la Prueba")
        self.lbl_detail_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        self.lbl_detail_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        detail_layout.addWidget(self.lbl_detail_title)
        
        detail_scroll = QScrollArea()
        detail_scroll.setWidgetResizable(True)
        detail_scroll.setFrameShape(QFrame.Shape.NoFrame)
        detail_scroll.setStyleSheet("background-color: transparent;")
        
        self.detail_widget = QWidget()
        self.detail_tasks_layout = QVBoxLayout(self.detail_widget)
        self.detail_tasks_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.detail_tasks_layout.setSpacing(10)
        
        detail_scroll.setWidget(self.detail_widget)
        detail_layout.addWidget(detail_scroll)
        
        # Final CTA inside detail view
        bottom_layout = QHBoxLayout()
        self.btn_load_from_detail = QPushButton("Repetir esta prueba")
        self.btn_load_from_detail.setProperty("class", "PrimaryButton")
        self.btn_load_from_detail.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_load_from_detail.setFixedWidth(250)
        
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.btn_load_from_detail)
        bottom_layout.addStretch()
        
        detail_layout.addLayout(bottom_layout)
        
        self.stack.addWidget(self.page_list)     # Index 0
        self.stack.addWidget(self.page_detail)   # Index 1
        
        main_layout.addWidget(self.stack, stretch=1)
        
    def handle_back(self):
        if self.stack.currentIndex() == 1:
            self.stack.setCurrentIndex(0)
        else:
            self.go_back.emit()

    def load_templates(self):
        self.stack.setCurrentIndex(0)
        self.clear_list()
        loading_label = QLabel("Cargando configuraciones desde MongoDB...")
        loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.list_layout.addWidget(loading_label)
        QApplication.processEvents()
        
        try:
            base_url = "http://127.0.0.1:8000"
            response = httpx.get(f"{base_url}/tests/templates/", timeout=5.0)
            if response.status_code == 200:
                templates = response.json()
                self.populate_list(templates)
            else:
                self.show_error(f"Error al obtener las configuraciones. (Código: {response.status_code})")
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
        w.setObjectName("TestItem")
        w.setStyleSheet("#TestItem { background-color: #F8F9FA; border-radius: 8px; border: 1px solid #DDDDDD; }")
        l = QHBoxLayout(w)
        l.setContentsMargins(15, 15, 15, 15)
        
        info_layout = QVBoxLayout()
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
        
        btn_view = QPushButton("Detalles de prueba")
        btn_view.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_view.setFixedWidth(200)
        btn_view.setStyleSheet("""
            QPushButton {
                background-color: #7E38B7;
                color: white;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #632C94;
            }
        """)
        btn_view.clicked.connect(lambda _, t=tmpl: self.show_detail(t))
        
        btn_delete = QPushButton("✖ Eliminar")
        btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_delete.setStyleSheet("""
            QPushButton {
                color: #E74C3C;
                background-color: transparent;
                font-weight: bold;
                font-size: 15px;
                border: none;
                padding: 10px;
                margin-left: 10px;
            }
            QPushButton:hover {
                color: #C0392B;
            }
        """)
        btn_delete.clicked.connect(lambda _, t=tmpl: self.confirm_delete(t))
        
        l.addLayout(info_layout)
        l.addStretch()
        l.addWidget(btn_view)
        l.addWidget(btn_delete)
        self.list_layout.addWidget(w)
        
    def confirm_delete(self, tmpl):
        template_id = tmpl.get("_id") or tmpl.get("id")
        if not template_id:
            return
            
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Eliminar Configuración")
        msg_box.setText(f"¿Estás seguro de que deseas eliminar '{tmpl.get('name', 'Prueba')}' permanentemente?")
        msg_box.setIcon(QMessageBox.Icon.Question)
        
        btn_si = msg_box.addButton("Sí", QMessageBox.ButtonRole.YesRole)
        btn_no = msg_box.addButton("No", QMessageBox.ButtonRole.NoRole)
        
        msg_box.exec()
        
        if msg_box.clickedButton() == btn_si:
            try:
                base_url = "http://127.0.0.1:8000"
                response = httpx.delete(f"{base_url}/tests/templates/{template_id}", timeout=5.0)
                if response.status_code == 204:
                    self.load_templates()
                else:
                    self.show_error(f"No se pudo eliminar la configuración. Código: {response.status_code}")
            except Exception as e:
                self.show_error(f"Error al conectar con la base de datos: {e}")

    def show_detail(self, tmpl):
        # Limpiar detalle anterior
        while self.detail_tasks_layout.count():
            item = self.detail_tasks_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        self.lbl_detail_title.setText(tmpl.get("name", "Detalles de la Prueba"))
        tasks = tmpl.get("tasks", [])
        
        for i, t in enumerate(tasks, 1):
            task_w = QWidget()
            task_w.setStyleSheet("background-color: white; border: 1px solid #CCC; border-radius: 6px;")
            tw_layout = QVBoxLayout(task_w)
            
            lbl_title = QLabel(f"<b>Tarea {i}:</b> {t.get('title', '')}")
            lbl_title.setStyleSheet("font-size: 14px; border: none;")
            
            lbl_desc = QLabel(t.get('description', ''))
            lbl_desc.setStyleSheet("font-size: 13px; color: #555; border: none;")
            lbl_desc.setWordWrap(True)
            
            tw_layout.addWidget(lbl_title)
            tw_layout.addWidget(lbl_desc)
            self.detail_tasks_layout.addWidget(task_w)
            
        # Reconnect button safely
        try:
            self.btn_load_from_detail.clicked.disconnect()
        except TypeError:
            pass # No connections existed
            
        self.btn_load_from_detail.clicked.connect(lambda: self.select_template(tasks))
        
        # Transition to detail view
        self.stack.setCurrentIndex(1)
        
    def select_template(self, tasks):
        session_manager.clear_tasks() if hasattr(session_manager, 'clear_tasks') else None
        if not hasattr(session_manager, 'clear_tasks'):
            session_manager.tasks = []
            
        for t in tasks:
            session_manager.add_task(t.get("title", ""), t.get("description", ""))
            
        # Registrar como una nueva prueba en la base de datos
        try:
            base_url = "http://127.0.0.1:8000"
            payload = {
                "test_id": session_manager.test_id,
                "name": f"Prueba #{session_manager.test_id} ({datetime.now().strftime('%d/%m/%Y %H:%M')})",
                "tasks": session_manager.tasks
            }
            httpx.post(f"{base_url}/tests/templates/", json=payload, timeout=3.0)
        except Exception as e:
            print(f"Aviso: No se pudo registrar la nueva copia en la BD. Detalles: {e}")
            
        QMessageBox.information(self, "Configuración Lista", f"Se ha preparado exitosamente la nueva Prueba #{session_manager.test_id} cargando {len(tasks)} tareas. Ya puedes continuar con el registro.")
        self.go_back.emit()
