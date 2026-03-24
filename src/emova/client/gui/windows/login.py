from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon

class LoginView(QWidget):
    go_back = Signal()
    go_to_register = Signal()
    go_to_recovery = Signal()
    login_success = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 20, 40, 20)
        
        # Back button row
        back_layout = QHBoxLayout()
        self.btn_back = QPushButton("← Regresar")
        self.btn_back.setProperty("class", "BackButton")
        self.btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_back.clicked.connect(self.go_back.emit)
        back_layout.addWidget(self.btn_back)
        back_layout.addStretch()
        layout.addLayout(back_layout)
        
        layout.addSpacing(10)
        
        # Center container
        center_layout = QVBoxLayout()
        center_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        center_widget = QWidget()
        center_widget.setMaximumWidth(500)
        cf_layout = QVBoxLayout(center_widget)
        cf_layout.setSpacing(5)
        
        # Title
        title = QLabel("Inicio de sesión")
        title.setProperty("class", "FormTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFixedHeight(50)
        cf_layout.addWidget(title)
        
        cf_layout.addSpacing(20)
        
        # Email Input
        lbl_email = QLabel("Correo electrónico*:")
        lbl_email.setProperty("class", "FormLabel")
        cf_layout.addWidget(lbl_email)
        
        input_email = QLineEdit()
        input_email.setFixedHeight(35)
        cf_layout.addWidget(input_email)
        
        cf_layout.addSpacing(5)
        
        # Password Input
        lbl_password = QLabel("Contraseña*:")
        lbl_password.setProperty("class", "FormLabel")
        cf_layout.addWidget(lbl_password)
        
        pwd_layout = QHBoxLayout()
        pwd_layout.setSpacing(5)
        input_password = QLineEdit()
        input_password.setFixedHeight(35)
        input_password.setEchoMode(QLineEdit.EchoMode.Password)
        
        btn_eye = QPushButton()
        btn_eye.setIcon(QIcon("src/emova/client/gui/assets/images/eye.svg"))
        btn_eye.setIconSize(QSize(24, 24))
        btn_eye.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_eye.setFixedSize(35, 35)
        btn_eye.setStyleSheet("background-color: transparent; border: none;")
        
        def toggle_pwd():
            if input_password.echoMode() == QLineEdit.EchoMode.Password:
                input_password.setEchoMode(QLineEdit.EchoMode.Normal)
                btn_eye.setIcon(QIcon("src/emova/client/gui/assets/images/eye_off.svg"))
            else:
                input_password.setEchoMode(QLineEdit.EchoMode.Password)
                btn_eye.setIcon(QIcon("src/emova/client/gui/assets/images/eye.svg"))
                
        btn_eye.clicked.connect(toggle_pwd)
        
        pwd_layout.addWidget(input_password)
        pwd_layout.addWidget(btn_eye)
        cf_layout.addLayout(pwd_layout)
        
        cf_layout.addSpacing(5)
        
        # Obligatorio Text
        obligatorio = QLabel("*Campos obligatorios")
        obligatorio.setStyleSheet("font-size: 12px; font-weight: bold; color: black;")
        cf_layout.addWidget(obligatorio)
        
        cf_layout.addSpacing(10)
        
        # Submit Button
        btn_submit = QPushButton("Ingresar")
        btn_submit.setProperty("class", "DialogButton")
        btn_submit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_submit.setFixedHeight(35)
        btn_submit.setMinimumWidth(200)
        self.btn_submit = btn_submit
        
        # For this prototype we will emit success unconditionally
        btn_submit.clicked.connect(self.login_success.emit)
        
        btn_wrapper = QHBoxLayout()
        btn_wrapper.addStretch()
        btn_wrapper.addWidget(btn_submit)
        btn_wrapper.addStretch()
        cf_layout.addLayout(btn_wrapper)
        
        cf_layout.addSpacing(10)
        
        # Forgot Password Link
        btn_forgot = QPushButton("Olvide mi contraseña")
        btn_forgot.setStyleSheet("border: none; background: transparent; color: #666666; font-size: 14px; font-weight: bold; text-decoration: none;")
        btn_forgot.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_forgot.clicked.connect(self.go_to_recovery.emit)
        
        forgot_wrapper = QHBoxLayout()
        forgot_wrapper.addStretch()
        forgot_wrapper.addWidget(btn_forgot)
        forgot_wrapper.addStretch()
        cf_layout.addLayout(forgot_wrapper)
        
        cf_layout.addSpacing(30)
        
        # Footer section (Don't have an account?)
        lbl_no_account = QLabel("¿No tienes cuenta?")
        lbl_no_account.setStyleSheet("font-size: 18px; font-weight: bold; color: black;")
        lbl_no_account.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cf_layout.addWidget(lbl_no_account)
        
        btn_register = QPushButton("Registrate")
        btn_register.setStyleSheet("border: none; background: transparent; color: #7b2cbf; font-size: 16px; font-weight: bold;")
        btn_register.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_register.clicked.connect(self.go_to_register.emit)
        
        register_wrapper = QHBoxLayout()
        register_wrapper.addStretch()
        register_wrapper.addWidget(btn_register)
        register_wrapper.addStretch()
        cf_layout.addLayout(register_wrapper)
        
        center_layout.addWidget(center_widget)
        layout.addLayout(center_layout)
        layout.addStretch()
