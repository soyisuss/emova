from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QMenu, QSizePolicy, QStackedWidget, QVBoxLayout, QWidgetAction
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QPixmap
import os

from emova.core.session.session_manager import session_manager

class TopHeader(QWidget):
    go_to_password_change = Signal()
    logout_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(100) # Increased height for scaling
        self.setStyleSheet("background-color: transparent;") # Remove grey background

        layout = QHBoxLayout(self)
        layout.setContentsMargins(40, 0, 40, 0)
        
        # Project ID
        self.project_label = QLabel(session_manager.test_id)
        self.project_label.setObjectName("HeaderProject")
        self.project_label.setFixedWidth(80) # Fixed width for proper centering
        layout.addWidget(self.project_label)
        
        layout.addStretch() # Spacer before logo
        
        # Logo Image
        self.logo_label = QLabel()
        self.logo_label.setObjectName("HeaderLogo")
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter) # Ensure label content is centered
        
        # Correctly resolve the absolute path to the client/gui/assets/images directory
        # __file__ is at emova/src/emova/client/gui/components/header.py
        current_dir = os.path.dirname(os.path.abspath(__file__))
        gui_root = os.path.abspath(os.path.join(current_dir, ".."))
        logo_path = os.path.join(gui_root, "assets", "images", "emova-logo.png")
             
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            # Scale the logo to fit nicely in the new enlarged header (80px height)
            self.logo_label.setPixmap(pixmap.scaledToHeight(80, Qt.TransformationMode.SmoothTransformation))
        else:
            self.logo_label.setText(f"EMOVA (Missing: {logo_path})")

        layout.addWidget(self.logo_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addStretch() # Spacer after logo
        
        # Spacer
        layout.addStretch()
        
        # User Button
        self.user_button = QPushButton("👤 Mi Cuenta") # Added descriptive text
        self.user_button.setObjectName("UserButton")
        self.user_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.user_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        
        # Setup dropdown menu
        self.user_menu = QMenu(self)
        self.user_menu.setContentsMargins(0, 0, 0, 0)
        
        # We will use a QStackedWidget embedded in the menu to cleanly toggle states
        self.menu_stack = QStackedWidget()
        self.menu_stack.setStyleSheet("""
            QStackedWidget {
                background-color: white;
                border: 1px solid #C0C0C0;
                border-radius: 4px;
            }
            QLabel { border: none; }
        """)
        
        # ---------------- GUEST PAGE ----------------
        self.page_guest = QWidget()
        guest_layout = QVBoxLayout(self.page_guest)
        guest_layout.setContentsMargins(15, 15, 15, 15)
        guest_layout.setSpacing(10)
        
        lbl_title = QLabel("Escoge una opción para entrar:")
        lbl_title.setStyleSheet("font-size: 12px; font-weight: bold; color: black;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        guest_layout.addWidget(lbl_title)
        
        btn_style = """
            QPushButton {
                background-color: #606060;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 6px 12px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #404040; }
        """
        
        self.btn_login = QPushButton("Iniciar sesión")
        self.btn_login.setStyleSheet(btn_style)
        self.btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.btn_register = QPushButton("Registrarse")
        self.btn_register.setStyleSheet(btn_style)
        self.btn_register.setCursor(Qt.CursorShape.PointingHandCursor)
        
        guest_layout.addWidget(self.btn_login)
        guest_layout.addWidget(self.btn_register)
        
        self.btn_login.clicked.connect(self.user_menu.hide)
        self.btn_register.clicked.connect(self.user_menu.hide)
        
        self.menu_stack.addWidget(self.page_guest)
        
        # ---------------- AUTH PAGE ----------------
        self.page_auth = QWidget()
        auth_layout = QVBoxLayout(self.page_auth)
        auth_layout.setContentsMargins(15, 15, 15, 15)
        auth_layout.setSpacing(10)
        
        self.lbl_user_email = QLabel("correo@ejemplo.com")
        self.lbl_user_email.setStyleSheet("font-size: 13px; font-weight: bold; color: black;")
        self.lbl_user_email.setAlignment(Qt.AlignmentFlag.AlignCenter)
        auth_layout.addWidget(self.lbl_user_email)
        
        self.btn_change_pwd = QPushButton("Cambiar Contraseña")
        self.btn_change_pwd.setStyleSheet(btn_style)
        self.btn_change_pwd.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_change_pwd.clicked.connect(self._handle_change_pwd)
        auth_layout.addWidget(self.btn_change_pwd)
        
        self.btn_logout = QPushButton("Cerrar Sesión")
        self.btn_logout.setStyleSheet(btn_style.replace("#606060", "#A83232").replace("#404040", "#8A1C1C"))
        self.btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_logout.clicked.connect(self._handle_logout)
        auth_layout.addWidget(self.btn_logout)
        
        self.menu_stack.addWidget(self.page_auth)
        
        # Action embedding
        widget_action = QWidgetAction(self)
        widget_action.setDefaultWidget(self.menu_stack)
        self.user_menu.addAction(widget_action)
        self.user_button.setMenu(self.user_menu)
        
        layout.addWidget(self.user_button)

    def set_auth_state(self, is_logged_in: bool, email: str = ""):
        if is_logged_in:
            self.user_button.setText("👤 Bienvenido")
            self.lbl_user_email.setText(email)
            self.menu_stack.setCurrentIndex(1)
        else:
            self.user_button.setText("👤 Mi Cuenta")
            self.menu_stack.setCurrentIndex(0)
            
    def _handle_change_pwd(self):
        self.user_menu.hide()
        self.go_to_password_change.emit()
        
    def _handle_logout(self):
        self.user_menu.hide()
        self.logout_requested.emit()
