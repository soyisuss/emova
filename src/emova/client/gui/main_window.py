from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStackedWidget
from emova.client.gui.components.header import TopHeader
from emova.client.gui.components.custom_dialog import CustomDialog
from emova.client.api_client import ApiClient
from emova.client.gui.windows.dashboard import DashboardView
from emova.client.gui.windows.password_change import PasswordChangeView
from emova.client.gui.windows.password_recovery import PasswordRecoveryView
from emova.client.gui.windows.register_task import RegisterTaskView
from emova.client.gui.windows.edit_tasks import EditTaskView
from emova.client.gui.windows.register_participant import RegisterParticipantView
from emova.client.gui.windows.login import LoginView
from emova.client.gui.windows.register_user import RegisterUserView
from emova.client.gui.windows.load_test_view import LoadTestView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EMOVA")
        self.setMinimumSize(1024, 768)
        
        # Contenedor central principal y diseño
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Agregar cabecera compartida (Top Header)
        self.header = TopHeader()
        main_layout.addWidget(self.header)
        
        # Gestor de vistas (Stack)
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)
        
        # Inicializar vistas
        self.view_dashboard = DashboardView()
        self.view_pwd_change = PasswordChangeView()
        self.view_pwd_recovery = PasswordRecoveryView()
        self.view_register_task = RegisterTaskView()
        self.view_edit_task = EditTaskView()
        self.view_register_participant = RegisterParticipantView()
        self.view_login = LoginView()
        self.view_register_user = RegisterUserView()
        self.view_load_test = LoadTestView()
        
        # Agregar vistas al stack con sus respectivos índices
        self.stack.addWidget(self.view_dashboard)             # Índice 0
        self.stack.addWidget(self.view_pwd_change)            # Índice 1
        self.stack.addWidget(self.view_pwd_recovery)          # Índice 2
        self.stack.addWidget(self.view_register_task)         # Índice 3
        self.stack.addWidget(self.view_edit_task)             # Índice 4
        self.stack.addWidget(self.view_register_participant)  # Índice 5
        self.stack.addWidget(self.view_login)                 # Índice 6
        self.stack.addWidget(self.view_register_user)         # Índice 7
        self.stack.addWidget(self.view_load_test)             # Índice 8
        
        # Connections
        self.api_client = ApiClient.get_instance()
        self.setup_connections()
        
        # Determinar la vista de inicio e hidratar el token
        if self.api_client.token:
            # Revalidar de manera silenciosa si existe un token persistente
            self.api_client.fetch_profile()
            self.stack.setCurrentIndex(0) # Mostrar dashboard temporalmente
        else:
            self.stack.setCurrentIndex(6)
        
    def setup_connections(self):
        # Enrutamiento desde la cabecera
        self.header.btn_login.clicked.connect(lambda: self.switch_view(6))      # Ir a Login
        self.header.btn_register.clicked.connect(lambda: self.switch_view(7))   # Ir a Registro de Usuario
        self.header.logo_label.mousePressEvent = lambda event: self.switch_view(0) # Clic en el logo redirige a inicio
        self.header.go_to_password_change.connect(lambda: self.switch_view(1))  # Ir a Cambio de Contraseña (Índice 1)
        self.header.logout_requested.connect(self._handle_logout)
        
        # Enrutamiento interno de vistas
        # Vista de cambio de contraseña
        self.view_pwd_change.go_back.connect(lambda: self.switch_view(0))
        
        # Vista de recuperación de contraseña
        self.view_pwd_recovery.go_back.connect(lambda: self.switch_view(6)) # Regresar a Login (índice 6)
        
        # Vista de inicio de sesión
        self.view_login.go_back.connect(lambda: self.switch_view(0))
        self.view_login.go_to_register.connect(lambda: self.switch_view(7))
        self.view_login.go_to_recovery.connect(lambda: self.switch_view(2)) # Ir a Recuperación de Contraseña
        
        # Estado de la sesión de autenticación
        self.api_client.profile_success.connect(self._on_profile_success)
        self.api_client.profile_error.connect(self._on_profile_error)
        
        # Vista de registro de usuario
        self.view_register_user.go_back.connect(lambda: self.switch_view(6))
        self.view_register_user.go_to_login.connect(lambda: self.switch_view(6))
        self.view_register_user.register_success.connect(self._on_register_success)
        
        # Rutas asociadas al registro de tareas y participantes
        self.view_dashboard.go_to_add_tasks.connect(lambda: self.switch_view(3))
        self.view_register_task.go_back.connect(lambda: self.switch_view(0))
        
        self.view_dashboard.go_to_edit_tasks.connect(lambda: self.switch_view(4))
        self.view_edit_task.go_back.connect(lambda: self.switch_view(0))
        self.view_edit_task.go_to_add.connect(lambda: self.switch_view(3)) # Enrutar directamente a creación de tareas
        
        self.view_dashboard.go_to_register_participant.connect(lambda: self.switch_view(5))
        self.view_register_participant.go_back.connect(lambda: self.switch_view(0))
        
        self.view_dashboard.go_to_load_test.connect(lambda: self.switch_view(8))
        self.view_load_test.go_back.connect(lambda: self.switch_view(0))
        
    def switch_view(self, index):
        """
        Cambia la vista activa del QStackedWidget.
        """
        # Middleware de protección de rutas (requiere sesión activa excepto para rutas no protegidas)
        unprotected_routes = [2, 6, 7] # Pantallas de recuperación, inicio de sesión y registro
        if not getattr(self.api_client, 'token', None) and index not in unprotected_routes:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Acceso Restringido", "Debes iniciar sesión para usar EMOVA.")
            self.stack.setCurrentIndex(6)
            return
            
        # Si se cambia a la vista de edición de tareas (índice 4), se recargan las tareas desde la sesión global
        if index == 4:
            self.view_edit_task.load_tasks_from_session()
        elif index == 8:
            self.view_load_test.load_templates()
            
        self.stack.setCurrentIndex(index)

    def _on_profile_success(self, user_data: dict):
        email = user_data.get("email", "Usuario")
        self.header.set_auth_state(True, email)
        
        # Evita mostrar el diálogo de bienvenida si se inicia sesión automáticamente mediante un token persistido
        was_login_screen = (self.stack.currentIndex() == 6)
        self.switch_view(0)
        
        if was_login_screen:
            dialog = CustomDialog(self, "Inicio de Sesión", f"¡Bienvenido! Has iniciado sesión como {email}.")
            dialog.exec()
            
    def _on_profile_error(self, message):
        """
        Cierra sesión de forma silenciosa si el token persistido expiró o es inválido.
        """
        self.api_client.set_token(None)
        self.header.set_auth_state(False)
        if self.stack.currentIndex() != 6:
            dialog = CustomDialog(self, "Sesión Caducada", "Tu sesión ha caducado. Por favor, inicia sesión nuevamente.")
            dialog.exec()
            self.stack.setCurrentIndex(6)
        
    def _on_register_success(self):
        self.switch_view(6)
        dialog = CustomDialog(self, "Registro Exitoso", "¡Tu cuenta ha sido creada exitosamente!\nPor favor, inicia sesión para continuar.")
        dialog.exec()
        
    def _handle_logout(self):
        self.api_client.set_token(None)
        self.header.set_auth_state(False)
        dialog = CustomDialog(self, "Sesión Cerrada", "Has cerrado tu sesión de forma segura.")
        dialog.exec()
        self.switch_view(6) # Redirigir siempre a la pantalla de Login

