from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon

class RegisterUserView(QWidget):
    go_back = Signal()
    go_to_login = Signal()
    register_success = Signal()
    
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
        title = QLabel("Crear Cuenta")
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
        self.input_password = QLineEdit()
        self.input_password.setFixedHeight(35)
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        
        btn_eye = QPushButton()
        btn_eye.setIcon(QIcon("src/emova/client/gui/assets/images/eye.svg"))
        btn_eye.setIconSize(QSize(24, 24))
        btn_eye.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_eye.setFixedSize(35, 35)
        btn_eye.setStyleSheet("background-color: transparent; border: none;")
        
        def toggle_pwd():
            if self.input_password.echoMode() == QLineEdit.EchoMode.Password:
                self.input_password.setEchoMode(QLineEdit.EchoMode.Normal)
                btn_eye.setIcon(QIcon("src/emova/client/gui/assets/images/eye_off.svg"))
            else:
                self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
                btn_eye.setIcon(QIcon("src/emova/client/gui/assets/images/eye.svg"))
                
        btn_eye.clicked.connect(toggle_pwd)
        
        pwd_layout.addWidget(self.input_password)
        pwd_layout.addWidget(btn_eye)
        cf_layout.addLayout(pwd_layout)
        
        cf_layout.addSpacing(5)
        
        # Password rules
        rules = QLabel(
            "<span style='color: #2E7D32; font-size: 13px;'>Aa Mayúscula</span> &nbsp;•&nbsp; "
            "<span style='color: #000000; font-size: 13px;'>8 caracteres mínimo</span> &nbsp;•&nbsp; "
            "<span style='color: #000000; font-size: 13px;'>+*- caracteres especiales</span>"
        )
        rules.setWordWrap(True)
        cf_layout.addWidget(rules)
        cf_layout.addSpacing(10)
        
        # Confirm password
        lbl_confirm = QLabel("Confirmar contraseña*:")
        lbl_confirm.setProperty("class", "FormLabel")
        cf_layout.addWidget(lbl_confirm)
        
        confirm_layout = QHBoxLayout()
        confirm_layout.setSpacing(5)
        self.input_confirm = QLineEdit()
        self.input_confirm.setFixedHeight(35)
        self.input_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        
        btn_eye_confirm = QPushButton()
        btn_eye_confirm.setIcon(QIcon("src/emova/client/gui/assets/images/eye.svg"))
        btn_eye_confirm.setIconSize(QSize(24, 24))
        btn_eye_confirm.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_eye_confirm.setFixedSize(35, 35)
        btn_eye_confirm.setStyleSheet("background-color: transparent; border: none;")
        
        def toggle_confirm_pwd():
            if self.input_confirm.echoMode() == QLineEdit.EchoMode.Password:
                self.input_confirm.setEchoMode(QLineEdit.EchoMode.Normal)
                btn_eye_confirm.setIcon(QIcon("src/emova/client/gui/assets/images/eye_off.svg"))
            else:
                self.input_confirm.setEchoMode(QLineEdit.EchoMode.Password)
                btn_eye_confirm.setIcon(QIcon("src/emova/client/gui/assets/images/eye.svg"))
                
        btn_eye_confirm.clicked.connect(toggle_confirm_pwd)
        
        confirm_layout.addWidget(self.input_confirm)
        confirm_layout.addWidget(btn_eye_confirm)
        cf_layout.addLayout(confirm_layout)
        
        cf_layout.addSpacing(5)
        
        # Error message mapping
        self.lbl_error = QLabel("La contraseña no coincide")
        self.lbl_error.setStyleSheet("color: #8C1C13; font-size: 14px; font-weight: bold;") 
        self.lbl_error.hide() # Hidden by default
        cf_layout.addWidget(self.lbl_error)
        
        def validate_passwords():
            p1 = self.input_password.text()
            p2 = self.input_confirm.text()
            if p1 and p2 and p1 != p2:
                self.lbl_error.show()
            else:
                self.lbl_error.hide()
                
        self.input_password.textChanged.connect(validate_passwords)
        self.input_confirm.textChanged.connect(validate_passwords)
        
        # Obligatorio Text
        obligatorio = QLabel("*Campos obligatorios")
        obligatorio.setStyleSheet("font-size: 12px; font-weight: bold; color: black;")
        cf_layout.addWidget(obligatorio)
        
        cf_layout.addSpacing(10)
        
        # Submit Button
        btn_submit = QPushButton("Registrarse")
        btn_submit.setProperty("class", "DialogButton") # Reusing similar styling
        btn_submit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_submit.setFixedHeight(35)
        btn_submit.setMinimumWidth(200)
        self.btn_submit = btn_submit
        
        btn_submit.clicked.connect(self.register_success.emit)
        
        btn_wrapper = QHBoxLayout()
        btn_wrapper.addStretch()
        btn_wrapper.addWidget(btn_submit)
        btn_wrapper.addStretch()
        cf_layout.addLayout(btn_wrapper)
        
        cf_layout.addSpacing(30)
        
        # Footer section (Already have an account?)
        lbl_has_account = QLabel("¿Ya tienes cuenta?")
        lbl_has_account.setStyleSheet("font-size: 18px; font-weight: bold; color: black;")
        lbl_has_account.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cf_layout.addWidget(lbl_has_account)
        
        btn_login = QPushButton("Iniciar sesión")
        btn_login.setStyleSheet("border: none; background: transparent; color: #7b2cbf; font-size: 16px; font-weight: bold;")
        btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_login.clicked.connect(self.go_to_login.emit)
        
        login_wrapper = QHBoxLayout()
        login_wrapper.addStretch()
        login_wrapper.addWidget(btn_login)
        login_wrapper.addStretch()
        cf_layout.addLayout(login_wrapper)
        
        center_layout.addWidget(center_widget)
        layout.addLayout(center_layout)
        layout.addStretch()
