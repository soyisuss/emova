from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt

class CustomDialog(QDialog):
    """
    A generic, centered modal dialog mimicking the clean aesthetic of the Privacy Notice.
    """
    def __init__(self, parent=None, title="", message=""):
        super().__init__(parent)
        self.setObjectName("PrivacyDialog") # Reusing the clean white container styling
        
        # Make it more compact and dynamic
        self.setMinimumWidth(350)
        self.setMaximumWidth(450)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        lbl_title = QLabel(title)
        lbl_title.setObjectName("PrivacyTitle") # Reusing the purple bold styling
        lbl_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #7E38B7;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_msg = QLabel(message)
        lbl_msg.setObjectName("PrivacyText") # Reusing the black bold text styling
        lbl_msg.setStyleSheet("font-size: 16px; color: #333;")
        lbl_msg.setWordWrap(True)
        lbl_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)
        
        btn_accept = QPushButton("Aceptar")
        btn_accept.setProperty("class", "DialogButton") # Reusing the purple filled button styling
        btn_accept.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_accept.clicked.connect(self.accept)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_accept)
        btn_layout.addStretch()
        
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_msg)
        layout.addLayout(btn_layout)
