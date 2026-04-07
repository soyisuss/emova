from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QStackedWidget
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon

from emova.client.api_client import ApiClient
from emova.client.gui.components.custom_dialog import CustomDialog

class PasswordRecoveryView(QWidget):
    go_back = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.api_client = ApiClient.get_instance()
        self.api_client.forgot_password_success.connect(self._on_forgot_success)
        self.api_client.forgot_password_error.connect(self._on_forgot_error)
        self.api_client.reset_password_success.connect(self._on_reset_success)
        self.api_client.reset_password_error.connect(self._on_reset_error)
        
        self.current_email = ""
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 20, 40, 20)
        
        # Back button row
        back_layout = QHBoxLayout()
        self.btn_back = QPushButton("← Regresar")
        self.btn_back.setProperty("class", "BackButton")
        self.btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Hook go_back to also reset state when returning to login
        self.btn_back.clicked.connect(self._go_back_clicked)
        back_layout.addWidget(self.btn_back)
        back_layout.addStretch()
        layout.addLayout(back_layout)
        
        layout.addSpacing(10)
        
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)
        
        self.setup_request_page()
        self.setup_reset_page()

    def _go_back_clicked(self):
        # Reset current stack index to 0 when going back, so next time we open it's on step 1
        self.stack.setCurrentIndex(0)
        self.input_email.clear()
        self.input_code.clear()
        self.input_new.clear()
        self.input_confirm.clear()
        self.lbl_req_error.hide()
        self.lbl_reset_error.hide()
        self.go_back.emit()
        
    def setup_request_page(self):
        self.page_request = QWidget()
        center_layout = QVBoxLayout(self.page_request)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        
        center_widget = QWidget()
        center_widget.setMaximumWidth(550)
        cf_layout = QVBoxLayout(center_widget)
        cf_layout.setSpacing(5)
        
        title = QLabel("Recuperación de contraseña")
        title.setProperty("class", "FormTitle")
        title.setFixedHeight(50)
        cf_layout.addWidget(title)
        cf_layout.addSpacing(20)
        
        info_text = QLabel("Ingresa tu correo electrónico y te enviaremos un código de recuperación.")
        info_text.setStyleSheet("font-size: 16px; color: #333333;")
        info_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_text.setWordWrap(True)
        cf_layout.addWidget(info_text)
        cf_layout.addSpacing(20)
        
        lbl_email = QLabel("Correo electrónico*:")
        lbl_email.setProperty("class", "FormLabel")
        cf_layout.addWidget(lbl_email)
        
        self.input_email = QLineEdit()
        self.input_email.setFixedHeight(45)
        self.input_email.setStyleSheet("padding: 5px; font-size: 16px;")
        cf_layout.addWidget(self.input_email)
        
        cf_layout.addSpacing(15)
        
        self.lbl_req_error = QLabel("")
        self.lbl_req_error.setStyleSheet("color: #8C1C13; font-size: 14px; font-weight: bold;")
        self.lbl_req_error.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_req_error.hide()
        cf_layout.addWidget(self.lbl_req_error)
        
        cf_layout.addSpacing(15)
        
        self.btn_request = QPushButton("Enviar código")
        self.btn_request.setProperty("class", "DialogButton")
        self.btn_request.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_request.setFixedHeight(35)
        self.btn_request.setMinimumWidth(200)
        self.btn_request.clicked.connect(self._handle_request)
        
        btn_wrapper = QHBoxLayout()
        btn_wrapper.addStretch()
        btn_wrapper.addWidget(self.btn_request)
        btn_wrapper.addStretch()
        cf_layout.addLayout(btn_wrapper)
        
        center_layout.addWidget(center_widget)
        self.stack.addWidget(self.page_request)
        
    def setup_reset_page(self):
        self.page_reset = QWidget()
        center_layout = QVBoxLayout(self.page_reset)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        
        center_widget = QWidget()
        center_widget.setMaximumWidth(550)
        cf_layout = QVBoxLayout(center_widget)
        cf_layout.setSpacing(5)
        
        title = QLabel("Restablecer contraseña")
        title.setProperty("class", "FormTitle")
        title.setFixedHeight(50)
        cf_layout.addWidget(title)
        cf_layout.addSpacing(20)
        
        self.lbl_reset_info = QLabel()
        self.lbl_reset_info.setStyleSheet("font-size: 16px; color: #333333;")
        self.lbl_reset_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_reset_info.setWordWrap(True)
        cf_layout.addWidget(self.lbl_reset_info)
        cf_layout.addSpacing(20)
        
        lbl_code = QLabel("Código de verificación*:")
        lbl_code.setProperty("class", "FormLabel")
        cf_layout.addWidget(lbl_code)
        
        self.input_code = QLineEdit()
        self.input_code.setFixedHeight(35)
        cf_layout.addWidget(self.input_code)
        cf_layout.addSpacing(5)
        
        lbl_new = QLabel("Nueva contraseña:")
        lbl_new.setProperty("class", "FormLabel")
        cf_layout.addWidget(lbl_new)
        
        pwd_layout = QHBoxLayout()
        pwd_layout.setSpacing(5)
        self.input_new = QLineEdit()
        self.input_new.setFixedHeight(35)
        self.input_new.setEchoMode(QLineEdit.EchoMode.Password)
        
        btn_eye = QPushButton()
        btn_eye.setIcon(QIcon("src/emova/client/gui/assets/images/eye.svg"))
        btn_eye.setIconSize(QSize(24, 24))
        btn_eye.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_eye.setFixedSize(35, 35)
        btn_eye.setStyleSheet("background-color: transparent; border: none;")
        
        def toggle_pwd():
            if self.input_new.echoMode() == QLineEdit.EchoMode.Password:
                self.input_new.setEchoMode(QLineEdit.EchoMode.Normal)
                btn_eye.setIcon(QIcon("src/emova/client/gui/assets/images/eye_off.svg"))
            else:
                self.input_new.setEchoMode(QLineEdit.EchoMode.Password)
                btn_eye.setIcon(QIcon("src/emova/client/gui/assets/images/eye.svg"))
                
        btn_eye.clicked.connect(toggle_pwd)
        pwd_layout.addWidget(self.input_new)
        pwd_layout.addWidget(btn_eye)
        cf_layout.addLayout(pwd_layout)
        cf_layout.addSpacing(5)
        
        self.lbl_rules = QLabel()
        self.lbl_rules.setWordWrap(True)
        cf_layout.addWidget(self.lbl_rules)
        cf_layout.addSpacing(10)
        
        def update_password_rules():
            text = self.input_new.text()
            has_upper = any(c.isupper() for c in text)
            has_length = len(text) >= 8
            has_special = any(not c.isalnum() for c in text)
            
            c_upper = "#2E7D32" if has_upper else "#888888"
            c_len = "#2E7D32" if has_length else "#888888"
            c_spec = "#2E7D32" if has_special else "#888888"
            
            self.lbl_rules.setText(
                f"<span style='color: {c_upper}; font-size: 13px;'>Aa Mayúscula</span> &nbsp;•&nbsp; "
                f"<span style='color: {c_len}; font-size: 13px;'>8 caracteres mínimo</span> &nbsp;•&nbsp; "
                f"<span style='color: {c_spec}; font-size: 13px;'>+*- caracteres especiales</span>"
            )
            
        self.input_new.textChanged.connect(update_password_rules)
        update_password_rules() # Initialize the form with grey rules
        
        lbl_confirm = QLabel("Confirmar contraseña:")
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
        
        self.lbl_reset_error = QLabel("La contraseña no coincide")
        self.lbl_reset_error.setStyleSheet("color: #8C1C13; font-size: 14px; font-weight: bold;")
        self.lbl_reset_error.hide()
        cf_layout.addWidget(self.lbl_reset_error)
        
        def validate_passwords():
            p1 = self.input_new.text()
            p2 = self.input_confirm.text()
            if p1 and p2 and p1 != p2:
                self.lbl_reset_error.setText("La contraseña no coincide")
                self.lbl_reset_error.show()
            else:
                self.lbl_reset_error.hide()
                
        self.input_new.textChanged.connect(validate_passwords)
        self.input_confirm.textChanged.connect(validate_passwords)
        
        cf_layout.addSpacing(15)
        
        self.btn_reset = QPushButton("Cambiar contraseña")
        self.btn_reset.setProperty("class", "DialogButton")
        self.btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset.setFixedHeight(35)
        self.btn_reset.setMinimumWidth(200)
        self.btn_reset.clicked.connect(self._handle_reset)
        
        btn_wrapper = QHBoxLayout()
        btn_wrapper.addStretch()
        btn_wrapper.addWidget(self.btn_reset)
        btn_wrapper.addStretch()
        cf_layout.addLayout(btn_wrapper)
        
        center_layout.addWidget(center_widget)
        self.stack.addWidget(self.page_reset)
        
    def _handle_request(self):
        self.lbl_req_error.hide()
        email = self.input_email.text().strip()
        if not email:
            self.lbl_req_error.setText("Por favor, ingresa tu correo electrónico.")
            self.lbl_req_error.show()
            return
            
        self.current_email = email
        self.btn_request.setEnabled(False)
        self.btn_request.setText("Enviando...")
        self.api_client.forgot_password(email)
        
    def _on_forgot_success(self, res: dict):
        self.btn_request.setEnabled(True)
        self.btn_request.setText("Enviar código")
        self.lbl_reset_info.setText(f"ⓘ Se ha enviado un código de verificación a tu correo\n\"{self.current_email}\", ingresalo para restablecer tu contraseña.")
        self.stack.setCurrentIndex(1)
        
    def _on_forgot_error(self, err_msg: str):
        self.btn_request.setEnabled(True)
        self.btn_request.setText("Enviar código")
        self.lbl_req_error.setText(f"Error: {err_msg}")
        self.lbl_req_error.show()
        
    def _handle_reset(self):
        self.lbl_reset_error.hide()
        code = self.input_code.text().strip()
        new_pwd = self.input_new.text()
        confirm_pwd = self.input_confirm.text()
        
        if not code or not new_pwd or not confirm_pwd:
            self.lbl_reset_error.setText("Todos los campos son obligatorios.")
            self.lbl_reset_error.show()
            return
            
        if new_pwd != confirm_pwd:
            self.lbl_reset_error.setText("La contraseña no coincide")
            self.lbl_reset_error.show()
            return
            
        self.btn_reset.setEnabled(False)
        self.btn_reset.setText("Cambiando...")
        self.api_client.reset_password(self.current_email, code, new_pwd)
        
    def _on_reset_success(self, res: dict):
        self.btn_reset.setEnabled(True)
        self.btn_reset.setText("Cambiar contraseña")
        self.input_code.clear()
        self.input_new.clear()
        self.input_confirm.clear()
        self.input_email.clear()
        self.stack.setCurrentIndex(0)
        
        dialog = CustomDialog(self, "Recuperación Exitosa", "Tu contraseña ha sido restablecida correctamente.\nYa puedes iniciar sesión.")
        dialog.exec()
        self.go_back.emit()
        
    def _on_reset_error(self, err_msg: str):
        self.btn_reset.setEnabled(True)
        self.btn_reset.setText("Cambiar contraseña")
        self.lbl_reset_error.setText(f"Error: {err_msg}")
        self.lbl_reset_error.show()
