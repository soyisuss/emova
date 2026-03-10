from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QFormLayout
from PySide6.QtCore import Qt, Signal

class PasswordChangeView(QWidget):
    go_back = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Back button row
        back_layout = QHBoxLayout()
        self.btn_back = QPushButton("← Regresar")
        self.btn_back.setProperty("class", "BackButton")
        self.btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_back.clicked.connect(self.go_back.emit)
        back_layout.addWidget(self.btn_back)
        back_layout.addStretch()
        layout.addLayout(back_layout)
        
        layout.addSpacing(40)
        
        # Center container
        center_layout = QVBoxLayout()
        center_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        center_widget = QWidget()
        center_widget.setMaximumWidth(500)
        cf_layout = QVBoxLayout(center_widget)
        cf_layout.setSpacing(20)
        
        # Title
        title = QLabel("Cambio de contraseña")
        title.setProperty("class", "FormTitle")
        # According to standard alignment context, form title rests on the top-left of the center form
        cf_layout.addWidget(title)
        
        # Inputs
        # Current Password
        lbl_current = QLabel("Contraseña actual:")
        lbl_current.setProperty("class", "FormLabel")
        input_current = QLineEdit()
        input_current.setEchoMode(QLineEdit.EchoMode.Password)
        
        cf_layout.addWidget(lbl_current)
        cf_layout.addWidget(input_current)
        
        # New password
        lbl_new = QLabel("Nueva contraseña:")
        lbl_new.setProperty("class", "FormLabel")
        input_new = QLineEdit()
        input_new.setEchoMode(QLineEdit.EchoMode.Password)
        
        cf_layout.addWidget(lbl_new)
        cf_layout.addWidget(input_new)
        
        # Password rules
        rules = QLabel(
            "<span style='color: #2E7D32;'>Aa Mayúscula</span><br>"
            "<span style='color: #000000;'>8 caracteres mínimo</span><br>"
            "<span style='color: #000000;'>+*- caracteres especiales</span>"
        )
        cf_layout.addWidget(rules)
        
        # Confirm password
        lbl_confirm = QLabel("Confirmar contraseña:")
        lbl_confirm.setProperty("class", "FormLabel")
        input_confirm = QLineEdit()
        input_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        
        cf_layout.addWidget(lbl_confirm)
        cf_layout.addWidget(input_confirm)
        
        # Error message mapping
        lbl_error = QLabel("La contraseña no coincide")
        lbl_error.setStyleSheet("color: #D32F2F; font-size: 12px; font-weight: bold;")
        cf_layout.addWidget(lbl_error)
        
        cf_layout.addSpacing(30)
        
        # Submit Button
        btn_submit = QPushButton("Actualizar")
        btn_submit.setProperty("class", "DialogButton") # Reusing similar styling
        btn_submit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_submit = btn_submit
        
        btn_wrapper = QHBoxLayout()
        btn_wrapper.addStretch()
        btn_wrapper.addWidget(btn_submit)
        btn_wrapper.addStretch()
        cf_layout.addLayout(btn_wrapper)
        
        center_layout.addWidget(center_widget)
        layout.addLayout(center_layout)
