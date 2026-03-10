from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt

class CustomDialog(QDialog):
    """
    A generic, centered modal dialog mimicking the clean aesthetic of the Privacy Notice.
    """
    def __init__(self, parent=None, title="", message=""):
        super().__init__(parent)
        self.setObjectName("PrivacyDialog") # Reusing the clean white container styling
        
        # We can dynamically size the dialog based on the amount of text if needed,
        # but a fixed size keeps it consistent with the Privacy Notice.
        self.setFixedSize(500, 300)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        lbl_title = QLabel(title)
        lbl_title.setObjectName("PrivacyTitle") # Reusing the purple bold styling
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_msg = QLabel(message)
        lbl_msg.setObjectName("PrivacyText") # Reusing the black bold text styling
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
