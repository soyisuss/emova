from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QRadioButton, QButtonGroup, QScrollArea, QFrame, QMessageBox
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIntValidator

from emova.core.session.session_manager import session_manager
from emova.client.gui.components.custom_dialog import CustomDialog

class RegisterParticipantView(QWidget):
    go_back = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 20, 40, 40)
        main_layout.setSpacing(20)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # --- Barra de navegación superior ---
        top_layout = QHBoxLayout()
        
        btn_back = QPushButton("← Regresar")
        btn_back.setProperty("class", "BackButton")
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.clicked.connect(self.go_back.emit)
        
        title = QLabel("Registro de participante")
        title.setProperty("class", "ViewTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        top_layout.addWidget(btn_back)
        top_layout.addStretch()
        top_layout.addWidget(title)
        top_layout.addStretch()
        dummy = QWidget()
        dummy.setFixedWidth(btn_back.sizeHint().width() if btn_back.sizeHint().width() > 0 else 100)
        top_layout.addWidget(dummy)
        
        main_layout.addLayout(top_layout)
        
        # --- Área de contenido desplazable ---
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("background-color: transparent;")
        
        scroll_widget = QWidget()
        form_layout = QVBoxLayout(scroll_widget)
        form_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        form_layout.setSpacing(25)
        form_layout.setContentsMargins(40, 20, 40, 20)
        
        # ID del participante
        lbl_id = QLabel("ID.Participante:001")
        lbl_id.setProperty("class", "TaskNumberLabel") # Reutiliza el estilo morado en negrita
        form_layout.addWidget(lbl_id)
        
        # Edad
        lbl_age = QLabel("Edad:")
        lbl_age_hint = QLabel("(Solo número)")
        lbl_age_hint.setStyleSheet("font-size: 11px; color: black; font-weight: bold;")
        
        self.input_age = QLineEdit()
        self.input_age.setValidator(QIntValidator(1, 120)) # Permitir únicamente números
        self.input_age.setFixedWidth(150)
        
        form_layout.addWidget(lbl_age)
        form_layout.addWidget(self.input_age)
        form_layout.addWidget(lbl_age_hint)
        
        # Género
        lbl_gender = QLabel("Genero:")
        form_layout.addWidget(lbl_gender)
        
        gender_layout = QHBoxLayout()
        self.btn_gender_group = QButtonGroup(self)
        
        rad_masc = QRadioButton("Masculino")
        rad_fem = QRadioButton("Femenino")
        rad_prefer = QRadioButton("Prefiero no responder")
        
        self.btn_gender_group.addButton(rad_masc)
        self.btn_gender_group.addButton(rad_fem)
        self.btn_gender_group.addButton(rad_prefer)
        
        gender_layout.addWidget(rad_masc)
        gender_layout.addWidget(rad_fem)
        gender_layout.addWidget(rad_prefer)
        gender_layout.addStretch()
        
        form_layout.addLayout(gender_layout)
        
        # Ocupación
        lbl_occ = QLabel("Ocupación:")
        self.input_occ = QLineEdit()
        self.input_occ.setFixedWidth(500)
        
        form_layout.addWidget(lbl_occ)
        form_layout.addWidget(self.input_occ)
        
        # Cuestionario de frecuencia
        lbl_freq = QLabel("¿Con qué frecuencia utiliza aplicaciones o sistemas digitales (apps, páginas web,\nplataformas)?")
        lbl_freq.setWordWrap(True)
        form_layout.addWidget(lbl_freq)
        form_layout.addSpacing(10)
        
        self.btn_freq_group = QButtonGroup(self)
        
        freq_options = [
            "Todos los días",
            "Varias veces a la semana",
            "Una vez por semana",
            "Casi nunca"
        ]
        
        for option in freq_options:
            rad = QRadioButton(option)
            self.btn_freq_group.addButton(rad)
            form_layout.addWidget(rad)
            form_layout.addSpacing(5)
            
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area, stretch=1)
        
        # --- Botón inferior para finalizar ---
        bottom_layout = QHBoxLayout()
        btn_finalize = QPushButton("Finalizar registro")
        btn_finalize.setProperty("class", "PrimaryButton")
        btn_finalize.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_finalize.setFixedWidth(300)
        
        bottom_layout.addStretch()
        bottom_layout.addWidget(btn_finalize)
        bottom_layout.addStretch()
        
        main_layout.addLayout(bottom_layout)
        
        # Conectar la acción de finalización
        btn_finalize.clicked.connect(self.save_participant)

    def save_participant(self):
        # Obtener la edad
        age = self.input_age.text().strip()
        
        # Obtener el género
        gender = "No especificado"
        checked_gender = self.btn_gender_group.checkedButton()
        if checked_gender:
            gender = checked_gender.text()
            
        # Obtener la ocupación
        occupation = self.input_occ.text().strip()
        
        # Obtener la frecuencia de uso
        frequency = "No especificado"
        checked_freq = self.btn_freq_group.checkedButton()
        if checked_freq:
            frequency = checked_freq.text()
            
        data = {
            "Edad": age if age else "No proporcionado",
            "Género": gender,
            "Ocupación": occupation if occupation else "No proporcionado",
            "Frecuencia de Uso Digital": frequency
        }
        
        # Guardar de forma segura en el estado central de la aplicación
        session_manager.set_participant(data)
        
        dialog = CustomDialog(
            parent=self.window(),
            title="Registro Exitoso",
            message="Datos del participante guardados exitosamente en la sesión actual."
        )
        dialog.exec()
        
        self.go_back.emit()
