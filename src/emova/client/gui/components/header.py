from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QMenu, QSizePolicy
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QPixmap
import os

class TopHeader(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(100) # Increased height for scaling
        self.setStyleSheet("background-color: transparent;") # Remove grey background

        layout = QHBoxLayout(self)
        layout.setContentsMargins(40, 0, 40, 0)
        
        # Project ID
        self.project_label = QLabel("PU-1")
        self.project_label.setObjectName("HeaderProject")
        self.project_label.setFixedWidth(50) # Fixed width for proper centering
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
        
        # Custom widget for the menu
        from PySide6.QtWidgets import QWidgetAction, QVBoxLayout
        
        menu_widget = QWidget()
        menu_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #C0C0C0;
                border-radius: 4px;
            }
            QLabel {
                border: none;
            }
        """)
        menu_layout = QVBoxLayout(menu_widget)
        menu_layout.setContentsMargins(15, 15, 15, 15)
        menu_layout.setSpacing(10)
        
        lbl_title = QLabel("Escoge una opción para entrar:")
        lbl_title.setStyleSheet("font-size: 12px; font-weight: bold; color: black;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        menu_layout.addWidget(lbl_title)
        
        # Buttons with dark gray style according to mockup
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
            QPushButton:hover {
                background-color: #404040;
            }
        """
        
        self.btn_login = QPushButton("Iniciar sesión")
        self.btn_login.setStyleSheet(btn_style)
        self.btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.btn_register = QPushButton("Registrarse")
        self.btn_register.setStyleSheet(btn_style)
        self.btn_register.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # To avoid the menu closing when clicking inside the widget unless a button is clicked,
        # we connect the buttons to emit a custom signal or close the menu and emit signal.
        # But we'll just connect them to properties on header that MainWindow can listen to.
        # Or even better, emit signals from the header.
        
        menu_layout.addWidget(self.btn_login)
        menu_layout.addWidget(self.btn_register)
        
        widget_action = QWidgetAction(self)
        widget_action.setDefaultWidget(menu_widget)
        
        self.user_menu.addAction(widget_action)
        self.user_button.setMenu(self.user_menu)
        
        # Close menu when button clicked
        self.btn_login.clicked.connect(self.user_menu.hide)
        self.btn_register.clicked.connect(self.user_menu.hide)

        layout.addWidget(self.user_button)
