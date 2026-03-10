from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStackedWidget
from emova.gui.components.header import TopHeader
from emova.gui.views.dashboard import DashboardView
from emova.gui.views.password_change import PasswordChangeView
from emova.gui.views.password_recovery import PasswordRecoveryView
from emova.gui.views.register_task import RegisterTaskView
from emova.gui.views.edit_tasks import EditTaskView
from emova.gui.views.register_participant import RegisterParticipantView

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
        
        # Add views to stack
        self.stack.addWidget(self.view_dashboard)             # Index 0
        self.stack.addWidget(self.view_pwd_change)            # Index 1
        self.stack.addWidget(self.view_pwd_recovery)          # Index 2
        self.stack.addWidget(self.view_register_task)         # Index 3
        self.stack.addWidget(self.view_edit_task)             # Index 4
        self.stack.addWidget(self.view_register_participant)  # Index 5
        
        # Connections
        self.setup_connections()
        
    def setup_connections(self):
        # Header routing
        self.header.action_login.triggered.connect(lambda: self.switch_view(1))    # To Change Pwd
        self.header.action_register.triggered.connect(lambda: self.switch_view(2)) # To Recovery Pwd
        self.header.logo_label.mousePressEvent = lambda event: self.switch_view(0) # Click logo to go home
        
        # View internal routing
        self.view_pwd_change.go_back.connect(lambda: self.switch_view(0))
        self.view_pwd_recovery.go_back.connect(lambda: self.switch_view(0))
        
        # New Registration Views Routing
        self.view_dashboard.go_to_add_tasks.connect(lambda: self.switch_view(3))
        self.view_register_task.go_back.connect(lambda: self.switch_view(0))
        
        self.view_dashboard.go_to_edit_tasks.connect(lambda: self.switch_view(4))
        self.view_edit_task.go_back.connect(lambda: self.switch_view(0))
        
        self.view_dashboard.go_to_register_participant.connect(lambda: self.switch_view(5))
        self.view_register_participant.go_back.connect(lambda: self.switch_view(0))
        
    def switch_view(self, index):
        """Helper to change the visible widget in the stack"""
        self.stack.setCurrentIndex(index)
