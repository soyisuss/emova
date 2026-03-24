from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QFormLayout, QMessageBox
from PySide6.QtCore import Qt, Signal, QSize, QTimer
from PySide6.QtGui import QIcon

from emova.client.api_client import ApiClient
from emova.client.gui.components.custom_dialog import CustomDialog

class PasswordChangeView(QWidget):
    go_back = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.api_client = ApiClient.get_instance()
        self.api_client.change_password_success.connect(self._on_password_changed)
        self.api_client.change_password_error.connect(self._on_password_error)
        
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
        title = QLabel("Cambio de contraseña")
        title.setProperty("class", "FormTitle")
        title.setFixedHeight(50)
        # According to standard alignment context, form title rests on the top-left of the center form
        cf_layout.addWidget(title)
        
        cf_layout.addSpacing(10)
        
        # Inputs
        # Current Password
        lbl_current = QLabel("Contraseña actual:")
        lbl_current.setProperty("class", "FormLabel")
        cf_layout.addWidget(lbl_current)
        
        current_layout = QHBoxLayout()
        current_layout.setSpacing(5)
        self.input_current = QLineEdit()
        self.input_current.setFixedHeight(35)
        self.input_current.setEchoMode(QLineEdit.EchoMode.Password)
        
        btn_eye_current = QPushButton()
        btn_eye_current.setIcon(QIcon("src/emova/client/gui/assets/images/eye.svg"))
        btn_eye_current.setIconSize(QSize(24, 24))
        btn_eye_current.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_eye_current.setFixedSize(35, 35)
        btn_eye_current.setStyleSheet("background-color: transparent; border: none;")
        
        def toggle_current_pwd():
            if self.input_current.echoMode() == QLineEdit.EchoMode.Password:
                self.input_current.setEchoMode(QLineEdit.EchoMode.Normal)
                btn_eye_current.setIcon(QIcon("src/emova/client/gui/assets/images/eye_off.svg"))
            else:
                self.input_current.setEchoMode(QLineEdit.EchoMode.Password)
                btn_eye_current.setIcon(QIcon("src/emova/client/gui/assets/images/eye.svg"))
                
        btn_eye_current.clicked.connect(toggle_current_pwd)
        
        current_layout.addWidget(self.input_current)
        current_layout.addWidget(btn_eye_current)
        cf_layout.addLayout(current_layout)
        
        cf_layout.addSpacing(5)
        
        # New password
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
        
        import re
        self.rules = QLabel()
        self.rules.setWordWrap(True)
        cf_layout.addWidget(self.rules)
        cf_layout.addSpacing(10)
        
        def update_rules_ui(pwd: str = ""):
            has_upper = bool(re.search(r'[A-Z]', pwd))
            has_len = len(pwd) >= 8
            has_spec = bool(re.search(r'[\W_]', pwd))
            
            c_upper = "#2E7D32" if has_upper else "#000000"
            c_len = "#2E7D32" if has_len else "#000000"
            c_spec = "#2E7D32" if has_spec else "#000000"
            
            html = f'''
            <span style="color: {c_upper}; font-size: 13px;">Aa Mayúscula</span> &nbsp;•&nbsp; 
            <span style="color: {c_len}; font-size: 13px;">8 Mínimo</span> &nbsp;•&nbsp; 
            <span style="color: {c_spec}; font-size: 13px;">+*- Especiales</span>
            '''
            self.rules.setText(html)
            
        update_rules_ui("")
        self.input_new.textChanged.connect(update_rules_ui)
        
        # Confirm password
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
        
        # Error message mapping
        self.lbl_error = QLabel("La contraseña no coincide")
        self.lbl_error.setStyleSheet("color: #8C1C13; font-size: 14px; font-weight: bold;")
        self.lbl_error.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_error.setWordWrap(True)
        self.lbl_error.hide()
        cf_layout.addWidget(self.lbl_error)
        
        def validate_passwords():
            p1 = self.input_new.text()
            p2 = self.input_confirm.text()
            if p1 and p2 and p1 != p2:
                self.lbl_error.show()
            else:
                self.lbl_error.hide()
                
        self.input_new.textChanged.connect(validate_passwords)
        self.input_confirm.textChanged.connect(validate_passwords)
        
        cf_layout.addSpacing(30)
        
        cf_layout.addSpacing(5)
        
        # Submit Button
        btn_submit = QPushButton("Actualizar")
        btn_submit.setProperty("class", "DialogButton") # Reusing similar styling
        btn_submit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_submit.setFixedHeight(35)
        btn_submit.setMinimumWidth(200)
        self.btn_submit = btn_submit
        def handle_submit():
            self.lbl_error.hide()
            current_pass = self.input_current.text()
            new_pass = self.input_new.text()
            confirm_pass = self.input_confirm.text()
            
            if not current_pass or not new_pass or not confirm_pass:
                self.lbl_error.setText("Los campos no pueden estar vacíos")
                self.lbl_error.show()
                return
                
            if current_pass == new_pass:
                self.lbl_error.setText("La nueva contraseña no puede ser idéntica a la actual.")
                self.lbl_error.show()
                return
                
            if new_pass != confirm_pass:
                self.lbl_error.setText("La nueva contraseña no coincide")
                self.lbl_error.show()
                return
                
            self.btn_submit.setEnabled(False)
            self.btn_submit.setText("Actualizando...")
            self.api_client.change_password(current_pass, new_pass)
            
        btn_submit.clicked.connect(handle_submit)
        
        btn_wrapper = QHBoxLayout()
        btn_wrapper.addStretch()
        btn_wrapper.addWidget(btn_submit)
        btn_wrapper.addStretch()
        cf_layout.addLayout(btn_wrapper)
        
        center_layout.addWidget(center_widget)
        layout.addLayout(center_layout)
        layout.addStretch()

    def _on_password_changed(self, response: dict):
        self.btn_submit.setEnabled(True)
        self.btn_submit.setText("Actualizar")
        
        # Clear fields securely
        self.input_current.clear()
        self.input_new.clear()
        self.input_confirm.clear()
        
        # In parent window, we can pop the dialog, but let's just do it directly here.
        dialog = CustomDialog(self, "Actualización Exitosa", "Tu contraseña ha sido cambiada correctamente.")
        dialog.exec()
        
        self.go_back.emit()
        
    def _on_password_error(self, err_msg: str):
        self.btn_submit.setEnabled(True)
        self.btn_submit.setText("Actualizar")
        self.lbl_error.setText(f"Error: {err_msg}")
        self.lbl_error.show()
