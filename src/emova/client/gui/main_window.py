from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStackedWidget
from emova.client.gui.components.header import TopHeader
from emova.client.gui.windows.dashboard import DashboardView
from emova.client.gui.windows.password_change import PasswordChangeView
from emova.client.gui.windows.password_recovery import PasswordRecoveryView
from emova.client.gui.windows.register_task import RegisterTaskView
from emova.client.gui.windows.edit_tasks import EditTaskView
from emova.client.gui.windows.register_participant import RegisterParticipantView
from emova.client.gui.windows.login import LoginView
from emova.client.gui.windows.register_user import RegisterUserView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EMOVA")
        self.setMinimumSize(1024, 768)
        
        # Main central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Add shared top header
        self.header = TopHeader()
        main_layout.addWidget(self.header)
        
        # View manager
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)
        
        # Initialize Views
        self.view_dashboard = DashboardView()
        self.view_pwd_change = PasswordChangeView()
        self.view_pwd_recovery = PasswordRecoveryView()
        self.view_register_task = RegisterTaskView()
        self.view_edit_task = EditTaskView()
        self.view_register_participant = RegisterParticipantView()
        self.view_login = LoginView()
        self.view_register_user = RegisterUserView()
        
        # Add views to stack
        self.stack.addWidget(self.view_dashboard)             # Index 0
        self.stack.addWidget(self.view_pwd_change)            # Index 1
        self.stack.addWidget(self.view_pwd_recovery)          # Index 2
        self.stack.addWidget(self.view_register_task)         # Index 3
        self.stack.addWidget(self.view_edit_task)             # Index 4
        self.stack.addWidget(self.view_register_participant)  # Index 5
        self.stack.addWidget(self.view_login)                 # Index 6
        self.stack.addWidget(self.view_register_user)         # Index 7
        
        # Connections
        self.setup_connections()
        
    def setup_connections(self):
        # Header routing
        self.header.btn_login.clicked.connect(lambda: self.switch_view(6))      # To Login
        self.header.btn_register.clicked.connect(lambda: self.switch_view(7))   # To Register User
        self.header.logo_label.mousePressEvent = lambda event: self.switch_view(0) # Click logo to go home
        
        # View internal routing
        # Change Password View
        self.view_pwd_change.go_back.connect(lambda: self.switch_view(0))
        
        # Password Recovery View
        self.view_pwd_recovery.go_back.connect(lambda: self.switch_view(6)) # Go back to Login (index 6) from Recovery
        
        # Login View Routing
        self.view_login.go_back.connect(lambda: self.switch_view(0))
        self.view_login.go_to_register.connect(lambda: self.switch_view(7))
        self.view_login.go_to_recovery.connect(lambda: self.switch_view(2)) # To Recovery Pwd
        self.view_login.login_success.connect(lambda: self.switch_view(0))
        
        # Register User View Routing
        self.view_register_user.go_back.connect(lambda: self.switch_view(0))
        self.view_register_user.go_to_login.connect(lambda: self.switch_view(6))
        self.view_register_user.register_success.connect(lambda: self.switch_view(6)) # Go to login after register? or dashboard. Let's go to login.
        
        # New Registration Views Routing
        self.view_dashboard.go_to_add_tasks.connect(lambda: self.switch_view(3))
        self.view_register_task.go_back.connect(lambda: self.switch_view(0))
        
        self.view_dashboard.go_to_edit_tasks.connect(lambda: self.switch_view(4))
        self.view_edit_task.go_back.connect(lambda: self.switch_view(0))
        self.view_edit_task.go_to_add.connect(lambda: self.switch_view(3)) # Route to Create Task View directly
        
        self.view_dashboard.go_to_register_participant.connect(lambda: self.switch_view(5))
        self.view_register_participant.go_back.connect(lambda: self.switch_view(0))
        
    def switch_view(self, index):
        """Helper to change the visible widget in the stack"""
        # If switching TO Edit Tasks (index 4), force it to reload UI dynamically from global state
        if index == 4:
            self.view_edit_task.load_tasks_from_session()
            
        self.stack.setCurrentIndex(index)
