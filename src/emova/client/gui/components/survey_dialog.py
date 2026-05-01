from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QRadioButton, QButtonGroup, QTextEdit, QScrollArea, QWidget, QMessageBox, QFrame
)
from PySide6.QtCore import Qt

from emova.core.session.session_manager import session_manager

class UsabilitySurveyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SurveyDialog")
        self.setWindowTitle("Encuesta de Usabilidad")
        self.setFixedSize(700, 800)
        
        # Diseño de Fondo
        self.setStyleSheet("""
            QDialog {
                background-color: #F4F6F9;
            }
        """)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Area desplazable
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        # Contenedor central (tarjeta blanca)
        content_widget = QWidget()
        content_widget.setObjectName("ContentContainer")
        content_widget.setStyleSheet("""
            QWidget#ContentContainer {
                background-color: white;
                border-radius: 12px;
            }
        """)
        
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setContentsMargins(40, 40, 40, 40)
        self.content_layout.setSpacing(25)
        
        title_lbl = QLabel("Prueba Finalizada")
        title_lbl.setStyleSheet("font-size: 26px; font-weight: bold; color: #7E38B7;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        subtitle_lbl = QLabel("Evalúa tu experiencia con cada tarea realizada y con la interfaz en general.\n(1 = Muy difícil/Muy en desacuerdo, 5 = Muy fácil/Muy de acuerdo)")
        subtitle_lbl.setStyleSheet("font-size: 15px; color: #666666; margin-bottom: 10px;")
        subtitle_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_lbl.setWordWrap(True)
        
        self.content_layout.addWidget(title_lbl)
        self.content_layout.addWidget(subtitle_lbl)
        
        # Separator Línea Desvanecida
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #DDDDDD; margin-bottom: 10px;")
        self.content_layout.addWidget(line)
        
        # Get tasks from session manager
        tasks = session_manager.tasks
        
        # === PER-TASK QUESTIONS ===
        self.questions_data = []
        
        if tasks:
            # Section title for tasks
            task_section_lbl = QLabel("EVALUACIÓN DE TAREAS")
            task_section_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #7E38B7; margin-top: 10px;")
            task_section_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.content_layout.addWidget(task_section_lbl)
            
            for idx, task in enumerate(tasks):
                task_title = task.get("title", f"Tarea {idx + 1}")
                
                # Question for this specific task
                self.questions_data.append((
                    f"task_{idx}_ease",
                    f"{idx + 1}. ¿Qué tan fácil fue realizar la tarea: \"{task_title}\"?"
                ))
        
        # === GENERAL USABILITY QUESTIONS (4 questions) ===
        general_section_lbl = QLabel("EVALUACIÓN GENERAL DE USABILIDAD")
        general_section_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #7E38B7; margin-top: 20px;")
        general_section_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(general_section_lbl)
        
        # Add 4 general usability questions
        general_questions = [
            ("ease_of_use", "La interfaz general fue fácil de utilizar."),
            ("navigation", "Fue intuitivo navegar por la plataforma."),
            ("difficulty", "¿Qué tan difícil fue completar las tareas?"),
            ("satisfaction", "Estoy satisfecho con la experiencia general.")
        ]
        
        # Offset for general questions
        question_offset = len(tasks) if tasks else 0
        
        for idx, (key, text) in enumerate(general_questions):
            self.questions_data.append((
                key,
                f"{idx + 1 + question_offset}. {text}"
            ))
        
        self.button_groups = {}
        
        for key, text in self.questions_data:
            q_widget = QWidget()
            q_layout = QVBoxLayout(q_widget)
            q_layout.setContentsMargins(0, 0, 0, 0)
            q_layout.setSpacing(10)
            
            q_lbl = QLabel(text)
            q_lbl.setStyleSheet("font-weight: 600; font-size: 15px; color: #333;")
            q_lbl.setWordWrap(True)
            q_layout.addWidget(q_lbl)
            
            opts_layout = QHBoxLayout()
            opts_layout.setSpacing(15)
            
            # Etiqueta Menor
            lbl_low = QLabel("Muy difícil (1)")
            lbl_low.setStyleSheet("color: #999; font-size: 12px; margin-right: 10px;")
            opts_layout.addWidget(lbl_low)
            
            bgroup = QButtonGroup(self)
            self.button_groups[key] = bgroup
            
            for i in range(1, 6):
                rb = QRadioButton(str(i))
                rb.setCursor(Qt.CursorShape.PointingHandCursor)
                rb.setStyleSheet("""
                    QRadioButton { 
                        font-size: 16px; 
                        padding: 5px;
                        color: #555;
                    }
                    QRadioButton::indicator {
                        width: 18px;
                        height: 18px;
                    }
                """)
                opts_layout.addWidget(rb)
                bgroup.addButton(rb, id=i)
            
            # Etiqueta Mayor
            lbl_high = QLabel("(5) Muy fácil")
            lbl_high.setStyleSheet("color: #999; font-size: 12px; margin-left: 10px;")
            opts_layout.addWidget(lbl_high)
            
            opts_layout.addStretch()
            q_layout.addLayout(opts_layout)
            
            self.content_layout.addWidget(q_widget)
            
        self.content_layout.addSpacing(10)
        
        # Comentarios libres
        com_widget = QWidget()
        com_layout = QVBoxLayout(com_widget)
        com_layout.setContentsMargins(0, 0, 0, 0)
        com_lbl = QLabel("Comentarios adicionales (Opcional):")
        com_lbl.setStyleSheet("font-weight: 600; font-size: 16px; color: #333;")
        com_layout.addWidget(com_lbl)
        
        self.txt_comments = QTextEdit()
        self.txt_comments.setFixedHeight(100)
        self.txt_comments.setPlaceholderText("Comentarios sobre tu experiencia...")
        self.txt_comments.setStyleSheet("""
            QTextEdit {
                border: 1px solid #D0D0D0; 
                border-radius: 6px; 
                padding: 10px;
                font-size: 14px;
                background-color: #FAFAFA;
            }
            QTextEdit:focus {
                border: 1px solid #7E38B7;
                background-color: white;
            }
        """)
        com_layout.addWidget(self.txt_comments)
        
        self.content_layout.addWidget(com_widget)
        self.content_layout.addStretch()
        
        scroll.setWidget(content_widget)
        
        # Añadir padding lateral en la ventana principal para dar el efecto flotante a la tarjeta
        main_content_layout = QHBoxLayout()
        main_content_layout.setContentsMargins(20, 20, 20, 0)
        main_content_layout.addWidget(scroll)
        main_layout.addLayout(main_content_layout)
        
        # Submit BTN
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(20, 15, 20, 20)
        
        btn_submit = QPushButton("Enviar y Finalizar Prueba")
        btn_submit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_submit = btn_submit
        btn_submit.setStyleSheet("""
            QPushButton {
                background-color: #7E38B7;
                color: white;
                font-weight: bold;
                font-size: 16px;
                padding: 14px 40px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #632C94;
            }
        """)
        btn_submit.clicked.connect(self.save_survey)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_submit)
        btn_layout.addStretch()
        
        main_layout.addLayout(btn_layout)

    def save_survey(self):
        results = {}
        
        # Check all questions are answered
        for key, text in self.questions_data:
            bgroup = self.button_groups[key]
            checked_id = bgroup.checkedId()
            if checked_id == -1: # No option selected
                QMessageBox.warning(self, "Campos Incompletos", "Por favor califica todas las preguntas para que tu encuesta sea válida.")
                return
            results[key] = checked_id
            
        results["comments"] = self.txt_comments.toPlainText().strip()
        
        # Save to session manager
        session_manager.survey = results
        
        # Success Box
        msg = QMessageBox(self)
        msg.setWindowTitle("Encuesta Completada")
        msg.setText("¡Muchas gracias por responder!\n\nHemos registrado tu respuesta correctamente.")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStyleSheet("""
            QLabel { color: #333; font-size: 14px; }
            QPushButton { background-color: #7E38B7; color: white; padding: 6px 15px; border-radius: 4px; font-weight: bold; }
        """)
        msg.exec()
        
        self.accept()
