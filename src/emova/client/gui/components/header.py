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
        
        # Setup dropdown menu
        self.user_menu = QMenu(self)
        
        self.action_login = QAction("Iniciar sesión", self)
        self.action_register = QAction("Registrarse", self)
        
        self.user_menu.addAction(self.action_login)
        self.user_menu.addAction(self.action_register)
        
        self.user_button.setMenu(self.user_menu)
        
        # We need to style the menu here or in QSS
        self.user_menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #D0D0D0;
            }
            QMenu::item {
                padding: 8px 24px 8px 24px;
            }
            QMenu::item:selected {
                background-color: #7E38B7;
                color: white;
            }
        """)

        layout.addWidget(self.user_button)
