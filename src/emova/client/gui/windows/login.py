from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon

from emova.client.api_client import ApiClient

class LoginView(QWidget):
    go_back = Signal()
    go_to_register = Signal()
    go_to_recovery = Signal()
    login_success = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.api_client = ApiClient.get_instance()
        self.api_client.login_success.connect(self._on_login_res)
        self.api_client.login_error.connect(self._on_login_err)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 20, 40, 20)
        
        # Back button row
        back_layout = QHBoxLayout()
        self.btn_back = QPushButton("← Regresar")
        self.btn_back.setObjectName("btnBack")
        self.btn_back.setProperty("class", "BackButton")
        self.btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_back.clicked.connect(self.go_back.emit)
        self.btn_back.hide() # Oculto por seguridad, la app inicia aquí
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
        
        self.input_email = QLineEdit()
        self.input_email.setObjectName("inputEmail")
        cf_layout.addWidget(self.input_email)
        
        cf_layout.addSpacing(5)
        
        # Password Input
        lbl_password = QLabel("Contraseña*:")
        lbl_password.setProperty("class", "FormLabel")
        cf_layout.addWidget(lbl_password)
        
        pwd_layout = QHBoxLayout()
        pwd_layout.setSpacing(5)
        self.input_password = QLineEdit()
        self.input_password.setObjectName("inputPassword")
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        
        btn_eye = QPushButton()
        btn_eye.setObjectName("btnTogglePassword")
        btn_eye.setIcon(QIcon("src/emova/client/gui/assets/images/eye.svg"))
        btn_eye.setIconSize(QSize(24, 24))
        btn_eye.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_eye.setFixedSize(40, 40)
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
        
        # Obligatorio Text
        obligatorio = QLabel("*Campos obligatorios")
        obligatorio.setStyleSheet("font-size: 12px; font-weight: bold; color: black;")
        cf_layout.addWidget(obligatorio)
        
        cf_layout.addSpacing(10)
        
        # Submit Button
        btn_submit = QPushButton("Ingresar")
        btn_submit.setObjectName("btnLoginSubmit")
        btn_submit.setProperty("class", "DialogButton")
        btn_submit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_submit.setMinimumWidth(200)
        self.btn_submit = btn_submit
        
        # Error Label
        self.lbl_error = QLabel("")
        self.lbl_error.setObjectName("lblLoginError")
        self.lbl_error.setStyleSheet("color: #8C1C13; font-size: 14px; font-weight: bold;") 
        self.lbl_error.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_error.hide()
        cf_layout.addWidget(self.lbl_error)
        
        def handle_login_click():
            self.lbl_error.hide()
            email = self.input_email.text()
            pwd = self.input_password.text()
            if not email or not pwd:
                self.lbl_error.setText("Los campos no pueden estar vacíos")
                self.lbl_error.show()
                return
            self.btn_submit.setEnabled(False)
            self.btn_submit.setText("Autenticando...")
            self.api_client.login(email, pwd)
            
        btn_submit.clicked.connect(handle_login_click)
        
        btn_wrapper = QHBoxLayout()
        btn_wrapper.addStretch()
        btn_wrapper.addWidget(btn_submit)
        btn_wrapper.addStretch()
        cf_layout.addLayout(btn_wrapper)
        
        cf_layout.addSpacing(10)
        
        # Forgot Password Link
        btn_forgot = QPushButton("Olvide mi contraseña")
        btn_forgot.setObjectName("btnForgotPassword")
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
        btn_register.setObjectName("btnRegister")
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

    def _on_login_res(self, token: str):
        self.btn_submit.setEnabled(True)
        self.btn_submit.setText("Ingresar")
        self.input_email.clear()
        self.input_password.clear()
        self.login_success.emit()
        
    def _on_login_err(self, err_msg: str):
        self.btn_submit.setEnabled(True)
        self.btn_submit.setText("Ingresar")
        self.lbl_error.setText(f"Error: {err_msg}")
        self.lbl_error.show()
